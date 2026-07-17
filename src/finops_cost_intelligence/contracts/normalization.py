"""Contracts for canonicalized billing output and conversion diagnostics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizationIssue:
    """One source value that could not be converted cleanly."""

    source_row_number: int
    canonical_field: str
    source_column: str
    severity: str
    message: str
    raw_value: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NormalizationReport:
    """Aggregate normalization results without hiding invalid rows."""

    rows_in: int
    rows_out: int
    rows_with_issues: int
    issue_count: int
    issue_counts_by_field: dict[str, int]
    issues: tuple[NormalizationIssue, ...]
    issue_sample_limit: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "rows_with_issues": self.rows_with_issues,
            "issue_count": self.issue_count,
            "issue_counts_by_field": dict(self.issue_counts_by_field),
            "issues": [issue.to_dict() for issue in self.issues],
            "issue_sample_limit": self.issue_sample_limit,
        }


@dataclass(frozen=True)
class NormalizedTable:
    """Canonical billing DataFrame plus the accepted mapping and diagnostics."""

    dataframe: Any
    mapping: dict[str, str | None]
    ingestion_id: str
    source_name: str
    report: NormalizationReport

    def to_dict(self) -> dict[str, Any]:
        return {
            "mapping": dict(self.mapping),
            "ingestion_id": self.ingestion_id,
            "source_name": self.source_name,
            "report": self.report.to_dict(),
        }
