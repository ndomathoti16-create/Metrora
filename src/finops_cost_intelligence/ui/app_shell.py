"""Minimal Streamlit shell used until the analytical milestones are implemented."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .ingestion_view import render_ingestion_view

if TYPE_CHECKING:
    from ..config import Settings


def render_app_shell(settings: Settings) -> None:
    """Render the foundation screen.

    Streamlit is imported inside the function so configuration and unit tests remain
    importable in environments where UI dependencies have not been installed yet.
    """
    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError(
            "Streamlit is not installed. Run `python -m pip install -e \".[dev]\"` "
            "before starting the application."
        ) from exc

    st.set_page_config(
        page_title="FinOps Cost Intelligence",
        page_icon="☁️",
        layout="wide",
    )
    st.title("FinOps Cost Intelligence Platform")
    st.caption("Milestone 0 · Project foundation")

    st.info(
        "Milestone 1 supports CSV, Excel, and Parquet upload with a read-only profile. "
        "Column mapping and financial analysis arrive in later milestones."
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Foundation status")
        st.success("Configuration loaded")
        st.write(f"Environment: `{settings.app_env}`")
        st.write(f"AI provider: `{settings.ai_provider}`")

    with right:
        st.subheader("Milestone 1 workflow")
        st.write("1. Upload one supported billing file")
        st.write("2. Inspect schema and inferred types")
        st.write("3. Review nulls, duplicates, and parseability")
        st.write("4. Preview source rows")

    render_ingestion_view(settings)
