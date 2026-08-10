"""Durable, shareable navigation state for the Metrora Streamlit application."""

from __future__ import annotations

from collections.abc import Mapping


def _first_value(value: object) -> str | None:
    """Return a normalized scalar from Streamlit's query-parameter values."""
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def read_route() -> dict[str, str]:
    """Read the current location without coupling routing to a browser session."""
    import streamlit as st

    params: Mapping[str, object] = st.query_params
    route: dict[str, str] = {}
    for key in ("surface", "page", "scenario"):
        value = _first_value(params.get(key))
        if value is not None:
            route[key] = value
    return route


def _write_route(route: Mapping[str, str]) -> None:
    """Replace Metrora's location values only when they have changed."""
    import streamlit as st

    normalized = {key: str(value) for key, value in route.items() if value}
    current = {
        key: value
        for key, raw_value in st.query_params.items()
        if (value := _first_value(raw_value)) is not None
    }
    if current == normalized:
        return
    st.query_params.clear()
    st.query_params.update(normalized)


def set_product_route(page: str) -> None:
    """Navigate to a public product page and retain it across a browser refresh."""
    import streamlit as st

    st.session_state["product_page"] = page
    _write_route({"surface": "product", "page": page})


def set_workspace_route(page: str, *, scenario_id: str | None = None) -> None:
    """Navigate within the workspace and preserve a restorable demo scenario."""
    import streamlit as st

    st.session_state["workspace_page"] = page
    route = {"surface": "workspace", "page": page}
    scenario = scenario_id or st.session_state.get("demo_scenario")
    if scenario:
        route["scenario"] = str(scenario)
    _write_route(route)
