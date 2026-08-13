"""Small, credential-free-at-import S3 adapter for standardized Parquet files."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import boto3
import pandas as pd
from botocore.exceptions import BotoCoreError, ClientError

from ..contracts.normalization import NormalizedTable


class S3StorageError(RuntimeError):
    """Raised when an S3 operation cannot be completed."""


def _validate_key(key: str) -> str:
    normalized = key.strip().lstrip("/")
    if not normalized or normalized.endswith("/"):
        raise S3StorageError("An S3 object key must contain a file name.")
    if ".." in Path(normalized).parts:
        raise S3StorageError("S3 object keys cannot traverse parent paths.")
    return normalized


class S3Storage:
    """Upload and download bytes without requiring AWS at local-app startup."""

    def __init__(
        self,
        bucket: str,
        *,
        region: str = "us-east-1",
        client: Any | None = None,
    ) -> None:
        if not bucket.strip():
            raise S3StorageError("An S3 bucket is required.")
        if not region.strip():
            raise S3StorageError("An AWS region is required.")
        self.bucket = bucket.strip()
        self.region = region.strip()
        self.client = client or boto3.client("s3", region_name=self.region)

    def uri(self, key: str) -> str:
        """Return the safe S3 URI for a validated object key."""
        return f"s3://{self.bucket}/{_validate_key(key)}"

    def upload_bytes(
        self,
        payload: bytes,
        key: str,
        *,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload bytes and return their S3 URI."""
        if not isinstance(payload, bytes):
            raise S3StorageError("S3 uploads require bytes payloads.")
        object_key = _validate_key(key)
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=payload,
                ContentType=content_type,
            )
        except (BotoCoreError, ClientError, OSError) as exc:
            raise S3StorageError(f"Could not upload s3://{self.bucket}/{object_key}.") from exc
        return self.uri(object_key)

    def upload_dataframe(self, dataframe: pd.DataFrame, key: str) -> str:
        """Serialize a DataFrame to Parquet in memory and upload it."""
        buffer = io.BytesIO()
        try:
            dataframe.to_parquet(buffer, index=False)
        except (OSError, TypeError, ValueError) as exc:
            raise S3StorageError("Could not serialize the DataFrame as Parquet.") from exc
        return self.upload_bytes(
            buffer.getvalue(),
            key,
            content_type="application/vnd.apache.parquet",
        )

    def upload_normalized(
        self,
        normalized: NormalizedTable,
        *,
        prefix: str = "standardized/cloud_cost",
    ) -> str:
        """Upload one canonical ingestion as a lineage-preserving Parquet object."""
        safe_prefix = prefix.strip().strip("/")
        if not safe_prefix:
            raise S3StorageError("The standardized S3 prefix cannot be empty.")
        key = f"{safe_prefix}/{normalized.ingestion_id}.parquet"
        return self.upload_dataframe(normalized.dataframe, key)

    def download_bytes(self, key: str) -> bytes:
        """Download one object as bytes."""
        object_key = _validate_key(key)
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=object_key)
            return bytes(response["Body"].read())
        except (BotoCoreError, ClientError, OSError, KeyError, TypeError) as exc:
            raise S3StorageError(f"Could not download s3://{self.bucket}/{object_key}.") from exc
