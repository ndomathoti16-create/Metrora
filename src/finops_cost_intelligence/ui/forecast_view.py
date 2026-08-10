"""Streamlit forecast and anomaly views."""

from __future__ import annotations

import pandas as pd

from ..analytics.spend import prepare_daily_spend
from ..anomalies import detect_spend_anomalies
from ..contracts.analytics import AnalyticsInputError
from ..contracts.forecasting import ForecastInputError
from ..forecasting import forecast_daily_spend
from .branding import apply_plotly_theme, render_compact_table

BLUE = "#9BB8FF"
RED = "#F2C58E"


def _render_forecast(
    actual: pd.DataFrame,
    source_key: str,
    *,
    show_settings: bool,
) -> None:
    import plotly.graph_objects as go
    import streamlit as st

    forecast_color = "#7EE0D0"
    forecast_fill = "rgba(126,224,208,0.14)"

    if show_settings:
        with st.expander("Forecast settings", expanded=False):
            horizon = st.select_slider(
                "Forecast horizon",
                options=[7, 14, 30],
                value=14,
                format_func=lambda value: f"{value} days",
                key=f"forecast_horizon_{source_key}",
            )
    else:
        horizon = int(st.session_state.get(f"forecast_horizon_{source_key}", 14))
    try:
        forecast, summary = forecast_daily_spend(actual, horizon_days=horizon)
        history = prepare_daily_spend(actual)
    except (ForecastInputError, AnalyticsInputError) as exc:
        st.error(f"Forecast unavailable: {exc}")
        return
    st.caption(
        f"Method: {summary.method.replace('_', ' ')} · history: {summary.history_start} to "
        f"{summary.history_end} · uncertainty uses residual variation from the fitted history."
    )
    metric_columns = st.columns(3)
    metric_columns[0].metric("Forecast total", f"{summary.forecast_total:,.2f}")
    metric_columns[1].metric("Forecast days", f"{summary.horizon_days:,}")
    metric_columns[2].metric("Residual standard deviation", f"{summary.residual_std:,.2f}")
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=history["usage_date"],
            y=history["cost"],
            mode="lines+markers",
            name="Actual daily spend",
            line={"color": BLUE, "width": 2},
            marker={"size": 5},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=forecast["usage_date"],
            y=forecast["upper_bound"],
            mode="lines",
            name="Upper bound",
            line={"color": forecast_color, "dash": "dot", "width": 1},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=forecast["usage_date"],
            y=forecast["lower_bound"],
            mode="lines",
            name="Lower bound",
            line={"color": forecast_color, "dash": "dot", "width": 1},
            fill="tonexty",
            fillcolor=forecast_fill,
        )
    )
    figure.add_trace(
        go.Scatter(
            x=forecast["usage_date"],
            y=forecast["forecast_cost"],
            mode="lines+markers",
            name="Forecast",
            line={"color": forecast_color, "width": 2.5},
            marker={"size": 5},
        )
    )
    figure.update_layout(
        title={"text": "Daily spend forecast", "x": 0, "xanchor": "left"},
        height=410,
        xaxis={"title": "Usage date", "automargin": True},
        yaxis={"title": "Cost", "tickformat": ",.0f", "automargin": True},
        hovermode="x unified",
        margin={"l": 82, "r": 28, "t": 72, "b": 62},
    )
    apply_plotly_theme(figure)
    st.plotly_chart(figure, width="stretch", theme=None)
    display = forecast.copy()
    for column in ("forecast_cost", "lower_bound", "upper_bound"):
        display[column] = display[column].round(2)
    with st.expander("View forecast values", expanded=False):
        render_compact_table(display, max_rows=30)


def _render_anomalies(
    actual: pd.DataFrame,
    source_key: str,
    *,
    show_settings: bool,
) -> None:
    import plotly.graph_objects as go
    import streamlit as st

    if show_settings:
        with st.expander("Anomaly settings", expanded=False):
            threshold = st.slider(
                "Anomaly sensitivity",
                min_value=2.5,
                max_value=6.0,
                value=3.5,
                step=0.5,
                key=f"anomaly_threshold_{source_key}",
                help="Lower values flag more deviations from the prior rolling baseline.",
            )
    else:
        threshold = float(st.session_state.get(f"anomaly_threshold_{source_key}", 3.5))
    try:
        diagnostics, summary = detect_spend_anomalies(actual, threshold=threshold)
    except AnalyticsInputError as exc:
        st.error(f"Anomaly scan unavailable: {exc}")
        return
    st.caption(
        f"Method: prior rolling median/MAD · window: {summary.window_days} days · "
        f"minimum history: {summary.minimum_history_days} days."
    )
    st.metric("Meaningful anomalies", f"{summary.anomaly_count:,}")
    if diagnostics.empty:
        st.info("No valid daily history is available for anomaly detection.")
        return
    figure = go.Figure(
        go.Scatter(
            x=diagnostics["usage_date"],
            y=diagnostics["cost"],
            mode="lines",
            name="Daily spend",
            line={"color": BLUE, "width": 2},
        )
    )
    anomalies = diagnostics.loc[diagnostics["is_anomaly"]]
    figure.add_trace(
        go.Scatter(
            x=anomalies["usage_date"],
            y=anomalies["cost"],
            mode="markers",
            name="Anomaly",
            marker={"color": RED, "size": 10, "symbol": "diamond"},
            text=anomalies["direction"],
            hovertemplate="%{x|%Y-%m-%d}<br>Cost: %{y:,.2f}<br>%{text}<extra></extra>",
        )
    )
    figure.update_layout(
        title={"text": "Historical daily spend anomalies", "x": 0, "xanchor": "left"},
        height=410,
        xaxis={"title": "Usage date", "automargin": True},
        yaxis={"title": "Cost", "tickformat": ",.0f", "automargin": True},
        hovermode="x unified",
        margin={"l": 82, "r": 28, "t": 72, "b": 62},
    )
    apply_plotly_theme(figure)
    st.plotly_chart(figure, width="stretch", theme=None)
    if anomalies.empty:
        st.success("No anomalies exceeded the selected threshold.")
        return
    display = anomalies[
        [
            "usage_date",
            "cost",
            "expected_cost",
            "absolute_change",
            "change_pct",
            "anomaly_score",
            "direction",
            "severity",
        ]
    ].copy()
    for column in ("cost", "expected_cost", "absolute_change"):
        display[column] = display[column].round(2)
    display["change_pct"] = display["change_pct"].map(
        lambda value: f"{value:+.1%}" if pd.notna(value) else "—"
    )
    display["anomaly_score"] = display["anomaly_score"].map(
        lambda value: "∞" if value == float("inf") else f"{value:.2f}"
    )
    with st.expander("View flagged dates", expanded=False):
        render_compact_table(display, max_rows=30)


def render_forecast_view(
    actual: pd.DataFrame,
    source_key: str,
    *,
    show_header: bool = True,
    show_settings: bool = False,
) -> None:
    """Render forecasting and anomaly detection over the filtered billing view."""
    import streamlit as st

    if show_header:
        st.header("Plan ahead")
        st.write(
            "Use transparent historical methods to estimate future spend and surface unusual "
            "changes, with the evidence behind every flag."
        )
    forecast_tab, anomaly_tab = st.tabs(["Forecast", "Anomalies"])
    with forecast_tab:
        _render_forecast(actual, source_key, show_settings=show_settings)
    with anomaly_tab:
        _render_anomalies(actual, source_key, show_settings=show_settings)


def render_forecast_panel(actual: pd.DataFrame, source_key: str) -> None:
    """Render the standard forecast without exposing model controls."""
    _render_forecast(actual, source_key, show_settings=False)


def render_anomaly_panel(actual: pd.DataFrame, source_key: str) -> None:
    """Render anomaly monitoring with the workspace's saved sensitivity."""
    _render_anomalies(actual, source_key, show_settings=False)
