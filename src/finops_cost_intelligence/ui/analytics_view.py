"""Streamlit dashboard for core FinOps spend analytics."""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

import pandas as pd

from ..analytics import (
    DEFAULT_BREAKDOWN_DIMENSIONS,
    aggregate_spend,
    calculate_spend_summary,
    filter_billing_data,
    prepare_daily_spend,
)
from ..contracts.analytics import AnalyticsInputError
from ..contracts.normalization import NormalizedTable
from .forecast_view import render_forecast_view
from .operations_view import render_operations_view
from .report_view import render_report_view

if TYPE_CHECKING:
    from ..config import Settings


BLUE = "#2F6BFF"
GOLD = "#D9A441"
TEXT = "#1F2937"


def _format_cost(value: float | None, currency: str) -> str:
    if value is None:
        return "—"
    if currency in {"Unspecified", "Mixed"}:
        return f"{value:,.2f}"
    return f"{currency} {value:,.2f}"


def _date_range(value: object) -> tuple[date | None, date | None]:
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return value[0], value[1]
    if isinstance(value, date):
        return value, value
    return None, None


def _render_kpis(summary, top_service_share: float | None) -> None:
    import streamlit as st

    change = summary.change_pct
    change_label = "No prior period"
    if change is not None:
        change_label = f"{change:+.1%} vs prior period"
    kpi_columns = st.columns(5)
    kpi_columns[0].metric(
        "Total spend",
        _format_cost(summary.total_cost, summary.currency),
        help="Sum of canonical cost values in the selected period.",
    )
    kpi_columns[1].metric(
        "Average daily spend",
        _format_cost(summary.average_daily_cost, summary.currency),
        help="Total spend divided by calendar days in the selected period.",
    )
    kpi_columns[2].metric(
        "Cost rows",
        f"{summary.row_count:,}",
        help="Number of normalized billing rows in the selected period.",
    )
    kpi_columns[3].metric(
        "Period change",
        change_label,
        delta=_format_cost(summary.change_amount, summary.currency)
        if summary.change_amount is not None
        else None,
    )
    kpi_columns[4].metric(
        "Top service share",
        f"{top_service_share:.1%}" if top_service_share is not None else "—",
        help="Largest service's share of selected-period spend.",
    )


def _render_trend(daily: pd.DataFrame, currency: str) -> None:
    import plotly.graph_objects as go
    import streamlit as st

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=daily["usage_date"],
            y=daily["cost"],
            mode="lines+markers",
            name="Daily spend",
            line={"color": BLUE, "width": 2},
            marker={"color": BLUE, "size": 5},
        )
    )
    daily = daily.copy()
    daily["rolling_7_day"] = daily["cost"].rolling(7, min_periods=1).mean()
    figure.add_trace(
        go.Scatter(
            x=daily["usage_date"],
            y=daily["rolling_7_day"],
            mode="lines",
            name="7-day average",
            line={"color": GOLD, "width": 2, "dash": "dash"},
        )
    )
    figure.update_layout(
        title="Daily cloud spend",
        xaxis_title="Usage date",
        yaxis_title=f"Cost ({currency})" if currency not in {"Unspecified", "Mixed"} else "Cost",
        hovermode="x unified",
        legend_title_text="Series",
        font={"color": TEXT},
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
    )
    st.plotly_chart(figure, use_container_width=True)


def _render_breakdown(dataframe: pd.DataFrame, currency: str, source_key: str) -> None:
    import plotly.express as px
    import streamlit as st

    available = [
        dimension
        for dimension in DEFAULT_BREAKDOWN_DIMENSIONS
        if dimension in dataframe.columns and dataframe[dimension].notna().any()
    ]
    if not available:
        st.info("No populated dimensions are available for a spend breakdown.")
        return
    dimension = st.selectbox(
        "Break down spend by",
        available,
        format_func=lambda value: value.replace("_", " ").title(),
        key=f"breakdown_dimension_{source_key}",
    )
    breakdown = aggregate_spend(dataframe, dimension, top_n=15)
    st.caption(
        f"Top {len(breakdown)} {dimension.replace('_', ' ')} values by cost. "
        "Share is calculated against total selected-period spend."
    )
    cost_label = f"Cost ({currency})" if currency not in {"Unspecified", "Mixed"} else "Cost"
    figure = px.bar(
        breakdown.sort_values("cost"),
        x="cost",
        y="value",
        orientation="h",
        color_discrete_sequence=[BLUE],
        labels={"cost": cost_label, "value": dimension.title()},
        title=f"Spend by {dimension.replace('_', ' ').title()}",
    )
    figure.update_layout(font={"color": TEXT}, margin={"l": 10, "r": 10, "t": 55, "b": 10})
    st.plotly_chart(figure, use_container_width=True)
    display = breakdown.copy()
    display["cost"] = display["cost"].round(2)
    display["share_of_total"] = (display["share_of_total"] * 100).round(2).astype(str) + "%"
    st.dataframe(display, use_container_width=True, hide_index=True)


def render_analytics_view(
    settings: Settings,
    normalized: NormalizedTable,
    source_key: str,
) -> None:
    """Render summary-first, filterable spend analytics from canonical data."""
    import streamlit as st

    quality_report = st.session_state.get("quality_report")
    if quality_report is not None and not quality_report.ready_for_analysis:
        st.warning("Analytics are paused until the blocking quality checks are resolved.")
        return

    dataframe = normalized.dataframe.copy()
    try:
        dates = pd.to_datetime(dataframe["usage_date"], errors="coerce").dropna()
        if dates.empty:
            raise AnalyticsInputError("No valid usage dates are available for analysis.")
        minimum_date = dates.min().date()
        maximum_date = dates.max().date()
    except KeyError as exc:
        st.error(f"Canonical data is missing {exc.args[0]!r}; analytics are unavailable.")
        return
    except AnalyticsInputError as exc:
        st.error(str(exc))
        return

    st.header("Core FinOps analytics")
    st.write(
        "Explore calculated spend trends and drivers. Filters apply to every KPI, "
        "chart, and table below."
    )
    with st.sidebar:
        st.header("Dashboard filters")
        selected_dates = st.date_input(
            "Analysis period",
            value=(minimum_date, maximum_date),
            min_value=minimum_date,
            max_value=maximum_date,
            key=f"analysis_dates_{source_key}",
        )
        date_start, date_end = _date_range(selected_dates)
        selections: dict[str, list[object]] = {}
        for dimension in ("service", "account_id", "department", "environment", "region"):
            if dimension not in dataframe.columns:
                continue
            options = sorted(dataframe[dimension].dropna().astype(str).unique().tolist())
            if not options:
                continue
            selections[dimension] = st.multiselect(
                dimension.replace("_", " ").title(),
                options,
                key=f"analysis_filter_{dimension}_{source_key}",
            )

    if date_start is None or date_end is None:
        st.info("Select both a start and end date to view analytics.")
        return
    try:
        filtered = filter_billing_data(
            dataframe,
            date_start=date_start,
            date_end=date_end,
            selections=selections,
        )
    except AnalyticsInputError as exc:
        st.error(str(exc))
        return
    if filtered.empty:
        st.warning("No billing rows match the selected filters.")
        return

    period_days = (date_end - date_start).days + 1
    prior_start = date_start - timedelta(days=period_days)
    prior_end = date_start - timedelta(days=1)
    prior = filter_billing_data(
        dataframe,
        date_start=prior_start,
        date_end=prior_end,
        selections=selections,
    )
    top_service = (
        aggregate_spend(filtered, "service", top_n=1) if "service" in filtered else pd.DataFrame()
    )
    top_share = float(top_service.iloc[0]["share_of_total"]) if not top_service.empty else None
    summary = calculate_spend_summary(
        filtered,
        prior_dataframe=prior,
        top_dimension="service" if "service" in filtered else None,
    )
    _render_kpis(summary, top_share)
    st.caption(
        f"Canonical billing rows · {summary.date_start} to {summary.date_end} · "
        f"currency: {summary.currency} · source: {normalized.source_name}"
    )

    daily = prepare_daily_spend(filtered)
    _render_trend(daily, summary.currency)
    _render_breakdown(filtered, summary.currency, source_key)
    st.session_state["analytics_filtered_table"] = filtered
    st.session_state["analytics_source_key"] = source_key
    render_operations_view(settings, normalized, source_key, filtered)
    render_forecast_view(filtered, source_key)
    render_report_view(settings, normalized, source_key, filtered)
