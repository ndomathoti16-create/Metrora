from __future__ import annotations

import unittest

import pandas as pd

from finops_cost_intelligence.contracts.mapping import CANONICAL_FIELD_NAMES
from finops_cost_intelligence.ingestion import load_table, profile_table
from finops_cost_intelligence.ingestion.readers import LoadedTable
from finops_cost_intelligence.mapping import (
    MappingValidationError,
    suggest_mappings,
    validate_mapping,
)
from finops_cost_intelligence.normalization import normalize_billing_table


class MappingDetectorTests(unittest.TestCase):
    def test_detector_finds_required_and_common_optional_fields(self) -> None:
        fixture_path = "tests/fixtures/sample_billing.csv"
        loaded = load_table(fixture_path)
        review = suggest_mappings(profile_table(loaded))
        suggested = review.suggested_mapping()

        self.assertEqual(suggested["usage_date"], "usage_date")
        self.assertEqual(suggested["service"], "service")
        self.assertEqual(suggested["cost"], "cost")
        self.assertEqual(suggested["account_id"], "account")
        self.assertEqual(suggested["region"], "region")
        self.assertEqual(suggested["environment"], "environment")
        self.assertEqual(len([value for value in suggested.values() if value]), 6)

        cost_suggestion = review.suggestion_for("cost")
        self.assertEqual(cost_suggestion.confidence, "high")
        self.assertIn("numeric parse rate", cost_suggestion.reason)

    def test_detector_does_not_assign_one_source_column_twice(self) -> None:
        source = pd.DataFrame(
            {
                "date": ["2025-01-01"],
                "service": ["Compute"],
                "cost": [10.0],
            }
        )
        loaded = LoadedTable(source, "simple.csv", "csv", None)
        review = suggest_mappings(profile_table(loaded))
        selected = [value for value in review.suggested_mapping().values() if value]

        self.assertEqual(len(selected), len(set(selected)))

    def test_numeric_account_identifier_keeps_its_semantic_mapping(self) -> None:
        source = pd.DataFrame(
            {
                "UsageDate": ["2026-01-01"],
                "Service": ["Compute"],
                "Cost": [10.0],
                "AccountNumber": [123456789],
            }
        )
        loaded = LoadedTable(source, "numeric-account.csv", "csv", None)

        mapping = suggest_mappings(profile_table(loaded)).suggested_mapping()

        self.assertEqual(mapping["account_id"], "AccountNumber")

    def test_focus_1_3_export_maps_to_the_trend_cost_model(self) -> None:
        source = pd.DataFrame(
            {
                "ChargePeriodStart": ["2026-01-01", "2026-01-02"],
                "ServiceName": ["Compute", "Storage"],
                "ServiceProviderName": ["Example Cloud", "Example Cloud"],
                "BilledCost": [110.0, 55.0],
                "EffectiveCost": [100.0, 50.0],
                "BillingCurrency": ["USD", "USD"],
                "BillingAccountId": ["billing-001", "billing-001"],
                "BillingAccountName": ["Corporate", "Corporate"],
                "RegionName": ["us-east", "us-east"],
                "ResourceId": ["vm-001", "bucket-001"],
                "ResourceName": ["api", "archive"],
                "ConsumedQuantity": [20.0, 500.0],
                "ConsumedUnit": ["Hours", "GB-Month"],
                "ChargeCategory": ["Usage", "Usage"],
                "Tags": ['{"environment":"prod"}', '{"environment":"prod"}'],
            }
        )
        loaded = LoadedTable(source, "focus-1.3.csv", "csv", None)

        review = suggest_mappings(profile_table(loaded))
        mapping = review.suggested_mapping()

        self.assertEqual(mapping["usage_date"], "ChargePeriodStart")
        self.assertEqual(mapping["service"], "ServiceName")
        self.assertEqual(mapping["provider"], "ServiceProviderName")
        self.assertEqual(mapping["cost"], "EffectiveCost")
        self.assertEqual(mapping["currency"], "BillingCurrency")
        self.assertEqual(mapping["account_id"], "BillingAccountId")
        self.assertEqual(mapping["region"], "RegionName")
        self.assertEqual(mapping["usage_quantity"], "ConsumedQuantity")
        self.assertEqual(mapping["usage_unit"], "ConsumedUnit")
        self.assertEqual(mapping["cost_type"], "ChargeCategory")
        self.assertIsNone(mapping["department"])
        self.assertIsNone(mapping["usage_type"])

        normalized = normalize_billing_table(loaded, mapping, ingestion_id="focus-1.3")

        self.assertEqual(normalized.report.issue_count, 0)
        self.assertEqual(float(normalized.dataframe["cost"].sum()), 150.0)
        self.assertEqual(set(normalized.dataframe["currency"]), {"USD"})
        self.assertEqual(set(normalized.dataframe["provider"]), {"Example Cloud"})


class MappingValidationTests(unittest.TestCase):
    def test_validation_returns_a_complete_mapping(self) -> None:
        mapping = validate_mapping(
            {"usage_date": "date", "service": "product", "cost": "amount"},
            ["date", "product", "amount", "region"],
        )

        self.assertEqual(mapping["usage_date"], "date")
        self.assertEqual(mapping["service"], "product")
        self.assertEqual(mapping["cost"], "amount")
        self.assertIsNone(mapping["region"])
        self.assertEqual(set(mapping), set(CANONICAL_FIELD_NAMES))

    def test_validation_rejects_missing_required_and_duplicate_source_columns(self) -> None:
        with self.assertRaises(MappingValidationError) as context:
            validate_mapping(
                {"usage_date": "date", "service": "date", "cost": None},
                ["date", "amount"],
            )

        message = str(context.exception)
        self.assertIn("mapped more than once", message)
        self.assertIn("Required field 'cost' is not mapped", message)

    def test_validation_rejects_unknown_source_columns(self) -> None:
        with self.assertRaisesRegex(MappingValidationError, "missing source column"):
            validate_mapping(
                {"usage_date": "missing_date", "service": "service", "cost": "cost"},
                ["service", "cost"],
            )


class NormalizationTests(unittest.TestCase):
    def test_normalizes_financial_values_and_preserves_invalid_rows(self) -> None:
        source = pd.DataFrame(
            {
                "Date": ["2025-01-01", "not-a-date", "2025-01-03"],
                "ProductName": ["Compute", "Storage", "Database"],
                "UnblendedCost": ["$1,234.50", "bad-cost", "(5.00)"],
                "AccountNumber": ["001", "002", "003"],
                "AWSRegion": ["us-east-1", "us-east-1", "us-west-2"],
                "Dept": ["Finance", "Engineering", "Engineering"],
                "ProjectName": ["Forecast", "Portal", "Portal"],
                "Env": ["prod", "prod", "staging"],
                "Usage": [1000, 2000, 50],
                "Unit": ["hours", "hours", "hours"],
                "Currency": ["usd", "USD", "usd"],
            }
        )
        loaded = LoadedTable(source, "mixed_billing.csv", "csv", None)
        mapping = {
            "usage_date": "Date",
            "service": "ProductName",
            "cost": "UnblendedCost",
            "account_id": "AccountNumber",
            "region": "AWSRegion",
            "department": "Dept",
            "project": "ProjectName",
            "environment": "Env",
            "usage_quantity": "Usage",
            "usage_unit": "Unit",
            "currency": "Currency",
        }

        normalized = normalize_billing_table(
            loaded,
            mapping,
            ingestion_id="test-run-001",
        )

        self.assertEqual(normalized.ingestion_id, "test-run-001")
        self.assertEqual(normalized.report.rows_in, 3)
        self.assertEqual(normalized.report.rows_out, 3)
        self.assertEqual(normalized.report.issue_count, 2)
        self.assertEqual(normalized.report.rows_with_issues, 1)
        self.assertEqual(float(normalized.dataframe.loc[0, "cost"]), 1234.50)
        self.assertEqual(float(normalized.dataframe.loc[2, "cost"]), -5.0)
        self.assertTrue(pd.isna(normalized.dataframe.loc[1, "cost"]))
        self.assertTrue(pd.isna(normalized.dataframe.loc[1, "usage_date"]))
        self.assertEqual(normalized.dataframe.loc[0, "currency"], "USD")
        self.assertEqual(
            list(normalized.dataframe["source_row_number"]),
            [1, 2, 3],
        )
        self.assertEqual(normalized.dataframe["source_row_hash"].nunique(), 3)
        self.assertEqual(
            list(normalized.dataframe.columns[:4]),
            ["ingestion_id", "source_file", "source_row_number", "source_row_hash"],
        )
        self.assertEqual(list(source.columns), list(loaded.dataframe.columns))

        issue_fields = {issue.canonical_field for issue in normalized.report.issues}
        self.assertEqual(issue_fields, {"usage_date", "cost"})

    def test_unmapped_optional_fields_are_present_and_tag_objects_are_serialized(self) -> None:
        source = pd.DataFrame(
            {
                "Date": ["2025-01-01", "2025-01-02"],
                "Service": ["Compute", "Storage"],
                "Amount": [10, 20],
                "Tags": [{"environment": "prod"}, {"environment": "dev"}],
            }
        )
        loaded = LoadedTable(source, "tagged.csv", "csv", None)
        normalized = normalize_billing_table(
            loaded,
            {
                "usage_date": "Date",
                "service": "Service",
                "cost": "Amount",
                "tags_json": "Tags",
            },
            ingestion_id="tag-run",
        )

        self.assertEqual(normalized.report.issue_count, 0)
        self.assertEqual(normalized.dataframe.loc[0, "tags_json"], '{"environment": "prod"}')
        self.assertTrue(normalized.dataframe["region"].isna().all())
        self.assertEqual(normalized.dataframe["source_row_hash"].nunique(), 2)

    def test_issue_sample_limit_does_not_change_row_count(self) -> None:
        source = pd.DataFrame(
            {
                "Date": ["bad-1", "bad-2", "bad-3"],
                "Service": ["Compute", "Compute", "Compute"],
                "Amount": ["bad-1", "bad-2", "bad-3"],
            }
        )
        loaded = LoadedTable(source, "invalid.csv", "csv", None)

        normalized = normalize_billing_table(
            loaded,
            {"usage_date": "Date", "service": "Service", "cost": "Amount"},
            issue_sample_limit=1,
        )

        self.assertEqual(normalized.report.rows_in, 3)
        self.assertEqual(normalized.report.rows_out, 3)
        self.assertEqual(normalized.report.issue_count, 6)
        self.assertEqual(len(normalized.report.issues), 1)


if __name__ == "__main__":
    unittest.main()
