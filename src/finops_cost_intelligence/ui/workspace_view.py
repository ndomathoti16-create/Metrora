"""Tabbed SpendArc workspace orchestration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .analytics_view import render_analytics_view
from .forecast_view import render_forecast_view
from .ingestion_view import render_ingestion_view
from .mapping_view import source_key_for
from .operations_view import render_operations_view
from .report_view import render_report_view

if TYPE_CHECKING:
    from ..config import Settings


def _context() -> tuple[object | None, str | None]:
    import streamlit as st

    normalized = st.session_state.get("normalized_table")
    loaded_table = st.session_state.get("loaded_table")
    profile = st.session_state.get("data_profile")
    if loaded_table is None or profile is None:
        return normalized, None
    return normalized, source_key_for(loaded_table, profile)


def _render_progress() -> None:
    import streamlit as st

    loaded = st.session_state.get("loaded_table") is not None
    normalized = st.session_state.get("normalized_table") is not None
    quality = st.session_state.get("quality_report")
    filtered = st.session_state.get("analytics_filtered_table") is not None
    stages = [
        ("01", "Source", loaded),
        ("02", "Model", normalized),
        ("03", "Quality", quality is not None and quality.ready_for_analysis),
        ("04", "Insights", filtered),
    ]
    pills = "".join(
        f'<span class="spendarc-step {"is-ready" if ready else ""}">'
        f'<b>{number}</b>{label}</span>'
        for number, label, ready in stages
    )
    stepbar = (
        '<div class="spendarc-stepbar">'
        '<span class="spendarc-stepbar-label">WORKSPACE PROGRESS</span>'
        f"{pills}</div>"
    )
    st.markdown(stepbar, unsafe_allow_html=True)


def _render_empty_state(title: str, message: str, next_step: str) -> None:
    import streamlit as st

    st.markdown(
        f"""
        <div class="spendarc-empty-state">
            <div class="spendarc-empty-icon">+</div>
            <div>
                <h3>{title}</h3>
                <p>{message}</p>
                <span class="spendarc-next-step">Next step · {next_step}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_prepare(settings: Settings) -> None:
    import streamlit as st

    st.subheader("Build a trusted cost model")
    st.caption(
        "Start here. SpendArc keeps the raw upload, mapping decisions, and validation results "
        "together before showing financial insights."
    )
    render_ingestion_view(settings, include_mapping=False)
    loaded_table = st.session_state.get("loaded_table")
    profile = st.session_state.get("data_profile")
    if loaded_table is not None and profile is not None:
        from .mapping_view import render_mapping_view

        render_mapping_view(
            settings,
            loaded_table,
            profile,
            include_analytics=False,
        )


def _render_explore(settings: Settings) -> None:
    normalized, source_key = _context()
    if normalized is None or source_key is None:
        _render_empty_state(
            "Your spend view will appear here",
            "Upload and normalize a billing file before exploring costs, drivers, and trends.",
            "Open Prepare data",
        )
        return
    render_analytics_view(
        settings,
        normalized,
        source_key,
        include_operations=False,
        include_forecast=False,
        include_report=False,
    )


def _render_plan(settings: Settings) -> None:
    import streamlit as st

    normalized, source_key = _context()
    actual = st.session_state.get("analytics_filtered_table")
    if normalized is None or source_key is None or actual is None:
        _render_empty_state(
            "Planning comes after exploration",
            "SpendArc applies planning and anomaly analysis to the same filtered view "
            "used by your spend dashboard.",
            "Open Explore spend and confirm your filters",
        )
        return
    render_operations_view(settings, normalized, source_key, actual)
    render_forecast_view(actual, source_key)


def _render_report(settings: Settings) -> None:
    import streamlit as st

    normalized, source_key = _context()
    actual = st.session_state.get("analytics_filtered_table")
    if normalized is None or source_key is None or actual is None:
        _render_empty_state(
            "Your executive brief will appear here",
            "Complete the data preparation and spend exploration steps before exporting a report.",
            "Open Explore spend",
        )
        return
    render_report_view(settings, normalized, source_key, actual)


def render_workspace(settings: Settings) -> None:
    """Render the product workspace as a progressive, four-stage journey."""
    import streamlit as st

    workspace_heading = (
        '<div class="spendarc-workspace-heading">'
        '<span>WORKSPACE</span>'
        '<h2>Make the next cost decision easier.</h2>'
        '<p>Move from source data to a concise, defensible point of view.</p>'
        '</div>'
    )
    st.markdown(workspace_heading, unsafe_allow_html=True)
    _render_progress()
    prepare_tab, explore_tab, plan_tab, report_tab = st.tabs(
        [
            "01  Prepare data",
            "02  Explore spend",
            "03  Plan & investigate",
            "04  Executive brief",
        ]
    )
    with prepare_tab:
        _render_prepare(settings)
    with explore_tab:
        _render_explore(settings)
    with plan_tab:
        _render_plan(settings)
    with report_tab:
        _render_report(settings)
