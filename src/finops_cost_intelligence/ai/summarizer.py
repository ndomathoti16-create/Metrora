"""Deterministic summary plus optional fact-grounded provider adapter."""

from __future__ import annotations

import json
from typing import Protocol

from ..contracts.ai import FactPack, SummaryResult
from .guardrails import AIResponseValidationError, validate_fact_references, validate_numeric_claims


class SummaryClient(Protocol):
    """Minimal provider interface used by the summarizer."""

    def complete(self, system_prompt: str, user_prompt: str) -> str: ...


def _fact_map(fact_pack: FactPack) -> dict[str, object]:
    return {fact.fact_id: fact.value for fact in fact_pack.facts}


def _format_value(value: object, unit: str) -> str:
    if isinstance(value, float):
        if unit == "share":
            return f"{value:.1%}"
        if len(unit) == 3 and unit.isalpha() and unit.upper() == unit:
            return f"{unit} {value:,.2f}"
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def deterministic_summary(fact_pack: FactPack) -> SummaryResult:
    """Produce an answer-first decision summary without a model dependency."""
    facts = {fact.fact_id: fact for fact in fact_pack.facts}
    total = facts.get("total_spend")
    rows = facts.get("cost_row_count")
    if total is None or rows is None:
        headline = (
            "The selected billing data does not contain enough calculated evidence "
            "for an executive summary."
        )
    else:
        headline = (
            f"Selected cloud spend was {_format_value(total.value, total.unit)} "
            f"across {_format_value(rows.value, rows.unit)} billing rows."
        )
    change = facts.get("spend_change_amount")
    change_pct = facts.get("spend_change_pct")
    window = facts.get("comparison_window_days")
    if change is not None and change_pct is not None and window is not None:
        direction = "increased" if float(change.value) > 0 else "decreased"
        if float(change.value) == 0:
            direction = "was unchanged"
        amount = _format_value(abs(float(change.value)), change.unit)
        if direction == "was unchanged":
            headline += f" Latest {window.value}-day spend was unchanged from the prior window."
        else:
            headline += (
                f" Latest {window.value}-day spend {direction} by {amount} "
                f"({_format_value(abs(float(change_pct.value)), change_pct.unit)}) versus "
                "the preceding equal window."
            )
    bullets: list[str] = []
    mover = facts.get("service_mover_1_name")
    mover_change = facts.get("service_mover_1_change_amount")
    mover_recent = facts.get("service_mover_1_recent_spend")
    mover_prior = facts.get("service_mover_1_prior_spend")
    mover_explanation = facts.get("service_mover_1_explanation")
    if all(value is not None for value in (mover, mover_change, mover_recent, mover_prior)):
        mover_direction = "added" if float(mover_change.value) > 0 else "reduced"
        driver_bullet = (
            f"Primary driver: {mover.value} {mover_direction} "
            f"{_format_value(abs(float(mover_change.value)), mover_change.unit)}, moving from "
            f"{_format_value(mover_prior.value, mover_prior.unit)} to "
            f"{_format_value(mover_recent.value, mover_recent.unit)} across the comparable windows."
        )
        if mover_explanation is not None:
            driver_bullet += f" Why: {mover_explanation.value}"
        bullets.append(driver_bullet)
    else:
        top_service = facts.get("top_service")
        top_share = facts.get("top_service_share")
        if top_service is not None and top_share is not None:
            bullets.append(
                f"Concentration: {top_service.value} was the largest service at "
                f"{_format_value(top_share.value, top_share.unit)} of selected spend."
            )
    budget = facts.get("budget_variance_amount")
    if budget is not None:
        direction = "above" if float(budget.value) > 0 else "at or below"
        utilization = facts.get("budget_utilization")
        utilization_clause = (
            f" ({_format_value(utilization.value, utilization.unit)} utilized)"
            if utilization is not None and utilization.value is not None
            else ""
        )
        bullets.append(
            f"Plan position: matched actual cost was "
            f"{_format_value(abs(float(budget.value)), budget.unit)} {direction} the supplied "
            f"budget{utilization_clause}."
        )
    forecast = facts.get("forecast_total")
    if forecast is not None:
        forecast_change = facts.get("forecast_change_amount")
        forecast_change_pct = facts.get("forecast_change_pct")
        lower = facts.get("forecast_lower_total")
        upper = facts.get("forecast_upper_total")
        comparison_clause = ""
        if forecast_change is not None and forecast_change_pct is not None:
            direction = "above" if float(forecast_change.value) > 0 else "below"
            formatted_change_pct = _format_value(
                abs(float(forecast_change_pct.value)), forecast_change_pct.unit
            )
            comparison_clause = (
                f", {_format_value(abs(float(forecast_change.value)), forecast_change.unit)} "
                f"({formatted_change_pct}) {direction} the latest 14-day actual run rate"
            )
        range_clause = ""
        if lower is not None and upper is not None:
            range_clause = (
                f"; modeled range {_format_value(lower.value, lower.unit)} to "
                f"{_format_value(upper.value, upper.unit)}"
            )
        bullets.append(
            f"Outlook: the 14-day forecast is {_format_value(forecast.value, forecast.unit)}"
            f"{comparison_clause}{range_clause}."
        )
    anomaly = facts.get("anomaly_increase_count")
    anomaly_impact = facts.get("anomaly_estimated_increase_total")
    if anomaly is not None and int(anomaly.value) > 0:
        top_date = facts.get("top_anomaly_date")
        top_service = facts.get("top_anomaly_largest_service")
        route = ""
        if top_date is not None:
            route = f" Start with {top_date.value}"
            if top_service is not None:
                route += f" and the {top_service.value} owner"
            route += "."
        bullets.append(
            f"Exception risk: {_format_value(anomaly.value, anomaly.unit)} upward anomaly "
            f"day(s) totaled {_format_value(anomaly_impact.value, anomaly_impact.unit)} above "
            f"their rolling baselines.{route}"
        )
    coverage = facts.get("allocation_cost_coverage")
    unallocated = facts.get("unallocated_positive_spend")
    if coverage is not None and unallocated is not None and float(unallocated.value) > 0:
        bullets.append(
            f"Accountability gap: ownership fields cover "
            f"{_format_value(coverage.value, coverage.unit)} of positive spend, leaving "
            f"{_format_value(unallocated.value, unallocated.unit)} without an owner."
        )
    if not bullets:
        bullets.append("No additional driver facts were available for the selected filters.")
    caveats = list(fact_pack.caveats)
    if fact_pack.quality_status == "warning":
        caveats.append("The run contains quality warnings; review them before sharing.")
    return SummaryResult(
        headline=headline,
        bullets=tuple(bullets[:4]),
        recommendation_ids=tuple(
            recommendation.recommendation_id for recommendation in fact_pack.recommendations
        ),
        used_fact_ids=tuple(fact.fact_id for fact in fact_pack.facts),
        caveats=tuple(dict.fromkeys(caveats)),
        provider="deterministic_fallback",
    )


def _provider_summary(fact_pack: FactPack, client: SummaryClient) -> SummaryResult:
    system_prompt = (
        "You write an answer-first FinOps executive decision brief using only the supplied "
        "fact pack. The headline must state the bottom line. Return at most four bullets "
        "covering: the comparable-period movement and driver, budget or forecast risk, "
        "material anomalies or ownership gaps, and the decision implication. Return JSON "
        "with headline, bullets, recommendation_ids, used_fact_ids, and caveats. Do not "
        "calculate new values, call baseline deviations savings, invent financial values, "
        "or reference unsupported IDs."
    )
    raw = client.complete(system_prompt, json.dumps(fact_pack.to_dict(), default=str))
    try:
        payload = json.loads(raw)
        result = SummaryResult(
            headline=str(payload["headline"]),
            bullets=tuple(str(value) for value in payload["bullets"]),
            recommendation_ids=tuple(str(value) for value in payload["recommendation_ids"]),
            used_fact_ids=tuple(str(value) for value in payload["used_fact_ids"]),
            caveats=tuple(str(value) for value in payload.get("caveats", [])),
            provider="external_provider",
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AIResponseValidationError("The AI response was not valid summary JSON.") from exc
    validate_fact_references(
        fact_pack,
        used_fact_ids=result.used_fact_ids,
        recommendation_ids=result.recommendation_ids,
    )
    validate_numeric_claims(
        " ".join((result.headline, *result.bullets, *result.caveats)), fact_pack
    )
    return result


def summarize_fact_pack(
    fact_pack: FactPack,
    *,
    client: SummaryClient | None = None,
) -> SummaryResult:
    """Use an optional provider only when supplied; safely fall back otherwise."""
    if client is None:
        return deterministic_summary(fact_pack)
    try:
        return _provider_summary(fact_pack, client)
    except (AIResponseValidationError, RuntimeError, OSError):
        fallback = deterministic_summary(fact_pack)
        return SummaryResult(
            headline=fallback.headline,
            bullets=fallback.bullets,
            recommendation_ids=fallback.recommendation_ids,
            used_fact_ids=fallback.used_fact_ids,
            caveats=fallback.caveats
            + ("External AI output failed validation; deterministic fallback used.",),
            provider="deterministic_fallback",
        )
