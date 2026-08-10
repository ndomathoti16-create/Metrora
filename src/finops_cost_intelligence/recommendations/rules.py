"""Conservative recommendation rules over calculated facts only."""

from __future__ import annotations

from collections.abc import Iterable

from ..contracts.ai import Fact, Recommendation


def _fact_map(facts: Iterable[Fact]) -> dict[str, Fact]:
    return {fact.fact_id: fact for fact in facts}


def _amount(fact: Fact) -> str:
    prefix = f"{fact.unit} " if fact.unit not in {"", "cost units"} else ""
    return f"{prefix}{abs(float(fact.value)):,.2f}"


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
                    f"The current run is marked {quality_status} and is not ready for analysis."
                ),
                evidence_strength="verified",
                fact_ids=(),
                owner="Data owner + FinOps",
                timeframe="Before any operational use",
            )
        )

    period_change = fact_map.get("spend_change_amount")
    period_change_pct = fact_map.get("spend_change_pct")
    primary_mover = fact_map.get("service_mover_1_name")
    primary_mover_change = fact_map.get("service_mover_1_change_amount")
    if (
        period_change is not None
        and period_change_pct is not None
        and float(period_change.value) != 0
        and abs(float(period_change_pct.value)) >= 0.10
    ):
        is_increase = float(period_change.value) > 0
        driver_clause = ""
        fact_ids = ["spend_change_amount", "spend_change_pct"]
        if primary_mover is not None and primary_mover_change is not None:
            driver_clause = (
                f" Start with {primary_mover.value}, which moved by "
                f"{primary_mover_change.unit} {float(primary_mover_change.value):+,.2f}."
            )
            fact_ids.extend(("service_mover_1_name", "service_mover_1_change_amount"))
        recommendations.append(
            Recommendation(
                recommendation_id=(
                    "recent_spend_increase_review"
                    if is_increase
                    else "recent_spend_decrease_confirmation"
                ),
                title=(
                    "Confirm the latest spend increase"
                    if is_increase
                    else "Confirm the latest spend decrease"
                ),
                priority=(
                    "high" if is_increase and float(period_change_pct.value) >= 0.25 else "medium"
                ),
                action=(
                    (
                        "Match the increase to deployments, traffic, usage quantities, and "
                        "rate changes, then record whether it is expected."
                        if is_increase
                        else "Confirm the decrease reflects a real workload or rate change—not "
                        "delayed billing, incomplete ingestion, or a changed filter."
                    )
                    + driver_clause
                ),
                rationale=(
                    f"Latest comparable-period spend "
                    f"{'increased' if is_increase else 'decreased'} by "
                    f"{_amount(period_change)} ({abs(float(period_change_pct.value)):.1%}) "
                    "versus the preceding period."
                ),
                evidence_strength="verified",
                fact_ids=tuple(fact_ids),
                owner="FinOps + affected service owner",
                timeframe="Within 3 business days",
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
                owner="Budget owner + Finance partner",
                timeframe="Before the next forecast update",
            )
        )

    forecast_change = fact_map.get("forecast_change_amount")
    forecast_change_pct = fact_map.get("forecast_change_pct")
    if (
        forecast_change is not None
        and forecast_change_pct is not None
        and float(forecast_change.value) > 0
        and float(forecast_change_pct.value) >= 0.10
    ):
        recommendations.append(
            Recommendation(
                recommendation_id="forecast_run_rate_review",
                title="Reconcile the higher near-term run rate",
                priority="medium",
                action=(
                    "Validate the workload assumptions behind the forecast and update the "
                    "operating forecast or delivery plan if the increase is expected."
                ),
                rationale=(
                    f"The 14-day outlook is {_amount(forecast_change)} "
                    f"({float(forecast_change_pct.value):.1%}) above the most recent "
                    "14-day actual spend."
                ),
                evidence_strength="modeled",
                fact_ids=("forecast_total", "forecast_change_amount", "forecast_change_pct"),
                owner="FinOps + Finance planning",
                timeframe="Before the next forecast update",
            )
        )

    allocation = fact_map.get("allocation_cost_coverage")
    if allocation is not None and float(allocation.value) < 0.80:
        unallocated = fact_map.get("unallocated_positive_spend")
        fact_ids = ["allocation_cost_coverage"]
        gap_clause = ""
        if unallocated is not None:
            gap_clause = f" The unowned positive spend is {_amount(unallocated)}."
            fact_ids.append("unallocated_positive_spend")
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
                    f"ownership field in the selected data.{gap_clause}"
                ),
                evidence_strength="verified",
                fact_ids=tuple(fact_ids),
                owner="Cloud governance + application owners",
                timeframe="Before the next allocation cycle",
            )
        )

    anomalies = fact_map.get("anomaly_increase_count") or fact_map.get("anomaly_count")
    anomaly_impact = fact_map.get("anomaly_estimated_increase_total")
    top_anomaly_date = fact_map.get("top_anomaly_date")
    top_anomaly_service = fact_map.get("top_anomaly_largest_service")
    if anomalies is not None and int(anomalies.value) > 0:
        facts_used = [anomalies.fact_id]
        impact_clause = ""
        date_clause = ""
        owner = "FinOps + affected service owner"
        if anomaly_impact is not None:
            impact_clause = f", totaling {_amount(anomaly_impact)} above their rolling baselines"
            facts_used.append("anomaly_estimated_increase_total")
        if top_anomaly_date is not None:
            date_clause = f" Begin with {top_anomaly_date.value}"
            facts_used.append("top_anomaly_date")
        if top_anomaly_service is not None:
            date_clause += f" and route the review to the {top_anomaly_service.value} owner."
            owner = f"{top_anomaly_service.value} owner + FinOps"
            facts_used.append("top_anomaly_largest_service")
        elif date_clause:
            date_clause += "."
        recommendations.append(
            Recommendation(
                recommendation_id="anomaly_triage",
                title="Triage detected spend changes",
                priority="medium",
                action=(
                    "Review the flagged dates against deployments, traffic, incidents, "
                    f"and provider rate changes before deciding whether action is needed."
                    f"{date_clause}"
                ),
                rationale=(
                    f"The historical scan identified {int(anomalies.value):,} upward "
                    f"anomaly day(s){impact_clause}. The estimate is a baseline deviation, "
                    "not confirmed waste."
                ),
                evidence_strength="verified",
                fact_ids=tuple(facts_used),
                owner=owner,
                timeframe="Within 2 business days",
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
                owner=f"{top_service.value} owner + FinOps",
                timeframe="At the next service cost review",
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
                owner="FinOps analyst",
                timeframe="At the next scheduled review",
            )
        )
    priority_order = {"high": 0, "medium": 1, "low": 2}
    return tuple(sorted(recommendations, key=lambda item: priority_order[item.priority]))
