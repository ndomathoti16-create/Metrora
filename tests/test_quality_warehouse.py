from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from finops_cost_intelligence.contracts.quality import QualityReport
from finops_cost_intelligence.ingestion.readers import LoadedTable
from finops_cost_intelligence.normalization import normalize_billing_table
from finops_cost_intelligence.quality import run_quality_checks
from finops_cost_intelligence.warehouse import DuckDBStore


def _loaded_table(dataframe: pd.DataFrame, source_name: str = "billing.csv") -> LoadedTable:
    return LoadedTable(
        dataframe=dataframe,
        source_name=source_name,
        file_format="csv",
        source_size_bytes=None,
    )


def _normalize(
    dataframe: pd.DataFrame,
    *,
    ingestion_id: str = "quality-run",
) -> tuple[LoadedTable, object]:
    loaded = _loaded_table(dataframe)
    normalized = normalize_billing_table(
        loaded,
        {
            "usage_date": "Date",
            "service": "Service",
            "cost": "Amount",
            "currency": "Currency",
            "region": "Region",
        },
        ingestion_id=ingestion_id,
    )
    return loaded, normalized


class QualityCheckTests(unittest.TestCase):
    def test_valid_run_passes_and_reconciles(self) -> None:
        loaded, normalized = _normalize(
            pd.DataFrame(
                {
                    "Date": ["2025-01-01", "2025-01-02"],
                    "Service": ["Compute", "Storage"],
                    "Amount": ["10.00", "20.00"],
                    "Currency": ["USD", "USD"],
                    "Region": ["us-east-1", "us-east-1"],
                }
            )
        )

        report = run_quality_checks(loaded, normalized)

        self.assertIsInstance(report, QualityReport)
        self.assertEqual(report.overall_status, "pass")
        self.assertTrue(report.ready_for_analysis)
        self.assertEqual(report.reconciliation.source_total, 30.0)
        self.assertEqual(report.reconciliation.canonical_total, 30.0)
        self.assertEqual(report.reconciliation.absolute_difference, 0.0)
        self.assertTrue(report.reconciliation.passed)
        json.dumps(report.to_dict())

    def test_invalid_required_values_block_analysis(self) -> None:
        loaded, normalized = _normalize(
            pd.DataFrame(
                {
                    "Date": ["not-a-date", "2025-01-02"],
                    "Service": [None, "Storage"],
                    "Amount": ["bad-cost", "20.00"],
                    "Currency": ["USD", "USD"],
                    "Region": ["us-east-1", "us-east-1"],
                }
            )
        )

        report = run_quality_checks(loaded, normalized)
        check_statuses = {check.check_name: check.status for check in report.checks}

        self.assertEqual(report.overall_status, "error")
        self.assertFalse(report.ready_for_analysis)
        self.assertEqual(check_statuses["normalization_conversion_errors"], "error")
        self.assertEqual(check_statuses["required_field_completeness:usage_date"], "error")
        self.assertEqual(check_statuses["required_field_completeness:service"], "error")
        self.assertEqual(check_statuses["required_field_completeness:cost"], "error")

    def test_duplicates_and_negative_costs_are_warnings(self) -> None:
        loaded, normalized = _normalize(
            pd.DataFrame(
                {
                    "Date": ["2025-01-01", "2025-01-01", "2025-01-02"],
                    "Service": ["Compute", "Compute", "Storage"],
                    "Amount": ["10.00", "10.00", "-2.00"],
                    "Currency": ["USD", "USD", "USD"],
                    "Region": ["us-east-1", "us-east-1", "us-east-1"],
                }
            )
        )

        report = run_quality_checks(loaded, normalized)
        check_statuses = {check.check_name: check.status for check in report.checks}

        self.assertEqual(report.overall_status, "warning")
        self.assertTrue(report.ready_for_analysis)
        self.assertEqual(check_statuses["exact_duplicate_canonical_rows"], "warning")
        self.assertEqual(check_statuses["negative_cost_values"], "warning")

    def test_mixed_currencies_block_analysis(self) -> None:
        loaded, normalized = _normalize(
            pd.DataFrame(
                {
                    "Date": ["2025-01-01", "2025-01-02"],
                    "Service": ["Compute", "Storage"],
                    "Amount": ["10.00", "20.00"],
                    "Currency": ["USD", "EUR"],
                    "Region": ["us-east-1", "us-east-1"],
                }
            )
        )

        report = run_quality_checks(loaded, normalized)
        currency_check = next(
            check for check in report.checks if check.check_name == "currency_consistency"
        )

        self.assertEqual(currency_check.status, "error")
        self.assertFalse(report.ready_for_analysis)

    def test_quality_configuration_is_validated(self) -> None:
        loaded, normalized = _normalize(
            pd.DataFrame(
                {
                    "Date": ["2025-01-01"],
                    "Service": ["Compute"],
                    "Amount": ["10.00"],
                    "Currency": ["USD"],
                    "Region": ["us-east-1"],
                }
            )
        )

        with self.assertRaises(ValueError):
            run_quality_checks(loaded, normalized, reconciliation_tolerance=-1)
        with self.assertRaises(ValueError):
            run_quality_checks(loaded, normalized, optional_null_warning_rate=2)


class DuckDBStoreTests(unittest.TestCase):
    def test_save_is_idempotent_for_the_same_ingestion_id(self) -> None:
        data = pd.DataFrame(
            {
                "Date": ["2025-01-01", "2025-01-02"],
                "Service": ["Compute", "Storage"],
                "Amount": ["10.00", "20.00"],
                "Currency": ["USD", "USD"],
                "Region": ["us-east-1", "us-east-1"],
            }
        )
        loaded, normalized = _normalize(data, ingestion_id="run-001")
        report = run_quality_checks(loaded, normalized)

        with tempfile.TemporaryDirectory() as temporary_directory:
            store = DuckDBStore(Path(temporary_directory) / "finops.duckdb")
            store.save_run(loaded, normalized, report)
            store.save_run(loaded, normalized, report)

            summary = store.get_run_summary("run-001")
            self.assertIsNotNone(summary)
            self.assertEqual(summary["cost_rows"], 2)
            self.assertEqual(summary["quality_checks"], len(report.checks))
            self.assertEqual(store.count_cost_rows("run-001"), 2)
            self.assertEqual(store.count_cost_rows(), 2)

    def test_multiple_runs_are_kept_separate(self) -> None:
        data = pd.DataFrame(
            {
                "Date": ["2025-01-01"],
                "Service": ["Compute"],
                "Amount": ["10.00"],
                "Currency": ["USD"],
                "Region": ["us-east-1"],
            }
        )
        loaded_one, normalized_one = _normalize(data, ingestion_id="run-001")
        loaded_two, normalized_two = _normalize(data, ingestion_id="run-002")

        with tempfile.TemporaryDirectory() as temporary_directory:
            store = DuckDBStore(Path(temporary_directory) / "finops.duckdb")
            store.save_run(
                loaded_one,
                normalized_one,
                run_quality_checks(loaded_one, normalized_one),
            )
            store.save_run(
                loaded_two,
                normalized_two,
                run_quality_checks(loaded_two, normalized_two),
            )

            self.assertEqual(store.count_cost_rows("run-001"), 1)
            self.assertEqual(store.count_cost_rows("run-002"), 1)
            self.assertEqual(store.count_cost_rows(), 2)


if __name__ == "__main__":
    unittest.main()
