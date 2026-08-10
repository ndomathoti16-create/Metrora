"""Streamlit quality report and local DuckDB persistence view."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pandas as pd

from ..contracts.quality import QualityReport
from ..ingestion.readers import LoadedTable
from ..quality import run_quality_checks
from ..warehouse import DuckDBStore, WarehouseError
from .branding import render_compact_table

if TYPE_CHECKING:
    from ..config import Settings


def _quality_frame(report: QualityReport) -> pd.DataFrame:
    def display_value(value: object) -> str:
        return json.dumps(value, default=str, ensure_ascii=False)

    return pd.DataFrame(
        [
            {
                "check": check.check_name,
                "status": check.status,
                "severity": check.severity,
                "observed": display_value(check.observed_value),
                "expected": display_value(check.expected_value),
                "affected rows": check.affected_rows,
                "detail": check.detail,
            }
            for check in report.checks
        ]
    )


def render_quality_view(
    settings: Settings,
    loaded_table: LoadedTable,
    source_key: str,
) -> None:
    """Render quality checks, reconciliation, and a save-to-DuckDB action."""
    import streamlit as st

    normalized = st.session_state.get("normalized_table")
    if normalized is None or st.session_state.get("normalized_source_key") != source_key:
        return

    report = run_quality_checks(loaded_table, normalized)
    st.session_state["quality_report"] = report
    st.session_state["quality_source_key"] = source_key
    currencies = (
        normalized.dataframe["currency"].dropna().astype(str).unique().tolist()
        if "currency" in normalized.dataframe.columns
        else []
    )
    currency = currencies[0] if len(currencies) == 1 else "Mixed" if currencies else None

    st.subheader("Financial quality checks")
    metrics = st.columns(4)
    metrics[0].metric("Overall status", report.overall_status.upper())
    metrics[1].metric("Ready for analysis", "Yes" if report.ready_for_analysis else "No")
    metrics[2].metric(
        "Source total",
        _format_currency(report.reconciliation.source_total, currency),
    )
    metrics[3].metric(
        "Reconciliation difference",
        _format_currency(report.reconciliation.absolute_difference, currency),
    )

    if report.ready_for_analysis:
        st.success("The normalized run passes all blocking quality checks.")
    else:
        st.error("Blocking quality checks failed. Review the findings before analysis.")
    if report.overall_status == "warning":
        st.warning("The run is usable with caveats. Review warnings before sharing results.")

    quality_frame = _quality_frame(report)
    findings = quality_frame.loc[~quality_frame["status"].eq("pass")]
    if not findings.empty:
        st.markdown("**Items to review**")
        render_compact_table(findings, max_rows=20)

    with st.expander("View all quality checks", expanded=False):
        render_compact_table(quality_frame, max_rows=len(quality_frame))

    with st.expander("View reconciliation evidence", expanded=False):
        reconciliation = report.reconciliation
        reconciliation_frame = pd.DataFrame(
            [
                {
                    "source total": _format_currency(reconciliation.source_total, currency),
                    "canonical total": _format_currency(
                        reconciliation.canonical_total,
                        currency,
                    ),
                    "absolute difference": _format_currency(
                        reconciliation.absolute_difference,
                        currency,
                    ),
                    "relative difference": (
                        f"{reconciliation.relative_difference:.4%}"
                        if reconciliation.relative_difference is not None
                        else "Unavailable"
                    ),
                    "tolerance": _format_currency(reconciliation.tolerance, currency),
                    "passed": "Yes" if reconciliation.passed else "No",
                }
            ]
        )
        render_compact_table(reconciliation_frame, max_rows=1)

    with st.expander("Local storage", expanded=False):
        st.caption(
            "Optional. Save the normalized rows and quality report to local DuckDB for "
            "repeatable analysis. Saving the same run replaces its stored version."
        )
        if st.button(
            "Save this run to local DuckDB",
            key=f"warehouse_save_{source_key}",
        ):
            try:
                store = DuckDBStore(settings.db_path)
                store.save_run(loaded_table, normalized, report)
                summary = store.get_run_summary(normalized.ingestion_id)
            except WarehouseError as exc:
                st.error(str(exc))
            else:
                st.session_state["warehouse_summary"] = summary
                st.session_state["warehouse_source_key"] = source_key
                st.success("Run saved to the Metrora local warehouse.")

        summary = st.session_state.get("warehouse_summary")
        if summary is not None and st.session_state.get("warehouse_source_key") == source_key:
            warehouse_metrics = st.columns(3)
            warehouse_metrics[0].metric("Stored cost rows", f"{summary['cost_rows']:,}")
            warehouse_metrics[1].metric(
                "Stored quality checks",
                f"{summary['quality_checks']:,}",
            )
            warehouse_metrics[2].metric("Run ID", normalized.ingestion_id)


def _format_currency(value: float | None, currency: str | None) -> str:
    if value is None:
        return "Unavailable"
    if currency and currency != "Mixed":
        return f"{currency} {value:,.2f}"
    return f"{value:,.2f}"
