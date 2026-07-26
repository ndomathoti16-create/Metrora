"""Business-volume joins and unit-cost calculations."""

from __future__ import annotations

import pandas as pd

from ..contracts.analytics import AnalyticsInputError
from ..contracts.business_metrics import UnitEconomicsSummary


def calculate_unit_economics(
    actual_dataframe: pd.DataFrame,
    metrics_dataframe: pd.DataFrame,
    metric_name: str,
) -> tuple[pd.DataFrame, UnitEconomicsSummary]:
    """Join daily spend to one business metric and calculate cost per unit."""
    required_actual = {"usage_date", "cost"}
    required_metric = {"metric_date", "metric_name", "metric_value"}
    missing_actual = sorted(required_actual - set(actual_dataframe.columns))
    missing_metric = sorted(required_metric - set(metrics_dataframe.columns))
    if missing_actual or missing_metric:
        raise AnalyticsInputError(
            "Missing columns for unit economics: "
            + ", ".join(missing_actual + missing_metric)
        )
    actual = actual_dataframe.copy()
    actual["usage_date"] = pd.to_datetime(actual["usage_date"], errors="coerce").dt.normalize()
    actual["cost"] = pd.to_numeric(actual["cost"], errors="coerce")
    metrics = metrics_dataframe.loc[metrics_dataframe["metric_name"].eq(metric_name)].copy()
    metrics["metric_date"] = pd.to_datetime(metrics["metric_date"], errors="coerce").dt.normalize()
    metrics["metric_value"] = pd.to_numeric(metrics["metric_value"], errors="coerce")
    actual_invalid = actual[["usage_date", "cost"]].isna().any().any()
    metric_invalid = metrics[["metric_date", "metric_value"]].isna().any().any()
    if actual_invalid or metric_invalid:
        raise AnalyticsInputError("Inputs contain invalid dates or values for unit economics.")
    if metrics.empty:
        raise AnalyticsInputError(f"Metric '{metric_name}' is not present in the upload.")

    daily_actual = actual.groupby("usage_date", as_index=False).agg(cost=("cost", "sum"))
    daily_metric = metrics.groupby("metric_date", as_index=False).agg(
        metric_value=("metric_value", "sum")
    )
    daily_metric = daily_metric.rename(columns={"metric_date": "usage_date"})
    joined = daily_metric.merge(daily_actual, on="usage_date", how="left")
    joined["cost"] = joined["cost"].fillna(0.0)
    joined["cost_per_unit"] = joined["cost"].where(joined["metric_value"].ne(0)).div(
        joined["metric_value"].where(joined["metric_value"].ne(0))
    )
    total_cost = float(joined["cost"].sum())
    total_metric = float(joined["metric_value"].sum())
    summary = UnitEconomicsSummary(
        metric_name=metric_name,
        total_cost=total_cost,
        total_metric_value=total_metric,
        cost_per_unit=total_cost / total_metric if total_metric else None,
        days_with_metric=len(joined),
        days_without_cost=int(joined["cost"].eq(0).sum()),
    )
    return joined.sort_values("usage_date").reset_index(drop=True), summary
