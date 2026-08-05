"""Normalize common budget file formats into the canonical budget model."""

from __future__ import annotations

import re

import pandas as pd

from ..contracts.budget import BudgetValidationError

_ALIASES: dict[str, tuple[str, ...]] = {
    "period_start": ("period start", "start date", "date", "month", "period"),
    "period_end": ("period end", "end date", "month end"),
    "scope_type": ("scope type", "dimension", "level", "budget dimension"),
    "scope_value": ("scope value", "dimension value", "value"),
    "budget_amount": (
        "budget",
        "budget amount",
        "budget cost",
        "budgeted cost",
        "limit",
        "amount",
    ),
    "currency": ("currency", "currency code", "bill currency"),
}


def _normal_name(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).strip().lower()).strip()


def _find_column(columns: list[str], aliases: tuple[str, ...]) -> str | None:
    normalized = {_normal_name(column): column for column in columns}
    for alias in aliases:
        if _normal_name(alias) in normalized:
            return normalized[_normal_name(alias)]
    return None


def _numeric(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    text = text.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    text = text.str.replace(r"[$€£¥]", "", regex=True)
    text = text.str.replace(",", "", regex=False)
    return pd.to_numeric(text, errors="coerce")


def normalize_budget_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Map a budget table to period, scope, amount, and currency columns."""
    if dataframe.empty:
        raise BudgetValidationError("The budget file contains no data rows.")
    source = dataframe.copy().reset_index(drop=True)
    source.columns = [str(column) for column in source.columns]
    columns = list(source.columns)
    matches = {canonical: _find_column(columns, aliases) for canonical, aliases in _ALIASES.items()}
    missing = [field for field in ("period_start", "budget_amount") if matches[field] is None]
    if missing:
        raise BudgetValidationError(
            "Budget data is missing required field(s): " + ", ".join(missing)
        )

    output = pd.DataFrame(index=source.index)
    output["period_start"] = pd.to_datetime(
        source[matches["period_start"]], errors="coerce", format="mixed"
    ).dt.normalize()
    if output["period_start"].isna().any():
        raise BudgetValidationError(
            f"period_start contains {int(output['period_start'].isna().sum()):,} invalid value(s)."
        )
    if matches["period_end"]:
        output["period_end"] = pd.to_datetime(
            source[matches["period_end"]], errors="coerce", format="mixed"
        ).dt.normalize()
    else:
        output["period_end"] = output["period_start"] + pd.offsets.MonthEnd(0)
    if output["period_end"].isna().any():
        raise BudgetValidationError("period_end contains invalid value(s).")
    if (output["period_end"] < output["period_start"]).any():
        raise BudgetValidationError("Every period_end must be on or after period_start.")

    if matches["scope_type"]:
        scope_type = source[matches["scope_type"]].astype("string").str.strip().str.lower()
    else:
        scope_type = pd.Series("total", index=source.index, dtype="string")
    scope_type = (
        scope_type.str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
        .replace(
            {
                "account": "account_id",
                "accounts": "account_id",
                "dept": "department",
                "app": "project",
                "env": "environment",
            }
        )
    )
    allowed_scopes = {
        "total",
        "service",
        "account_id",
        "department",
        "project",
        "environment",
        "region",
    }
    unknown_scopes = sorted(set(scope_type.dropna()) - allowed_scopes)
    if unknown_scopes:
        raise BudgetValidationError(
            "Unsupported budget scope type(s): " + ", ".join(unknown_scopes)
        )
    output["scope_type"] = scope_type.fillna("total")
    if matches["scope_value"]:
        scope_value = source[matches["scope_value"]].astype("string").str.strip()
    else:
        scope_value = pd.Series(pd.NA, index=source.index, dtype="string")
    output["scope_value"] = scope_value.mask(scope_value.eq(""), pd.NA)
    output.loc[output["scope_type"].eq("total"), "scope_value"] = "Total"
    non_total_missing = output["scope_type"].ne("total") & output["scope_value"].isna()
    if non_total_missing.any():
        raise BudgetValidationError("Non-total budget rows require a scope_value.")

    output["budget_amount"] = _numeric(source[matches["budget_amount"]])
    if output["budget_amount"].isna().any():
        raise BudgetValidationError(
            "budget_amount contains "
            f"{int(output['budget_amount'].isna().sum()):,} invalid value(s)."
        )
    if (output["budget_amount"] < 0).any():
        raise BudgetValidationError("budget_amount cannot be negative.")
    if matches["currency"]:
        output["currency"] = source[matches["currency"]].astype("string").str.strip().str.upper()
    else:
        output["currency"] = "Unspecified"
    output["currency"] = output["currency"].fillna("Unspecified").replace("", "Unspecified")
    output["budget_row_number"] = pd.Series(range(1, len(output) + 1), dtype="Int64")
    return output[
        [
            "budget_row_number",
            "period_start",
            "period_end",
            "scope_type",
            "scope_value",
            "budget_amount",
            "currency",
        ]
    ]
