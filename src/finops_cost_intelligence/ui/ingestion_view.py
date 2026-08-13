"""Streamlit view for uploading and profiling a single source file."""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

import pandas as pd

from ..ingestion import IngestionError, load_table, profile_table
from ..ingestion.readers import LoadedTable
from ..mapping import MappingValidationError
from ..runtime import resource_path
from .branding import render_compact_table
from .mapping_view import build_automatic_model, render_mapping_view, source_key_for

if TYPE_CHECKING:
    from ..config import Settings


def _format_bytes(size_bytes: int | None) -> str:
    if size_bytes is None:
        return "Unknown"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.1f} MB"
    return f"{size_bytes / 1024**3:.2f} GB"


def _render_source_summary(loaded_table, profile) -> None:
    import streamlit as st

    source_name = escape(str(profile.source_name))
    source_format = escape(str(profile.file_format).upper())
    source_size = escape(_format_bytes(profile.source_size_bytes))
    st.markdown(
        f"""
        <div class="metrora-source-strip">
            <div><small>Source</small><strong>{source_name}</strong></div>
            <div><small>Format</small><strong>{source_format}</strong></div>
            <div><small>Rows</small><strong>{profile.row_count:,}</strong></div>
            <div><small>Columns</small><strong>{profile.column_count:,}</strong></div>
            <div><small>File size</small><strong>{source_size}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Inspect source details", expanded=False):
        column_frame = pd.DataFrame(profile.column_records())
        column_frame["sample_values"] = column_frame["sample_values"].map(
            lambda values: ", ".join(str(value) for value in values)
        )
        for rate_column in ("null_rate", "numeric_parse_rate", "datetime_parse_rate"):
            column_frame[rate_column] = column_frame[rate_column].map(lambda value: f"{value:.1%}")
        st.markdown("**Column profile**")
        render_compact_table(
            column_frame[
                [
                    "name",
                    "inferred_type",
                    "null_rate",
                    "unique_count",
                    "numeric_parse_rate",
                    "datetime_parse_rate",
                    "sample_values",
                ]
            ],
            max_rows=30,
        )
        st.markdown("**Source preview**")
        render_compact_table(loaded_table.dataframe, max_rows=12)


def _prepare_source_automatically(loaded_table, profile) -> str:
    """Build all deterministic artifacts for one source and return its session key."""
    import streamlit as st

    source_key = source_key_for(loaded_table, profile)
    if st.session_state.get("auto_attempted_source_key") == source_key:
        return source_key

    st.session_state["auto_attempted_source_key"] = source_key
    st.session_state["mapping_source_key"] = source_key
    st.session_state.pop("auto_analysis_message", None)
    st.session_state.pop("auto_analysis_error", None)
    try:
        accepted_mapping, normalized, report = build_automatic_model(
            loaded_table,
            profile,
        )
    except (MappingValidationError, ValueError, KeyError) as exc:
        st.session_state["auto_analysis_error"] = str(exc)
        st.session_state["mapping_edit_mode"] = True
        return source_key

    st.session_state.update(
        {
            "column_mapping": accepted_mapping,
            "normalized_table": normalized,
            "normalized_source_key": source_key,
            "quality_report": report,
            "quality_source_key": source_key,
            "mapping_edit_mode": False,
            "auto_analysis_message": (
                "Upload complete. Metrora detected the fields, normalized the source, "
                "and ran the financial quality checks automatically."
            ),
        }
    )
    return source_key


def activate_loaded_table(loaded_table: LoadedTable) -> tuple[object, str, bool]:
    """Install any trusted file or cloud source into the shared analytical workflow.

    Cloud connectors call this same boundary as the file uploader. That keeps mapping,
    normalization, reconciliation, quality checks, and all downstream calculations
    identical regardless of where the billing rows came from.
    """
    import streamlit as st

    profile = profile_table(loaded_table)
    existing_loaded = st.session_state.get("loaded_table")
    existing_profile = st.session_state.get("data_profile")
    incoming_key = source_key_for(loaded_table, profile)
    current_key = (
        source_key_for(existing_loaded, existing_profile)
        if existing_loaded is not None and existing_profile is not None
        else None
    )
    was_new_source = incoming_key != current_key
    if was_new_source:
        for key in (
            "column_mapping",
            "normalized_table",
            "normalized_source_key",
            "quality_report",
            "quality_source_key",
            "warehouse_summary",
            "warehouse_source_key",
            "analytics_filtered_table",
            "analytics_source_key",
            "fact_pack",
            "summary_result",
            "summary_source_key",
            "auto_attempted_source_key",
        ):
            st.session_state.pop(key, None)
    st.session_state["loaded_table"] = loaded_table
    st.session_state["data_profile"] = profile
    source_key = _prepare_source_automatically(loaded_table, profile)
    return profile, source_key, was_new_source


def render_ingestion_view(settings: Settings, *, include_mapping: bool = True) -> None:
    """Render one-step ingestion with automated mapping, normalization, and checks."""
    import streamlit as st

    existing_loaded = st.session_state.get("loaded_table")
    existing_profile = st.session_state.get("data_profile")
    was_new_source = False

    st.subheader("Billing source")
    st.write(
        "Upload one billing export. Metrora will detect its fields, build a standard cost "
        "model, reconcile the totals, and open the results automatically."
    )

    def source_uploader(label: str):
        return st.file_uploader(
            label,
            type=["csv", "xlsx", "xls", "parquet"],
            key="billing_upload",
            help=(
                f"CSV, Excel, or Parquet · maximum {settings.max_upload_mb:,} MB. "
                "Only review the suggested mapping if Metrora flags an exception."
            ),
        )

    if existing_loaded is not None:
        with st.expander("Replace billing source", expanded=False):
            uploaded_file = source_uploader("New billing file")
    else:
        uploaded_file = source_uploader("Billing file")

    if uploaded_file is None:
        loaded_table = existing_loaded
        profile = existing_profile
        if loaded_table is None or profile is None:
            st.info(
                "No billing source is loaded. Upload your own file, or open the guided demo "
                "from the product page."
            )
            demo_path = resource_path("data", "demo", "cloud_billing_demo.csv")
            if demo_path.is_file():
                st.download_button(
                    "Download sample billing CSV",
                    data=demo_path.read_bytes(),
                    file_name="metrora_sample_billing.csv",
                    mime="text/csv",
                    help="Synthetic data for learning the Metrora workflow.",
                )
            return
    else:
        max_bytes = settings.max_upload_mb * 1024 * 1024
        try:
            loaded_table = load_table(uploaded_file, max_bytes=max_bytes)
        except IngestionError as exc:
            st.error(str(exc))
            return
        profile, _, was_new_source = activate_loaded_table(loaded_table)

    _prepare_source_automatically(loaded_table, profile)
    quality_report = st.session_state.get("quality_report")
    if was_new_source and quality_report is not None and quality_report.ready_for_analysis:
        st.session_state["workspace_page"] = "Home"
        st.rerun()
    message = st.session_state.get("auto_analysis_message")
    error = st.session_state.get("auto_analysis_error")
    if message:
        st.success(message)
    if error:
        st.warning(
            "Metrora could not safely finish the automatic model. Correct the required "
            f"field mapping below. Details: {error}"
        )

    _render_source_summary(loaded_table, profile)

    if include_mapping:
        render_mapping_view(
            settings,
            loaded_table,
            profile,
            include_analytics=False,
        )
