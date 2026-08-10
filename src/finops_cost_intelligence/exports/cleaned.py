"""In-memory exports with no implicit local file writes."""

from __future__ import annotations

import io
import json

import pandas as pd

from ..contracts.ai import FactPack
from ..contracts.normalization import NormalizedTable
from ..contracts.quality import QualityReport


def cleaned_csv_bytes(normalized: NormalizedTable | pd.DataFrame) -> bytes:
    """Return canonical rows as UTF-8 CSV bytes."""
    # Attribute-based unwrapping stays reliable across Streamlit hot reloads, where an
    # instance can outlive the exact imported class object used by ``isinstance``.
    dataframe = getattr(normalized, "dataframe", normalized)
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Cleaned CSV export requires a normalized pandas dataframe.")
    return dataframe.to_csv(index=False).encode("utf-8")


def cleaned_parquet_bytes(normalized: NormalizedTable | pd.DataFrame) -> bytes:
    """Return canonical rows as Parquet bytes."""
    dataframe = getattr(normalized, "dataframe", normalized)
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Cleaned Parquet export requires a normalized pandas dataframe.")
    buffer = io.BytesIO()
    dataframe.to_parquet(buffer, index=False)
    return buffer.getvalue()


def fact_pack_json_bytes(fact_pack: FactPack) -> bytes:
    """Return the exact structured evidence pack as formatted JSON bytes."""
    return (
        json.dumps(fact_pack.to_dict(), indent=2, ensure_ascii=False, default=str) + "\n"
    ).encode("utf-8")


def quality_report_json_bytes(report: QualityReport) -> bytes:
    """Return quality status and checks as formatted JSON bytes."""
    return (json.dumps(report.to_dict(), indent=2, ensure_ascii=False, default=str) + "\n").encode(
        "utf-8"
    )
