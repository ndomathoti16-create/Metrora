"""Defensive CSV serialization for files that may be opened in spreadsheet software."""

from __future__ import annotations

import pandas as pd

FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def neutralize_spreadsheet_formulas(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Prefix formula-like text while preserving numeric and missing values."""
    safe = dataframe.copy()
    text_columns = safe.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        safe[column] = safe[column].map(
            lambda value: (
                f"'{value}"
                if isinstance(value, str) and value.lstrip(" ").startswith(FORMULA_PREFIXES)
                else value
            )
        )
    return safe
