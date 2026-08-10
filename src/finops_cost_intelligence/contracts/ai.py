"""Structured contracts for evidence-backed summaries and recommendations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Fact:
    """One calculated value that can be cited by a recommendation or summary."""

    fact_id: str
    label: str
    value: Any
    unit: str
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Recommendation:
    """An evidence-bounded operational recommendation."""

    recommendation_id: str
    title: str
    priority: str
    action: str
    rationale: str
    evidence_strength: str
    fact_ids: tuple[str, ...]
    owner: str = "FinOps analyst"
    timeframe: str = "Before the next cost review"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"fact_ids": list(self.fact_ids)}


@dataclass(frozen=True)
class FactPack:
    """Versioned analytical evidence supplied to a summary layer."""

    schema_version: str
    generated_at: str
    ingestion_id: str
    source_name: str
    period_start: str | None
    period_end: str | None
    filters: dict[str, Any]
    quality_status: str
    quality_ready: bool
    facts: tuple[Fact, ...]
    recommendations: tuple[Recommendation, ...]
    caveats: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "ingestion_id": self.ingestion_id,
            "source_name": self.source_name,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "filters": dict(self.filters),
            "quality_status": self.quality_status,
            "quality_ready": self.quality_ready,
            "facts": [fact.to_dict() for fact in self.facts],
            "recommendations": [
                recommendation.to_dict() for recommendation in self.recommendations
            ],
            "caveats": list(self.caveats),
        }


@dataclass(frozen=True)
class SummaryResult:
    """Reader-facing summary with traceable fact and recommendation references."""

    headline: str
    bullets: tuple[str, ...]
    recommendation_ids: tuple[str, ...]
    used_fact_ids: tuple[str, ...]
    caveats: tuple[str, ...]
    provider: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            "bullets": list(self.bullets),
            "recommendation_ids": list(self.recommendation_ids),
            "used_fact_ids": list(self.used_fact_ids),
            "caveats": list(self.caveats),
        }
