"""Allocation and tagging coverage calculations."""

from __future__ import annotations

import pandas as pd

from ..contracts.analytics import AnalyticsInputError

DEFAULT_ALLOCATION_FIELDS = ("account_id", "department", "project", "environment")


def calculate_allocation_coverage(
    dataframe: pd.DataFrame,
    fields: tuple[str, ...] | list[str] = DEFAULT_ALLOCATION_FIELDS,
) -> pd.DataFrame:
    """Calculate row- and positive-cost-weighted coverage by ownership field.

    Positive spend is used as the cost denominator so credits and refunds do not
    make coverage exceed 100% or obscure whether spend is tagged.
    """
    if "cost" not in dataframe.columns:
        raise AnalyticsInputError("Canonical billing data is missing cost.")
    selected_fields = [field for field in fields if field in dataframe.columns]
    if not selected_fields:
        raise AnalyticsInputError("No requested allocation fields are present in the data.")
    costs = pd.to_numeric(dataframe["cost"], errors="coerce")
    if costs.isna().any():
        raise AnalyticsInputError("cost contains invalid values for allocation analysis.")
    positive_cost = costs.clip(lower=0)
    total_positive_cost = float(positive_cost.sum())
    rows: list[dict[str, object]] = []
    populated_masks: list[pd.Series] = []
    for field in selected_fields:
        values = dataframe[field]
        populated = values.notna() & values.astype("string").str.strip().ne("")
        populated_masks.append(populated)
        allocated_cost = float(positive_cost.loc[populated].sum())
        rows.append(
            {
                "field": field,
                "total_rows": len(dataframe),
                "populated_rows": int(populated.sum()),
                "row_coverage": float(populated.mean()) if len(dataframe) else 0.0,
                "positive_cost": total_positive_cost,
                "allocated_positive_cost": allocated_cost,
                "cost_coverage": allocated_cost / total_positive_cost
                if total_positive_cost
                else None,
            }
        )
    any_populated = pd.concat(populated_masks, axis=1).any(axis=1)
    any_cost = float(positive_cost.loc[any_populated].sum())
    rows.append(
        {
            "field": "any ownership field",
            "total_rows": len(dataframe),
            "populated_rows": int(any_populated.sum()),
            "row_coverage": float(any_populated.mean()) if len(dataframe) else 0.0,
            "positive_cost": total_positive_cost,
            "allocated_positive_cost": any_cost,
            "cost_coverage": any_cost / total_positive_cost if total_positive_cost else None,
        }
    )
    return pd.DataFrame(rows)
