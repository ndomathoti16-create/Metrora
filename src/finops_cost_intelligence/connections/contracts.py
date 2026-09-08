"""Shared contracts for read-only cloud billing connections."""

from __future__ import annotations

import gzip
import io
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import PurePosixPath

import pandas as pd

from ..ingestion.readers import LoadedTable, load_table


class CloudConnectionError(RuntimeError):
    """Raised when a cloud export cannot be discovered or imported safely."""


class CloudDependencyError(CloudConnectionError):
    """Raised when an optional cloud SDK is not installed."""


@dataclass(frozen=True)
class RemoteBillingObject:
    """One data object discovered in a provider-managed export location."""

    key: str
    size_bytes: int
    last_modified: datetime

    @property
    def parent(self) -> str:
        """Return the normalized remote parent path."""
        parent = str(PurePosixPath(self.key).parent)
        return "" if parent == "." else parent


@dataclass(frozen=True)
class CloudSyncResult:
    """A cloud import plus the operational metadata shown in the workspace."""

    provider: str
    source_uri: str
    loaded_table: LoadedTable
    object_count: int
    total_bytes: int
    latest_modified: datetime
    synced_at: datetime


SUPPORTED_REMOTE_SUFFIXES = (".csv", ".csv.gz", ".parquet")
DEFAULT_CLOUD_IMPORT_LIMIT_BYTES = 200 * 1024 * 1024


def _size_label(size_bytes: int) -> str:
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def validate_max_bytes(max_bytes: int | None) -> None:
    """Validate an optional connector import limit."""
    if max_bytes is not None and max_bytes <= 0:
        raise ValueError("max_bytes must be greater than zero when provided.")


def enforce_size_limit(size_bytes: int, max_bytes: int | None, *, label: str) -> None:
    """Reject an advertised or observed payload size above the configured limit."""
    validate_max_bytes(max_bytes)
    if max_bytes is not None and size_bytes > max_bytes:
        raise CloudConnectionError(
            f"{label} is {_size_label(size_bytes)}, above the configured "
            f"{_size_label(max_bytes)} import limit."
        )


def enforce_batch_limit(
    objects: list[RemoteBillingObject], max_bytes: int | None, *, provider: str
) -> None:
    """Reject a discovered export batch before any object is downloaded."""
    advertised_size = sum(max(0, item.size_bytes) for item in objects)
    enforce_size_limit(advertised_size, max_bytes, label=f"{provider} export batch")


def is_supported_billing_object(key: str) -> bool:
    """Return whether a remote object is a supported tabular billing payload."""
    normalized = key.casefold()
    return normalized.endswith(SUPPORTED_REMOTE_SUFFIXES) and not normalized.endswith(
        ("manifest.csv", "manifest.json")
    )


def select_latest_batch(
    objects: list[RemoteBillingObject],
    *,
    configured_prefix: str = "",
) -> list[RemoteBillingObject]:
    """Select every chunk belonging to the newest provider export batch.

    AWS and Azure can split one export into multiple files under one run directory.
    Objects in that directory must be combined; unrelated files at the configured root
    remain separate batches so an old export is never silently appended to a new one.
    """
    if not objects:
        raise CloudConnectionError(
            "No CSV, CSV.GZ, or Parquet billing files were found at this location."
        )

    root = configured_prefix.strip("/")
    batches: dict[str, list[RemoteBillingObject]] = {}
    for remote_object in objects:
        parent = remote_object.parent.strip("/")
        batch_key = remote_object.key if parent in {"", root} else parent
        batches.setdefault(batch_key, []).append(remote_object)

    newest_key = max(
        batches,
        key=lambda key: max(item.last_modified for item in batches[key]),
    )
    return sorted(batches[newest_key], key=lambda item: item.key.casefold())


def _load_remote_payload(
    key: str,
    payload: bytes,
    *,
    max_bytes: int | None = DEFAULT_CLOUD_IMPORT_LIMIT_BYTES,
) -> LoadedTable:
    source_name = PurePosixPath(key).name
    enforce_size_limit(len(payload), max_bytes, label=f"Billing object {source_name!r}")
    if source_name.casefold().endswith(".csv.gz"):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(payload)) as compressed:
                payload = compressed.read(None if max_bytes is None else max_bytes + 1)
        except (OSError, EOFError) as exc:
            raise CloudConnectionError(
                f"The compressed billing object {source_name!r} could not be opened."
            ) from exc
        enforce_size_limit(
            len(payload),
            max_bytes,
            label=f"Decompressed billing object {source_name!r}",
        )
        source_name = source_name[:-3]
    try:
        return load_table(payload, source_name=source_name, max_bytes=max_bytes)
    except Exception as exc:
        raise CloudConnectionError(
            f"The billing object {source_name!r} could not be parsed: {exc}"
        ) from exc


def combine_remote_payloads(
    payloads: list[tuple[RemoteBillingObject, bytes]],
    *,
    source_uri: str,
    max_bytes: int | None = DEFAULT_CLOUD_IMPORT_LIMIT_BYTES,
) -> LoadedTable:
    """Combine all chunks in one export batch into one lineage-preserving table."""
    if not payloads:
        raise CloudConnectionError("The selected export batch did not contain any data files.")

    validate_max_bytes(max_bytes)
    enforce_size_limit(
        sum(len(payload) for _, payload in payloads),
        max_bytes,
        label="Downloaded export batch",
    )
    tables: list[LoadedTable] = []
    logical_bytes = 0
    for item, payload in payloads:
        remaining_bytes = None if max_bytes is None else max_bytes - logical_bytes
        if remaining_bytes is not None and remaining_bytes <= 0:
            raise CloudConnectionError(
                "Expanded export batch reached the configured import limit before every "
                "file could be parsed."
            )
        table = _load_remote_payload(item.key, payload, max_bytes=remaining_bytes)
        logical_bytes += table.source_size_bytes or len(payload)
        enforce_size_limit(logical_bytes, max_bytes, label="Expanded export batch")
        tables.append(table)
    try:
        dataframe = pd.concat(
            [table.dataframe for table in tables],
            ignore_index=True,
            sort=False,
        )
    except (TypeError, ValueError) as exc:
        raise CloudConnectionError(
            "The files in the latest export batch could not be combined into one table."
        ) from exc

    dataframe_bytes = int(dataframe.memory_usage(index=True, deep=True).sum())
    enforce_size_limit(dataframe_bytes, max_bytes, label="Imported billing table in memory")

    formats = sorted({table.file_format for table in tables})
    return LoadedTable(
        dataframe=dataframe,
        source_name=source_uri,
        file_format=formats[0] if len(formats) == 1 else "cloud-export",
        source_size_bytes=sum(item.size_bytes for item, _ in payloads),
    )


def utc_now() -> datetime:
    """Return one timezone-aware timestamp for sync and audit records."""
    return datetime.now(UTC)
