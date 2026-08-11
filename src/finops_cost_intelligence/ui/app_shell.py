"""Streamlit application shell for the Metrora analytical workspace."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ..ingestion import IngestionError
from ..runtime import resource_path
from .branding import (
    enable_scroll_reveals,
    inject_styles,
    render_top_navigation,
)
from .navigation import read_route, set_product_route
from .product_page import (
    DEMO_SCENARIOS,
    PUBLIC_PAGES,
    activate_demo_session,
    render_product_page,
)
from .workspace_view import WORKSPACE_PAGES, render_workspace

if TYPE_CHECKING:
    from ..config import Settings


def _restore_route(settings: Settings) -> None:
    """Restore the public or demo location after a browser refresh."""
    import streamlit as st

    route = read_route()
    surface = route.get("surface")
    if surface == "product":
        page = route.get("page", "Product")
        st.session_state["product_page"] = page if page in PUBLIC_PAGES else "Product"
        # A product URL is intentionally a public destination, even if it was opened
        # from a previous guided-demo session.
        st.session_state.pop("demo_authenticated", None)
        st.session_state.pop("demo_mode", None)
        return

    if surface != "workspace":
        return

    scenario_id = route.get("scenario")
    if scenario_id not in DEMO_SCENARIOS:
        if st.session_state.get("demo_authenticated", False):
            # The current session can keep an uploaded source even though a fresh
            # browser session cannot reconstruct it from a URL.
            requested_page = route.get("page", "Home")
            st.session_state["workspace_page"] = (
                requested_page if requested_page in WORKSPACE_PAGES else "Home"
            )
            return
        # A local upload cannot be reconstructed from a URL. Send a fresh browser
        # session to the scenario chooser instead of showing a misleading blank view.
        set_product_route("Demo")
        return

    if (
        not st.session_state.get("demo_authenticated", False)
        or st.session_state.get("demo_scenario") != scenario_id
    ):
        try:
            activate_demo_session(settings, scenario_id, persist_route=False)
        except IngestionError as exc:
            st.session_state["route_restore_error"] = str(exc)
            set_product_route("Demo")
            return

    requested_page = route.get("page", "Home")
    st.session_state["workspace_page"] = (
        requested_page if requested_page in WORKSPACE_PAGES else "Home"
    )


def render_app_shell(settings: Settings) -> None:
    """Render the upload, mapping, and normalization workflow."""
    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError(
            'Streamlit is not installed. Run `python -m pip install -e ".[dev]"` '
            "before starting the application."
        ) from exc

    page_icon = resource_path("docs", "assets", "metrora-mark.svg")
    st.set_page_config(
        page_title="Metrora | Cloud FinOps Intelligence",
        page_icon=str(page_icon) if page_icon.is_file() else "M",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Metrora has one intentional workspace appearance. Keeping the state true also
    # gives the analytical charts a single, deterministic visual palette.
    st.session_state["dark_mode"] = True
    desktop_mode = os.environ.get("METRORA_DESKTOP", "").strip() == "1"
    st.session_state["desktop_mode"] = desktop_mode
    if desktop_mode:
        st.session_state["demo_authenticated"] = True
        st.session_state["demo_mode"] = False
        st.session_state.setdefault("demo_workspace", "Desktop workspace")
    inject_styles()
    enable_scroll_reveals()
    _restore_route(settings)

    if not st.session_state.get("demo_authenticated", False):
        render_top_navigation(settings)
        if error := st.session_state.pop("route_restore_error", None):
            st.warning(f"The selected demo could not be restored: {error}")
        render_product_page(settings)
        return

    render_top_navigation(settings)
    render_workspace(settings)
