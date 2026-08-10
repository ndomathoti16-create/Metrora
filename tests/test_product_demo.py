"""Tests for the local guided demo experience."""

from pathlib import Path

import pytest

from finops_cost_intelligence.config import Settings
from finops_cost_intelligence.ingestion import load_table, profile_table
from finops_cost_intelligence.ui.mapping_view import build_automatic_model
from finops_cost_intelligence.ui.product_page import build_demo_artifacts


def test_guided_demo_builds_a_ready_analysis_run() -> None:
    """The product demo should provide a deterministic, usable Metrora run."""
    settings = Settings.from_environment(base_dir=Path.cwd())

    loaded, profile, mapping, normalized, report = build_demo_artifacts(settings)

    assert loaded.source_name == "cloud_billing_demo.csv"
    assert profile.row_count > 0
    assert mapping["usage_date"] == "UsageStartDate"
    assert mapping["service"] == "ProductName"
    assert mapping["cost"] == "UnblendedCost"
    assert len(normalized.dataframe) == profile.row_count
    assert report.ready_for_analysis


def test_automatic_workflow_produces_results_without_manual_mapping() -> None:
    """A supported billing source should reach validated results in one automated pass."""
    demo_path = Path("data/demo/cloud_billing_demo.csv")
    loaded = load_table(demo_path)
    profile = profile_table(loaded)

    mapping, normalized, report = build_automatic_model(loaded, profile)

    assert mapping["usage_date"] == "UsageStartDate"
    assert mapping["service"] == "ProductName"
    assert mapping["cost"] == "UnblendedCost"
    assert len(normalized.dataframe) == len(loaded.dataframe)
    assert report.reconciliation.passed
    assert report.ready_for_analysis


@pytest.mark.parametrize(
    ("scenario_id", "expected_status", "expected_ready"),
    [
        ("healthy", "pass", True),
        ("quality_risk", "error", False),
        ("forecast_risk", "pass", True),
    ],
)
def test_guided_scenarios_have_the_expected_quality_decision(
    scenario_id: str,
    expected_status: str,
    expected_ready: bool,
) -> None:
    settings = Settings.from_environment(base_dir=Path.cwd())

    _, _, _, _, report = build_demo_artifacts(settings, scenario_id)

    assert report.overall_status == expected_status
    assert report.ready_for_analysis is expected_ready


def test_bad_data_scenario_exposes_multiple_distinct_failures() -> None:
    settings = Settings.from_environment(base_dir=Path.cwd())

    _, _, _, _, report = build_demo_artifacts(settings, "quality_risk")
    failed_checks = {check.check_name for check in report.checks if check.status == "error"}

    assert "normalization_conversion_errors" in failed_checks
    assert "currency_consistency" in failed_checks
    assert "required_field_completeness:usage_date" in failed_checks
