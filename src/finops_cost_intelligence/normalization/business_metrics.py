"""Normalize business-volume files for cost-efficiency analysis."""

from __future__ import annotations

import re

import pandas as pd

from ..contracts.business_metrics import BusinessMetricValidationError

_ALIASES: dict[str, tuple[str, ...]] = {
    "metric_date": ("metric date", "date", "period date", "usage date", "day"),
    "metric_name": ("metric name", "metric", "kpi", "measure"),
    "metric_value": ("metric value", "value", "amount", "quantity", "count", "volume"),
    "unit": ("unit", "metric unit", "unit type"),
}


def _normal_name(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).strip().lower()).strip()


def _find_column(columns: list[str], aliases: tuple[str, ...]) -> str | None:
    normalized = {_normal_name(column): column for column in columns}
    for alias in aliases:
        if _normal_name(alias) in normalized:
            return normalized[_normal_name(alias)]
    return None


def normalize_business_metrics(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Map a business metric table to date, name, value, and unit."""
    if dataframe.empty:
        raise BusinessMetricValidationError("The business metrics file contains no rows.")
    source = dataframe.copy().reset_index(drop=True)
    source.columns = [str(column) for column in source.columns]
    columns = list(source.columns)
    matches = {canonical: _find_column(columns, aliases) for canonical, aliases in _ALIASES.items()}
    missing = [
        field for field in ("metric_date", "metric_name", "metric_value") if matches[field] is None
    ]
    if missing:
        raise BusinessMetricValidationError(
            "Business metrics are missing required field(s): " + ", ".join(missing)
        )
    output = pd.DataFrame(index=source.index)
    output["metric_date"] = pd.to_datetime(
        source[matches["metric_date"]], errors="coerce", format="mixed"
    ).dt.normalize()
    output["metric_name"] = source[matches["metric_name"]].astype("string").str.strip()
    output["metric_value"] = pd.to_numeric(source[matches["metric_value"]], errors="coerce")
    output["unit"] = (
        source[matches["unit"]].astype("string").str.strip()
        if matches["unit"]
        else pd.Series("units", index=source.index, dtype="string")
    )
    if output[["metric_date", "metric_name", "metric_value"]].isna().any().any():
        raise BusinessMetricValidationError(
            "Business metrics contain invalid date, name, or value fields."
        )
    if (output["metric_name"].eq("")).any():
        raise BusinessMetricValidationError("metric_name cannot be blank.")
    if (output["metric_value"] < 0).any():
        raise BusinessMetricValidationError("metric_value cannot be negative.")
    output["unit"] = output["unit"].fillna("units").replace("", "units")
    output["metric_row_number"] = pd.Series(range(1, len(output) + 1), dtype="Int64")
    return output[["metric_row_number", "metric_date", "metric_name", "metric_value", "unit"]]
