"""High-signal quality checks for the canonical cost model."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..contracts.mapping import CANONICAL_FIELD_SPECS
from ..contracts.normalization import NormalizedTable
from ..contracts.quality import QualityCheckResult, QualityReport, ReconciliationResult
from ..ingestion.readers import LoadedTable
from ..normalization.billing import normalize_numeric_values

DEFAULT_RECONCILIATION_TOLERANCE = 0.01
DEFAULT_OPTIONAL_NULL_WARNING_RATE = 0.50


def _status_for_count(count: int, *, warning: bool = False) -> tuple[str, str]:
    if count == 0:
        return "pass", "info"
    return ("warning", "warning") if warning else ("error", "error")


def _check(
    check_name: str,
    status: str,
    severity: str,
    observed_value: Any,
    expected_value: Any,
    affected_rows: int,
    detail: str,
) -> QualityCheckResult:
    return QualityCheckResult(
        check_name=check_name,
        status=status,
        severity=severity,
        observed_value=observed_value,
        expected_value=expected_value,
        affected_rows=affected_rows,
        detail=detail,
    )


def _source_with_string_columns(loaded_table: LoadedTable) -> pd.DataFrame:
    source = loaded_table.dataframe.reset_index(drop=True).copy(deep=False)
    source.columns = [str(column) for column in source.columns]
    return source


def _cost_total(series: pd.Series) -> float | None:
    numeric = normalize_numeric_values(series)
    if numeric.notna().sum() == 0:
        return None
    return round(float(numeric.sum(skipna=True)), 10)


def _canonical_cost_total(normalized: NormalizedTable) -> float | None:
    series = normalized.dataframe["cost"]
    if series.notna().sum() == 0:
        return None
    return round(float(series.sum(skipna=True)), 10)


def _reconciliation(
    loaded_table: LoadedTable,
    normalized: NormalizedTable,
    tolerance: float,
) -> tuple[ReconciliationResult, QualityCheckResult]:
    source_column = normalized.mapping.get("cost")
    source = _source_with_string_columns(loaded_table)
    source_total = _cost_total(source[source_column]) if source_column else None
    canonical_total = _canonical_cost_total(normalized)

    if source_total is None or canonical_total is None:
        result = ReconciliationResult(
            source_total=source_total,
            canonical_total=canonical_total,
            absolute_difference=None,
            relative_difference=None,
            tolerance=tolerance,
            passed=False,
        )
        return result, _check(
            "source_to_canonical_reconciliation",
            "error",
            "error",
            "unavailable",
            f"numeric totals required; tolerance {tolerance}",
            normalized.report.rows_out,
            "A source and canonical cost total could not both be computed.",
        )

    absolute_difference = round(abs(source_total - canonical_total), 10)
    denominator = max(abs(source_total), tolerance)
    relative_difference = round(absolute_difference / denominator, 10)
    passed = absolute_difference <= tolerance
    result = ReconciliationResult(
        source_total=source_total,
        canonical_total=canonical_total,
        absolute_difference=absolute_difference,
        relative_difference=relative_difference,
        tolerance=tolerance,
        passed=passed,
    )
    return result, _check(
        "source_to_canonical_reconciliation",
        "pass" if passed else "error",
        "info" if passed else "error",
        absolute_difference,
        f"<= {tolerance}",
        0 if passed else normalized.report.rows_out,
        (
            f"Source total {source_total:.2f}; canonical total {canonical_total:.2f}; "
            f"absolute difference {absolute_difference:.2f}."
        ),
    )


def _required_completeness(normalized: NormalizedTable) -> list[QualityCheckResult]:
    checks: list[QualityCheckResult] = []
    for spec in CANONICAL_FIELD_SPECS:
        if not spec.required:
            continue
        series = normalized.dataframe[spec.name]
        missing = int(series.isna().sum())
        status, severity = _status_for_count(missing)
        checks.append(
            _check(
                f"required_field_completeness:{spec.name}",
                status,
                severity,
                missing,
                0,
                missing,
                f"{missing:,} row(s) are missing the required {spec.label.lower()}.",
            )
        )
    return checks


def _optional_completeness(
    normalized: NormalizedTable,
    warning_rate: float,
) -> list[QualityCheckResult]:
    checks: list[QualityCheckResult] = []
    row_count = max(len(normalized.dataframe), 1)
    for spec in CANONICAL_FIELD_SPECS:
        if spec.required:
            continue
        source_column = normalized.mapping.get(spec.name)
        if source_column is None:
            checks.append(
                _check(
                    f"optional_field_mapping:{spec.name}",
                    "pass",
                    "info",
                    "not mapped",
                    "optional",
                    0,
                    f"{spec.label} is not mapped; related analysis will be unavailable.",
                )
            )
            continue
        missing = int(normalized.dataframe[spec.name].isna().sum())
        null_rate = missing / row_count
        warning = null_rate > warning_rate
        checks.append(
            _check(
                f"optional_field_completeness:{spec.name}",
                "warning" if warning else "pass",
                "warning" if warning else "info",
                round(null_rate, 4),
                f"<= {warning_rate:.0%}",
                missing,
                f"{spec.label} has {null_rate:.1%} missing values after normalization.",
            )
        )
    return checks


def _currency_consistency(normalized: NormalizedTable) -> QualityCheckResult:
    values = normalized.dataframe["currency"].dropna().astype("string").str.strip()
    currencies = sorted({str(value) for value in values if str(value)})
    if not currencies:
        return _check(
            "currency_consistency",
            "warning",
            "warning",
            "not available",
            "one currency or an explicit conversion policy",
            len(normalized.dataframe),
            (
                "Currency is not mapped or populated; financial comparability "
                "needs an explicit assumption."
            ),
        )
    if len(currencies) > 1:
        return _check(
            "currency_consistency",
            "error",
            "error",
            currencies,
            "one currency or an explicit conversion policy",
            len(normalized.dataframe),
            "Multiple currencies are present without a conversion policy.",
        )
    return _check(
        "currency_consistency",
        "pass",
        "info",
        currencies[0],
        currencies[0],
        0,
        f"All populated cost rows use {currencies[0]}.",
    )


def _duplicate_check(normalized: NormalizedTable) -> QualityCheckResult:
    canonical_columns = [spec.name for spec in CANONICAL_FIELD_SPECS]
    duplicate_rows = int(normalized.dataframe.duplicated(subset=canonical_columns).sum())
    status, severity = _status_for_count(duplicate_rows, warning=True)
    return _check(
        "exact_duplicate_canonical_rows",
        status,
        severity,
        duplicate_rows,
        0,
        duplicate_rows,
        (
            f"{duplicate_rows:,} duplicate canonical row(s) found. "
            "Duplicates may be valid credits or repeated exports and require review."
            if duplicate_rows
            else "No exact duplicate canonical rows found."
        ),
    )


def _negative_cost_check(normalized: NormalizedTable) -> QualityCheckResult:
    negative_rows = int((normalized.dataframe["cost"] < 0).fillna(False).sum())
    status, severity = _status_for_count(negative_rows, warning=True)
    return _check(
        "negative_cost_values",
        status,
        severity,
        negative_rows,
        0,
        negative_rows,
        (
            (
                f"{negative_rows:,} negative cost row(s) found; these may be "
                "credits, refunds, or corrections."
            )
            if negative_rows
            else "No negative cost values found."
        ),
    )


def _normalization_issue_check(normalized: NormalizedTable) -> QualityCheckResult:
    required_names = {spec.name for spec in CANONICAL_FIELD_SPECS if spec.required}
    required_issue_count = sum(
        count
        for field, count in normalized.report.issue_counts_by_field.items()
        if field in required_names
    )
    optional_issue_count = normalized.report.issue_count - required_issue_count
    if required_issue_count:
        return _check(
            "normalization_conversion_errors",
            "error",
            "error",
            required_issue_count,
            0,
            normalized.report.rows_with_issues,
            "Required fields contain values that could not be normalized.",
        )
    if optional_issue_count:
        return _check(
            "normalization_conversion_errors",
            "warning",
            "warning",
            optional_issue_count,
            0,
            normalized.report.rows_with_issues,
            "Optional fields contain values that could not be normalized.",
        )
    return _check(
        "normalization_conversion_errors",
        "pass",
        "info",
        0,
        0,
        0,
        "All mapped values were normalized successfully.",
    )


def run_quality_checks(
    loaded_table: LoadedTable,
    normalized: NormalizedTable,
    *,
    reconciliation_tolerance: float = DEFAULT_RECONCILIATION_TOLERANCE,
    optional_null_warning_rate: float = DEFAULT_OPTIONAL_NULL_WARNING_RATE,
) -> QualityReport:
    """Run deterministic checks and return a downstream analysis decision."""
    if reconciliation_tolerance < 0:
        raise ValueError("reconciliation_tolerance cannot be negative.")
    if not 0 <= optional_null_warning_rate <= 1:
        raise ValueError("optional_null_warning_rate must be between zero and one.")

    reconciliation, reconciliation_check = _reconciliation(
        loaded_table,
        normalized,
        reconciliation_tolerance,
    )
    rows_preserved = normalized.report.rows_in == normalized.report.rows_out
    checks: list[QualityCheckResult] = [
        _check(
            "row_count_preservation",
            "pass" if rows_preserved else "error",
            "info" if rows_preserved else "error",
            normalized.report.rows_out,
            normalized.report.rows_in,
            abs(normalized.report.rows_in - normalized.report.rows_out),
            "No rows were dropped during normalization."
            if rows_preserved
            else "Row count changed during normalization.",
        ),
        reconciliation_check,
        _normalization_issue_check(normalized),
        *_required_completeness(normalized),
        *_optional_completeness(normalized, optional_null_warning_rate),
        _currency_consistency(normalized),
        _duplicate_check(normalized),
        _negative_cost_check(normalized),
    ]
    statuses = {check.status for check in checks}
    overall_status = (
        "error"
        if "error" in statuses
        else "warning"
        if "warning" in statuses
        else "pass"
    )
    return QualityReport(
        ingestion_id=normalized.ingestion_id,
        source_name=normalized.source_name,
        rows_in=normalized.report.rows_in,
        rows_out=normalized.report.rows_out,
        overall_status=overall_status,
        ready_for_analysis=overall_status != "error",
        reconciliation=reconciliation,
        checks=tuple(checks),
    )
