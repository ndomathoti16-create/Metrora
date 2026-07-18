"""Normalize mapped billing data into the canonical FinOps cost model."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

import pandas as pd

from ..contracts.mapping import CANONICAL_FIELD_SPECS, CanonicalFieldSpec
from ..contracts.normalization import (
    NormalizationIssue,
    NormalizationReport,
    NormalizedTable,
)
from ..ingestion.readers import LoadedTable
from ..mapping.validator import validate_mapping

DEFAULT_ISSUE_SAMPLE_LIMIT = 100


def _is_missing_scalar(value: Any) -> bool:
    if value is None:
        return True
    try:
        missing = pd.isna(value)
        return isinstance(missing, bool) and missing
    except (TypeError, ValueError):
        return False


def _raw_value_text(value: Any) -> str:
    if _is_missing_scalar(value):
        return "<missing>"
    try:
        text = json.dumps(value, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        text = str(value)
    return text[:200]


def _empty_series(spec: CanonicalFieldSpec, row_count: int) -> pd.Series:
    if spec.kind == "date":
        return pd.Series(pd.NaT, index=range(row_count), dtype="datetime64[ns]")
    if spec.kind == "numeric":
        return pd.Series(pd.NA, index=range(row_count), dtype="Float64")
    return pd.Series(pd.NA, index=range(row_count), dtype="string")


def _normalize_string(series: pd.Series) -> pd.Series:
    normalized = series.astype("string").str.strip().str.replace(
        r"\s+",
        " ",
        regex=True,
    )
    return normalized.mask(normalized.eq(""), pd.NA)


def _normalize_currency(series: pd.Series) -> pd.Series:
    return _normalize_string(series).str.upper()


def _normalize_tags(series: pd.Series) -> pd.Series:
    def normalize_value(value: Any) -> str | None:
        if _is_missing_scalar(value):
            return None
        if isinstance(value, (dict, list, tuple)):
            return json.dumps(value, default=str, ensure_ascii=False, sort_keys=True)
        return str(value).strip() or None

    return series.map(normalize_value).astype("string")


def _normalize_numeric(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    text = text.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    text = text.str.replace(r"[$€£¥]", "", regex=True)
    text = text.str.replace(",", "", regex=False)
    return pd.to_numeric(text, errors="coerce").astype("Float64")


def normalize_numeric_values(series: pd.Series) -> pd.Series:
    """Parse billing-style numeric values for quality reconciliation and normalization."""
    return _normalize_numeric(series)


def _normalize_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", format="mixed").dt.normalize()


def _converted_series(spec: CanonicalFieldSpec, series: pd.Series) -> pd.Series:
    if spec.kind == "date":
        return _normalize_date(series)
    if spec.kind == "numeric":
        return _normalize_numeric(series)
    if spec.kind == "currency":
        return _normalize_currency(series)
    if spec.kind == "tags":
        return _normalize_tags(series)
    return _normalize_string(series)


def _invalid_mask(
    spec: CanonicalFieldSpec,
    source_series: pd.Series,
    converted: pd.Series,
) -> pd.Series:
    source_present = source_series.notna()
    if spec.kind in {"string", "currency", "tags"}:
        return source_present & converted.isna()
    return source_present & converted.isna()


def _row_hashes(dataframe: pd.DataFrame, source_name: str) -> list[str]:
    try:
        raw_hashes = pd.util.hash_pandas_object(dataframe, index=False)
    except (TypeError, ValueError):
        return [
            hashlib.sha256(
                json.dumps(
                    [source_name, row_number, row.to_dict()],
                    default=str,
                    ensure_ascii=False,
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
            for row_number, (_, row) in enumerate(dataframe.iterrows(), start=1)
        ]
    return [
        hashlib.sha256(
            f"{source_name}|{row_number}|{int(raw_hash)}".encode()
        ).hexdigest()
        for row_number, raw_hash in enumerate(raw_hashes, start=1)
    ]


def normalize_billing_table(
    loaded_table: LoadedTable,
    mapping: Mapping[str, str | None],
    *,
    ingestion_id: str | None = None,
    issue_sample_limit: int = DEFAULT_ISSUE_SAMPLE_LIMIT,
) -> NormalizedTable:
    """Apply an accepted mapping without dropping rows or hiding conversions.

    Required-field mapping errors raise immediately. Invalid values remain as
    missing values in the output and are recorded in the normalization report so
    the next quality milestone can decide whether the run is analytically usable.
    """
    if issue_sample_limit <= 0:
        raise ValueError("issue_sample_limit must be greater than zero.")

    source = loaded_table.dataframe.reset_index(drop=True).copy(deep=True)
    source.columns = [str(column) for column in source.columns]
    accepted_mapping = validate_mapping(mapping, tuple(str(column) for column in source.columns))
    run_id = ingestion_id or uuid4().hex
    rows_in = len(source)
    output = pd.DataFrame(index=range(rows_in))
    issue_counts: Counter[str] = Counter()
    issue_rows: set[int] = set()
    issues: list[NormalizationIssue] = []

    for spec in CANONICAL_FIELD_SPECS:
        source_column = accepted_mapping[spec.name]
        if source_column is None:
            output[spec.name] = _empty_series(spec, rows_in)
            continue

        raw_series = source[source_column]
        converted = _converted_series(spec, raw_series)
        output[spec.name] = converted
        invalid = _invalid_mask(spec, raw_series, converted)
        invalid_positions = [int(position) for position in invalid[invalid].index]
        issue_counts[spec.name] += len(invalid_positions)
        issue_rows.update(invalid_positions)
        severity = "error" if spec.required else "warning"
        for position in invalid_positions[: max(0, issue_sample_limit - len(issues))]:
            issues.append(
                NormalizationIssue(
                    source_row_number=position + 1,
                    canonical_field=spec.name,
                    source_column=source_column,
                    severity=severity,
                    message=f"Could not normalize value as {spec.kind}.",
                    raw_value=_raw_value_text(raw_series.iloc[position]),
                )
            )

    output = output.assign(
        ingestion_id=pd.Series(run_id, index=range(rows_in)),
        source_file=pd.Series(loaded_table.source_name, index=range(rows_in)),
        source_row_number=pd.Series(range(1, rows_in + 1), dtype="Int64"),
        source_row_hash=pd.Series(_row_hashes(source, loaded_table.source_name)),
    )
    ordered_columns = [
        "ingestion_id",
        "source_file",
        "source_row_number",
        "source_row_hash",
        *(spec.name for spec in CANONICAL_FIELD_SPECS),
    ]
    output = output[ordered_columns]
    report = NormalizationReport(
        rows_in=rows_in,
        rows_out=len(output),
        rows_with_issues=len(issue_rows),
        issue_count=sum(issue_counts.values()),
        issue_counts_by_field=dict(issue_counts),
        issues=tuple(issues),
        issue_sample_limit=issue_sample_limit,
    )
    return NormalizedTable(
        dataframe=output,
        mapping=accepted_mapping,
        ingestion_id=run_id,
        source_name=loaded_table.source_name,
        report=report,
    )
