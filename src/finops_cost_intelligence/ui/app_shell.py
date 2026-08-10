"""Streamlit application shell for the Metrora analytical workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .branding import (
    inject_styles,
    render_sidebar,
)
from .product_page import render_product_page
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
        page_title="Metrora | Cloud FinOps Intelligence",
        page_icon="M",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Metrora has one intentional workspace appearance. Keeping the state true also
    # gives the analytical charts a single, deterministic visual palette.
    st.session_state["dark_mode"] = True
    inject_styles()

    if not st.session_state.get("demo_authenticated", False):
        render_product_page(settings)
        return

    render_sidebar(settings)
    render_workspace(settings)
