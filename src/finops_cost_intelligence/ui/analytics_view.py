"""Application-style Streamlit views for core FinOps spend analytics."""

from __future__ import annotations

from datetime import date, timedelta
from html import escape
from typing import TYPE_CHECKING

import pandas as pd

from ..analytics import (
    DEFAULT_BREAKDOWN_DIMENSIONS,
    aggregate_spend,
    analyze_service_cost_drivers,
    calculate_spend_summary,
    filter_billing_data,
    prepare_daily_spend,
)
from ..anomalies import detect_spend_anomalies
from ..contracts.analytics import AnalyticsInputError
from ..contracts.forecasting import ForecastInputError
from ..contracts.normalization import NormalizedTable
from ..forecasting import forecast_daily_spend
from .branding import apply_plotly_theme, render_compact_table

if TYPE_CHECKING:
    from ..config import Settings


VIOLET = "#6658E8"
MINT = "#2F9F83"


def _format_cost(value: float | None, currency: str) -> str:
    if value is None:
        return "—"
    if currency in {"Unspecified", "Mixed"}:
        return f"{value:,.2f}"
    return f"{currency} {value:,.2f}"


def _format_cost_delta(value: float | None, currency: str) -> str | None:
    """Keep the sign first so Streamlit renders the correct delta direction."""
    if value is None:
        return None
    sign = "+" if value > 0 else "-" if value < 0 else ""
    magnitude = abs(float(value))
    if currency in {"Unspecified", "Mixed"}:
        return f"{sign}{magnitude:,.2f}"
    return f"{sign}{currency} {magnitude:,.2f}"


def _date_range(value: object) -> tuple[date | None, date | None]:
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return value[0], value[1]
    if isinstance(value, date):
        return value, value
    return None, None


def _available_dimensions(dataframe: pd.DataFrame) -> list[str]:
    return [
        dimension
        for dimension in DEFAULT_BREAKDOWN_DIMENSIONS
        if dimension in dataframe.columns and dataframe[dimension].notna().any()
    ]


def _equal_periods(
    dataframe: pd.DataFrame,
    *,
    maximum_days: int = 14,
) -> tuple[pd.DataFrame, pd.DataFrame, tuple[pd.Timestamp, ...] | None, int]:
    daily = prepare_daily_spend(dataframe)
    if len(daily) < 2:
        return dataframe.copy(), dataframe.iloc[0:0].copy(), None, max(len(daily), 1)
    window_days = min(maximum_days, len(daily) // 2)
    recent_end = pd.Timestamp(daily["usage_date"].max()).normalize()
    recent_start = recent_end - pd.Timedelta(int(window_days - 1), unit="D")
    prior_end = recent_start - pd.Timedelta(1, unit="D")
    prior_start = prior_end - pd.Timedelta(int(window_days - 1), unit="D")
    recent = filter_billing_data(
        dataframe,
        date_start=recent_start,
        date_end=recent_end,
    )
    prior = filter_billing_data(
        dataframe,
        date_start=prior_start,
        date_end=prior_end,
    )
    return recent, prior, (recent_start, recent_end, prior_start, prior_end), window_days


def _render_home_kpis(
    current: pd.DataFrame,
    prior: pd.DataFrame,
    *,
    window_days: int,
) -> tuple[object, int | None, object | None]:
    import streamlit as st

    summary = calculate_spend_summary(
        current,
        prior_dataframe=prior,
        top_dimension="service" if "service" in current else None,
    )
    anomaly_count: int | None = None
    try:
        _, anomaly_summary = detect_spend_anomalies(pd.concat([prior, current]))
        anomaly_count = anomaly_summary.anomaly_count
    except (AnalyticsInputError, KeyError, ValueError):
        pass

    forecast_summary = None
    try:
        _, forecast_summary = forecast_daily_spend(
            pd.concat([prior, current]), horizon_days=14
        )
    except (AnalyticsInputError, ForecastInputError, KeyError, ValueError):
        pass

    change_label = (
        f"{summary.change_pct:+.1%}" if summary.change_pct is not None else "No comparison"
    )
    columns = st.columns(4)
    columns[0].metric(
        "Current window spend",
        _format_cost(summary.total_cost, summary.currency),
        help=f"Canonical cost in the latest {window_days}-day window.",
    )
    columns[1].metric(
        "Change vs prior",
        change_label,
        delta=_format_cost_delta(summary.change_amount, summary.currency),
        delta_color="inverse",
        help="Current window compared with the immediately preceding equal window.",
    )
    columns[2].metric(
        "Next 14 days",
        (
            _format_cost(forecast_summary.forecast_total, summary.currency)
            if forecast_summary is not None
            else "Unavailable"
        ),
        help="Deterministic forecast from the available daily history.",
    )
    columns[3].metric(
        "Anomalies to review",
        f"{anomaly_count:,}" if anomaly_count is not None else "Unavailable",
        help="Historical days exceeding the deterministic rolling-baseline threshold.",
    )
    return summary, anomaly_count, forecast_summary


def _render_trend(
    daily: pd.DataFrame,
    currency: str,
    *,
    title: str = "Spend over time",
    height: int = 390,
) -> None:
    import plotly.graph_objects as go
    import streamlit as st

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=daily["usage_date"],
            y=daily["cost"],
            mode="lines+markers",
            name="Daily spend",
            line={"color": VIOLET, "width": 2.5},
            marker={"color": VIOLET, "size": 5},
            hovertemplate="%{x|%b %d, %Y}<br>Cost: %{y:,.2f}<extra></extra>",
        )
    )
    working = daily.copy()
    working["rolling_7_day"] = working["cost"].rolling(7, min_periods=1).mean()
    figure.add_trace(
        go.Scatter(
            x=working["usage_date"],
            y=working["rolling_7_day"],
            mode="lines",
            name="7-day average",
            line={"color": MINT, "width": 2, "dash": "dash"},
            hovertemplate="%{x|%b %d, %Y}<br>Average: %{y:,.2f}<extra></extra>",
        )
    )
    figure.update_layout(
        title={"text": title, "x": 0, "xanchor": "left"},
        height=height,
        xaxis={"title": None, "automargin": True},
        yaxis={
            "title": (
                f"Cost ({currency})"
                if currency not in {"Unspecified", "Mixed"}
                else "Cost"
            ),
            "tickformat": ",.0f",
            "automargin": True,
        },
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.08, "x": 0},
        margin={"l": 82, "r": 24, "t": 72, "b": 52},
    )
    apply_plotly_theme(figure)
    st.plotly_chart(figure, width="stretch", theme=None)


def _render_breakdown(
    dataframe: pd.DataFrame,
    currency: str,
    dimension: str,
    *,
    top_n: int = 8,
) -> pd.DataFrame:
    import plotly.express as px
    import streamlit as st

    breakdown = aggregate_spend(dataframe, dimension, top_n=top_n)
    cost_label = f"Cost ({currency})" if currency not in {"Unspecified", "Mixed"} else "Cost"
    dimension_label = dimension.replace("_", " ").title()
    chart_data = breakdown.sort_values("cost").copy()
    chart_data["value"] = chart_data["value"].astype(str)
    figure = px.bar(
        chart_data,
        x="cost",
        y="value",
        orientation="h",
        color_discrete_sequence=[VIOLET],
        labels={"cost": cost_label, "value": dimension_label},
        title=f"Spend by {dimension_label}",
    )
    figure.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Cost: %{x:,.2f}<extra></extra>",
    )
    figure.update_layout(
        title={"text": f"Spend by {dimension_label}", "x": 0, "xanchor": "left"},
        height=390,
        xaxis={"title": cost_label, "tickformat": ",.0f", "automargin": True},
        yaxis={"title": None, "automargin": True},
        margin={"l": 132, "r": 62, "t": 72, "b": 62},
        showlegend=False,
        uniformtext={"minsize": 10, "mode": "hide"},
    )
    apply_plotly_theme(figure)
    st.plotly_chart(figure, width="stretch", theme=None)
    return breakdown


def _driver_signal(value: object) -> str:
    return f"{float(value):+.1%}" if pd.notna(value) else "Unavailable"


def _render_driver_rows(drivers: pd.DataFrame, currency: str) -> None:
    """Render driver evidence without forcing users through a wide table."""
    import streamlit as st

    rows: list[str] = []
    for _, driver in drivers.head(3).iterrows():
        change = _format_cost_delta(float(driver["change_amount"]), currency) or "0.00"
        usage_signal = escape(_driver_signal(driver["usage_change_pct"]))
        rate_signal = escape(_driver_signal(driver["effective_rate_change_pct"]))
        evidence = escape(str(driver["evidence_level"]))
        rows.append(
            f'<article class="metrora-driver-row">'
            f'<div class="metrora-driver-head"><div>'
            f"<strong>{escape(str(driver['service']))}</strong>"
            f"<span>{escape(str(driver['driver_type']))}</span>"
            f"</div><b>{escape(change)}</b></div>"
            f'<div class="metrora-driver-body">'
            f'<div class="metrora-driver-why"><small>Why this moved</small>'
            f"<p>{escape(str(driver['explanation']))}</p></div>"
            f"<div><small>Usage signal</small><strong>{usage_signal}</strong></div>"
            f"<div><small>Rate / mix</small><strong>{rate_signal}</strong></div>"
            f"<div><small>Evidence</small><strong>{evidence}</strong></div>"
            "</div></article>"
        )
    st.markdown(
        f'<div class="metrora-driver-list">{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def _render_attention_item(title: str, detail: str, tone: str = "neutral") -> None:
    import streamlit as st

    st.markdown(
        f"""
        <div class="metrora-attention-item {escape(tone)}">
            <span></span>
            <div><strong>{escape(title)}</strong><p>{escape(detail)}</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _navigate_button(label: str, page: str, key: str) -> None:
    import streamlit as st

    if st.button(label, key=key, width="stretch"):
        st.session_state["workspace_page"] = page
        st.rerun()


def render_home_view(
    settings: Settings,
    normalized: NormalizedTable,
    source_key: str,
) -> None:
    """Render an automated operating home with no required analytical controls."""
    del settings
    import streamlit as st

    quality_report = st.session_state.get("quality_report")
    if quality_report is not None and not quality_report.ready_for_analysis:
        st.warning("A blocking data-quality check needs attention before analysis can continue.")
        _navigate_button("Review data quality", "Advanced", "home_review_quality")
        return

    dataframe = normalized.dataframe.copy()
    try:
        current, prior, bounds, window_days = _equal_periods(dataframe)
        summary, anomaly_count, _ = _render_home_kpis(
            current,
            prior,
            window_days=window_days,
        )
        daily = prepare_daily_spend(dataframe)
    except (AnalyticsInputError, KeyError, ValueError) as exc:
        st.error(f"The workspace could not calculate a spend overview: {exc}")
        return

    st.caption(
        f"Latest {window_days}-day window · {summary.date_start} to {summary.date_end} · "
        f"{summary.row_count:,} cost rows · {summary.currency} · {normalized.source_name}"
    )

    drivers = pd.DataFrame()
    if bounds is not None:
        recent_start, recent_end, prior_start, prior_end = bounds
        try:
            drivers = analyze_service_cost_drivers(
                dataframe,
                recent_start=recent_start,
                recent_end=recent_end,
                prior_start=prior_start,
                prior_end=prior_end,
                top_n=3,
            )
        except (AnalyticsInputError, KeyError, ValueError):
            pass

    st.markdown(
        '<div class="metrora-subsection-label">Operating view</div>',
        unsafe_allow_html=True,
    )
    chart_column, attention_column = st.columns([1.55, 0.78], gap="large")
    with chart_column:
        _render_trend(daily, summary.currency, title="Daily spend and short-term baseline")
    with attention_column:
        st.markdown("#### Attention queue")
        st.caption("The shortest path from signal to the next useful action.")
        if not drivers.empty:
            mover = drivers.iloc[0]
            _render_attention_item(
                f"Inspect {mover['service']}",
                (
                    f"{_format_cost(float(mover['change_amount']), summary.currency)} movement. "
                    f"Observed mechanism: {mover['driver_type']}."
                ),
                "attention" if float(mover["change_amount"]) > 0 else "positive",
            )
            _navigate_button("Open Cost explorer", "Cost explorer", "home_open_explorer")
        if anomaly_count:
            _render_attention_item(
                "Review unusual spend days",
                f"{anomaly_count:,} historical day(s) exceeded the rolling baseline.",
                "attention",
            )
            _navigate_button("Review anomalies", "Plans & alerts", "home_open_anomalies")
        if st.session_state.get("budget_table") is None:
            _render_attention_item(
                "Add plan context",
                "No budget is connected, so forecast-to-plan risk is not yet available.",
            )
            _navigate_button("Connect a budget", "Plans & alerts", "home_open_budget")
        if drivers.empty and not anomaly_count:
            st.success("No material movement or anomaly requires immediate review.")

    if not drivers.empty:
        st.markdown("### What is moving spend")
        st.caption(
            "Billing-observed explanation only. Metrora labels operational root cause as "
            "unconfirmed until usage, pricing, or deployment evidence supports it."
        )
        _render_driver_rows(drivers, summary.currency)

    st.session_state["analytics_filtered_table"] = current
    st.session_state["analytics_source_key"] = source_key


def render_cost_explorer_view(
    settings: Settings,
    normalized: NormalizedTable,
    source_key: str,
    *,
    show_header: bool = False,
) -> None:
    """Render a focused cost explorer with filters, grouping, and driver diagnostics."""
    del settings
    import streamlit as st

    quality_report = st.session_state.get("quality_report")
    if quality_report is not None and not quality_report.ready_for_analysis:
        st.warning("Analysis is paused until the blocking quality checks are resolved in Advanced.")
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

    if show_header:
        st.header("Cost explorer")
        st.write("Filter one trusted cost model and inspect the exact values behind the chart.")

    available_dimensions = _available_dimensions(dataframe)
    default_start = max(minimum_date, maximum_date - timedelta(days=29))
    controls = st.columns([1.15, 0.85])
    with controls[0]:
        selected_dates = st.date_input(
            "Analysis period",
            value=(default_start, maximum_date),
            min_value=minimum_date,
            max_value=maximum_date,
            key=f"analysis_dates_{source_key}",
        )
    with controls[1]:
        preferred_dimension = st.session_state.get(
            f"default_breakdown_dimension_{source_key}", "service"
        )
        dimension_index = (
            available_dimensions.index(preferred_dimension)
            if preferred_dimension in available_dimensions
            else 0
        )
        dimension = st.selectbox(
            "Group spend by",
            available_dimensions,
            index=dimension_index,
            format_func=lambda value: value.replace("_", " ").title(),
            key=f"breakdown_dimension_{source_key}",
            disabled=not available_dimensions,
        )
    date_start, date_end = _date_range(selected_dates)

    selections: dict[str, list[object]] = {}
    filter_dimensions = [
        dimension_name
        for dimension_name in (
            "service",
            "account_id",
            "department",
            "project",
            "environment",
            "region",
        )
        if dimension_name in dataframe.columns and dataframe[dimension_name].notna().any()
    ]
    if filter_dimensions:
        with st.expander("Filters", expanded=False):
            st.caption("Optional. Empty selections include the complete analysis period.")
            filter_columns = st.columns(3)
            for index, dimension_name in enumerate(filter_dimensions):
                options = sorted(
                    dataframe[dimension_name].dropna().astype(str).unique().tolist()
                )
                with filter_columns[index % len(filter_columns)]:
                    selections[dimension_name] = st.multiselect(
                        dimension_name.replace("_", " ").title(),
                        options,
                        key=f"analysis_filter_{dimension_name}_{source_key}",
                    )

    if date_start is None or date_end is None:
        st.info("Select both a start and end date to view the analysis.")
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
        st.warning("No billing rows match this view. Remove a filter to continue.")
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
    summary = calculate_spend_summary(
        filtered,
        prior_dataframe=prior,
        top_dimension="service" if "service" in filtered else None,
    )
    top_share = summary.top_dimension_share
    change_label = (
        "No prior period" if summary.change_pct is None else f"{summary.change_pct:+.1%}"
    )
    kpis = st.columns(4)
    kpis[0].metric("Total spend", _format_cost(summary.total_cost, summary.currency))
    kpis[1].metric(
        "Period change",
        change_label,
        delta=_format_cost_delta(summary.change_amount, summary.currency),
        delta_color="inverse",
    )
    kpis[2].metric(
        "Average per day", _format_cost(summary.average_daily_cost, summary.currency)
    )
    kpis[3].metric(
        "Top service share", f"{top_share:.1%}" if top_share is not None else "—"
    )
    active_filters = sum(bool(values) for values in selections.values())
    st.caption(
        f"{summary.date_start} to {summary.date_end} · {summary.row_count:,} cost rows · "
        f"{summary.currency} · {active_filters} active filter(s) · {normalized.source_name}"
    )

    top_n = int(st.session_state.get(f"breakdown_top_n_{source_key}", 8))
    daily = prepare_daily_spend(filtered)
    chart_columns = st.columns([1.22, 1], gap="large")
    with chart_columns[0]:
        _render_trend(daily, summary.currency)
    with chart_columns[1]:
        breakdown = (
            _render_breakdown(
                filtered,
                summary.currency,
                dimension,
                top_n=top_n,
            )
            if available_dimensions and dimension
            else pd.DataFrame()
        )

    if not breakdown.empty:
        with st.expander("Exact breakdown values", expanded=False):
            display = breakdown.copy()
            display["cost"] = display["cost"].round(2)
            display["share_of_total"] = display["share_of_total"].map(
                lambda value: f"{value:.1%}"
            )
            render_compact_table(display, max_rows=max(top_n, 15))

    if "service" in filtered.columns and not prior.empty:
        try:
            drivers = analyze_service_cost_drivers(
                pd.concat([prior, filtered], ignore_index=True),
                recent_start=date_start,
                recent_end=date_end,
                prior_start=prior_start,
                prior_end=prior_end,
                top_n=3,
            )
        except (AnalyticsInputError, KeyError, ValueError):
            drivers = pd.DataFrame()
        if not drivers.empty:
            st.markdown("### Driver diagnosis")
            st.caption(
                "This explains the billing-observed mechanism. It does not infer a deployment, "
                "incident, or optimization cause without supporting operational data."
            )
            _render_driver_rows(drivers, summary.currency)

    st.session_state["analytics_filtered_table"] = filtered
    st.session_state["analytics_source_key"] = source_key


def render_analytics_view(
    settings: Settings,
    normalized: NormalizedTable,
    source_key: str,
    *,
    include_operations: bool = True,
    include_forecast: bool = True,
    include_report: bool = True,
    show_header: bool = True,
) -> None:
    """Backward-compatible combined view used by earlier application integrations."""
    render_cost_explorer_view(
        settings,
        normalized,
        source_key,
        show_header=show_header,
    )
    filtered = normalized.dataframe.copy()
    try:
        import streamlit as st

        filtered = st.session_state.get("analytics_filtered_table", filtered)
    except ImportError:
        pass
    if include_operations:
        from .operations_view import render_operations_view

        render_operations_view(settings, normalized, source_key, filtered)
    if include_forecast:
        from .forecast_view import render_forecast_view

        render_forecast_view(filtered, source_key)
    if include_report:
        from .report_view import render_report_view

        render_report_view(settings, normalized, source_key, filtered)
