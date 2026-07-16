"""Data profiling for loaded tabular sources."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from typing import Any

import pandas as pd

from ..contracts.profile import ColumnProfile, DataProfile
from .readers import LoadedTable

PROFILE_VERSION = "1.0"


def _json_safe(value: Any) -> Any:
    if value is None:
        return None

    try:
        missing = pd.isna(value)
        if isinstance(missing, bool) and missing:
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (ValueError, TypeError):
            pass
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _parse_rate(series: pd.Series, parser: Callable[..., Any]) -> float:
    non_null = series.dropna()
    if len(non_null) == 0:
        return 0.0
    try:
        parsed = parser(non_null, errors="coerce")
        return round(float(parsed.notna().mean()), 4)
    except (TypeError, ValueError):
        return 0.0


def _inferred_type(
    series: pd.Series,
    numeric_parse_rate: float,
    datetime_parse_rate: float,
) -> str:
    dtype = series.dtype
    if pd.api.types.is_bool_dtype(dtype):
        return "boolean"
    if pd.api.types.is_integer_dtype(dtype):
        return "integer"
    if pd.api.types.is_float_dtype(dtype) or pd.api.types.is_numeric_dtype(dtype):
        return "decimal"
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "datetime"
    if datetime_parse_rate >= 0.8 and datetime_parse_rate > numeric_parse_rate:
        return "datetime-like"
    if numeric_parse_rate >= 0.8:
        return "numeric-like"
    return "string"


def _sample_values(series: pd.Series, limit: int) -> tuple[Any, ...]:
    values: list[Any] = []
    seen: set[str] = set()
    for value in series.dropna().tolist():
        safe_value = _json_safe(value)
        key = repr(safe_value)
        if key in seen:
            continue
        seen.add(key)
        values.append(safe_value)
        if len(values) >= limit:
            break
    return tuple(values)


def _column_profile(series: pd.Series, sample_value_limit: int) -> ColumnProfile:
    row_count = int(len(series))
    non_null_count = int(series.notna().sum())
    null_count = row_count - non_null_count
    null_rate = round(null_count / row_count, 4) if row_count else 0.0
    numeric_parse_rate = _parse_rate(series, pd.to_numeric)
    datetime_parse_rate = _parse_rate(
        series,
        lambda values, errors: pd.to_datetime(
            values,
            errors=errors,
            format="mixed",
        ),
    )
    return ColumnProfile(
        name=str(series.name),
        dtype=str(series.dtype),
        inferred_type=_inferred_type(series, numeric_parse_rate, datetime_parse_rate),
        row_count=row_count,
        non_null_count=non_null_count,
        null_count=null_count,
        null_rate=null_rate,
        unique_count=int(series.nunique(dropna=True)),
        numeric_parse_rate=numeric_parse_rate,
        datetime_parse_rate=datetime_parse_rate,
        sample_values=_sample_values(series, sample_value_limit),
    )


def _sample_rows(dataframe: pd.DataFrame, limit: int) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for _, row in dataframe.head(limit).iterrows():
        rows.append({str(column): _json_safe(value) for column, value in row.items()})
    return tuple(rows)


def profile_table(
    loaded_table: LoadedTable,
    *,
    sample_rows: int = 5,
    sample_values: int = 5,
) -> DataProfile:
    """Profile a loaded table without modifying its DataFrame."""
    if sample_rows <= 0:
        raise ValueError("sample_rows must be greater than zero.")
    if sample_values <= 0:
        raise ValueError("sample_values must be greater than zero.")

    dataframe = loaded_table.dataframe
    columns = tuple(
        _column_profile(dataframe[column], sample_values) for column in dataframe.columns
    )
    return DataProfile(
        profile_version=PROFILE_VERSION,
        source_name=loaded_table.source_name,
        file_format=loaded_table.file_format,
        source_size_bytes=loaded_table.source_size_bytes,
        sheet_name=loaded_table.sheet_name,
        row_count=int(len(dataframe)),
        column_count=int(len(dataframe.columns)),
        duplicate_row_count=int(dataframe.duplicated(keep="first").sum()),
        all_null_row_count=int(dataframe.isna().all(axis=1).sum()),
        memory_usage_bytes=int(dataframe.memory_usage(deep=True).sum()),
        columns=columns,
        sample_rows=_sample_rows(dataframe, sample_rows),
    )
