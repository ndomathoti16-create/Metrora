"""Streamlit view for uploading and profiling a single source file."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from ..ingestion import IngestionError, load_table, profile_table
from .mapping_view import render_mapping_view

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


def render_ingestion_view(settings: Settings) -> None:
    """Render file upload, profile summary, and a small data preview."""
    import streamlit as st

    st.header("Start with your billing data")
    st.write(
        "Drop in a cloud billing export and SpendArc will inspect its structure before "
        "any mapping or financial analysis is applied."
    )
    uploaded_file = st.file_uploader(
        "Choose a billing file",
        type=["csv", "xlsx", "xls", "parquet"],
        help="Supported formats: CSV, Excel (.xlsx/.xls), and Parquet.",
    )

    if uploaded_file is None:
        st.caption("No billing source loaded yet · CSV, Excel, and Parquet are supported.")
        return

    max_bytes = settings.max_upload_mb * 1024 * 1024
    try:
        loaded_table = load_table(
            uploaded_file,
            max_bytes=max_bytes,
        )
        profile = profile_table(loaded_table)
    except IngestionError as exc:
        st.error(str(exc))
        return

    st.session_state["loaded_table"] = loaded_table
    st.session_state["data_profile"] = profile

    metric_columns = st.columns(5)
    metric_columns[0].metric("Rows", f"{profile.row_count:,}")
    metric_columns[1].metric("Columns", f"{profile.column_count:,}")
    metric_columns[2].metric("File size", _format_bytes(profile.source_size_bytes))
    metric_columns[3].metric("Duplicate rows", f"{profile.duplicate_row_count:,}")
    metric_columns[4].metric("All-null rows", f"{profile.all_null_row_count:,}")

    details = f"{profile.source_name} · {profile.file_format.upper()}"
    if profile.sheet_name:
        details += f" · worksheet: {profile.sheet_name}"
    st.success(f"Source ready · {details}")

    st.subheader("Column profile")
    column_records = profile.column_records()
    column_frame = pd.DataFrame(column_records)
    column_frame["sample_values"] = column_frame["sample_values"].map(
        lambda values: ", ".join(str(value) for value in values)
    )
    for rate_column in [
        "null_rate",
        "numeric_parse_rate",
        "datetime_parse_rate",
    ]:
        column_frame[rate_column] = column_frame[rate_column].map(lambda value: f"{value:.1%}")
    st.dataframe(
        column_frame[
            [
                "name",
                "dtype",
                "inferred_type",
                "null_rate",
                "unique_count",
                "numeric_parse_rate",
                "datetime_parse_rate",
                "sample_values",
            ]
        ],
        width="stretch",
        hide_index=True,
    )

    st.subheader("Data preview")
    st.dataframe(loaded_table.dataframe.head(20), width="stretch", hide_index=True)

    with st.expander("Profile details"):
        st.json(profile.to_dict())

    render_mapping_view(settings, loaded_table, profile)
