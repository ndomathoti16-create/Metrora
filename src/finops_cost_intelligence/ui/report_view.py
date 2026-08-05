"""Executive summary and export controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from ..ai import build_fact_pack, summarize_fact_pack
from ..ai.client import AIProviderError, OpenAICompatibleClient
from ..contracts.normalization import NormalizedTable
from ..exports import (
    cleaned_csv_bytes,
    cleaned_parquet_bytes,
    executive_report_html,
    fact_pack_json_bytes,
    quality_report_json_bytes,
)
from ..storage import S3Storage, S3StorageError

if TYPE_CHECKING:
    from ..config import Settings


def _render_summary(summary) -> None:
    st.subheader("Evidence-backed executive summary")
    st.write(summary.headline)
    for bullet in summary.bullets:
        st.markdown(f"- {bullet}")
    if summary.caveats:
        with st.expander("Summary caveats"):
            for caveat in summary.caveats:
                st.warning(caveat)
    st.caption(f"Summary source: {summary.provider}")


def render_report_view(
    settings: Settings,
    normalized: NormalizedTable,
    source_key: str,
    filtered: object,
) -> None:
    """Render grounded summary generation and reproducible download artifacts."""
    quality_report = st.session_state.get("quality_report")
    if quality_report is None:
        return
    st.header("Share the story")
    st.write(
        "Turn the calculated fact pack into a concise executive brief, then export the "
        "evidence, quality checks, and cleaned dataset for review."
    )
    budget = st.session_state.get("budget_table")
    business_metrics = st.session_state.get("business_metrics_table")
    metric_name = st.session_state.get(f"business_metric_name_{source_key}")
    fact_pack = build_fact_pack(
        normalized,
        quality_report,
        dataframe=filtered,
        budget_dataframe=budget,
        business_metrics_dataframe=business_metrics,
        metric_name=metric_name,
        filters={"source_key": source_key},
    )
    st.session_state["fact_pack"] = fact_pack
    if st.button("Generate evidence-backed summary", key=f"summary_button_{source_key}"):
        client = None
        if settings.ai_provider in {"openai", "openai-compatible"}:
            try:
                client = OpenAICompatibleClient(
                    api_key=settings.ai_api_key or "",
                    model=settings.ai_model or "",
                    base_url=settings.ai_base_url,
                )
            except AIProviderError as exc:
                st.warning(f"Optional AI provider is not ready; using fallback: {exc}")
        elif settings.ai_provider != "none":
            st.warning(
                f"AI provider `{settings.ai_provider}` is not supported by this adapter; "
                "using the deterministic fallback."
            )
        st.session_state["summary_result"] = summarize_fact_pack(
            fact_pack,
            client=client,
        )
    summary = st.session_state.get("summary_result")
    if summary is not None:
        _render_summary(summary)
    else:
        st.info("Generate the summary when you are ready to review the evidence-backed narrative.")

    st.subheader("Download artifacts")
    st.caption(
        "Exports reflect the current canonical selection and include the fact pack or "
        "quality status needed to reproduce the narrative."
    )
    if summary is None:
        st.info("Generate the summary before downloading the executive HTML report.")
    else:
        st.download_button(
            "Download executive HTML report",
            data=executive_report_html(fact_pack, summary).encode("utf-8"),
            file_name="spendarc_executive_brief.html",
            mime="text/html",
            key=f"download_report_{source_key}",
        )
    columns = st.columns(4)
    columns[0].download_button(
        "Cleaned CSV",
        data=cleaned_csv_bytes(normalized),
        file_name="spendarc_canonical_cloud_cost.csv",
        mime="text/csv",
        key=f"download_csv_{source_key}",
    )
    columns[1].download_button(
        "Cleaned Parquet",
        data=cleaned_parquet_bytes(normalized),
        file_name="spendarc_canonical_cloud_cost.parquet",
        mime="application/octet-stream",
        key=f"download_parquet_{source_key}",
    )
    columns[2].download_button(
        "Fact pack JSON",
        data=fact_pack_json_bytes(fact_pack),
        file_name="spendarc_fact_pack.json",
        mime="application/json",
        key=f"download_fact_pack_{source_key}",
    )
    columns[3].download_button(
        "Quality JSON",
        data=quality_report_json_bytes(quality_report),
        file_name="spendarc_quality_report.json",
        mime="application/json",
        key=f"download_quality_{source_key}",
    )
    if settings.s3_bucket:
        st.subheader("Optional AWS persistence")
        st.caption(
            f"AWS export is configured for bucket `{settings.s3_bucket}`. "
            "Canonical Parquet will be stored under the standardized prefix."
        )
        if st.button("Upload canonical Parquet to S3", key=f"s3_upload_{source_key}"):
            try:
                uri = S3Storage(
                    settings.s3_bucket,
                    region=settings.aws_region,
                ).upload_normalized(normalized)
            except S3StorageError as exc:
                st.error(f"S3 upload failed: {exc}")
            else:
                st.success(f"Uploaded standardized Parquet to {uri}")
