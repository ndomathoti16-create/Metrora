"""Task-focused Metrora workspace orchestration."""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

from ..analytics import DEFAULT_BREAKDOWN_DIMENSIONS, select_comparable_anomaly_history
from .analytics_view import render_cost_explorer_view, render_home_view
from .forecast_view import render_anomaly_panel, render_forecast_panel
from .ingestion_view import render_ingestion_view
from .mapping_view import source_key_for
from .operations_view import (
    render_allocation_panel,
    render_budget_panel,
    render_business_metric_panel,
)
from .report_view import render_report_view

if TYPE_CHECKING:
    from ..config import Settings


WORKSPACE_PAGES = (
    "Home",
    "Cost explorer",
    "Plans & alerts",
    "Reports",
    "Advanced",
)

LEGACY_PAGE_ALIASES = {
    "Overview": "Home",
    "Data & quality": "Advanced",
    "Investigate": "Plans & alerts",
    "Reports & exports": "Reports",
}


def _context() -> tuple[object | None, str | None]:
    import streamlit as st

    normalized = st.session_state.get("normalized_table")
    loaded_table = st.session_state.get("loaded_table")
    profile = st.session_state.get("data_profile")
    if loaded_table is None or profile is None:
        return normalized, None
    return normalized, source_key_for(loaded_table, profile)


def _render_page_header(page: str) -> None:
    import streamlit as st

    copy = {
        "Home": (
            "Overview",
            "Start with the current cost position, what needs attention, and the next action.",
        ),
        "Cost explorer": (
            "Spend explorer",
            "Filter the trusted cost model, compare periods, and inspect the exact drivers.",
        ),
        "Plans & alerts": (
            "Forecast & alerts",
            "Monitor forecast and anomaly risk, then connect budgets and business context.",
        ),
        "Reports": (
            "Reports & exports",
            "Package the calculated decision brief and export its supporting evidence.",
        ),
        "Advanced": (
            "Data settings",
            "Review source internals, semantic mappings, reconciliation, and model defaults.",
        ),
    }
    title, description = copy[page]
    loaded = st.session_state.get("loaded_table")
    profile = st.session_state.get("data_profile")
    quality = st.session_state.get("quality_report")
    if loaded is None or profile is None:
        status = "Waiting for data"
    elif quality is None:
        status = "Preparing analysis"
    elif quality.ready_for_analysis:
        status = "Analysis ready"
    else:
        status = "Review needed"
    if loaded is None or profile is None:
        context = (
            '<span class="metrora-workspace-context-item"><small>Source</small>'
            "<strong>None loaded</strong></span>"
        )
    else:
        verification = (
            "Verified" if quality is not None and quality.ready_for_analysis else "In review"
        )
        context = (
            '<span class="metrora-workspace-context-item"><small>Source</small>'
            f"<strong>{escape(loaded.source_name)}</strong></span>"
            '<span class="metrora-workspace-context-item"><small>Rows</small>'
            f"<strong>{profile.row_count:,}</strong></span>"
            '<span class="metrora-workspace-context-item"><small>Model</small>'
            f"<strong>{verification}</strong></span>"
        )
    st.markdown(
        f"""
        <header class="metrora-workspace-topbar">
            <div class="metrora-workspace-location">
                <span>Metrora</span><i>/</i><strong>{escape(title)}</strong>
                <span class="metrora-workspace-state">{escape(status)}</span>
            </div>
            <div class="metrora-workspace-title-row">
                <div class="metrora-workspace-title-copy">
                    <h1>{escape(title)}</h1>
                    <p>{escape(description)}</p>
                </div>
                <div class="metrora-workspace-command-meta">
                    {context}
                </div>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def _render_analysis_flow() -> None:
    """Show where the current run sits between source data and a decision."""
    import streamlit as st

    has_source = st.session_state.get("loaded_table") is not None
    has_model = st.session_state.get("normalized_table") is not None
    quality = st.session_state.get("quality_report")
    quality_ready = bool(quality is not None and quality.ready_for_analysis)
    has_context = bool(
        st.session_state.get("budget_table") is not None
        or st.session_state.get("business_metrics_table") is not None
    )

    steps = (
        (
            "01",
            "Source",
            "Billing data loaded" if has_source else "Awaiting billing data",
            has_source,
        ),
        ("02", "Model", "Fields normalized" if has_model else "Builds automatically", has_model),
        (
            "03",
            "Trust",
            "Checks reconciled" if quality_ready else "Validation pending",
            quality_ready,
        ),
        (
            "04",
            "Decision",
            "Context connected" if has_context else "Optional context",
            has_context,
        ),
    )
    nodes: list[str] = []
    for index, (number, label, detail, ready) in enumerate(steps):
        state = "is-ready" if ready else "is-pending"
        nodes.append(
            f'<div class="metrora-flow-node {state}">'
            f"<span>{number}</span><div><strong>{label}</strong><small>{detail}</small></div>"
            "</div>"
        )
        if index < len(steps) - 1:
            nodes.append('<div class="metrora-flow-link"><i></i></div>')
    st.markdown(
        '<section class="metrora-analysis-flow" aria-label="Analysis workflow">'
        '<div class="metrora-flow-heading"><span>Analysis flow</span>'
        "<small>Automated path</small></div>"
        f'<div class="metrora-flow-track">{"".join(nodes)}</div>'
        "</section>",
        unsafe_allow_html=True,
    )


def _render_empty_state(title: str, message: str, next_step: str) -> None:
    import streamlit as st

    st.markdown(
        f"""
        <div class="metrora-empty-state">
            <div class="metrora-empty-icon">+</div>
            <div>
                <h3>{escape(title)}</h3>
                <p>{escape(message)}</p>
                <span class="metrora-next-step">{escape(next_step)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _current_analysis_table(normalized, source_key: str):
    import streamlit as st

    filtered = st.session_state.get("analytics_filtered_table")
    if filtered is not None and st.session_state.get("analytics_source_key") == source_key:
        return filtered
    return normalized.dataframe.copy()


def _render_home(settings: Settings) -> None:
    normalized, source_key = _context()
    _render_analysis_flow()
    if normalized is None or source_key is None:
        import streamlit as st

        st.markdown(
            """
            <div class="metrora-automation-note">
                <strong>Drop in one billing export.</strong>
                <span>Metrora detects the fields, builds the cost model, reconciles the total,
                and opens the completed analysis automatically.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_ingestion_view(settings, include_mapping=False)
        return
    render_home_view(settings, normalized, source_key)


def _render_cost_explorer(settings: Settings) -> None:
    normalized, source_key = _context()
    if normalized is None or source_key is None:
        _render_empty_state(
            "No cost model yet",
            "Add a billing source on Overview before exploring spend.",
            "Overview > Billing source",
        )
        return
    render_cost_explorer_view(settings, normalized, source_key)


def _render_plans(settings: Settings) -> None:
    import streamlit as st

    normalized, source_key = _context()
    if normalized is None or source_key is None:
        _render_empty_state(
            "No cost model yet",
            "Add a billing source before forecasting or connecting planning data.",
            "Overview > Billing source",
        )
        return
    quality = st.session_state.get("quality_report")
    if quality is not None and not quality.ready_for_analysis:
        st.warning(
            "Planning is paused because a blocking data-quality check needs attention. "
            "Open Data settings to review it."
        )
        return

    actual = _current_analysis_table(normalized, source_key)
    anomaly_history = select_comparable_anomaly_history(normalized.dataframe)
    selected_scope = (
        "Spend explorer selection"
        if st.session_state.get("analytics_source_key") == source_key
        else "Full trusted model"
    )
    budget_status = "Connected" if st.session_state.get("budget_table") is not None else "Optional"
    business_status = (
        "Connected" if st.session_state.get("business_metrics_table") is not None else "Optional"
    )
    st.markdown(
        '<div class="metrora-planning-strip">'
        f"<div><span>Analysis scope</span><strong>{escape(selected_scope)}</strong></div>"
        f"<div><span>Budget</span><strong>{budget_status}</strong></div>"
        f"<div><span>Business metrics</span><strong>{business_status}</strong></div>"
        "<small>Model tuning lives in Data settings.</small></div>",
        unsafe_allow_html=True,
    )
    forecast_tab, anomaly_tab, budget_tab, ownership_tab, unit_tab = st.tabs(
        ["Forecast", "Anomalies", "Budgets", "Ownership", "Unit economics"]
    )
    with forecast_tab:
        render_forecast_panel(actual, source_key)
    with anomaly_tab:
        render_anomaly_panel(anomaly_history, source_key)
    with budget_tab:
        render_budget_panel(actual, source_key)
    with ownership_tab:
        render_allocation_panel(actual)
    with unit_tab:
        render_business_metric_panel(actual, source_key)


def _render_reports(settings: Settings) -> None:
    normalized, source_key = _context()
    if normalized is None or source_key is None:
        _render_empty_state(
            "Nothing to report yet",
            "Add a billing source so Metrora can calculate and package the evidence.",
            "Overview > Billing source",
        )
        return
    actual = _current_analysis_table(normalized, source_key)
    render_report_view(
        settings,
        normalized,
        source_key,
        actual,
        show_header=False,
    )


def _render_analysis_defaults(normalized, source_key: str) -> None:
    import streamlit as st

    st.subheader("Analysis defaults")
    st.write(
        "These controls tune the workspace for experienced analysts. Most users can leave "
        "the defaults unchanged and work entirely from Overview, Spend explorer, and "
        "Forecast & alerts."
    )
    horizon_key = f"forecast_horizon_{source_key}"
    anomaly_key = f"anomaly_threshold_{source_key}"
    top_n_key = f"breakdown_top_n_{source_key}"
    dimension_key = f"default_breakdown_dimension_{source_key}"
    st.session_state.setdefault(horizon_key, 14)
    st.session_state.setdefault(anomaly_key, 3.5)
    st.session_state.setdefault(top_n_key, 8)

    available_dimensions = [
        dimension
        for dimension in DEFAULT_BREAKDOWN_DIMENSIONS
        if dimension in normalized.dataframe.columns
        and normalized.dataframe[dimension].notna().any()
    ]
    if available_dimensions:
        preferred = st.session_state.get(dimension_key, "service")
        if preferred not in available_dimensions:
            st.session_state[dimension_key] = available_dimensions[0]
        else:
            st.session_state.setdefault(dimension_key, preferred)

    left, right = st.columns(2, gap="large")
    with left:
        st.select_slider(
            "Forecast horizon",
            options=[7, 14, 30],
            key=horizon_key,
            format_func=lambda value: f"{value} days",
            help="Applied to the forecast panel under Forecast & alerts.",
        )
        st.slider(
            "Anomaly sensitivity",
            min_value=2.5,
            max_value=6.0,
            step=0.5,
            key=anomaly_key,
            help="Lower values flag more deviations from the prior rolling baseline.",
        )
    with right:
        st.slider(
            "Breakdown rows",
            min_value=5,
            max_value=15,
            step=1,
            key=top_n_key,
            help="Maximum number of categories shown in a Spend explorer chart.",
        )
        if available_dimensions:
            st.selectbox(
                "Default cost dimension",
                available_dimensions,
                key=dimension_key,
                format_func=lambda value: value.replace("_", " ").title(),
            )
    st.info(
        "Metrora still calculates financial values deterministically. These settings only "
        "change the analytical view, not the source data or reconciliation result."
    )


def _render_advanced(settings: Settings) -> None:
    import streamlit as st

    normalized, source_key = _context()
    st.markdown(
        """
        <div class="metrora-advanced-note">
            <strong>Power-user area</strong>
            <span>Use this page to inspect or override automation. It is not required for a
            standard analysis unless Metrora flags an exception.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if normalized is None or source_key is None:
        render_ingestion_view(settings, include_mapping=True)
        return
    data_tab, defaults_tab = st.tabs(["Data source & model", "Analysis defaults"])
    with data_tab:
        render_ingestion_view(settings, include_mapping=True)
    with defaults_tab:
        _render_analysis_defaults(normalized, source_key)


def render_workspace(settings: Settings) -> None:
    """Render one task-focused workspace destination inside an application shell."""
    import streamlit as st

    requested_page = st.session_state.get("workspace_page", "Home")
    page = LEGACY_PAGE_ALIASES.get(requested_page, requested_page)
    if page not in WORKSPACE_PAGES:
        page = "Home"
    st.session_state["workspace_page"] = page

    with st.container(key="workspace-shell"):
        _render_page_header(page)
        if page == "Home":
            _render_home(settings)
        elif page == "Cost explorer":
            _render_cost_explorer(settings)
        elif page == "Plans & alerts":
            _render_plans(settings)
        elif page == "Reports":
            _render_reports(settings)
        else:
            _render_advanced(settings)
