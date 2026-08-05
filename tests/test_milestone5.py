import pandas as pd
import pytest

from finops_cost_intelligence.analytics.allocation import calculate_allocation_coverage
from finops_cost_intelligence.analytics.budgets import calculate_budget_variance
from finops_cost_intelligence.analytics.business_metrics import calculate_unit_economics
from finops_cost_intelligence.contracts.analytics import AnalyticsInputError
from finops_cost_intelligence.contracts.budget import BudgetValidationError
from finops_cost_intelligence.normalization.budgets import normalize_budget_dataframe
from finops_cost_intelligence.normalization.business_metrics import normalize_business_metrics


def test_budget_normalization_supports_common_headers_and_month_end():
    normalized = normalize_budget_dataframe(
        pd.DataFrame(
            {
                "Month": ["2025-01-01"],
                "Dimension": ["service"],
                "Value": ["Compute"],
                "Budget": ["$1,000.00"],
                "Currency Code": ["usd"],
            }
        )
    )

    assert normalized.loc[0, "period_end"] == pd.Timestamp("2025-01-31")
    assert normalized.loc[0, "scope_type"] == "service"
    assert normalized.loc[0, "budget_amount"] == 1000.0
    assert normalized.loc[0, "currency"] == "USD"


def test_budget_normalization_rejects_negative_amount():
    with pytest.raises(BudgetValidationError, match="cannot be negative"):
        normalize_budget_dataframe(pd.DataFrame({"date": ["2025-01-01"], "budget": [-10]}))


def test_budget_variance_matches_total_and_service_scopes():
    actual = pd.DataFrame(
        {
            "usage_date": ["2025-01-01", "2025-01-01", "2025-01-02"],
            "service": ["Compute", "Storage", "Compute"],
            "cost": [100.0, 25.0, 50.0],
        }
    )
    budget = normalize_budget_dataframe(
        pd.DataFrame(
            {
                "period_start": ["2025-01-01", "2025-01-01"],
                "period_end": ["2025-01-31", "2025-01-31"],
                "scope_type": ["total", "service"],
                "scope_value": ["Total", "Compute"],
                "budget_amount": [200, 120],
            }
        )
    )

    comparison, summary = calculate_budget_variance(actual, budget)

    assert comparison["actual_cost"].tolist() == [175.0, 150.0]
    assert comparison["status"].tolist() == ["on_track", "over_budget"]
    assert summary.budget_total == 320.0
    assert summary.actual_total == 325.0
    assert summary.variance_amount == 5.0


def test_allocation_coverage_uses_positive_cost_denominator():
    data = pd.DataFrame(
        {
            "cost": [100.0, 50.0, -20.0],
            "department": ["Engineering", None, "Finance"],
            "project": ["A", None, None],
        }
    )

    coverage = calculate_allocation_coverage(data, ["department", "project"])

    department = coverage.loc[coverage["field"].eq("department")].iloc[0]
    any_field = coverage.loc[coverage["field"].eq("any ownership field")].iloc[0]
    assert department["row_coverage"] == pytest.approx(2 / 3)
    assert department["cost_coverage"] == pytest.approx(100 / 150)
    assert any_field["cost_coverage"] == pytest.approx(100 / 150)


def test_business_metric_normalization_and_unit_economics():
    metrics = normalize_business_metrics(
        pd.DataFrame(
            {
                "Date": ["2025-01-01", "2025-01-02"],
                "Metric": ["Customers", "Customers"],
                "Value": [10, 20],
            }
        )
    )
    actual = pd.DataFrame(
        {
            "usage_date": ["2025-01-01", "2025-01-02"],
            "cost": [100.0, 60.0],
        }
    )

    joined, summary = calculate_unit_economics(actual, metrics, "Customers")

    assert joined["cost_per_unit"].tolist() == [10.0, 3.0]
    assert summary.total_metric_value == 30.0
    assert summary.cost_per_unit == pytest.approx(160 / 30)


def test_unit_economics_rejects_missing_metric_name():
    actual = pd.DataFrame({"usage_date": ["2025-01-01"], "cost": [10.0]})
    metrics = pd.DataFrame(
        {
            "metric_date": ["2025-01-01"],
            "metric_name": ["Customers"],
            "metric_value": [1],
        }
    )

    with pytest.raises(AnalyticsInputError, match="not present"):
        calculate_unit_economics(actual, metrics, "Revenue")
