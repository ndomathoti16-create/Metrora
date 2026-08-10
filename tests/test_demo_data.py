import pandas as pd

from data.demo.generate_demo_data import build_demo_scenarios, build_demo_tables


def test_demo_tables_are_deterministic_and_cover_the_demo_workflow():
    billing_one, budget_one, metrics_one = build_demo_tables(seed=42)
    billing_two, budget_two, metrics_two = build_demo_tables(seed=42)

    pd.testing.assert_frame_equal(billing_one, billing_two)
    pd.testing.assert_frame_equal(budget_one, budget_two)
    pd.testing.assert_frame_equal(metrics_one, metrics_two)
    assert len(billing_one) == 59 * 4
    assert {"Customers", "Transactions"}.issubset(set(metrics_one["metric_name"]))
    assert billing_one["Dept"].isna().any()
    assert budget_one["scope_type"].eq("total").any()


def test_demo_scenarios_cover_healthy_quality_and_forward_risk_stories():
    scenarios = build_demo_scenarios(seed=42)

    assert set(scenarios) == {"healthy", "quality_risk", "forecast_risk"}

    healthy, _, _ = scenarios["healthy"]
    assert not healthy[["UsageStartDate", "ProductName", "UnblendedCost"]].isna().any().any()
    assert healthy["Currency"].nunique() == 1
    assert not healthy.duplicated().any()

    quality_risk, _, _ = scenarios["quality_risk"]
    assert "not-a-date" in set(quality_risk["UsageStartDate"])
    assert "not-a-cost" in set(quality_risk["UnblendedCost"])
    assert quality_risk["Currency"].nunique() > 1
    assert quality_risk.duplicated().any()

    forecast_risk, _, _ = scenarios["forecast_risk"]
    daily = (
        forecast_risk.assign(UsageStartDate=pd.to_datetime(forecast_risk["UsageStartDate"]))
        .groupby("UsageStartDate")["UnblendedCost"]
        .sum()
        .sort_index()
    )
    assert daily.tail(7).mean() > daily.iloc[-14:-7].mean()
