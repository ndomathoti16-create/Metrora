"""Streamlit quality report and local DuckDB persistence view."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pandas as pd

from ..contracts.quality import QualityReport
from ..ingestion.readers import LoadedTable
from ..quality import run_quality_checks
from ..warehouse import DuckDBStore, WarehouseError

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

    st.header("Trust the numbers")
    metrics = st.columns(4)
    metrics[0].metric("Overall status", report.overall_status.upper())
    metrics[1].metric("Ready for analysis", "Yes" if report.ready_for_analysis else "No")
    metrics[2].metric("Source total", _format_currency(report.reconciliation.source_total))
    metrics[3].metric(
        "Reconciliation difference",
        _format_currency(report.reconciliation.absolute_difference),
    )

    if report.ready_for_analysis:
        st.success("The normalized run passes all blocking quality checks.")
    else:
        st.error("Blocking quality checks failed. Review the findings before analysis.")
    if report.overall_status == "warning":
        st.warning("The run is usable with caveats. Review warnings before sharing results.")

    st.dataframe(_quality_frame(report), width="stretch", hide_index=True)
    with st.expander("Reconciliation details"):
        st.json(report.reconciliation.to_dict())

    st.caption(
        "DuckDB stores the normalized rows and quality report locally. "
        "Saving the same ingestion ID replaces its previous stored version."
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
        st.success("Run saved to the SpendArc local warehouse.")

    summary = st.session_state.get("warehouse_summary")
    if summary is not None and st.session_state.get("warehouse_source_key") == source_key:
        st.subheader("Warehouse status")
        warehouse_metrics = st.columns(3)
        warehouse_metrics[0].metric("Stored cost rows", f"{summary['cost_rows']:,}")
        warehouse_metrics[1].metric("Stored quality checks", f"{summary['quality_checks']:,}")
        warehouse_metrics[2].metric("Run ID", normalized.ingestion_id)


def _format_currency(value: float | None) -> str:
    if value is None:
        return "Unavailable"
    return "$" + format(value, ",.2f")
