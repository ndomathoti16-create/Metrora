"""Provider-neutral decision register and outcome verification workspace."""

from __future__ import annotations

from datetime import date
from html import escape
from typing import TYPE_CHECKING
from uuid import uuid4

import streamlit as st

from ..ai import build_fact_pack
from ..connections import (
    AwsCostOptimizationConnector,
    AwsOptimizationConfig,
    CloudConnectionError,
    ConnectionStore,
)
from ..decisions import (
    DECISION_STATUSES,
    DecisionRecord,
    DecisionStore,
    decisions_csv_bytes,
    decisions_json_bytes,
    merge_decisions,
    ranked_decisions,
    recommendations_to_decisions,
)

if TYPE_CHECKING:
    from ..config import Settings
    from ..contracts.normalization import NormalizedTable


def _uses_session_register() -> bool:
    """Keep public demos isolated; only the downloadable app writes local state."""
    return not bool(st.session_state.get("desktop_mode", False))


def _decision_store(settings: Settings) -> DecisionStore:
    return DecisionStore(settings.data_dir / "state" / "decisions.json")


def _connection_store(settings: Settings) -> ConnectionStore:
    return ConnectionStore(settings.data_dir / "state" / "connections.json")


def _load_decisions(settings: Settings) -> list[DecisionRecord]:
    if _uses_session_register():
        payload = st.session_state.get("decision_register", [])
        return [DecisionRecord.from_dict(item) for item in payload]
    return _decision_store(settings).list()


def _save_decisions(settings: Settings, decisions: list[DecisionRecord]) -> None:
    if _uses_session_register():
        st.session_state["decision_register"] = [item.to_dict() for item in decisions]
        return
    _decision_store(settings).save_many(decisions)


def _replace_decision(
    decisions: list[DecisionRecord],
    updated: DecisionRecord,
) -> list[DecisionRecord]:
    return sorted(
        [item for item in decisions if item.decision_id != updated.decision_id] + [updated],
        key=lambda item: (item.created_at, item.decision_id),
    )


def _build_current_fact_pack(normalized: NormalizedTable, source_key: str):
    quality_report = st.session_state.get("quality_report")
    if quality_report is None:
        return None
    filtered = st.session_state.get("analytics_filtered_table")
    if filtered is None or st.session_state.get("analytics_source_key") != source_key:
        filtered = normalized.dataframe.copy()
    return build_fact_pack(
        normalized,
        quality_report,
        dataframe=filtered,
        budget_dataframe=st.session_state.get("budget_table"),
        business_metrics_dataframe=st.session_state.get("business_metrics_table"),
        metric_name=st.session_state.get(f"business_metric_name_{source_key}"),
        filters={"source_key": source_key},
    )


def _sync_calculated_actions(
    settings: Settings,
    normalized: NormalizedTable | None,
    source_key: str | None,
) -> list[DecisionRecord]:
    existing = _load_decisions(settings)
    if normalized is None or source_key is None:
        return existing
    fact_pack = _build_current_fact_pack(normalized, source_key)
    if fact_pack is None:
        return existing
    st.session_state["fact_pack"] = fact_pack
    incoming = recommendations_to_decisions(fact_pack)
    merged = merge_decisions(existing, incoming)
    if merged != existing:
        _save_decisions(settings, merged)
    return merged


def _format_amount(amount: float | None, currency: str, *, signed: bool = False) -> str:
    if amount is None:
        return "Not quantified"
    sign = "+" if signed and amount > 0 else ""
    prefix = f"{currency} " if currency not in {"", "Unspecified", "Mixed"} else ""
    return f"{prefix}{sign}{amount:,.2f}"


def _impact_label(decision: DecisionRecord) -> str:
    labels = {
        "provider_estimated_monthly_savings": "Provider estimate / month",
        "observed_spend_movement": "Observed movement",
        "observed_budget_variance": "Observed budget variance",
        "modeled_forecast_gap": "Modeled forecast gap",
        "observed_unallocated_spend": "Observed unallocated spend",
        "observed_baseline_deviation": "Observed baseline deviation",
        "not_quantified": "Evidence only",
    }
    return labels.get(decision.impact_kind, decision.impact_kind.replace("_", " ").title())


def _summary_value(decisions: list[DecisionRecord]) -> tuple[str, str]:
    verified = [item for item in decisions if item.verified_value > 0]
    currencies = {item.currency for item in verified if item.currency not in {"", "Unspecified"}}
    if not verified:
        return "0.00", "No outcome has been verified yet"
    total = sum(item.verified_value for item in verified)
    if len(currencies) == 1:
        currency = next(iter(currencies))
        return f"{currency} {total:,.2f}", "Measured from supplied before/after actuals"
    return f"{total:,.2f}", "Mixed currencies; review records separately"


def _render_register_metrics(decisions: list[DecisionRecord]) -> None:
    open_items = [item for item in decisions if item.is_open]
    unassigned = sum(item.owner.casefold() == "unassigned" for item in open_items)
    today = date.today()
    overdue = sum(
        bool(item.due_date and date.fromisoformat(item.due_date) < today) for item in open_items
    )
    verified_value, verified_help = _summary_value(decisions)
    columns = st.columns(4, gap="small")
    columns[0].metric("Open decisions", len(open_items))
    columns[1].metric("Unassigned", unassigned)
    columns[2].metric("Overdue", overdue)
    columns[3].metric("Verified value", verified_value, help=verified_help)


def _render_priority_queue(decisions: list[DecisionRecord]) -> None:
    st.markdown("### Priority queue")
    st.caption(
        "The score ranks work; it is not a savings claim. It combines relative exposure, "
        "evidence, timing, effort, and business criticality."
    )
    ranked = [(item, score) for item, score in ranked_decisions(decisions) if item.is_open]
    if not ranked:
        st.success("No open decision requires action in the current register.")
        return
    rows: list[str] = []
    for item, score in ranked:
        due = item.due_date or item.target_timing
        owner = item.owner or "Unassigned"
        amount = _format_amount(item.impact_amount, item.currency, signed=True)
        rows.append(
            '<article class="metrora-decision-row">'
            f'<div class="metrora-decision-score"><span>{score}</span><small>Priority</small></div>'
            '<div class="metrora-decision-main">'
            f"<span>{escape(item.category)} / {escape(item.provider)}</span>"
            f"<strong>{escape(item.title)}</strong>"
            f"<p>{escape(item.evidence_summary)}</p></div>"
            '<div class="metrora-decision-meta">'
            f"<div><small>Impact basis</small><strong>{escape(_impact_label(item))}</strong>"
            f"<span>{escape(amount)}</span></div>"
            f"<div><small>Owner / due</small><strong>{escape(owner)}</strong>"
            f"<span>{escape(due)}</span></div>"
            f"<div><small>Status</small><strong>{escape(item.status)}</strong>"
            f"<span>{escape(item.evidence_strength.replace('_', ' ').title())}</span></div>"
            "</div></article>"
        )
    st.markdown(
        f'<div class="metrora-decision-list">{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def _decision_options(decisions: list[DecisionRecord]) -> dict[str, DecisionRecord]:
    return {
        f"{item.title} — {item.status} — {item.owner}": item
        for item in sorted(decisions, key=lambda value: value.title.casefold())
    }


def _render_update_form(settings: Settings, decisions: list[DecisionRecord]) -> None:
    st.markdown("### Assign and decide")
    st.caption(
        "Record the human disposition. Metrora refreshes the evidence without overwriting "
        "the owner, decision note, or outcome."
    )
    if not decisions:
        st.info("No decision is available to update yet.")
        return
    options = _decision_options(decisions)
    selected_label = st.selectbox("Decision", list(options), key="decision_update_selection")
    selected = options[selected_label]
    status_options = [
        status
        for status in DECISION_STATUSES
        if status != "Verified" or selected.status == "Verified"
    ]
    with st.form("decision_update_form"):
        left, right = st.columns(2, gap="large")
        with left:
            owner = st.text_input("Owner", value=selected.owner)
            status = st.selectbox(
                "Status",
                status_options,
                index=status_options.index(selected.status),
            )
            due_date = st.text_input(
                "Due date (optional)",
                value=selected.due_date or "",
                placeholder="YYYY-MM-DD",
            )
        with right:
            effort = st.selectbox(
                "Implementation effort",
                ["Unknown", "Low", "Medium", "High"],
                index=["Unknown", "Low", "Medium", "High"].index(selected.effort),
            )
            risk = st.selectbox(
                "Operational risk",
                ["Unknown", "Low", "Medium", "High"],
                index=["Unknown", "Low", "Medium", "High"].index(selected.operational_risk),
            )
            criticality = st.selectbox(
                "Business criticality",
                ["Low", "Medium", "High"],
                index=["Low", "Medium", "High"].index(selected.business_criticality),
            )
        note = st.text_area("Decision note", value=selected.decision_note)
        rejection_reason = st.text_input(
            "Rejection reason (required only when rejected)",
            value=selected.rejection_reason,
        )
        submitted = st.form_submit_button("Save decision", type="primary")
    if submitted:
        try:
            updated = selected.with_updates(
                owner=owner.strip() or "Unassigned",
                status=status,
                due_date=due_date.strip() or None,
                effort=effort,
                operational_risk=risk,
                business_criticality=criticality,
                decision_note=note.strip(),
                rejection_reason=rejection_reason.strip(),
            )
        except ValueError as exc:
            st.error(str(exc))
            return
        _save_decisions(settings, _replace_decision(decisions, updated))
        st.success("Decision updated without changing its source evidence.")
        st.rerun()


def _render_new_decision_form(settings: Settings, decisions: list[DecisionRecord]) -> None:
    st.markdown("### Add a decision")
    st.caption(
        "Use this for Azure Advisor, Google Cloud, Kubernetes, SaaS, or an internal review "
        "that is not yet connected automatically."
    )
    with st.form("new_decision_form"):
        left, right = st.columns(2, gap="large")
        with left:
            title = st.text_input("Decision title")
            provider = st.text_input("Provider or team", value="Internal")
            category = st.selectbox(
                "Category",
                [
                    "Optimization",
                    "Cost change",
                    "Budget",
                    "Forecast",
                    "Allocation",
                    "Anomaly",
                    "Data quality",
                    "Governance",
                ],
            )
            owner = st.text_input("Initial owner", value="Unassigned")
        with right:
            source_kind = st.selectbox(
                "Evidence source",
                [
                    "Manual review",
                    "Azure Advisor",
                    "Google Cloud FinOps Hub",
                    "AWS native recommendation",
                    "Internal engineering evidence",
                ],
            )
            source_reference = st.text_input(
                "Source reference",
                placeholder="Recommendation ID, ticket, query, or report",
            )
            impact_kind = st.selectbox(
                "Financial basis",
                [
                    "not_quantified",
                    "provider_estimated_monthly_savings",
                    "observed_spend_movement",
                    "observed_budget_variance",
                    "modeled_forecast_gap",
                ],
                format_func=lambda value: value.replace("_", " ").title(),
            )
            amount = st.text_input(
                "Amount (optional)",
                help="Enter only a calculated observation or an explicitly sourced estimate.",
            )
            currency = st.text_input("Currency", value="USD")
        evidence = st.text_area(
            "Evidence and proposed action",
            placeholder="State what was observed, where it came from, and what should be reviewed.",
        )
        submitted = st.form_submit_button("Add to decision register", type="primary")
    if submitted:
        try:
            parsed_amount = float(amount.replace(",", "")) if amount.strip() else None
            created = DecisionRecord(
                decision_id=f"manual-{uuid4().hex}",
                title=title,
                category=category,
                status="Proposed",
                source_kind=source_kind,
                source_reference=source_reference,
                evidence_summary=evidence,
                evidence_strength="user_supplied",
                impact_kind=impact_kind,
                impact_amount=parsed_amount,
                currency=currency.strip() or "Unspecified",
                owner=owner.strip() or "Unassigned",
                provider=provider.strip() or "Internal",
            )
        except ValueError as exc:
            st.error(str(exc))
            return
        _save_decisions(settings, _replace_decision(decisions, created))
        st.success("Decision added. Assign it, record the disposition, and verify the outcome.")
        st.rerun()


def _render_verification_form(settings: Settings, decisions: list[DecisionRecord]) -> None:
    st.markdown("### Verify the outcome")
    st.caption(
        "Provider savings are estimates. Verified value is calculated only from the actual "
        "baseline and comparable post-change cost entered here."
    )
    eligible = [item for item in decisions if item.status in {"Implemented", "Verified"}]
    if not eligible:
        st.info("Mark a decision Implemented before measuring its result.")
        return
    options = _decision_options(eligible)
    selected_label = st.selectbox(
        "Implemented decision",
        list(options),
        key="decision_verification_selection",
    )
    selected = options[selected_label]
    with st.form("decision_verification_form"):
        left, right = st.columns(2, gap="large")
        with left:
            baseline = st.number_input(
                "Comparable baseline actual cost",
                min_value=0.0,
                value=float(selected.baseline_cost or 0.0),
                step=100.0,
            )
            baseline_period = st.text_input(
                "Baseline period",
                value=selected.baseline_period,
                placeholder="2026-06-01 to 2026-06-30",
            )
        with right:
            post_change = st.number_input(
                "Comparable post-change actual cost",
                min_value=0.0,
                value=float(selected.post_change_cost or 0.0),
                step=100.0,
            )
            measurement_period = st.text_input(
                "Measurement period",
                value=selected.measurement_period,
                placeholder="2026-07-01 to 2026-07-31",
            )
        note = st.text_area(
            "Verification note",
            value=selected.decision_note,
            placeholder="Document scope changes, seasonality, credits, or other caveats.",
        )
        submitted = st.form_submit_button("Verify with actuals", type="primary")
    if submitted:
        if not baseline_period.strip() or not measurement_period.strip():
            st.error("Both comparable measurement periods are required.")
            return
        try:
            updated = selected.with_updates(
                status="Verified",
                baseline_cost=float(baseline),
                post_change_cost=float(post_change),
                baseline_period=baseline_period.strip(),
                measurement_period=measurement_period.strip(),
                decision_note=note.strip(),
            )
        except ValueError as exc:
            st.error(str(exc))
            return
        _save_decisions(settings, _replace_decision(decisions, updated))
        change = updated.actual_cost_change or 0.0
        label = "measured reduction" if change >= 0 else "measured increase"
        st.success(f"Outcome verified: {_format_amount(abs(change), updated.currency)} {label}.")
        st.rerun()


def _render_aws_import(settings: Settings, decisions: list[DecisionRecord]) -> None:
    st.markdown("### Import AWS optimization recommendations")
    st.caption(
        "Metrora reads Cost Optimization Hub recommendations and treats the returned savings "
        "as provider estimates. It never resizes, stops, or deletes a resource."
    )
    try:
        aws_profiles = [
            item for item in _connection_store(settings).list() if item.provider == "aws"
        ]
    except ValueError as exc:
        st.warning(str(exc))
        aws_profiles = []
    profile_labels = ["Default AWS credential chain"] + [
        f"Saved billing identity: {item.name}" for item in aws_profiles
    ]
    with st.form("aws_recommendation_import_form"):
        selected_label = st.selectbox("AWS identity", profile_labels)
        selected_index = profile_labels.index(selected_label)
        selected_profile = aws_profiles[selected_index - 1] if selected_index else None
        default_region = (
            str(selected_profile.settings.get("region", settings.aws_region))
            if selected_profile
            else settings.aws_region
        )
        region = st.text_input("AWS region", value=default_region)
        max_items = st.number_input(
            "Maximum recommendations",
            min_value=1,
            max_value=1000,
            value=200,
            step=25,
        )
        submitted = st.form_submit_button("Import recommendations", type="primary")
    if submitted:
        profile_name = (
            str(selected_profile.settings.get("profile_name") or "") or None
            if selected_profile
            else None
        )
        try:
            connector = AwsCostOptimizationConnector(
                AwsOptimizationConfig(region=region, profile_name=profile_name)
            )
            with st.spinner("Reading AWS Cost Optimization Hub recommendations..."):
                incoming = connector.list_decisions(max_items=int(max_items))
        except (CloudConnectionError, ValueError) as exc:
            st.error(str(exc))
            return
        merged = merge_decisions(decisions, incoming)
        _save_decisions(settings, merged)
        st.success(
            f"Imported {len(incoming):,} AWS recommendation(s). Human dispositions and "
            "previously verified outcomes were preserved."
        )
        st.rerun()
    st.info(
        "AWS import is available now. Azure Advisor and Google Cloud findings can be added "
        "through the provider-neutral form while their direct adapters remain on the roadmap."
    )


def _render_exports(decisions: list[DecisionRecord]) -> None:
    if not decisions:
        return
    st.markdown("### Export the operating record")
    st.caption(
        "Share the CSV with finance or the JSON with another system. Source type and impact "
        "basis remain explicit in both formats."
    )
    left, right = st.columns(2, gap="large")
    left.download_button(
        "Download decision register (CSV)",
        data=decisions_csv_bytes(decisions),
        file_name="metrora_decision_register.csv",
        mime="text/csv",
        width="stretch",
    )
    right.download_button(
        "Download audit record (JSON)",
        data=decisions_json_bytes(decisions),
        file_name="metrora_decision_register.json",
        mime="application/json",
        width="stretch",
    )


def render_decision_view(
    settings: Settings,
    normalized: NormalizedTable | None,
    source_key: str | None,
) -> None:
    """Render the accountability layer between a cost signal and a verified outcome."""
    try:
        decisions = _sync_calculated_actions(settings, normalized, source_key)
    except ValueError as exc:
        st.error(str(exc))
        decisions = []
    st.markdown(
        """
        <div class="metrora-automation-note">
            <strong>Native tools find opportunities. Metrora closes the loop.</strong>
            <span>Calculated signals and provider recommendations become owned decisions with
            evidence, disposition, due dates, and measured outcomes.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_register_metrics(decisions)
    if not bool(st.session_state.get("desktop_mode", False)):
        _render_priority_queue(decisions)
        st.info(
            "This hosted workspace is read-only and uses synthetic data. Download the "
            "Windows app to assign owners, import provider recommendations, record "
            "decisions, and verify outcomes."
        )
        return
    queue_tab, update_tab, new_tab, verify_tab, import_tab = st.tabs(
        [
            "Priority queue",
            "Assign & decide",
            "Add decision",
            "Verify outcome",
            "Import AWS",
        ]
    )
    with queue_tab:
        _render_priority_queue(decisions)
    with update_tab:
        _render_update_form(settings, decisions)
    with new_tab:
        _render_new_decision_form(settings, decisions)
    with verify_tab:
        _render_verification_form(settings, decisions)
    with import_tab:
        _render_aws_import(settings, decisions)
    st.divider()
    _render_exports(decisions)
