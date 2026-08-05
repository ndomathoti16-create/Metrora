"""Streamlit application shell for the current analytical milestone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .ingestion_view import render_ingestion_view

if TYPE_CHECKING:
    from ..config import Settings


def render_app_shell(settings: Settings) -> None:
    """Render the upload, mapping, and normalization workflow."""
    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError(
            'Streamlit is not installed. Run `python -m pip install -e ".[dev]"` '
            "before starting the application."
        ) from exc

    st.set_page_config(
        page_title="FinOps Cost Intelligence",
        page_icon="cloud",
        layout="wide",
    )
    st.title("FinOps Cost Intelligence Platform")
    st.caption("Milestones 0–9 · Full local MVP with optional AWS extension")

    st.info(
        "The application validates cloud billing data before calculating spend, "
        "budgets, business efficiency, forecasts, anomalies, and evidence-backed summaries."
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Application status")
        st.success("Configuration loaded")
        st.write(f"Environment: `{settings.app_env}`")
        st.write(f"AI provider: `{settings.ai_provider}`")

    with right:
        st.subheader("Current workflow")
        st.write("1. Upload one supported billing file")
        st.write("2. Inspect schema and inferred types")
        st.write("3. Review and correct semantic mappings")
        st.write("4. Normalize to the canonical cost model")
        st.write("5. Review quality checks and reconciliation")
        st.write("6. Save the run to local DuckDB")
        st.write("7. Explore spend KPIs, trends, and cost drivers")
        st.write("8. Review budgets, allocation, business metrics, forecasts, and anomalies")
        st.write("9. Generate an executive report and export the fact pack")

    render_ingestion_view(settings)
