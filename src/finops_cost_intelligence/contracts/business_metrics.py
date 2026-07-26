"""Contracts for business metric uploads and unit economics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class BusinessMetricValidationError(ValueError):
    """Raised when a business metric upload is not analytically usable."""


@dataclass(frozen=True)
class UnitEconomicsSummary:
    """Cost and business-volume totals for one selected metric."""

    metric_name: str
    total_cost: float
    total_metric_value: float
    cost_per_unit: float | None
    days_with_metric: int
    days_without_cost: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
