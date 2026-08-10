from datetime import date

import pandas as pd
import pytest

from finops_cost_intelligence.analytics import (
    aggregate_spend,
    analyze_service_cost_drivers,
    calculate_spend_summary,
    filter_billing_data,
    prepare_daily_spend,
)
from finops_cost_intelligence.contracts.analytics import AnalyticsInputError


@pytest.fixture
def billing_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "usage_date": ["2025-01-01", "2025-01-01", "2025-01-03", "2025-01-04"],
            "service": ["Compute", "Storage", "Compute", "Compute"],
            "account_id": ["prod", "prod", "prod", "dev"],
            "department": ["Engineering", "Engineering", "Engineering", "Finance"],
            "cost": [100.0, 25.0, 50.0, 10.0],
            "currency": ["USD", "USD", "USD", "USD"],
        }
    )


def test_filtering_is_inclusive_and_applies_dimension_selection(billing_data):
    filtered = filter_billing_data(
        billing_data,
        date_start=date(2025, 1, 1),
        date_end=date(2025, 1, 3),
        selections={"service": ["Compute"]},
    )

    assert len(filtered) == 2
    assert filtered["cost"].sum() == 150.0


def test_filter_rejects_reversed_dates(billing_data):
    with pytest.raises(AnalyticsInputError, match="cannot be before"):
        filter_billing_data(
            billing_data,
            date_start="2025-01-04",
            date_end="2025-01-01",
        )


def test_daily_spend_fills_missing_calendar_days(billing_data):
    daily = prepare_daily_spend(billing_data)

    assert daily["usage_date"].dt.date.tolist() == [
        date(2025, 1, 1),
        date(2025, 1, 2),
        date(2025, 1, 3),
        date(2025, 1, 4),
    ]
    assert daily["cost"].tolist() == [125.0, 0.0, 50.0, 10.0]
    assert daily["row_count"].tolist() == [2, 0, 1, 1]


def test_breakdown_calculates_cost_share(billing_data):
    breakdown = aggregate_spend(billing_data, "service")

    assert breakdown.iloc[0]["value"] == "Compute"
    assert breakdown.iloc[0]["cost"] == 160.0
    assert breakdown["share_of_total"].sum() == pytest.approx(1.0)


def test_summary_calculates_period_change_and_currency(billing_data):
    current = billing_data.iloc[2:].copy()
    prior = billing_data.iloc[:2].copy()

    summary = calculate_spend_summary(current, prior_dataframe=prior, top_dimension="service")

    assert summary.total_cost == 60.0
    assert summary.calendar_days == 2
    assert summary.average_daily_cost == 30.0
    assert summary.prior_period_cost == 125.0
    assert summary.change_amount == -65.0
    assert summary.change_pct == pytest.approx(-0.52)
    assert summary.currency == "USD"


def test_summary_rejects_invalid_costs(billing_data):
    billing_data["cost"] = billing_data["cost"].astype(object)
    billing_data.loc[0, "cost"] = "not-a-number"

    with pytest.raises(AnalyticsInputError, match="cost contains"):
        calculate_spend_summary(billing_data)


def test_service_drivers_separate_usage_from_effective_rate_mix():
    dataframe = pd.DataFrame(
        {
            "usage_date": ["2025-01-01", "2025-01-02"] * 2,
            "service": ["Compute", "Compute", "Storage", "Storage"],
            "cost": [200.0, 300.0, 100.0, 150.0],
            "usage_quantity": [100.0, 150.0, 100.0, 100.0],
            "usage_unit": ["hours"] * 4,
        }
    )

    drivers = analyze_service_cost_drivers(
        dataframe,
        recent_start="2025-01-02",
        recent_end="2025-01-02",
        prior_start="2025-01-01",
        prior_end="2025-01-01",
    ).set_index("service")

    assert drivers.loc["Compute", "driver_type"] == "Usage-driven"
    assert drivers.loc["Compute", "usage_change_pct"] == pytest.approx(0.5)
    assert drivers.loc["Compute", "effective_rate_change_pct"] == pytest.approx(0.0)
    assert drivers.loc["Storage", "driver_type"] == "Effective rate/mix-driven"
    assert drivers.loc["Storage", "usage_change_pct"] == pytest.approx(0.0)
    assert drivers.loc["Storage", "effective_rate_change_pct"] == pytest.approx(0.5)


def test_service_driver_does_not_invent_cause_without_comparable_usage():
    drivers = analyze_service_cost_drivers(
        pd.DataFrame(
            {
                "usage_date": ["2025-01-01", "2025-01-02"],
                "service": ["Compute", "Compute"],
                "cost": [100.0, 150.0],
            }
        ),
        recent_start="2025-01-02",
        recent_end="2025-01-02",
        prior_start="2025-01-01",
        prior_end="2025-01-01",
    )

    assert drivers.iloc[0]["driver_type"] == "Billing-only"
    assert drivers.iloc[0]["evidence_level"].startswith("Low")
    assert "confirm root cause" in drivers.iloc[0]["explanation"]
