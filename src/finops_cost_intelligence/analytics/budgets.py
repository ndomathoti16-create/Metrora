"""Actual-versus-budget calculations over canonical billing and budget data."""

from __future__ import annotations

import pandas as pd

from ..contracts.analytics import AnalyticsInputError
from ..contracts.budget import BudgetVarianceSummary


def calculate_budget_variance(
    actual_dataframe: pd.DataFrame,
    budget_dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, BudgetVarianceSummary]:
    """Match actual cost to each budget row by inclusive period and scope."""
    required_actual = {"usage_date", "cost"}
    missing_actual = sorted(required_actual - set(actual_dataframe.columns))
    if missing_actual:
        raise AnalyticsInputError("Actual billing data is missing: " + ", ".join(missing_actual))
    required_budget = {
        "period_start",
        "period_end",
        "scope_type",
        "scope_value",
        "budget_amount",
    }
    missing_budget = sorted(required_budget - set(budget_dataframe.columns))
    if missing_budget:
        raise AnalyticsInputError("Normalized budget data is missing: " + ", ".join(missing_budget))
    actual = actual_dataframe.copy()
    actual["usage_date"] = pd.to_datetime(actual["usage_date"], errors="coerce").dt.normalize()
    actual["cost"] = pd.to_numeric(actual["cost"], errors="coerce")
    if actual[["usage_date", "cost"]].isna().any().any():
        raise AnalyticsInputError("Actual data contains invalid usage_date or cost values.")
    budget = budget_dataframe.copy()
    budget["period_start"] = pd.to_datetime(budget["period_start"], errors="coerce").dt.normalize()
    budget["period_end"] = pd.to_datetime(budget["period_end"], errors="coerce").dt.normalize()
    budget["budget_amount"] = pd.to_numeric(budget["budget_amount"], errors="coerce")
    if budget[["period_start", "period_end", "budget_amount"]].isna().any().any():
        raise AnalyticsInputError("Budget data contains invalid period or amount values.")

    rows: list[dict[str, object]] = []
    for _, budget_row in budget.iterrows():
        start = budget_row["period_start"]
        end = budget_row["period_end"]
        mask = actual["usage_date"].between(start, end, inclusive="both")
        scope_type = str(budget_row["scope_type"])
        scope_value = str(budget_row["scope_value"])
        if scope_type != "total":
            if scope_type not in actual.columns:
                raise AnalyticsInputError(
                    f"Actual billing data has no '{scope_type}' column for budget matching."
                )
            mask &= actual[scope_type].astype("string").eq(scope_value)
        actual_cost = float(actual.loc[mask, "cost"].sum())
        budget_amount = float(budget_row["budget_amount"])
        variance = actual_cost - budget_amount
        utilization = actual_cost / budget_amount if budget_amount else None
        if actual_cost == 0:
            status = "no_actuals"
        elif variance > 0:
            status = "over_budget"
        else:
            status = "on_track"
        rows.append(
            {
                **budget_row.to_dict(),
                "actual_cost": actual_cost,
                "variance_amount": variance,
                "variance_pct": variance / budget_amount if budget_amount else None,
                "utilization_pct": utilization,
                "status": status,
            }
        )

    comparison = pd.DataFrame(rows)
    summary = BudgetVarianceSummary(
        budget_total=float(comparison["budget_amount"].sum()),
        actual_total=float(comparison["actual_cost"].sum()),
        variance_amount=float(comparison["variance_amount"].sum()),
        utilization_pct=(
            float(comparison["actual_cost"].sum() / comparison["budget_amount"].sum())
            if comparison["budget_amount"].sum()
            else None
        ),
        rows_compared=len(comparison),
    )
    return comparison, summary
