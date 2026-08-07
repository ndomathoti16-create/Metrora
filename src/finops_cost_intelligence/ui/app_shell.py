"""Streamlit application shell for the SpendArc analytical workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .branding import inject_styles, render_brand_header, render_sidebar
from .workspace_view import render_workspace

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
        page_title="SpendArc | Cloud FinOps Intelligence",
        page_icon="◒",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_styles()
    render_sidebar(settings)
    render_brand_header()

    render_workspace(settings)
