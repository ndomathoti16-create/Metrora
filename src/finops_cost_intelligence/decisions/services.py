"""Create, merge, and export accountable decisions from calculated evidence."""

from __future__ import annotations

import io
import json
from dataclasses import replace
from hashlib import sha256

import pandas as pd

from ..contracts.ai import FactPack, Recommendation
from .models import DecisionRecord

IMPACT_FACTS = {
    "recent_spend_increase_review": ("spend_change_amount", "observed_spend_movement"),
    "recent_spend_decrease_confirmation": (
        "spend_change_amount",
        "observed_spend_movement",
    ),
    "budget_overrun_investigation": (
        "budget_variance_amount",
        "observed_budget_variance",
    ),
    "forecast_run_rate_review": ("forecast_change_amount", "modeled_forecast_gap"),
    "allocation_coverage_improvement": (
        "unallocated_positive_spend",
        "observed_unallocated_spend",
    ),
    "anomaly_triage": (
        "anomaly_estimated_increase_total",
        "observed_baseline_deviation",
    ),
    "top_service_driver_review": (
        "service_mover_1_change_amount",
        "observed_spend_movement",
    ),
}

CATEGORIES = {
    "data_quality_blocker": "Data quality",
    "recent_spend_increase_review": "Cost change",
    "recent_spend_decrease_confirmation": "Cost change",
    "budget_overrun_investigation": "Budget",
    "forecast_run_rate_review": "Forecast",
    "allocation_coverage_improvement": "Allocation",
    "anomaly_triage": "Anomaly",
    "top_service_driver_review": "Cost driver",
}


def _stable_id(source_name: str, recommendation_id: str) -> str:
    signature = sha256(f"{source_name.casefold()}|{recommendation_id}".encode()).hexdigest()[:20]
    return f"metrora-{signature}"


def _impact_for(
    recommendation: Recommendation, fact_pack: FactPack
) -> tuple[str, float | None, str]:
    fact_id, impact_kind = IMPACT_FACTS.get(
        recommendation.recommendation_id,
        ("", "not_quantified"),
    )
    facts = {fact.fact_id: fact for fact in fact_pack.facts}
    fact = facts.get(fact_id)
    if fact is None or not isinstance(fact.value, (int, float)):
        return impact_kind, None, "Unspecified"
    currency = fact.unit if fact.unit not in {"", "share", "cost units"} else "Unspecified"
    return impact_kind, float(fact.value), currency


def recommendation_to_decision(
    recommendation: Recommendation,
    fact_pack: FactPack,
) -> DecisionRecord:
    """Translate one evidence-bounded recommendation without inventing savings."""
    impact_kind, impact_amount, currency = _impact_for(recommendation, fact_pack)
    criticality = "High" if recommendation.priority == "high" else "Medium"
    return DecisionRecord(
        decision_id=_stable_id(fact_pack.source_name, recommendation.recommendation_id),
        title=recommendation.title,
        category=CATEGORIES.get(recommendation.recommendation_id, "Operating review"),
        status="Proposed",
        source_kind="Metrora calculated signal",
        source_reference=recommendation.recommendation_id,
        evidence_summary=f"{recommendation.rationale} {recommendation.action}".strip(),
        evidence_strength=recommendation.evidence_strength,
        impact_kind=impact_kind,
        impact_amount=impact_amount,
        currency=currency,
        owner=recommendation.owner or "Unassigned",
        target_timing=recommendation.timeframe,
        effort="Unknown",
        operational_risk="Unknown",
        business_criticality=criticality,
        provider="Metrora",
        metadata={
            "ingestion_id": fact_pack.ingestion_id,
            "source_name": fact_pack.source_name,
            "fact_ids": list(recommendation.fact_ids),
            "priority": recommendation.priority,
        },
    )


def recommendations_to_decisions(fact_pack: FactPack) -> list[DecisionRecord]:
    """Build only actionable records; a continue-monitoring message is not work."""
    return [
        recommendation_to_decision(item, fact_pack)
        for item in fact_pack.recommendations
        if item.recommendation_id != "continue_monitoring"
    ]


def merge_decisions(
    existing: list[DecisionRecord],
    incoming: list[DecisionRecord],
) -> list[DecisionRecord]:
    """Refresh evidence while preserving human workflow choices and measured outcomes."""
    indexed = {item.decision_id: item for item in existing}
    for candidate in incoming:
        current = indexed.get(candidate.decision_id)
        if current is None:
            indexed[candidate.decision_id] = candidate
            continue
        indexed[candidate.decision_id] = replace(
            candidate,
            status=current.status,
            owner=current.owner,
            due_date=current.due_date,
            effort=current.effort,
            operational_risk=current.operational_risk,
            business_criticality=current.business_criticality,
            decision_note=current.decision_note,
            rejection_reason=current.rejection_reason,
            baseline_cost=current.baseline_cost,
            post_change_cost=current.post_change_cost,
            baseline_period=current.baseline_period,
            measurement_period=current.measurement_period,
            created_at=current.created_at,
        )
    return sorted(indexed.values(), key=lambda item: (item.created_at, item.decision_id))


def decisions_json_bytes(decisions: list[DecisionRecord]) -> bytes:
    return json.dumps(
        {"schema_version": "1.0", "decisions": [item.to_dict() for item in decisions]},
        indent=2,
        default=str,
    ).encode("utf-8")


def decisions_csv_bytes(decisions: list[DecisionRecord]) -> bytes:
    records = []
    for item in decisions:
        payload = item.to_dict()
        payload.pop("metadata", None)
        records.append(payload)
    dataframe = pd.DataFrame.from_records(records)
    output = io.StringIO()
    dataframe.to_csv(output, index=False)
    return output.getvalue().encode("utf-8")
