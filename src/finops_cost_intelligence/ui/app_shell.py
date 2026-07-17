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
            "Streamlit is not installed. Run `python -m pip install -e \".[dev]\"` "
            "before starting the application."
        ) from exc

    st.set_page_config(
        page_title="FinOps Cost Intelligence",
        page_icon="cloud",
        layout="wide",
    )
    st.title("FinOps Cost Intelligence Platform")
    st.caption("Milestone 2 · Mapping and canonical normalization")

    st.info(
        "Milestone 2 adds reviewable semantic mapping and canonical normalization. "
        "Quality gates and financial analysis arrive in later milestones."
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
        st.write("5. Preview conversion issues and lineage")

    render_ingestion_view(settings)
