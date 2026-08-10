import io
import json

import pandas as pd
import pytest

from finops_cost_intelligence.ai import build_fact_pack, summarize_fact_pack
from finops_cost_intelligence.ai.guardrails import AIResponseValidationError
from finops_cost_intelligence.exports import (
    cleaned_csv_bytes,
    cleaned_parquet_bytes,
    executive_report_html,
)
from finops_cost_intelligence.ingestion.readers import LoadedTable
from finops_cost_intelligence.normalization import normalize_billing_table
from finops_cost_intelligence.normalization.budgets import normalize_budget_dataframe
from finops_cost_intelligence.quality import run_quality_checks


def _run_with_evidence():
    source = pd.DataFrame(
        {
            "Date": pd.date_range("2025-01-01", periods=16, freq="D"),
            "Service": ["Compute"] * 15 + ["Storage"],
            "Amount": [10.0] * 14 + [100.0, 10.0],
            "Currency": ["USD"] * 16,
            "Account": ["prod"] * 16,
            "Department": ["Engineering"] * 16,
            "Project": ["Portal"] * 16,
            "Environment": ["prod"] * 16,
        }
    )
    loaded = LoadedTable(source, "demo_billing.csv", "csv", None)
    normalized = normalize_billing_table(
        loaded,
        {
            "usage_date": "Date",
            "service": "Service",
            "cost": "Amount",
            "currency": "Currency",
            "account_id": "Account",
            "department": "Department",
            "project": "Project",
            "environment": "Environment",
        },
        ingestion_id="report-run",
    )
    quality = run_quality_checks(loaded, normalized)
    budget = normalize_budget_dataframe(
        pd.DataFrame(
            {
                "period_start": ["2025-01-01"],
                "period_end": ["2025-01-31"],
                "scope_type": ["total"],
                "scope_value": ["Total"],
                "budget_amount": [200.0],
                "currency": ["USD"],
            }
        )
    )
    return normalized, quality, budget


def test_fact_pack_contains_calculated_facts_and_evidence_bounded_recommendations():
    normalized, quality, budget = _run_with_evidence()

    fact_pack = build_fact_pack(
        normalized,
        quality,
        budget_dataframe=budget,
    )

    fact_ids = {fact.fact_id for fact in fact_pack.facts}
    assert fact_pack.schema_version == "1.0"
    assert "total_spend" in fact_ids
    assert "spend_change_amount" in fact_ids
    assert "service_mover_1_name" in fact_ids
    assert "service_mover_1_explanation" in fact_ids
    assert "service_mover_1_evidence_level" in fact_ids
    assert "forecast_lower_total" in fact_ids
    assert "forecast_upper_total" in fact_ids
    assert "anomaly_estimated_increase_total" in fact_ids
    assert "budget_variance_amount" in fact_ids
    assert any(
        recommendation.recommendation_id == "budget_overrun_investigation"
        for recommendation in fact_pack.recommendations
    )
    for recommendation in fact_pack.recommendations:
        assert set(recommendation.fact_ids).issubset(fact_ids)
    json.dumps(fact_pack.to_dict())


def test_deterministic_summary_and_html_report_use_fact_pack_values():
    normalized, quality, budget = _run_with_evidence()
    fact_pack = build_fact_pack(normalized, quality, budget_dataframe=budget)
    summary = summarize_fact_pack(fact_pack)

    assert summary.provider == "deterministic_fallback"
    assert "Selected cloud spend" in summary.headline
    assert "Latest 8-day spend" in summary.headline
    assert any("Primary driver" in bullet for bullet in summary.bullets)
    assert any("Why:" in bullet for bullet in summary.bullets)
    report = executive_report_html(fact_pack, summary)
    assert "Executive decision brief" in report
    assert "What changed and why" in report
    assert "Questions for the next review" in report
    assert "Owner" in report
    assert "Calculated evidence" in report
    assert "budget_overrun_investigation" not in report
    assert "Actual minus budget" in report


def test_cleaned_exports_round_trip():
    normalized, _, _ = _run_with_evidence()

    csv_frame = pd.read_csv(io.BytesIO(cleaned_csv_bytes(normalized)))
    parquet_frame = pd.read_parquet(io.BytesIO(cleaned_parquet_bytes(normalized)))

    assert len(csv_frame) == len(normalized.dataframe)
    assert len(parquet_frame) == len(normalized.dataframe)
    assert csv_frame["service"].tolist() == normalized.dataframe["service"].tolist()


def test_external_summary_with_unsupported_number_falls_back():
    normalized, quality, _ = _run_with_evidence()
    fact_pack = build_fact_pack(normalized, quality)
    fact_ids = [fact.fact_id for fact in fact_pack.facts]

    class BadClient:
        def complete(self, system_prompt: str, user_prompt: str) -> str:
            del system_prompt, user_prompt
            return json.dumps(
                {
                    "headline": "Spend changed by 999999 units.",
                    "bullets": [],
                    "recommendation_ids": [],
                    "used_fact_ids": fact_ids,
                    "caveats": [],
                }
            )

    summary = summarize_fact_pack(fact_pack, client=BadClient())

    assert summary.provider == "deterministic_fallback"
    assert any("failed validation" in caveat for caveat in summary.caveats)


def test_fact_reference_guardrail_rejects_unknown_fact():
    normalized, quality, _ = _run_with_evidence()
    fact_pack = build_fact_pack(normalized, quality)

    with pytest.raises(AIResponseValidationError, match="unsupported evidence"):
        from finops_cost_intelligence.ai.guardrails import validate_fact_references

        validate_fact_references(
            fact_pack,
            used_fact_ids=["not-a-real-fact"],
            recommendation_ids=[],
        )
