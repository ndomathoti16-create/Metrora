"""Read-only AWS Data Exports and CUR ingestion from Amazon S3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import PurePosixPath
from typing import Any

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)

from .contracts import (
    CloudConnectionError,
    CloudSyncResult,
    RemoteBillingObject,
    combine_remote_payloads,
    is_supported_billing_object,
    select_latest_batch,
    utc_now,
)


@dataclass(frozen=True)
class AwsS3ExportConfig:
    """Non-secret configuration for an AWS billing export in S3."""

    bucket: str
    prefix: str = ""
    region: str = "us-east-1"
    profile_name: str | None = None
    expected_bucket_owner: str | None = None

    def __post_init__(self) -> None:
        if not self.bucket.strip():
            raise ValueError("An S3 bucket name is required.")
        if not self.region.strip():
            raise ValueError("An AWS region is required.")
        if ".." in PurePosixPath(self.prefix).parts:
            raise ValueError("The S3 prefix cannot traverse parent paths.")
        owner = (self.expected_bucket_owner or "").strip()
        if owner and (not owner.isdigit() or len(owner) != 12):
            raise ValueError("Expected bucket owner must be a 12-digit AWS account ID.")

    @property
    def normalized_prefix(self) -> str:
        return self.prefix.strip().strip("/")


class AwsS3BillingConnector:
    """Discover and download the latest complete billing-export batch from S3."""

    provider = "AWS"

    def __init__(self, config: AwsS3ExportConfig, *, client: Any | None = None) -> None:
        self.config = config
        self._client = client

    @property
    def client(self):
        if self._client is None:
            session = boto3.Session(
                profile_name=(self.config.profile_name or None),
                region_name=self.config.region,
            )
            self._client = session.client("s3", region_name=self.config.region)
        return self._client

    def _request(self) -> dict[str, str]:
        request = {
            "Bucket": self.config.bucket.strip(),
            "Prefix": self.config.normalized_prefix,
        }
        if self.config.expected_bucket_owner:
            request["ExpectedBucketOwner"] = self.config.expected_bucket_owner.strip()
        return request

    def list_objects(self) -> list[RemoteBillingObject]:
        """List supported billing objects without downloading their contents."""
        request = self._request()
        discovered: list[RemoteBillingObject] = []
        try:
            paginator_factory = getattr(self.client, "get_paginator", None)
            if callable(paginator_factory):
                pages = paginator_factory("list_objects_v2").paginate(**request)
            else:
                pages = [self.client.list_objects_v2(**request)]
            for page in pages:
                for item in page.get("Contents", []):
                    key = str(item.get("Key", ""))
                    if not is_supported_billing_object(key):
                        continue
                    modified = item.get("LastModified") or datetime.now(UTC)
                    if modified.tzinfo is None:
                        modified = modified.replace(tzinfo=UTC)
                    discovered.append(
                        RemoteBillingObject(
                            key=key,
                            size_bytes=int(item.get("Size", 0) or 0),
                            last_modified=modified,
                        )
                    )
        except (BotoCoreError, ClientError, NoCredentialsError, PartialCredentialsError) as exc:
            raise CloudConnectionError(
                "AWS could not list this export. Confirm the selected AWS profile or role "
                "has s3:ListBucket permission for the bucket and prefix."
            ) from exc
        return discovered

    def sync_latest(self) -> CloudSyncResult:
        """Download and combine the newest complete AWS billing-export batch."""
        batch = select_latest_batch(
            self.list_objects(),
            configured_prefix=self.config.normalized_prefix,
        )
        payloads: list[tuple[RemoteBillingObject, bytes]] = []
        try:
            for item in batch:
                request = {"Bucket": self.config.bucket.strip(), "Key": item.key}
                if self.config.expected_bucket_owner:
                    request["ExpectedBucketOwner"] = self.config.expected_bucket_owner.strip()
                response = self.client.get_object(**request)
                payloads.append((item, bytes(response["Body"].read())))
        except (BotoCoreError, ClientError, NoCredentialsError, PartialCredentialsError) as exc:
            raise CloudConnectionError(
                "AWS could not download the latest export. Confirm the selected identity "
                "has s3:GetObject permission for every export chunk."
            ) from exc
        except (KeyError, OSError, TypeError, ValueError) as exc:
            raise CloudConnectionError("AWS returned an unreadable billing object.") from exc

        parent = batch[0].parent or batch[0].key
        source_uri = f"s3://{self.config.bucket.strip()}/{parent}"
        loaded = combine_remote_payloads(payloads, source_uri=source_uri)
        return CloudSyncResult(
            provider=self.provider,
            source_uri=source_uri,
            loaded_table=loaded,
            object_count=len(batch),
            total_bytes=sum(item.size_bytes for item in batch),
            latest_modified=max(item.last_modified for item in batch),
            synced_at=utc_now(),
        )
