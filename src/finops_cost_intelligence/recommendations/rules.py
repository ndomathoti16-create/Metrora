"""Conservative recommendation rules over calculated facts only."""

from __future__ import annotations

from collections.abc import Iterable

from ..contracts.ai import Fact, Recommendation


def _fact_map(facts: Iterable[Fact]) -> dict[str, Fact]:
    return {fact.fact_id: fact for fact in facts}


def generate_recommendations(
    facts: Iterable[Fact],
    *,
    quality_status: str,
    quality_ready: bool,
) -> tuple[Recommendation, ...]:
    """Return investigation or operating actions supported by available facts.

    Billing-only evidence does not justify claiming a specific savings amount.
    Rules therefore use language such as ``investigate`` and cite the underlying
    fact identifiers instead of inventing optimization values.
    """
    fact_map = _fact_map(facts)
    recommendations: list[Recommendation] = []

    if not quality_ready:
        recommendations.append(
            Recommendation(
                recommendation_id="data_quality_blocker",
                title="Resolve blocking data-quality issues",
                priority="high",
                action=(
                    "Correct required-field, normalization, or reconciliation "
                    "failures before using the analysis operationally."
                ),
                rationale=(
                    f"The current run is marked {quality_status} and is not ready "
                    "for analysis."
                ),
                evidence_strength="verified",
                fact_ids=(),
            )
        )

    budget_variance = fact_map.get("budget_variance_amount")
    if budget_variance is not None and float(budget_variance.value) > 0:
        recommendations.append(
            Recommendation(
                recommendation_id="budget_overrun_investigation",
                title="Investigate the budget overrun",
                priority="high",
                action=(
                    "Review the largest service or ownership drivers behind the "
                    "positive variance and confirm whether the budget or workload "
                    "changed."
                ),
                rationale=f"Actual cost is {budget_variance.value:,.2f} above the supplied budget.",
                evidence_strength="verified",
                fact_ids=("budget_variance_amount",),
            )
        )

    allocation = fact_map.get("allocation_cost_coverage")
    if allocation is not None and float(allocation.value) < 0.80:
        recommendations.append(
            Recommendation(
                recommendation_id="allocation_coverage_improvement",
                title="Improve ownership coverage",
                priority="medium",
                action=(
                    "Prioritize tagging or allocation rules for unowned positive "
                    "spend so future reviews can reach the responsible team faster."
                ),
                rationale=(
                    f"Only {float(allocation.value):.1%} of positive spend has an "
                    "ownership field in the selected data."
                ),
                evidence_strength="verified",
                fact_ids=("allocation_cost_coverage",),
            )
        )

    anomalies = fact_map.get("anomaly_count")
    if anomalies is not None and int(anomalies.value) > 0:
        recommendations.append(
            Recommendation(
                recommendation_id="anomaly_triage",
                title="Triage detected spend changes",
                priority="medium",
                action=(
                    "Review the flagged dates against deployments, traffic, incidents, "
                    "and provider rate changes before deciding whether action is needed."
                ),
                rationale=(
                    f"The historical scan identified {int(anomalies.value):,} "
                    "meaningful anomaly or anomalies."
                ),
                evidence_strength="verified",
                fact_ids=("anomaly_count",),
            )
        )

    top_share = fact_map.get("top_service_share")
    top_service = fact_map.get("top_service")
    if top_share is not None and top_service is not None and float(top_share.value) >= 0.50:
        recommendations.append(
            Recommendation(
                recommendation_id="top_service_driver_review",
                title="Review the dominant service driver",
                priority="low",
                action=(
                    f"Decompose {top_service.value} by account, project, environment, "
                    "and usage type before evaluating optimization opportunities."
                ),
                rationale=(
                    f"{top_service.value} represents "
                    f"{float(top_share.value):.1%} of selected-period spend."
                ),
                evidence_strength="verified",
                fact_ids=("top_service", "top_service_share"),
            )
        )

    if not recommendations:
        recommendations.append(
            Recommendation(
                recommendation_id="continue_monitoring",
                title="Continue monitoring the selected period",
                priority="low",
                action=(
                    "Keep the dashboard filters and data-quality checks consistent "
                    "in the next review so changes remain comparable."
                ),
                rationale=(
                    "No rule-based risk or coverage threshold was triggered by the "
                    "available evidence."
                ),
                evidence_strength="verified",
                fact_ids=(),
            )
        )
    return tuple(recommendations)
