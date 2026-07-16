"""Serializable data-profile contracts used by the ingestion workflow."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ColumnProfile:
    """Observed characteristics of one source column."""

    name: str
    dtype: str
    inferred_type: str
    row_count: int
    non_null_count: int
    null_count: int
    null_rate: float
    unique_count: int
    numeric_parse_rate: float
    datetime_parse_rate: float
    sample_values: tuple[Any, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary representation."""
        return asdict(self) | {"sample_values": list(self.sample_values)}


@dataclass(frozen=True)
class DataProfile:
    """Summary of a loaded tabular source before semantic mapping."""

    profile_version: str
    source_name: str
    file_format: str
    source_size_bytes: int | None
    sheet_name: str | None
    row_count: int
    column_count: int
    duplicate_row_count: int
    all_null_row_count: int
    memory_usage_bytes: int
    columns: tuple[ColumnProfile, ...]
    sample_rows: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary representation."""
        return {
            "profile_version": self.profile_version,
            "source_name": self.source_name,
            "file_format": self.file_format,
            "source_size_bytes": self.source_size_bytes,
            "sheet_name": self.sheet_name,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "duplicate_row_count": self.duplicate_row_count,
            "all_null_row_count": self.all_null_row_count,
            "memory_usage_bytes": self.memory_usage_bytes,
            "columns": [column.to_dict() for column in self.columns],
            "sample_rows": list(self.sample_rows),
        }

    def column_records(self) -> list[dict[str, Any]]:
        """Return column profiles in a format convenient for a UI table."""
        return [column.to_dict() for column in self.columns]
