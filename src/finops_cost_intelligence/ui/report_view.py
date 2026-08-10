"""Executive summary and export controls."""

from __future__ import annotations

import json
from hashlib import sha256
from html import escape
from typing import TYPE_CHECKING

import pandas as pd
import streamlit as st

from ..ai import build_fact_pack, summarize_fact_pack
from ..ai.client import AIProviderError, OpenAICompatibleClient
from ..contracts.normalization import NormalizedTable
from ..exports import (
    cleaned_csv_bytes,
    cleaned_parquet_bytes,
    executive_report_html,
    fact_pack_json_bytes,
    quality_report_json_bytes,
)
from ..storage import S3Storage, S3StorageError
from .branding import render_compact_table

if TYPE_CHECKING:
    from ..config import Settings


def _fact_map(fact_pack) -> dict[str, object]:
    return {fact.fact_id: fact for fact in fact_pack.facts}


def _amount(value: float | int, currency: str, *, signed: bool = False) -> str:
    sign = "+" if signed and float(value) > 0 else ""
    prefix = f"{currency} " if currency not in {"", "Unspecified", "Mixed"} else ""
    return f"{prefix}{sign}{float(value):,.2f}"


def _display_fact(fact) -> str:
    value = fact.value
    if isinstance(value, float):
        if fact.unit == "share":
            return f"{value:.1%}"
        return _amount(value, fact.unit)
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def _kpi_html(fact_pack) -> str:
    facts = _fact_map(fact_pack)
    total = facts.get("total_spend")
    currency = total.unit if total is not None else ""
    cards: list[tuple[str, str, str, str]] = []
    if total is not None:
        period = f"{fact_pack.period_start or '—'} to {fact_pack.period_end or '—'}"
        cards.append(("Selected spend", _amount(total.value, currency), period, "neutral"))

    change = facts.get("spend_change_amount")
    change_pct = facts.get("spend_change_pct")
    window = facts.get("comparison_window_days")
    if change is not None and change_pct is not None:
        tone = "risk" if float(change.value) > 0 else "positive"
        cards.append(
            (
                "Recent movement",
                f"{float(change_pct.value):+.1%}",
                (
                    f"{_amount(change.value, currency, signed=True)} vs prior "
                    f"{window.value}-day window"
                ),
                tone,
            )
        )
    else:
        cards.append(("Recent movement", "—", "Not enough comparable history", "neutral"))

    forecast = facts.get("forecast_total")
    forecast_change = facts.get("forecast_change_pct")
    if forecast is not None:
        detail = "Next 14 calendar days"
        tone = "neutral"
        if forecast_change is not None:
            detail = f"{float(forecast_change.value):+.1%} vs latest 14-day actual"
            tone = "risk" if float(forecast_change.value) > 0 else "positive"
        cards.append(("Near-term outlook", _amount(forecast.value, currency), detail, tone))

    budget = facts.get("budget_utilization")
    budget_variance = facts.get("budget_variance_amount")
    anomaly_impact = facts.get("anomaly_estimated_increase_total")
    anomaly_count = facts.get("anomaly_increase_count")
    if (
        budget is not None
        and budget.value is not None
        and budget_variance is not None
        and budget_variance.value is not None
    ):
        tone = "risk" if float(budget_variance.value) > 0 else "positive"
        cards.append(
            (
                "Budget position",
                f"{float(budget.value):.1%} used",
                f"{_amount(budget_variance.value, currency, signed=True)} actual minus budget",
                tone,
            )
        )
    elif anomaly_impact is not None and anomaly_count is not None:
        cards.append(
            (
                "Flagged impact",
                _amount(anomaly_impact.value, currency),
                f"Above baseline across {int(anomaly_count.value):,} upward anomaly day(s)",
                "risk" if float(anomaly_impact.value) > 0 else "positive",
            )
        )

    rendered = "".join(
        (
            f'<div class="metrora-report-kpi {escape(tone)}">'
            f"<span>{escape(label)}</span><strong>{escape(value)}</strong>"
            f"<small>{escape(detail)}</small></div>"
        )
        for label, value, detail, tone in cards[:4]
    )
    return f'<div class="metrora-report-kpis">{rendered}</div>'


def _numeric_fact(facts: dict[str, object], fact_id: str) -> float | None:
    fact = facts.get(fact_id)
    if fact is None or fact.value is None:
        return None
    try:
        return float(fact.value)
    except (TypeError, ValueError):
        return None


def _plain_language_brief(fact_pack, summary) -> dict[str, str]:
    """Translate calculated facts into a three-question, non-technical decision view."""
    facts = _fact_map(fact_pack)
    total = facts.get("total_spend")
    currency = total.unit if total is not None else ""
    change = _numeric_fact(facts, "spend_change_amount")
    change_pct = _numeric_fact(facts, "spend_change_pct")
    window = _numeric_fact(facts, "comparison_window_days")
    forecast = _numeric_fact(facts, "forecast_total")
    forecast_change = _numeric_fact(facts, "forecast_change_pct")
    budget_variance = _numeric_fact(facts, "budget_variance_amount")
    mover = facts.get("service_mover_1_name")
    mover_change = _numeric_fact(facts, "service_mover_1_change_amount")
    mover_explanation = facts.get("service_mover_1_explanation")

    if not fact_pack.quality_ready:
        status, tone = "Data review required", "risk"
        headline = "Do not use these numbers yet."
        why = (
            "At least one blocking quality check failed, so totals, comparisons, and "
            "recommendations should not be shared until the source is corrected."
        )
    elif budget_variance is not None and budget_variance > 0:
        status, tone = "Action required", "risk"
        headline = "Spend is above the supplied plan."
        why = (
            f"Actual spend is {_amount(budget_variance, currency)} above the matched budget. "
            "Confirm the scope and owner before the next review."
        )
    elif forecast_change is not None and forecast_change >= 0.10:
        status, tone = "Watch the outlook", "watch"
        headline = "Spend is controlled now, but the near-term outlook is rising."
        forecast_text = _amount(forecast, currency) if forecast is not None else "higher"
        why = (
            f"The forecast is {forecast_text}, {forecast_change:.1%} above the latest "
            "comparable run rate. This is forward-looking risk, not a confirmed overrun."
        )
    elif change_pct is not None and abs(change_pct) >= 0.05:
        status, tone = "Movement detected", "watch"
        direction = "increased" if change_pct > 0 else "decreased"
        headline = f"Spend {direction} enough to review the driver."
        why = (
            "The latest comparable window moved materially. Validate the main service driver "
            "before treating the change as structural."
        )
    else:
        status, tone = "On track", "positive"
        headline = "Spend is stable within the available planning context."
        why = (
            "No calculated budget, forecast, or data-quality signal currently requires an "
            "urgent response. Continue normal monitoring."
        )

    if total is not None:
        happened = f"Selected spend was {_amount(total.value, currency)}"
        if change is not None and change_pct is not None:
            days = int(window) if window is not None else None
            period = f" latest {days}-day window" if days else " latest comparison"
            direction = "up" if change > 0 else "down"
            happened += (
                f". The{period} was {direction} {_amount(abs(change), currency)} "
                f"({abs(change_pct):.1%})."
            )
        else:
            happened += ". There is not enough comparable history to measure movement."
    else:
        happened = summary.headline

    if mover is not None and mover_change is not None:
        explanation = (
            str(mover_explanation.value)
            if mover_explanation is not None
            else "The operational root cause still needs confirmation."
        )
        happened += (
            f" The largest service movement was {mover.value}: "
            f"{_amount(mover_change, currency, signed=True)}. {explanation}"
        )

    if fact_pack.recommendations:
        recommendation = fact_pack.recommendations[0]
        next_step = (
            f"{recommendation.action} Owner: {recommendation.owner}. "
            f"Timing: {recommendation.timeframe}."
        )
    else:
        next_step = "Continue monitoring and confirm the planning context at the next review."

    return {
        "status": status,
        "tone": tone,
        "headline": headline,
        "happened": happened,
        "why": why,
        "next": next_step,
    }


def _render_decision_brief(fact_pack, summary) -> None:
    brief = _plain_language_brief(fact_pack, summary)
    st.markdown(
        f"""
        <section class="metrora-report-decision {escape(brief["tone"])}">
            <span>{escape(brief["status"])}</span>
            <h2>{escape(brief["headline"])}</h2>
            <p>Read the three answers below first. Open the evidence only when you need to
            verify or hand off the decision.</p>
        </section>
        <div class="metrora-report-answers">
            <article>
                <small>01 / What happened?</small>
                <p>{escape(brief["happened"])}</p>
            </article>
            <article>
                <small>02 / Why does it matter?</small>
                <p>{escape(brief["why"])}</p>
            </article>
            <article>
                <small>03 / What should happen next?</small>
                <p>{escape(brief["next"])}</p>
            </article>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _service_mover_frame(fact_pack) -> pd.DataFrame:
    facts = _fact_map(fact_pack)
    total = facts.get("total_spend")
    currency = total.unit if total is not None else ""
    rows: list[dict[str, str]] = []
    for rank in range(1, 4):
        prefix = f"service_mover_{rank}"
        name = facts.get(f"{prefix}_name")
        recent = facts.get(f"{prefix}_recent_spend")
        prior = facts.get(f"{prefix}_prior_spend")
        change = facts.get(f"{prefix}_change_amount")
        driver_type = facts.get(f"{prefix}_driver_type")
        explanation = facts.get(f"{prefix}_explanation")
        evidence_level = facts.get(f"{prefix}_evidence_level")
        usage_change = facts.get(f"{prefix}_usage_change_pct")
        rate_change = facts.get(f"{prefix}_effective_rate_change_pct")
        if any(value is None for value in (name, recent, prior, change)):
            continue
        rows.append(
            {
                "Service": str(name.value),
                "Latest window": _amount(recent.value, currency),
                "Prior window": _amount(prior.value, currency),
                "Change": _amount(change.value, currency, signed=True),
                "Observed mechanism": (
                    str(driver_type.value) if driver_type is not None else "Billing-only"
                ),
                "Usage signal": (
                    f"{float(usage_change.value):+.1%}"
                    if usage_change is not None
                    else "Unavailable"
                ),
                "Effective rate / mix": (
                    f"{float(rate_change.value):+.1%}" if rate_change is not None else "Unavailable"
                ),
                "Why": (
                    str(explanation.value)
                    if explanation is not None
                    else "More operational context is required."
                ),
                "Evidence": (str(evidence_level.value) if evidence_level is not None else "Low"),
            }
        )
    return pd.DataFrame(rows)


def _render_service_movers(movers: pd.DataFrame) -> None:
    """Show each driver as a readable evidence row at laptop widths."""
    rows: list[str] = []
    for _, mover in movers.head(3).iterrows():
        comparison = f"{mover['Prior window']} → {mover['Latest window']}"
        usage_rate = (
            f"{escape(str(mover['Usage signal']))} / {escape(str(mover['Effective rate / mix']))}"
        )
        rows.append(
            f'<article class="metrora-driver-row">'
            f'<div class="metrora-driver-head"><div>'
            f"<strong>{escape(str(mover['Service']))}</strong>"
            f"<span>{escape(str(mover['Observed mechanism']))}</span>"
            f"</div><b>{escape(str(mover['Change']))}</b></div>"
            f'<div class="metrora-driver-body report">'
            f'<div class="metrora-driver-why"><small>Why this moved</small>'
            f"<p>{escape(str(mover['Why']))}</p></div>"
            f"<div><small>Window comparison</small><strong>{escape(comparison)}</strong></div>"
            f"<div><small>Usage / rate-mix</small><strong>{usage_rate}</strong></div>"
            f"<div><small>Evidence</small><strong>{escape(str(mover['Evidence']))}</strong></div>"
            "</div></article>"
        )
    st.markdown(
        f'<div class="metrora-driver-list">{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def _render_actions(fact_pack) -> None:
    st.markdown("### Action plan")
    st.caption(
        "The highest-priority response comes first. Suggested owners and timing can be changed "
        "before the brief is shared."
    )
    for recommendation in fact_pack.recommendations:
        priority = recommendation.priority.lower()
        st.markdown(
            f"""
            <div class="metrora-report-action">
                <span class="metrora-report-priority {escape(priority)}">
                    {escape(priority.upper())}
                </span>
                <div>
                    <h4>{escape(recommendation.title)}</h4>
                    <p>{escape(recommendation.action)}</p>
                    <small><strong>Owner:</strong> {escape(recommendation.owner)} ·
                    <strong>When:</strong> {escape(recommendation.timeframe)}</small>
                    <small><strong>Why now:</strong> {escape(recommendation.rationale)}</small>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _review_questions(fact_pack) -> list[str]:
    facts = _fact_map(fact_pack)
    questions: list[str] = []
    if "budget_total" not in facts:
        questions.append(
            "Which approved budget or operating forecast should this scope be measured against?"
        )
    if "cost_per_business_unit" not in facts:
        questions.append(
            "Which business output—customers, revenue, transactions, or usage—should "
            "define unit economics?"
        )
    questions.append(
        "Do utilization, commitment coverage, and pricing data support a quantified "
        "optimization decision?"
    )
    if not fact_pack.quality_ready or fact_pack.quality_status == "warning":
        questions.append(
            "Which data-quality exceptions must be resolved before this brief is shared?"
        )
    return questions


def _render_evidence(fact_pack, summary) -> None:
    with st.expander("Evidence, definitions & limitations", expanded=False):
        st.write(
            f"Source: **{fact_pack.source_name}** · Period: **{fact_pack.period_start or '—'} to "
            f"{fact_pack.period_end or '—'}** · Quality: **{fact_pack.quality_status.upper()}** · "
            f"Narrative: **{summary.provider.replace('_', ' ')}**"
        )
        evidence = pd.DataFrame(
            [
                {
                    "Calculated fact": fact.label,
                    "Value": _display_fact(fact),
                    "Definition": fact.evidence,
                }
                for fact in fact_pack.facts
            ]
        )
        render_compact_table(evidence, max_rows=100)
        caveats = tuple(dict.fromkeys((*fact_pack.caveats, *summary.caveats)))
        if caveats:
            st.markdown("**Limitations**")
            for caveat in caveats:
                st.markdown(f"- {caveat}")


def _render_summary(fact_pack, summary) -> None:
    st.markdown(
        '<div class="metrora-section-kicker">Executive decision brief</div>',
        unsafe_allow_html=True,
    )
    st.subheader("The decision in one minute")
    st.caption(
        "Plain-language answers first. Supporting calculations and audit detail remain attached."
    )
    _render_decision_brief(fact_pack, summary)
    st.markdown("### Key numbers")
    st.markdown(_kpi_html(fact_pack), unsafe_allow_html=True)

    movers = _service_mover_frame(fact_pack)
    if not movers.empty:
        st.markdown("### What moved the bill")
        st.caption(
            "These are observed billing mechanisms. Where the source cannot prove an operational "
            "root cause, Metrora says so instead of guessing."
        )
        _render_service_movers(movers)

    _render_actions(fact_pack)
    with st.expander("More calculated findings", expanded=False):
        st.markdown("\n".join(f"- {bullet}" for bullet in summary.bullets))
    with st.expander("Questions to resolve before the next review", expanded=False):
        st.caption("Missing context that would materially improve the next decision.")
        st.markdown("\n".join(f"- {question}" for question in _review_questions(fact_pack)))
    _render_evidence(fact_pack, summary)


def render_report_view(
    settings: Settings,
    normalized: NormalizedTable,
    source_key: str,
    filtered: object,
    *,
    show_header: bool = True,
) -> None:
    """Render grounded summary generation and reproducible download artifacts."""
    quality_report = st.session_state.get("quality_report")
    if quality_report is None:
        return
    if show_header:
        st.header("Share the story")
        st.write(
            "Turn the calculated fact pack into a concise executive brief, then export the "
            "evidence, quality checks, and cleaned dataset for review."
        )
    budget = st.session_state.get("budget_table")
    business_metrics = st.session_state.get("business_metrics_table")
    metric_name = st.session_state.get(f"business_metric_name_{source_key}")
    fact_pack = build_fact_pack(
        normalized,
        quality_report,
        dataframe=filtered,
        budget_dataframe=budget,
        business_metrics_dataframe=business_metrics,
        metric_name=metric_name,
        filters={"source_key": source_key},
    )
    st.session_state["fact_pack"] = fact_pack
    signature_payload = fact_pack.to_dict()
    signature_payload.pop("generated_at", None)
    fact_signature = sha256(
        json.dumps(signature_payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()
    if st.session_state.get("summary_fact_signature") != fact_signature:
        st.session_state["summary_result"] = summarize_fact_pack(fact_pack, client=None)
        st.session_state["summary_fact_signature"] = fact_signature

    if settings.ai_provider != "none":
        with st.expander("Optional AI narrative", expanded=False):
            st.caption(
                "The provider can rewrite the calculated evidence for readability. It cannot "
                "add values, calculate savings, or see data outside this fact pack."
            )
            if st.button(
                "Refresh narrative with configured AI",
                key=f"summary_button_{source_key}",
            ):
                client = None
                if settings.ai_provider in {"openai", "openai-compatible"}:
                    try:
                        client = OpenAICompatibleClient(
                            api_key=settings.ai_api_key or "",
                            model=settings.ai_model or "",
                            base_url=settings.ai_base_url,
                        )
                    except AIProviderError as exc:
                        st.warning(f"Optional AI provider is not ready; using fallback: {exc}")
                elif settings.ai_provider != "none":
                    st.warning(
                        f"AI provider `{settings.ai_provider}` is not supported by this adapter; "
                        "using the deterministic fallback."
                    )
                st.session_state["summary_result"] = summarize_fact_pack(
                    fact_pack,
                    client=client,
                )
    summary = st.session_state.get("summary_result")
    if summary is not None:
        _render_summary(fact_pack, summary)

    st.divider()
    st.subheader("Share or continue the analysis")
    st.caption(
        "Choose the human-readable brief for a review meeting or the cleaned CSV for further "
        "analysis. Technical audit files are available below."
    )
    primary_exports = st.columns(2, gap="large")
    if summary is not None:
        primary_exports[0].download_button(
            "Download decision brief",
            data=executive_report_html(fact_pack, summary).encode("utf-8"),
            file_name="metrora_executive_brief.html",
            mime="text/html",
            key=f"download_report_{source_key}",
            type="primary",
            width="stretch",
        )
    primary_exports[1].download_button(
        "Download cleaned data (CSV)",
        data=cleaned_csv_bytes(normalized),
        file_name="metrora_canonical_cloud_cost.csv",
        mime="text/csv",
        key=f"download_csv_{source_key}",
        width="stretch",
    )
    with st.expander("Analyst and audit files", expanded=False):
        st.caption(
            "Use these formats for data pipelines, reproducibility, or a detailed quality review."
        )
        technical_exports = st.columns(3)
        technical_exports[0].download_button(
            "Cleaned Parquet",
            data=cleaned_parquet_bytes(normalized),
            file_name="metrora_canonical_cloud_cost.parquet",
            mime="application/octet-stream",
            key=f"download_parquet_{source_key}",
            width="stretch",
        )
        technical_exports[1].download_button(
            "Calculated fact pack",
            data=fact_pack_json_bytes(fact_pack),
            file_name="metrora_fact_pack.json",
            mime="application/json",
            key=f"download_fact_pack_{source_key}",
            width="stretch",
        )
        technical_exports[2].download_button(
            "Quality report",
            data=quality_report_json_bytes(quality_report),
            file_name="metrora_quality_report.json",
            mime="application/json",
            key=f"download_quality_{source_key}",
            width="stretch",
        )
    if settings.s3_bucket:
        with st.expander("AWS export", expanded=False):
            st.caption(
                f"AWS export is configured for bucket `{settings.s3_bucket}`. "
                "Canonical Parquet will be stored under the standardized prefix."
            )
            if st.button("Upload canonical Parquet to S3", key=f"s3_upload_{source_key}"):
                try:
                    uri = S3Storage(
                        settings.s3_bucket,
                        region=settings.aws_region,
                    ).upload_normalized(normalized)
                except S3StorageError as exc:
                    st.error(f"S3 upload failed: {exc}")
                else:
                    st.success(f"Uploaded standardized Parquet to {uri}")
