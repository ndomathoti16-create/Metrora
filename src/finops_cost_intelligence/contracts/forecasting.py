"""Contracts for deterministic cloud-spend forecasting."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class ForecastInputError(ValueError):
    """Raised when a spend history cannot support a forecast."""


@dataclass(frozen=True)
class ForecastSummary:
    """Metadata and aggregate output for one forecast run."""

    method: str
    history_start: str
    history_end: str
    horizon_days: int
    forecast_total: float
    residual_std: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
