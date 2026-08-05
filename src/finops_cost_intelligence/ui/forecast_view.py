"""Streamlit forecast and anomaly views."""

from __future__ import annotations

import pandas as pd

from ..analytics.spend import prepare_daily_spend
from ..anomalies import detect_spend_anomalies
from ..contracts.analytics import AnalyticsInputError
from ..contracts.forecasting import ForecastInputError
from ..forecasting import forecast_daily_spend

BLUE = "#2878F0"
GOLD = "#D9F36B"
RED = "#FF816B"


def _render_forecast(actual: pd.DataFrame, source_key: str) -> None:
    import plotly.graph_objects as go
    import streamlit as st

    horizon = st.select_slider(
        "Forecast horizon",
        options=[7, 14, 30],
        value=14,
        format_func=lambda value: f"{value} days",
        key=f"forecast_horizon_{source_key}",
    )
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
            line={"color": GOLD, "dash": "dot", "width": 1},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=forecast["usage_date"],
            y=forecast["lower_bound"],
            mode="lines",
            name="Lower bound",
            line={"color": GOLD, "dash": "dot", "width": 1},
            fill="tonexty",
            fillcolor="rgba(217,164,65,0.14)",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=forecast["usage_date"],
            y=forecast["forecast_cost"],
            mode="lines+markers",
            name="Forecast",
            line={"color": GOLD, "width": 2},
            marker={"size": 5},
        )
    )
    figure.update_layout(
        title="Daily spend forecast",
        xaxis_title="Usage date",
        yaxis_title="Cost",
        hovermode="x unified",
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
    )
    st.plotly_chart(figure, width="stretch")
    display = forecast.copy()
    for column in ("forecast_cost", "lower_bound", "upper_bound"):
        display[column] = display[column].round(2)
    st.dataframe(display, width="stretch", hide_index=True)


def _render_anomalies(actual: pd.DataFrame, source_key: str) -> None:
    import plotly.graph_objects as go
    import streamlit as st

    threshold = st.slider(
        "Anomaly sensitivity",
        min_value=2.5,
        max_value=6.0,
        value=3.5,
        step=0.5,
        key=f"anomaly_threshold_{source_key}",
        help="Lower values flag more deviations from the prior rolling baseline.",
    )
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
        title="Historical daily spend anomalies",
        xaxis_title="Usage date",
        yaxis_title="Cost",
        hovermode="x unified",
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
    )
    st.plotly_chart(figure, width="stretch")
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
    st.dataframe(display, width="stretch", hide_index=True)


def render_forecast_view(actual: pd.DataFrame, source_key: str) -> None:
    """Render forecasting and anomaly detection over the filtered billing view."""
    import streamlit as st

    st.header("Plan ahead")
    st.write(
        "Use transparent historical methods to estimate future spend and surface unusual "
        "changes, with the evidence behind every flag."
    )
    forecast_tab, anomaly_tab = st.tabs(["Forecast", "Anomalies"])
    with forecast_tab:
        _render_forecast(actual, source_key)
    with anomaly_tab:
        _render_anomalies(actual, source_key)
