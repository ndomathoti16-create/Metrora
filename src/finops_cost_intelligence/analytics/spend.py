"""Core spend calculations for the FinOps dashboard.

All numbers in this module are calculated with pandas before they are shown in
the UI or passed to any future language-model summarizer.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date, datetime

import pandas as pd

from ..contracts.analytics import AnalyticsInputError, SpendSummary

DEFAULT_BREAKDOWN_DIMENSIONS = (
    "service",
    "account_id",
    "department",
    "project",
    "environment",
    "region",
    "provider",
    "cost_type",
)


def _require_columns(dataframe: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [column for column in columns if column not in dataframe.columns]
    if missing:
        raise AnalyticsInputError(
            "Canonical billing data is missing required column(s): " + ", ".join(missing)
        )


def _coerce_dates(dataframe: pd.DataFrame) -> pd.Series:
    dates = pd.to_datetime(dataframe["usage_date"], errors="coerce")
    if dates.isna().any():
        raise AnalyticsInputError(
            f"usage_date contains {int(dates.isna().sum()):,} invalid or missing value(s)."
        )
    return dates.dt.normalize()


def _coerce_cost(dataframe: pd.DataFrame) -> pd.Series:
    costs = pd.to_numeric(dataframe["cost"], errors="coerce")
    if costs.isna().any():
        raise AnalyticsInputError(
            f"cost contains {int(costs.isna().sum()):,} invalid or missing value(s)."
        )
    return costs.astype(float)


def _as_timestamp(value: date | datetime | str | pd.Timestamp) -> pd.Timestamp:
    timestamp = pd.to_datetime(value, errors="coerce")
    if pd.isna(timestamp):
        raise AnalyticsInputError(f"Invalid analysis date: {value!r}")
    return pd.Timestamp(timestamp).normalize()


def filter_billing_data(
    dataframe: pd.DataFrame,
    *,
    date_start: date | datetime | str | pd.Timestamp | None = None,
    date_end: date | datetime | str | pd.Timestamp | None = None,
    selections: Mapping[str, Iterable[object] | None] | None = None,
) -> pd.DataFrame:
    """Apply inclusive date and dimension filters to canonical billing data."""
    _require_columns(dataframe, ("usage_date", "cost"))
    dates = _coerce_dates(dataframe)
    costs = _coerce_cost(dataframe)
    filtered = dataframe.copy()
    filtered["usage_date"] = dates
    filtered["cost"] = costs

    if date_start is not None:
        start = _as_timestamp(date_start)
        filtered = filtered.loc[filtered["usage_date"] >= start]
    if date_end is not None:
        end = _as_timestamp(date_end)
        if date_start is not None and end < _as_timestamp(date_start):
            raise AnalyticsInputError("Analysis end date cannot be before its start date.")
        filtered = filtered.loc[filtered["usage_date"] <= end]

    for dimension, values in (selections or {}).items():
        if values is None:
            continue
        if dimension not in filtered.columns:
            raise AnalyticsInputError(f"Cannot filter by '{dimension}'; the column is not present.")
        selected_values = list(values)
        if selected_values:
            filtered = filtered.loc[filtered[dimension].isin(selected_values)]

    return filtered.reset_index(drop=True)


def prepare_daily_spend(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Aggregate cost by day and fill missing calendar days with zero cost."""
    _require_columns(dataframe, ("usage_date", "cost"))
    if dataframe.empty:
        return pd.DataFrame(columns=["usage_date", "cost", "row_count"])

    dates = _coerce_dates(dataframe)
    costs = _coerce_cost(dataframe)
    working = pd.DataFrame({"usage_date": dates, "cost": costs})
    daily = (
        working.groupby("usage_date", as_index=False)
        .agg(cost=("cost", "sum"), row_count=("cost", "size"))
        .sort_values("usage_date")
    )
    calendar = pd.DataFrame(
        {"usage_date": pd.date_range(daily["usage_date"].min(), daily["usage_date"].max())}
    )
    daily = calendar.merge(daily, on="usage_date", how="left")
    daily["cost"] = daily["cost"].fillna(0.0).astype(float)
    daily["row_count"] = daily["row_count"].fillna(0).astype(int)
    return daily


def aggregate_spend(
    dataframe: pd.DataFrame,
    dimension: str,
    *,
    top_n: int | None = 15,
) -> pd.DataFrame:
    """Aggregate cost and row counts by one canonical dimension."""
    _require_columns(dataframe, ("usage_date", "cost", dimension))
    if top_n is not None and top_n < 1:
        raise AnalyticsInputError("top_n must be at least 1 or None.")
    if dataframe.empty:
        return pd.DataFrame(columns=["value", "cost", "row_count", "share_of_total"])

    working = dataframe.copy()
    working["cost"] = _coerce_cost(working)
    working["value"] = working[dimension].where(
        working[dimension].notna() & working[dimension].astype(str).ne(""),
        "Unallocated",
    )
    breakdown = (
        working.groupby("value", as_index=False, dropna=False)
        .agg(cost=("cost", "sum"), row_count=("cost", "size"))
        .sort_values(["cost", "value"], ascending=[False, True])
    )
    total_cost = float(breakdown["cost"].sum())
    breakdown["share_of_total"] = (
        breakdown["cost"].div(total_cost).fillna(0.0) if total_cost else 0.0
    )
    if top_n is not None:
        breakdown = breakdown.head(top_n)
    return breakdown.reset_index(drop=True)


def _currency_label(dataframe: pd.DataFrame) -> str:
    if "currency" not in dataframe.columns:
        return "Unspecified"
    currencies = (
        dataframe["currency"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda values: values.ne("")]
        .unique()
    )
    if len(currencies) == 1:
        return str(currencies[0])
    if len(currencies) > 1:
        return "Mixed"
    return "Unspecified"


def calculate_spend_summary(
    dataframe: pd.DataFrame,
    *,
    prior_dataframe: pd.DataFrame | None = None,
    top_dimension: str | None = None,
) -> SpendSummary:
    """Calculate auditable KPIs and optional prior-period comparison."""
    _require_columns(dataframe, ("usage_date", "cost"))
    if dataframe.empty:
        return SpendSummary(
            total_cost=0.0,
            row_count=0,
            calendar_days=0,
            average_daily_cost=0.0,
            date_start=None,
            date_end=None,
            currency=_currency_label(dataframe),
            prior_period_cost=None,
            change_amount=None,
            change_pct=None,
        )

    dates = _coerce_dates(dataframe)
    costs = _coerce_cost(dataframe)
    date_min = dates.min()
    date_max = dates.max()
    calendar_days = int((date_max - date_min).days) + 1
    total_cost = float(costs.sum())

    prior_cost: float | None = None
    change_amount: float | None = None
    change_pct: float | None = None
    if prior_dataframe is not None and not prior_dataframe.empty:
        _require_columns(prior_dataframe, ("usage_date", "cost"))
        prior_cost = float(_coerce_cost(prior_dataframe).sum())
        change_amount = total_cost - prior_cost
        change_pct = change_amount / prior_cost if prior_cost else None

    top_cost: float | None = None
    top_share: float | None = None
    if top_dimension is not None:
        breakdown = aggregate_spend(dataframe, top_dimension, top_n=1)
        if not breakdown.empty:
            top_cost = float(breakdown.iloc[0]["cost"])
            top_share = float(breakdown.iloc[0]["share_of_total"])

    return SpendSummary(
        total_cost=total_cost,
        row_count=int(len(dataframe)),
        calendar_days=calendar_days,
        average_daily_cost=total_cost / calendar_days,
        date_start=date_min.date().isoformat(),
        date_end=date_max.date().isoformat(),
        currency=_currency_label(dataframe),
        prior_period_cost=prior_cost,
        change_amount=change_amount,
        change_pct=change_pct,
        top_dimension=top_dimension,
        top_dimension_cost=top_cost,
        top_dimension_share=top_share,
    )
