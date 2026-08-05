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
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def deterministic_summary(fact_pack: FactPack) -> SummaryResult:
    """Produce a grounded summary without a network call or model dependency."""
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
    bullets: list[str] = []
    top_service = facts.get("top_service")
    top_share = facts.get("top_service_share")
    if top_service is not None and top_share is not None:
        bullets.append(
            f"{top_service.value} was the largest service driver at "
            f"{_format_value(top_share.value, top_share.unit)} of selected spend."
        )
    budget = facts.get("budget_variance_amount")
    if budget is not None:
        direction = "above" if float(budget.value) > 0 else "at or below"
        bullets.append(
            f"Actual cost was {_format_value(abs(float(budget.value)), budget.unit)} "
            f"{direction} the supplied budget on a matched-scope basis."
        )
    coverage = facts.get("allocation_cost_coverage")
    if coverage is not None:
        bullets.append(
            f"Ownership fields covered {_format_value(coverage.value, coverage.unit)} "
            "of positive selected spend."
        )
    forecast = facts.get("forecast_total")
    if forecast is not None:
        bullets.append(
            "The 14-day deterministic forecast totals "
            f"{_format_value(forecast.value, forecast.unit)}."
        )
    anomaly = facts.get("anomaly_count")
    if anomaly is not None:
        bullets.append(
            "The historical scan identified "
            f"{_format_value(anomaly.value, anomaly.unit)} meaningful anomaly "
            "or anomalies."
        )
    if not bullets:
        bullets.append("No additional driver facts were available for the selected filters.")
    return SummaryResult(
        headline=headline,
        bullets=tuple(bullets),
        recommendation_ids=tuple(
            recommendation.recommendation_id for recommendation in fact_pack.recommendations
        ),
        used_fact_ids=tuple(fact.fact_id for fact in fact_pack.facts),
        caveats=(
            fact_pack.caveats
            + ("The run contains quality warnings; review them before sharing.",)
            if fact_pack.quality_status == "warning"
            else fact_pack.caveats
        ),
        provider="deterministic_fallback",
    )


def _provider_summary(fact_pack: FactPack, client: SummaryClient) -> SummaryResult:
    system_prompt = (
        "You summarize FinOps evidence. Use only the supplied fact pack. "
        "Return JSON with headline, bullets, recommendation_ids, used_fact_ids, and caveats. "
        "Do not calculate new values, invent savings, or reference unsupported IDs."
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
            + (
                "External AI output failed validation; deterministic fallback used.",
            ),
            provider="deterministic_fallback",
        )
