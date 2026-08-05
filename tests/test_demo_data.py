import pandas as pd

from data.demo.generate_demo_data import build_demo_tables


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
