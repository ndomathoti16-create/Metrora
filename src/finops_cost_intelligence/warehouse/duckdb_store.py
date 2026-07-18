"""DuckDB persistence with idempotent ingestion-run replacement."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb

from ..contracts.normalization import NormalizedTable
from ..contracts.quality import QualityReport
from ..ingestion.readers import LoadedTable


class WarehouseError(RuntimeError):
    """Raised when a local warehouse operation cannot be completed."""


def _json_text(value: Any) -> str:
    return json.dumps(value, default=str, ensure_ascii=False, sort_keys=True)


def _schema_sql() -> str:
    schema_path = Path(__file__).with_name("schema.sql")
    try:
        return schema_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise WarehouseError(f"Could not read DuckDB schema: {schema_path}") from exc


class DuckDBStore:
    """Small local warehouse adapter used by the Streamlit workflow."""

    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path).expanduser().resolve()

    def initialize(self) -> None:
        """Create the local schema if it does not already exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with duckdb.connect(str(self.db_path)) as connection:
                connection.execute(_schema_sql())
        except duckdb.Error as exc:
            raise WarehouseError(f"Could not initialize DuckDB at {self.db_path}.") from exc

    def save_run(
        self,
        loaded_table: LoadedTable,
        normalized: NormalizedTable,
        quality_report: QualityReport,
    ) -> None:
        """Persist one run and replace any previous run with the same ID."""
        if normalized.ingestion_id != quality_report.ingestion_id:
            raise WarehouseError("Normalized table and quality report use different ingestion IDs.")

        self.initialize()
        run_id = normalized.ingestion_id
        quality_rows = [
            (
                run_id,
                check.check_name,
                check.status,
                check.severity,
                _json_text(check.observed_value),
                _json_text(check.expected_value),
                check.affected_rows,
                check.detail,
            )
            for check in quality_report.checks
        ]
        run_values = (
            run_id,
            loaded_table.source_name,
            loaded_table.file_format,
            loaded_table.source_size_bytes,
            normalized.report.rows_in,
            normalized.report.rows_out,
            quality_report.ready_for_analysis,
            quality_report.overall_status,
            _json_text(normalized.mapping),
            _json_text(quality_report.to_dict()),
            datetime.now(UTC),
        )
        try:
            with duckdb.connect(str(self.db_path)) as connection:
                connection.begin()
                connection.execute(
                    "DELETE FROM quality_check_result WHERE ingestion_id = ?",
                    [run_id],
                )
                connection.execute(
                    "DELETE FROM fact_cloud_cost WHERE ingestion_id = ?",
                    [run_id],
                )
                connection.execute(
                    "DELETE FROM ingestion_run WHERE ingestion_id = ?",
                    [run_id],
                )
                connection.register("normalized_input", normalized.dataframe)
                connection.execute(
                    """
                    INSERT INTO fact_cloud_cost
                    SELECT
                        ingestion_id,
                        source_file,
                        source_row_number,
                        source_row_hash,
                        usage_date,
                        service,
                        cost,
                        currency,
                        provider,
                        account_id,
                        account_name,
                        region,
                        department,
                        project,
                        environment,
                        resource_id,
                        resource_name,
                        usage_quantity,
                        usage_unit,
                        usage_type,
                        cost_type,
                        tags_json
                    FROM normalized_input
                    """
                )
                connection.unregister("normalized_input")
                connection.execute(
                    """
                    INSERT INTO ingestion_run (
                        ingestion_id,
                        source_name,
                        file_format,
                        source_size_bytes,
                        rows_in,
                        rows_out,
                        ready_for_analysis,
                        overall_status,
                        mapping_json,
                        quality_report_json,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    run_values,
                )
                connection.executemany(
                    """
                    INSERT INTO quality_check_result (
                        ingestion_id,
                        check_name,
                        status,
                        severity,
                        observed_value,
                        expected_value,
                        affected_rows,
                        detail
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    quality_rows,
                )
                connection.commit()
        except duckdb.Error as exc:
            raise WarehouseError(f"Could not persist ingestion run {run_id!r}.") from exc

    def get_run_summary(self, ingestion_id: str) -> dict[str, Any] | None:
        """Return persisted metadata for one run, if it exists."""
        self.initialize()
        try:
            with duckdb.connect(str(self.db_path), read_only=True) as connection:
                result = connection.execute(
                    """
                    SELECT
                        ingestion_id,
                        source_name,
                        file_format,
                        rows_in,
                        rows_out,
                        ready_for_analysis,
                        overall_status,
                        created_at,
                        (SELECT COUNT(*) FROM fact_cloud_cost WHERE ingestion_id = ?) AS cost_rows,
                        (
                            SELECT COUNT(*)
                            FROM quality_check_result
                            WHERE ingestion_id = ?
                        ) AS quality_checks
                    FROM ingestion_run
                    WHERE ingestion_id = ?
                    """,
                    [ingestion_id, ingestion_id, ingestion_id],
                )
                row = result.fetchone()
                if row is None:
                    return None
                return dict(zip([column[0] for column in result.description], row))
        except duckdb.Error as exc:
            raise WarehouseError(f"Could not read ingestion run {ingestion_id!r}.") from exc

    def count_cost_rows(self, ingestion_id: str | None = None) -> int:
        """Count stored canonical cost rows, optionally for one run."""
        self.initialize()
        try:
            with duckdb.connect(str(self.db_path), read_only=True) as connection:
                if ingestion_id is None:
                    row = connection.execute("SELECT COUNT(*) FROM fact_cloud_cost").fetchone()
                else:
                    row = connection.execute(
                        "SELECT COUNT(*) FROM fact_cloud_cost WHERE ingestion_id = ?",
                        [ingestion_id],
                    ).fetchone()
                return int(row[0]) if row else 0
        except duckdb.Error as exc:
            raise WarehouseError("Could not count stored cost rows.") from exc
