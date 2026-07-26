"""Contracts for explainable cloud-spend anomaly detection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AnomalySummary:
    """Metadata for a leakage-safe historical anomaly scan."""

    method: str
    threshold: float
    window_days: int
    minimum_history_days: int
    anomaly_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
