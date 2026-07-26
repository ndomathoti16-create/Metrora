"""Contracts for budget uploads and actual-versus-budget analysis."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class BudgetValidationError(ValueError):
    """Raised when a budget upload cannot be normalized safely."""


@dataclass(frozen=True)
class BudgetVarianceSummary:
    """Totals for an actual-versus-budget comparison."""

    budget_total: float
    actual_total: float
    variance_amount: float
    utilization_pct: float | None
    rows_compared: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
