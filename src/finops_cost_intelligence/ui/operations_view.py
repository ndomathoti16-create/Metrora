"""Optional budgets, allocation coverage, and business-metric analysis views."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import TYPE_CHECKING

import pandas as pd

from ..analytics.allocation import calculate_allocation_coverage
from ..analytics.budgets import calculate_budget_variance
from ..analytics.business_metrics import calculate_unit_economics
from ..contracts.analytics import AnalyticsInputError
from ..contracts.budget import BudgetValidationError
from ..contracts.business_metrics import BusinessMetricValidationError
from ..contracts.normalization import NormalizedTable
from ..ingestion.readers import IngestionError, load_table
from ..normalization.budgets import normalize_budget_dataframe
from ..normalization.business_metrics import normalize_business_metrics
from .branding import apply_plotly_theme, render_compact_table

if TYPE_CHECKING:
    from ..config import Settings


def _format_amount(value: float | None, currency: str = "Unspecified") -> str:
    if value is None:
        return "—"
    if currency not in {"Unspecified", "Mixed"}:
        return f"{currency} {value:,.2f}"
    return f"{value:,.2f}"


def _load_optional(uploaded_file, kind: str):
    try:
        loaded = load_table(uploaded_file)
        if kind == "budget":
            return normalize_budget_dataframe(loaded.dataframe)
        return normalize_business_metrics(loaded.dataframe)
    except (IngestionError, BudgetValidationError, BusinessMetricValidationError) as exc:
        raise ValueError(str(exc)) from exc


def _render_budget_view(actual: pd.DataFrame, source_key: str) -> None:
    import plotly.express as px
    import streamlit as st

    uploaded = st.file_uploader(
        "Upload a budget file",
        type=["csv", "xlsx", "xls", "parquet"],
        key=f"budget_upload_{source_key}",
        help="Accepted fields include period_start, budget_amount, scope_type, and scope_value.",
    )
    budget = st.session_state.get("budget_table")
    if uploaded is not None:
        upload_key = f"{uploaded.name}:{getattr(uploaded, 'size', '')}"
        if st.session_state.get("budget_upload_key") != upload_key:
            try:
                budget = _load_optional(uploaded, "budget")
            except ValueError as exc:
                st.error(f"Budget upload needs attention: {exc}")
                st.session_state.pop("budget_table", None)
                return
            st.session_state["budget_table"] = budget
            st.session_state["budget_upload_key"] = upload_key
    if budget is None:
        st.info("Optional: upload a budget table to compare planned and actual cost.")
        return
    if st.session_state.get("demo_mode") and uploaded is None:
        st.caption("Guided demo context loaded from budget_demo.csv. Upload a file to replace it.")
    try:
        comparison, summary = calculate_budget_variance(actual, budget)
    except AnalyticsInputError as exc:
        st.error(f"Budget comparison could not be calculated: {exc}")
        return
    currency = str(budget["currency"].iloc[0]) if budget["currency"].nunique() == 1 else "Mixed"
    metrics = st.columns(4)
    metrics[0].metric("Budget", _format_amount(summary.budget_total, currency))
    metrics[1].metric("Actual", _format_amount(summary.actual_total, currency))
    metrics[2].metric("Variance", _format_amount(summary.variance_amount, currency))
    metrics[3].metric(
        "Utilization",
        f"{summary.utilization_pct:.1%}" if summary.utilization_pct is not None else "—",
    )
    st.caption(
        "Variance is actual cost minus budget. Positive variance means actual spending "
        "is above budget; zero-budget rows have no percentage utilization."
    )
    display = comparison.copy()
    for column in ("budget_amount", "actual_cost", "variance_amount"):
        display[column] = display[column].round(2)
    for column in ("variance_pct", "utilization_pct"):
        display[column] = display[column].map(
            lambda value: f"{value:.1%}" if pd.notna(value) else "—"
        )
    with st.expander("View budget comparison values", expanded=False):
        render_compact_table(display, max_rows=30)
    chart_data = comparison.assign(
        label=comparison["period_start"].dt.strftime("%Y-%m-%d")
        + " · "
        + comparison["scope_value"].astype(str),
    )
    chart_data = chart_data.melt(
        id_vars=["label"],
        value_vars=["budget_amount", "actual_cost"],
        var_name="series",
        value_name="amount",
    )
    figure = px.bar(
        chart_data,
        x="label",
        y="amount",
        color="series",
        barmode="group",
        color_discrete_map={"budget_amount": "#6E7E95", "actual_cost": "#91A8FF"},
        labels={"label": "Budget row", "amount": "Amount", "series": "Series"},
        title="Actual versus budget",
    )
    figure.update_layout(
        title={"text": "Actual versus budget", "x": 0, "xanchor": "left"},
        height=410,
        xaxis={"automargin": True},
        yaxis={"tickformat": ",.0f", "automargin": True},
        margin={"l": 82, "r": 28, "t": 72, "b": 90},
    )
    apply_plotly_theme(figure)
    st.plotly_chart(figure, width="stretch", theme=None)


def _render_allocation_view(actual: pd.DataFrame) -> None:
    import streamlit as st

    st.write(
        "Coverage measures whether cost rows have populated ownership fields. "
        "Cost coverage uses positive spend as its denominator."
    )
    available = [
        field
        for field in ("account_id", "department", "project", "environment", "region")
        if field in actual.columns
    ]
    if not available:
        st.info("No ownership dimensions are present in the normalized billing data.")
        return
    fields = st.multiselect(
        "Ownership fields to evaluate",
        available,
        default=available,
        key="allocation_fields",
    )
    if not fields:
        st.info("Select at least one ownership field.")
        return
    try:
        coverage = calculate_allocation_coverage(actual, fields)
    except AnalyticsInputError as exc:
        st.error(str(exc))
        return
    any_row = coverage.loc[coverage["field"].eq("any ownership field")].iloc[0]
    metrics = st.columns(2)
    metrics[0].metric("Rows with any ownership field", f"{any_row['row_coverage']:.1%}")
    metrics[1].metric("Positive cost with any ownership field", f"{any_row['cost_coverage']:.1%}")
    display = coverage.copy()
    display["row_coverage"] = (display["row_coverage"] * 100).round(2).astype(str) + "%"
    display["cost_coverage"] = display["cost_coverage"].map(
        lambda value: f"{value:.1%}" if pd.notna(value) else "—"
    )
    display["allocated_positive_cost"] = display["allocated_positive_cost"].round(2)
    with st.expander("View coverage values", expanded=False):
        render_compact_table(display, max_rows=20)


def _render_business_metric_view(actual: pd.DataFrame, source_key: str) -> None:
    import plotly.express as px
    import streamlit as st

    uploaded = st.file_uploader(
        "Upload a business metrics file",
        type=["csv", "xlsx", "xls", "parquet"],
        key=f"business_upload_{source_key}",
        help="Accepted fields include metric_date, metric_name, and metric_value.",
    )
    metrics = st.session_state.get("business_metrics_table")
    if uploaded is not None:
        upload_key = f"{uploaded.name}:{getattr(uploaded, 'size', '')}"
        if st.session_state.get("business_upload_key") != upload_key:
            try:
                metrics = _load_optional(uploaded, "business")
            except ValueError as exc:
                st.error(f"Business metrics upload needs attention: {exc}")
                st.session_state.pop("business_metrics_table", None)
                return
            st.session_state["business_metrics_table"] = metrics
            st.session_state["business_upload_key"] = upload_key
    if metrics is None:
        st.info("Optional: upload customers, revenue, transactions, or usage metrics.")
        return
    if st.session_state.get("demo_mode") and uploaded is None:
        st.caption(
            "Guided demo context loaded from business_metrics_demo.csv. "
            "Upload a file to replace it."
        )
    names = sorted(metrics["metric_name"].unique().tolist())
    metric_name = st.selectbox(
        "Business metric",
        names,
        key=f"business_metric_name_{source_key}",
    )
    try:
        joined, summary = calculate_unit_economics(actual, metrics, metric_name)
    except AnalyticsInputError as exc:
        st.error(f"Unit economics could not be calculated: {exc}")
        return
    metrics_columns = st.columns(3)
    metrics_columns[0].metric("Cloud cost", _format_amount(summary.total_cost))
    metrics_columns[1].metric("Business volume", f"{summary.total_metric_value:,.2f}")
    metrics_columns[2].metric(
        "Cost per unit",
        _format_amount(summary.cost_per_unit),
        help="Total selected-period cost divided by total selected metric value.",
    )
    st.caption(
        f"Metric: {summary.metric_name} · {summary.days_with_metric:,} days with metric data · "
        f"{summary.days_without_cost:,} metric day(s) without matching billing cost"
    )
    figure = px.line(
        joined,
        x="usage_date",
        y="cost_per_unit",
        markers=True,
        color_discrete_sequence=["#6FE2D3"],
        labels={"usage_date": "Metric date", "cost_per_unit": "Cost per unit"},
        title=f"Cost per unit over time · {metric_name}",
    )
    figure.update_layout(
        title={
            "text": f"Cost per unit over time · {metric_name}",
            "x": 0,
            "xanchor": "left",
        },
        height=410,
        xaxis={"automargin": True},
        yaxis={"tickformat": ",.2f", "automargin": True},
        margin={"l": 82, "r": 28, "t": 72, "b": 62},
    )
    apply_plotly_theme(figure)
    st.plotly_chart(figure, width="stretch", theme=None)
    with st.expander("View business metric values", expanded=False):
        render_compact_table(joined, max_rows=30)


def _governance_row(
    policy: str,
    status: str,
    evidence: str,
    action: str,
    *,
    tone: str,
) -> str:
    return (
        f'<article class="metrora-governance-row {escape(tone)}">'
        f'<div><span>{escape(status)}</span><strong>{escape(policy)}</strong></div>'
        f'<p>{escape(evidence)}</p><small>{escape(action)}</small></article>'
    )


def render_governance_panel(actual: pd.DataFrame, source_key: str) -> None:
    """Translate FinOps controls into a plain-language policy and action review."""
    import streamlit as st

    target_key = f"allocation_target_{source_key}"
    st.session_state.setdefault(target_key, 0.90)
    allocation_target = float(st.session_state[target_key])
    report = st.session_state.get("quality_report")
    budget = st.session_state.get("budget_table")
    business_metrics = st.session_state.get("business_metrics_table")
    sync = st.session_state.get("connection_sync") or {}
    rows: list[str] = []
    needs_attention = 0
    not_configured = 0

    quality_ready = bool(report is not None and report.ready_for_analysis)
    reconciliation = getattr(report, "reconciliation", None)
    difference = getattr(reconciliation, "absolute_difference", None)
    if quality_ready:
        rows.append(
            _governance_row(
                "Trusted cost model",
                "Met",
                "Source and canonical totals reconcile with a "
                f"{float(difference or 0):,.2f} difference.",
                "No action required unless the source changes.",
                tone="met",
            )
        )
    else:
        needs_attention += 1
        rows.append(
            _governance_row(
                "Trusted cost model",
                "Needs attention",
                "At least one blocking data-quality or reconciliation check is unresolved.",
                "Open Data settings and resolve the blocking evidence before sharing results.",
                tone="attention",
            )
        )

    ownership_fields = [
        field
        for field in ("account_id", "department", "project", "environment")
        if field in actual.columns
    ]
    if ownership_fields:
        try:
            coverage = calculate_allocation_coverage(actual, ownership_fields)
            any_row = coverage.loc[coverage["field"].eq("any ownership field")].iloc[0]
            cost_coverage = float(any_row["cost_coverage"] or 0.0)
            unallocated = max(
                0.0,
                float(any_row["positive_cost"])
                - float(any_row["allocated_positive_cost"]),
            )
        except (AnalyticsInputError, KeyError, ValueError):
            cost_coverage = 0.0
            unallocated = float(pd.to_numeric(actual["cost"], errors="coerce").clip(lower=0).sum())
        if cost_coverage >= allocation_target:
            rows.append(
                _governance_row(
                    "Cost ownership",
                    "Met",
                    f"{cost_coverage:.1%} of positive spend has at least one ownership field.",
                    f"Maintain coverage at or above the {allocation_target:.0%} policy target.",
                    tone="met",
                )
            )
        else:
            needs_attention += 1
            rows.append(
                _governance_row(
                    "Cost ownership",
                    "Needs attention",
                    f"{cost_coverage:.1%} is allocated; {unallocated:,.2f} of positive "
                    "spend has no owner.",
                    "Assign missing cost centers, projects, or environments to reach "
                    f"{allocation_target:.0%}.",
                    tone="attention",
                )
            )
    else:
        needs_attention += 1
        rows.append(
            _governance_row(
                "Cost ownership",
                "Needs attention",
                "No account, department, project, or environment field is available.",
                "Add an ownership dimension to enable accountability and showback.",
                tone="attention",
            )
        )

    if budget is not None:
        rows.append(
            _governance_row(
                "Budget accountability",
                "Met",
                "A budget is connected to the current workspace.",
                "Review Budget variance for scope-level utilization and exceptions.",
                tone="met",
            )
        )
    else:
        not_configured += 1
        rows.append(
            _governance_row(
                "Budget accountability",
                "Not configured",
                "Current cost and forecast cannot yet be compared with an approved plan.",
                "Upload a budget in this workspace to activate plan-risk monitoring.",
                tone="neutral",
            )
        )

    if business_metrics is not None:
        rows.append(
            _governance_row(
                "Business value linkage",
                "Met",
                "Business-volume data is connected for unit-cost analysis.",
                "Review Unit economics and track cost per outcome over time.",
                tone="met",
            )
        )
    else:
        not_configured += 1
        rows.append(
            _governance_row(
                "Business value linkage",
                "Not configured",
                "Cloud cost is not yet connected to customers, revenue, transactions, or usage.",
                "Add a business metric to measure cost per outcome.",
                tone="neutral",
            )
        )

    modified_text = sync.get("latest_modified")
    if modified_text:
        try:
            modified = datetime.fromisoformat(str(modified_text)).astimezone()
            age_hours = max(
                0.0,
                (datetime.now().astimezone() - modified).total_seconds() / 3600,
            )
        except ValueError:
            age_hours = 999.0
        if age_hours <= 48:
            rows.append(
                _governance_row(
                    "Source freshness",
                    "Met",
                    f"The connected cloud export is {age_hours:.1f} hours old.",
                    "Refresh-on-open will check for a newer complete export.",
                    tone="met",
                )
            )
        else:
            needs_attention += 1
            rows.append(
                _governance_row(
                    "Source freshness",
                    "Needs attention",
                    f"The latest connected cloud export is {age_hours / 24:.1f} days old.",
                    "Check the provider export schedule and run Sync latest in Data sources.",
                    tone="attention",
                )
            )
    else:
        not_configured += 1
        rows.append(
            _governance_row(
                "Source freshness",
                "Manual source",
                "This file upload has no provider refresh timestamp.",
                "Connect a scheduled cloud export if automated freshness monitoring is required.",
                tone="neutral",
            )
        )

    status_columns = st.columns(3)
    status_columns[0].metric("Policies reviewed", len(rows))
    status_columns[1].metric("Needs attention", needs_attention)
    status_columns[2].metric("Not configured", not_configured)
    st.caption(
        "Default ownership target: "
        f"{allocation_target:.0%}. Change it under Data settings → Analysis defaults."
    )
    st.markdown(
        f'<section class="metrora-governance-list">{"".join(rows)}</section>',
        unsafe_allow_html=True,
    )


def render_operations_view(
    settings: Settings,
    normalized: NormalizedTable,
    source_key: str,
    actual: pd.DataFrame,
    *,
    show_header: bool = True,
) -> None:
    """Render optional planning and business-context analyses."""
    del settings
    import streamlit as st

    if show_header:
        st.header("Connect spend to the business")
        st.write(
            "Layer budgets, ownership coverage, and business metrics onto the current view "
            "without changing the canonical billing table."
        )
    budget_tab, allocation_tab, business_tab = st.tabs(
        ["Budget variance", "Allocation coverage", "Business efficiency"]
    )
    with budget_tab:
        _render_budget_view(actual, source_key)
    with allocation_tab:
        _render_allocation_view(actual)
    with business_tab:
        _render_business_metric_view(actual, source_key)


def render_budget_panel(actual: pd.DataFrame, source_key: str) -> None:
    """Render budget connection and variance as a standalone planning panel."""
    _render_budget_view(actual, source_key)


def render_allocation_panel(actual: pd.DataFrame) -> None:
    """Render ownership coverage as a standalone accountability panel."""
    _render_allocation_view(actual)


def render_business_metric_panel(actual: pd.DataFrame, source_key: str) -> None:
    """Render business-volume and unit-cost context as a standalone panel."""
    _render_business_metric_view(actual, source_key)
