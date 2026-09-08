"""Read-only Azure Cost Management export ingestion from Blob Storage."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlparse

from .contracts import (
    DEFAULT_CLOUD_IMPORT_LIMIT_BYTES,
    CloudConnectionError,
    CloudDependencyError,
    CloudSyncResult,
    RemoteBillingObject,
    combine_remote_payloads,
    enforce_batch_limit,
    enforce_size_limit,
    is_supported_billing_object,
    select_latest_batch,
    utc_now,
)

_AZURE_BLOB_HOST_SUFFIXES = (
    "blob.core.windows.net",
    "blob.core.usgovcloudapi.net",
    "blob.core.chinacloudapi.cn",
    "blob.core.cloudapi.de",
)
_STORAGE_ACCOUNT_PATTERN = re.compile(r"^[a-z0-9]{3,24}$")


@dataclass(frozen=True)
class AzureBlobExportConfig:
    """Non-secret configuration for a scheduled Azure Cost Management export."""

    account_url: str
    container: str
    prefix: str = ""

    def __post_init__(self) -> None:
        parsed = urlparse(self.account_url.strip())
        try:
            port = parsed.port
        except ValueError as exc:
            raise ValueError("Azure storage account URL contains an invalid port.") from exc
        hostname = (parsed.hostname or "").casefold()
        account_name = next(
            (
                hostname[: -(len(suffix) + 1)]
                for suffix in _AZURE_BLOB_HOST_SUFFIXES
                if hostname.endswith(f".{suffix}")
            ),
            "",
        )
        invalid_url_parts = (
            parsed.scheme != "https"
            or not hostname
            or parsed.username is not None
            or parsed.password is not None
            or port is not None
            or parsed.path not in {"", "/"}
            or bool(parsed.params or parsed.query or parsed.fragment)
        )
        if invalid_url_parts or not _STORAGE_ACCOUNT_PATTERN.fullmatch(account_name):
            raise ValueError(
                "Enter a direct Azure Blob Storage account URL, for example "
                "https://companycosts.blob.core.windows.net. Custom domains and "
                "non-Azure hosts are not accepted because this connection uses your "
                "Azure identity."
            )
        container = self.container.strip()
        if not container:
            raise ValueError("An Azure Blob container is required.")
        if ".." in PurePosixPath(self.prefix).parts:
            raise ValueError("The Azure blob prefix cannot traverse parent paths.")

    @property
    def normalized_prefix(self) -> str:
        return self.prefix.strip().strip("/")


class AzureBlobBillingConnector:
    """Discover and import the latest Azure Cost Management export batch."""

    provider = "Azure"

    def __init__(
        self,
        config: AzureBlobExportConfig,
        *,
        container_client: Any | None = None,
        max_bytes: int | None = DEFAULT_CLOUD_IMPORT_LIMIT_BYTES,
    ) -> None:
        self.config = config
        self._container_client = container_client
        self.max_bytes = max_bytes or DEFAULT_CLOUD_IMPORT_LIMIT_BYTES
        enforce_size_limit(0, self.max_bytes, label="Azure export batch")

    @property
    def container_client(self):
        if self._container_client is None:
            try:
                from azure.identity import DefaultAzureCredential
                from azure.storage.blob import BlobServiceClient
            except ImportError as exc:
                raise CloudDependencyError(
                    'Azure connections require the cloud extras. Install with "pip install '
                    '-e .[cloud]" or use the packaged Metrora desktop release.'
                ) from exc
            credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
            service = BlobServiceClient(
                account_url=self.config.account_url.strip().rstrip("/"),
                credential=credential,
            )
            self._container_client = service.get_container_client(self.config.container.strip())
        return self._container_client

    def list_objects(self) -> list[RemoteBillingObject]:
        """List supported export blobs using the current Azure identity."""
        discovered: list[RemoteBillingObject] = []
        try:
            blobs = self.container_client.list_blobs(
                name_starts_with=self.config.normalized_prefix or None
            )
            for blob in blobs:
                key = str(getattr(blob, "name", ""))
                if not is_supported_billing_object(key):
                    continue
                modified = getattr(blob, "last_modified", None) or datetime.now(UTC)
                if modified.tzinfo is None:
                    modified = modified.replace(tzinfo=UTC)
                discovered.append(
                    RemoteBillingObject(
                        key=key,
                        size_bytes=int(getattr(blob, "size", 0) or 0),
                        last_modified=modified,
                    )
                )
        except CloudDependencyError:
            raise
        except CloudConnectionError:
            raise
        except Exception as exc:
            raise CloudConnectionError(
                "Azure could not list this export. Sign in with Azure CLI or a managed "
                "identity and confirm Storage Blob Data Reader access to the container."
            ) from exc
        return discovered

    def sync_latest(self) -> CloudSyncResult:
        """Download and combine the newest Azure export batch."""
        batch = select_latest_batch(
            self.list_objects(),
            configured_prefix=self.config.normalized_prefix,
        )
        enforce_batch_limit(batch, self.max_bytes, provider="Azure")
        payloads: list[tuple[RemoteBillingObject, bytes]] = []
        downloaded_bytes = 0
        try:
            for item in batch:
                download = self.container_client.download_blob(item.key)
                remaining_bytes = (
                    None if self.max_bytes is None else self.max_bytes - downloaded_bytes
                )
                if remaining_bytes is None:
                    payload = bytes(download.readall())
                else:
                    payload_buffer = bytearray()
                    for chunk in download.chunks():
                        payload_buffer.extend(bytes(chunk))
                        enforce_size_limit(
                            len(payload_buffer),
                            remaining_bytes,
                            label=f"Azure billing object {item.key!r}",
                        )
                    payload = bytes(payload_buffer)
                downloaded_bytes += len(payload)
                enforce_size_limit(
                    downloaded_bytes,
                    self.max_bytes,
                    label="Downloaded Azure export batch",
                )
                payloads.append((item, payload))
        except CloudConnectionError:
            raise
        except Exception as exc:
            raise CloudConnectionError(
                "Azure could not download every file in the latest export batch. Confirm "
                "the current identity has read access to the complete export path."
            ) from exc

        parent = batch[0].parent or batch[0].key
        account = urlparse(self.config.account_url).netloc
        source_uri = f"azure://{account}/{self.config.container.strip()}/{parent}"
        loaded = combine_remote_payloads(
            payloads,
            source_uri=source_uri,
            max_bytes=self.max_bytes,
        )
        return CloudSyncResult(
            provider=self.provider,
            source_uri=source_uri,
            loaded_table=loaded,
            object_count=len(batch),
            total_bytes=sum(item.size_bytes for item in batch),
            latest_modified=max(item.last_modified for item in batch),
            synced_at=utc_now(),
        )
