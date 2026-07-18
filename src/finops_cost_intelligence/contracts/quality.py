"""Contracts for data-quality checks and reconciliation decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ReconciliationResult:
    """Comparison of the source-derived and canonical cost totals."""

    source_total: float | None
    canonical_total: float | None
    absolute_difference: float | None
    relative_difference: float | None
    tolerance: float
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QualityCheckResult:
    """One quality assertion with evidence and analytical impact."""

    check_name: str
    status: str
    severity: str
    observed_value: Any
    expected_value: Any
    affected_rows: int
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QualityReport:
    """Complete quality decision for one normalized ingestion run."""

    ingestion_id: str
    source_name: str
    rows_in: int
    rows_out: int
    overall_status: str
    ready_for_analysis: bool
    reconciliation: ReconciliationResult
    checks: tuple[QualityCheckResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ingestion_id": self.ingestion_id,
            "source_name": self.source_name,
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "overall_status": self.overall_status,
            "ready_for_analysis": self.ready_for_analysis,
            "reconciliation": self.reconciliation.to_dict(),
            "checks": [check.to_dict() for check in self.checks],
        }
