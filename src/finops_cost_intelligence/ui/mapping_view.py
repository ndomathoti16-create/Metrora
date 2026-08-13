"""Streamlit review and apply step for source-to-canonical mappings."""

from __future__ import annotations

from hashlib import sha256
from typing import TYPE_CHECKING

import pandas as pd

from ..contracts.mapping import CANONICAL_FIELD_SPECS, MappingReview
from ..contracts.normalization import NormalizedTable
from ..contracts.profile import DataProfile
from ..contracts.quality import QualityReport
from ..ingestion.readers import LoadedTable
from ..mapping import MappingValidationError, suggest_mappings, validate_mapping
from ..normalization import normalize_billing_table
from ..quality import run_quality_checks
from .analytics_view import render_analytics_view
from .branding import render_compact_table
from .quality_view import render_quality_view

if TYPE_CHECKING:
    from ..config import Settings


NOT_MAPPED = "Not mapped"


def source_key_for(loaded_table: LoadedTable, profile: DataProfile) -> str:
    """Return the stable session key for the current uploaded source."""
    try:
        row_hashes = pd.util.hash_pandas_object(
            loaded_table.dataframe,
            index=True,
            categorize=True,
        )
        content_digest = sha256(row_hashes.to_numpy().tobytes()).hexdigest()[:16]
    except (TypeError, ValueError):
        content_digest = sha256(
            "|".join(str(column) for column in loaded_table.dataframe.columns).encode("utf-8")
        ).hexdigest()[:16]
    return ":".join(
        [
            loaded_table.source_name,
            str(loaded_table.source_size_bytes),
            str(profile.row_count),
            str(profile.column_count),
            content_digest,
        ]
    )


def build_automatic_model(
    loaded_table: LoadedTable,
    profile: DataProfile,
) -> tuple[dict[str, str | None], NormalizedTable, QualityReport]:
    """Build and validate the suggested model without requiring a confirmation click."""
    review = suggest_mappings(profile)
    suggested_mapping = {
        suggestion.canonical_field: suggestion.source_column for suggestion in review.suggestions
    }
    accepted_mapping = validate_mapping(suggested_mapping, review.source_columns)
    normalized = normalize_billing_table(loaded_table, accepted_mapping)
    report = run_quality_checks(loaded_table, normalized)
    return accepted_mapping, normalized, report


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

    def render_field(spec) -> None:
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
            help=(f"Suggested: {suggestion.source_column or NOT_MAPPED}. {suggestion.reason}"),
        )
        selected[spec.name] = None if chosen == NOT_MAPPED else chosen

    required_specs = [spec for spec in CANONICAL_FIELD_SPECS if spec.required]
    required_columns = st.columns(len(required_specs))
    for column, spec in zip(required_columns, required_specs, strict=True):
        with column:
            render_field(spec)

    optional_specs = [spec for spec in CANONICAL_FIELD_SPECS if not spec.required]
    with st.expander("Optional fields", expanded=False):
        st.caption(
            "Metrora already applied its best matches. Change only the fields your analysis needs."
        )
        optional_columns = st.columns(3)
        for index, spec in enumerate(optional_specs):
            with optional_columns[index % len(optional_columns)]:
                render_field(spec)
    return selected


def _render_normalized_result(source_key: str) -> None:
    import streamlit as st

    normalized = st.session_state.get("normalized_table")
    if normalized is None or st.session_state.get("normalized_source_key") != source_key:
        return

    report = normalized.report
    if report.rows_in == report.rows_out and report.issue_count == 0:
        st.success(
            f"Trusted cost model ready · {report.rows_out:,} rows normalized without "
            "conversion issues."
        )
    elif report.rows_in == report.rows_out:
        st.warning(
            f"Normalized all {report.rows_out:,} rows, but recorded "
            f"{report.issue_count:,} conversion issue(s). No rows were dropped."
        )
    else:
        st.error("Normalization changed the row count; investigate before proceeding.")

    with st.expander("Inspect normalized rows", expanded=False):
        st.caption(
            "This preview is for verification. Metrora uses the complete normalized table "
            "for every calculation."
        )
        render_compact_table(normalized.dataframe, max_rows=15)
        if report.issue_count:
            st.markdown("**Conversion issues by field**")
            render_compact_table(
                pd.DataFrame(
                    [
                        {"canonical field": field, "issue count": count}
                        for field, count in report.issue_counts_by_field.items()
                    ]
                ),
                max_rows=20,
            )
            st.markdown("**Sample conversion issues**")
            render_compact_table(
                pd.DataFrame([issue.to_dict() for issue in report.issues]),
                max_rows=report.issue_sample_limit,
            )


def render_mapping_view(
    settings: Settings,
    loaded_table: LoadedTable,
    profile: DataProfile,
    *,
    include_analytics: bool = True,
) -> None:
    """Render detector suggestions, overrides, normalization, and optional analytics."""
    import streamlit as st

    source_key = source_key_for(loaded_table, profile)
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

    normalized = st.session_state.get("normalized_table")
    model_ready = bool(
        normalized is not None and st.session_state.get("normalized_source_key") == source_key
    )
    matched_count = sum(suggestion.source_column is not None for suggestion in review.suggestions)
    required_count = sum(spec.required for spec in CANONICAL_FIELD_SPECS)
    required_matched = sum(
        bool(review.suggestion_for(spec.name).source_column)
        for spec in CANONICAL_FIELD_SPECS
        if spec.required
    )
    optional_count = len(CANONICAL_FIELD_SPECS) - required_count
    optional_matched = matched_count - required_matched

    st.subheader("Automatic field mapping")
    st.write(
        "Metrora matched the source columns to its standard cost model. You only need "
        "to intervene when a required field is missing or a suggestion is incorrect."
    )
    metrics = st.columns(3)
    metrics[0].metric("Required fields", f"{required_matched}/{required_count} matched")
    metrics[1].metric("Optional context", f"{optional_matched}/{optional_count} matched")
    metrics[2].metric("Model status", "Ready" if model_ready else "Review needed")

    with st.expander("Review detected fields", expanded=not model_ready):
        render_compact_table(_review_frame(review), max_rows=len(review.suggestions))

    edit_mode = bool(st.session_state.get("mapping_edit_mode", False)) or not model_ready
    if model_ready and not edit_mode:
        if st.button(
            "Change field mapping",
            key=f"edit_mapping_{source_key}",
            type="secondary",
        ):
            st.session_state["mapping_edit_mode"] = True
            st.rerun()

    submitted = False
    cancelled = False
    selected_mapping: dict[str, str | None] = {}
    if edit_mode:
        st.markdown("#### Correct a detected field")
        st.caption(
            "Required fields are shown first. Optional fields stay out of the way until "
            "you need them."
        )
        with st.form(key=f"mapping_form_{source_key}"):
            selected_mapping = _selected_mapping_from_form(review, existing_mapping)
            actions = st.columns([1.7, 1, 4])
            submitted = actions[0].form_submit_button(
                "Apply mapping and rerun checks",
                type="primary",
                width="stretch",
            )
            if model_ready:
                cancelled = actions[1].form_submit_button(
                    "Cancel",
                    width="stretch",
                )

    if cancelled:
        st.session_state["mapping_edit_mode"] = False
        st.rerun()

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
            st.session_state["quality_report"] = run_quality_checks(
                loaded_table,
                normalized,
            )
            st.session_state["quality_source_key"] = source_key
            st.session_state["mapping_edit_mode"] = False
            st.session_state["auto_analysis_message"] = (
                "Field corrections applied. Metrora rebuilt and rechecked the cost model."
            )
            st.rerun()

    _render_normalized_result(source_key)
    render_quality_view(settings, loaded_table, source_key)
    normalized = st.session_state.get("normalized_table")
    if (
        include_analytics
        and normalized is not None
        and st.session_state.get("normalized_source_key") == source_key
    ):
        render_analytics_view(settings, normalized, source_key)
