"""Streamlit review and apply step for source-to-canonical mappings."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from ..contracts.mapping import CANONICAL_FIELD_SPECS, MappingReview
from ..contracts.profile import DataProfile
from ..ingestion.readers import LoadedTable
from ..mapping import MappingValidationError, suggest_mappings, validate_mapping
from ..normalization import normalize_billing_table
from .analytics_view import render_analytics_view
from .quality_view import render_quality_view

if TYPE_CHECKING:
    from ..config import Settings


NOT_MAPPED = "Not mapped"


def _source_key(loaded_table: LoadedTable, profile: DataProfile) -> str:
    return ":".join(
        [
            loaded_table.source_name,
            str(loaded_table.source_size_bytes),
            str(profile.row_count),
            str(profile.column_count),
        ]
    )


def _review_frame(review: MappingReview) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "field": suggestion.label,
                "required": "Yes" if suggestion.required else "No",
                "suggested source": suggestion.source_column or NOT_MAPPED,
                "confidence": suggestion.confidence,
                "score": suggestion.score,
                "reason": suggestion.reason,
            }
            for suggestion in review.suggestions
        ]
    )


def _selected_mapping_from_form(
    review: MappingReview,
    existing_mapping: dict[str, str | None] | None,
) -> dict[str, str | None]:
    import streamlit as st

    source_options = [NOT_MAPPED, *review.source_columns]
    selected: dict[str, str | None] = {}
    for spec in CANONICAL_FIELD_SPECS:
        suggestion = review.suggestion_for(spec.name)
        default_value = (
            existing_mapping.get(spec.name)
            if existing_mapping is not None
            else suggestion.source_column
        )
        if default_value not in source_options:
            default_value = None
        default_index = source_options.index(default_value) if default_value else 0
        chosen = st.selectbox(
            f"{spec.label}{' *' if spec.required else ''}",
            source_options,
            index=default_index,
            key=f"mapping_{spec.name}",
            help=(
                f"Suggested: {suggestion.source_column or NOT_MAPPED}. "
                f"{suggestion.reason}"
            ),
        )
        selected[spec.name] = None if chosen == NOT_MAPPED else chosen
    return selected


def _render_normalized_result(source_key: str) -> None:
    import streamlit as st

    normalized = st.session_state.get("normalized_table")
    if normalized is None or st.session_state.get("normalized_source_key") != source_key:
        return

    report = normalized.report
    st.subheader("Canonical preview")
    if report.rows_in == report.rows_out and report.issue_count == 0:
        st.success(f"Normalized {report.rows_out:,} rows without conversion issues.")
    elif report.rows_in == report.rows_out:
        st.warning(
            f"Normalized all {report.rows_out:,} rows, but recorded "
            f"{report.issue_count:,} conversion issue(s). No rows were dropped."
        )
    else:
        st.error("Normalization changed the row count; investigate before proceeding.")

    st.dataframe(normalized.dataframe.head(20), use_container_width=True, hide_index=True)
    if report.issue_count:
        st.caption("Issue counts by canonical field")
        st.dataframe(
            pd.DataFrame(
                [
                    {"canonical field": field, "issue count": count}
                    for field, count in report.issue_counts_by_field.items()
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
        with st.expander(
            f"Sample conversion issues (up to {report.issue_sample_limit})"
        ):
            st.dataframe(
                pd.DataFrame([issue.to_dict() for issue in report.issues]),
                use_container_width=True,
                hide_index=True,
            )


def render_mapping_view(
    settings: Settings,
    loaded_table: LoadedTable,
    profile: DataProfile,
) -> None:
    """Render detector suggestions, manual overrides, and normalization output."""
    import streamlit as st

    source_key = _source_key(loaded_table, profile)
    if st.session_state.get("mapping_source_key") != source_key:
        st.session_state.pop("column_mapping", None)
        st.session_state.pop("normalized_table", None)
        st.session_state.pop("normalized_source_key", None)
        st.session_state.pop("quality_report", None)
        st.session_state.pop("quality_source_key", None)
        st.session_state.pop("warehouse_summary", None)
        st.session_state.pop("warehouse_source_key", None)
        st.session_state["mapping_source_key"] = source_key

    review = suggest_mappings(profile)
    existing_mapping = st.session_state.get("column_mapping")

    st.header("Review column mappings")
    st.write(
        "Suggestions use source names and profile signals. Review every required "
        "field before applying the mapping; optional fields may remain unmapped."
    )
    with st.expander("Detector suggestions", expanded=True):
        st.dataframe(
            _review_frame(review),
            use_container_width=True,
            hide_index=True,
        )

    with st.form(key=f"mapping_form_{source_key}"):
        selected_mapping = _selected_mapping_from_form(review, existing_mapping)
        submitted = st.form_submit_button("Apply mapping and normalize")

    if submitted:
        try:
            accepted_mapping = validate_mapping(selected_mapping, review.source_columns)
            normalized = normalize_billing_table(loaded_table, accepted_mapping)
        except MappingValidationError as exc:
            st.error(f"Mapping needs attention: {exc}")
        except (ValueError, KeyError) as exc:
            st.error(f"Normalization could not be applied: {exc}")
        else:
            st.session_state["column_mapping"] = accepted_mapping
            st.session_state["normalized_table"] = normalized
            st.session_state["normalized_source_key"] = source_key

    _render_normalized_result(source_key)
    render_quality_view(settings, loaded_table, source_key)
    normalized = st.session_state.get("normalized_table")
    if normalized is not None and st.session_state.get("normalized_source_key") == source_key:
        render_analytics_view(settings, normalized, source_key)
