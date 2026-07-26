"""Contracts and errors used by deterministic FinOps analytics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class AnalyticsInputError(ValueError):
    """Raised when a canonical billing table cannot support an analysis."""


@dataclass(frozen=True)
class SpendSummary:
    """Calculated spend KPIs for an explicitly selected analysis period."""

    total_cost: float
    row_count: int
    calendar_days: int
    average_daily_cost: float
    date_start: str | None
    date_end: str | None
    currency: str
    prior_period_cost: float | None
    change_amount: float | None
    change_pct: float | None
    top_dimension: str | None = None
    top_dimension_cost: float | None = None
    top_dimension_share: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation for reports and AI prompts."""
        return asdict(self)
