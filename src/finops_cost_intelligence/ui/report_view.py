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
                    f"{float(rate_change.value):+.1%}"
                    if rate_change is not None
                    else "Unavailable"
                ),
                "Why": (
                    str(explanation.value)
                    if explanation is not None
                    else "More operational context is required."
                ),
                "Evidence": (
                    str(evidence_level.value) if evidence_level is not None else "Low"
                ),
            }
        )
    return pd.DataFrame(rows)


def _render_service_movers(movers: pd.DataFrame) -> None:
    """Show each driver as a readable evidence row at laptop widths."""
    rows: list[str] = []
    for _, mover in movers.head(3).iterrows():
        comparison = f"{mover['Prior window']} → {mover['Latest window']}"
        usage_rate = (
            f"{escape(str(mover['Usage signal']))} / "
            f"{escape(str(mover['Effective rate / mix']))}"
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
    st.markdown("### Recommended next actions")
    st.caption(
        "Prioritized from calculated evidence. Owners and timing are suggested operating "
        "defaults and can be changed before the brief is shared."
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
    st.subheader("What leaders need to know")
    st.caption(
        "Answer-first view of movement, drivers, risk, and accountability. Every financial "
        "value below is calculated before the narrative is written."
    )
    st.markdown(_kpi_html(fact_pack), unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="metrora-report-bottom-line">
            <span>Bottom line</span>
            <p>{escape(summary.headline)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Key findings")
    st.markdown("\n".join(f"- {bullet}" for bullet in summary.bullets))

    movers = _service_mover_frame(fact_pack)
    if not movers.empty:
        st.markdown("### What changed and why")
        st.caption(
            "Metrora separates the observed billing driver from the still-unconfirmed "
            "operational root cause. Usage and effective-rate signals appear only when the "
            "source contains comparable usage units."
        )
        _render_service_movers(movers)

    _render_actions(fact_pack)
    st.markdown("### Questions for the next review")
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
    st.subheader("Download artifacts")
    st.caption(
        "Exports reflect the current canonical selection and include the fact pack or "
        "quality status needed to reproduce the narrative."
    )
    if summary is not None:
        st.download_button(
            "Download executive HTML report",
            data=executive_report_html(fact_pack, summary).encode("utf-8"),
            file_name="metrora_executive_brief.html",
            mime="text/html",
            key=f"download_report_{source_key}",
        )
    columns = st.columns(4)
    columns[0].download_button(
        "Cleaned CSV",
        data=cleaned_csv_bytes(normalized),
        file_name="metrora_canonical_cloud_cost.csv",
        mime="text/csv",
        key=f"download_csv_{source_key}",
    )
    columns[1].download_button(
        "Cleaned Parquet",
        data=cleaned_parquet_bytes(normalized),
        file_name="metrora_canonical_cloud_cost.parquet",
        mime="application/octet-stream",
        key=f"download_parquet_{source_key}",
    )
    columns[2].download_button(
        "Fact pack JSON",
        data=fact_pack_json_bytes(fact_pack),
        file_name="metrora_fact_pack.json",
        mime="application/json",
        key=f"download_fact_pack_{source_key}",
    )
    columns[3].download_button(
        "Quality JSON",
        data=quality_report_json_bytes(quality_report),
        file_name="metrora_quality_report.json",
        mime="application/json",
        key=f"download_quality_{source_key}",
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
