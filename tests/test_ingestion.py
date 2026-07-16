from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from finops_cost_intelligence.ingestion import (
    EmptyTableError,
    FileTooLargeError,
    SourceNotFoundError,
    UnsupportedFileTypeError,
    load_table,
    profile_table,
)


class ReaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = Path(__file__).parent / "fixtures" / "sample_billing.csv"

    def test_loads_csv_path_and_preserves_source_metadata(self) -> None:
        loaded = load_table(self.fixture_path)

        self.assertEqual(loaded.file_format, "csv")
        self.assertEqual(loaded.source_name, "sample_billing.csv")
        self.assertEqual(loaded.dataframe.shape, (5, 6))
        self.assertEqual(loaded.dataframe.loc[0, "service"], "Compute Engine")

    def test_loads_csv_file_like_object_with_explicit_name(self) -> None:
        payload = io.BytesIO(b"usage_date,service,cost\n2025-01-01,Storage,12.5\n")

        loaded = load_table(payload, source_name="upload.CSV")

        self.assertEqual(loaded.file_format, "csv")
        self.assertEqual(loaded.source_name, "upload.CSV")
        self.assertEqual(float(loaded.dataframe.loc[0, "cost"]), 12.5)

    def test_loads_xlsx_and_parquet_files(self) -> None:
        source = pd.DataFrame(
            {
                "usage_date": ["2025-01-01", "2025-01-02"],
                "service": ["Compute", "Storage"],
                "cost": [10.0, 20.0],
            }
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            xlsx_path = directory / "billing.xlsx"
            parquet_path = directory / "billing.parquet"
            source.to_excel(xlsx_path, index=False, sheet_name="Charges")
            source.to_parquet(parquet_path, index=False)

            xlsx_loaded = load_table(xlsx_path)
            parquet_loaded = load_table(parquet_path)

            self.assertEqual(xlsx_loaded.file_format, "xlsx")
            self.assertEqual(xlsx_loaded.sheet_name, "Charges")
            self.assertEqual(parquet_loaded.file_format, "parquet")
            pd.testing.assert_frame_equal(
                xlsx_loaded.dataframe.astype({"cost": "float64"}),
                source.astype({"cost": "float64"}),
            )
            pd.testing.assert_frame_equal(parquet_loaded.dataframe, source)

    def test_selects_first_nonempty_excel_worksheet(self) -> None:
        source = pd.DataFrame(
            {"usage_date": ["2025-01-01"], "service": ["Compute"], "cost": [10.0]}
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "multi_sheet.xlsx"
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                pd.DataFrame().to_excel(writer, index=False, sheet_name="Blank")
                source.to_excel(writer, index=False, sheet_name="Charges")

            loaded = load_table(path)

            self.assertEqual(loaded.sheet_name, "Charges")
            self.assertEqual(len(loaded.dataframe), 1)

    def test_rejects_unsupported_extension(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "billing.txt"
            path.write_text("not a supported table", encoding="utf-8")

            with self.assertRaises(UnsupportedFileTypeError):
                load_table(path)

    def test_rejects_missing_path(self) -> None:
        with self.assertRaises(SourceNotFoundError):
            load_table(Path("does-not-exist.csv"))

    def test_rejects_file_above_size_limit_before_parsing(self) -> None:
        payload = io.BytesIO(b"usage_date,service,cost\n2025-01-01,Storage,12.5\n")

        with self.assertRaises(FileTooLargeError):
            load_table(payload, source_name="billing.csv", max_bytes=5)

    def test_rejects_empty_table(self) -> None:
        payload = io.BytesIO(b"usage_date,service,cost\n")

        with self.assertRaises(EmptyTableError):
            load_table(payload, source_name="empty.csv")


class ProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = Path(__file__).parent / "fixtures" / "sample_billing.csv"

    def test_profile_contains_quality_signals_and_json_safe_samples(self) -> None:
        source = pd.DataFrame(
            {
                "usage_date": pd.to_datetime(
                    ["2025-01-01", "2025-01-02", "2025-01-02", None]
                ),
                "service": ["Compute", "Storage", "Storage", None],
                "cost": [10.0, 20.0, 20.0, None],
                "region": ["us-east-1", "us-west-2", "us-west-2", None],
            }
        )
        loaded = load_table(
            io.BytesIO(source.to_csv(index=False).encode("utf-8")),
            source_name="profile.csv",
        )
        original_columns = list(loaded.dataframe.columns)

        profile = profile_table(loaded)

        self.assertEqual(profile.profile_version, "1.0")
        self.assertEqual(profile.row_count, 4)
        self.assertEqual(profile.column_count, 4)
        self.assertEqual(profile.duplicate_row_count, 1)
        self.assertEqual(profile.all_null_row_count, 1)
        self.assertEqual(original_columns, list(loaded.dataframe.columns))
        self.assertEqual(profile.columns[0].inferred_type, "datetime-like")
        self.assertAlmostEqual(profile.columns[1].null_rate, 0.25)
        self.assertEqual(len(profile.sample_rows), 4)

        serialized = json.dumps(profile.to_dict())
        self.assertIn("profile.csv", serialized)
        self.assertIn("2025-01-01", serialized)

    def test_profile_rejects_non_positive_sample_limits(self) -> None:
        loaded = load_table(self.fixture_path)

        with self.assertRaises(ValueError):
            profile_table(loaded, sample_rows=0)
        with self.assertRaises(ValueError):
            profile_table(loaded, sample_values=0)


if __name__ == "__main__":
    unittest.main()
