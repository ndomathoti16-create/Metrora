"""Read-only Google Cloud Billing export ingestion from BigQuery."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

import pandas as pd

from ..ingestion.readers import LoadedTable
from .contracts import (
    DEFAULT_CLOUD_IMPORT_LIMIT_BYTES,
    CloudConnectionError,
    CloudDependencyError,
    CloudSyncResult,
    enforce_size_limit,
    utc_now,
)

_PROJECT_PATTERN = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")
_DATASET_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,1023}$")
_TABLE_PATTERN = re.compile(r"^[A-Za-z0-9_]+\*?$")


@dataclass(frozen=True)
class GcpBigQueryExportConfig:
    """Non-secret configuration for a standard Google Cloud Billing export."""

    project_id: str
    dataset: str
    table: str = "gcp_billing_export_v1_*"
    lookback_days: int = 120

    def __post_init__(self) -> None:
        if not _PROJECT_PATTERN.fullmatch(self.project_id.strip()):
            raise ValueError("Enter a valid Google Cloud project ID.")
        if not _DATASET_PATTERN.fullmatch(self.dataset.strip()):
            raise ValueError("Enter a valid BigQuery dataset name.")
        if not _TABLE_PATTERN.fullmatch(self.table.strip()):
            raise ValueError("Enter a valid billing export table name or suffix wildcard.")
        if not 7 <= int(self.lookback_days) <= 366:
            raise ValueError("Google Cloud lookback must be between 7 and 366 days.")


class GcpBigQueryBillingConnector:
    """Query a standard GCP billing export through Application Default Credentials."""

    provider = "Google Cloud"

    def __init__(
        self,
        config: GcpBigQueryExportConfig,
        *,
        client=None,
        max_bytes: int | None = DEFAULT_CLOUD_IMPORT_LIMIT_BYTES,
    ) -> None:
        self.config = config
        self._client = client
        self.max_bytes = max_bytes or DEFAULT_CLOUD_IMPORT_LIMIT_BYTES
        enforce_size_limit(0, self.max_bytes, label="Google Cloud billing result")

    @property
    def client(self):
        if self._client is None:
            try:
                from google.cloud import bigquery
            except ImportError as exc:
                raise CloudDependencyError(
                    'Google Cloud connections require the cloud extras. Install with "pip '
                    'install -e .[cloud]" or use the packaged Metrora desktop release.'
                ) from exc
            self._client = bigquery.Client(project=self.config.project_id.strip())
        return self._client

    def _query_text(self) -> str:
        table_ref = (
            f"{self.config.project_id.strip()}."
            f"{self.config.dataset.strip()}.{self.config.table.strip()}"
        )
        # Every interpolated identifier is allow-list validated in the config model and the
        # lookback is converted to a bounded integer before this read-only query is built.
        return f"""
            SELECT
              usage_start_time AS UsageStartDate,
              service.description AS ProductName,
              cost + IFNULL((SELECT SUM(credit.amount) FROM UNNEST(credits) credit), 0)
                AS EffectiveCost,
              currency AS Currency,
              'GCP' AS Provider,
              billing_account_id AS AccountId,
              project.id AS ProjectId,
              project.name AS ProjectName,
              location.region AS Region,
              usage.amount AS UsageQuantity,
              usage.unit AS UsageUnit,
              cost_type AS CostType,
              TO_JSON_STRING(labels) AS Labels
            FROM `{table_ref}`
            WHERE DATE(usage_start_time) >= DATE_SUB(
              CURRENT_DATE(), INTERVAL {int(self.config.lookback_days)} DAY
            )
        """  # nosec B608

    def sync_latest(self) -> CloudSyncResult:
        """Query the configured export and return its calculated net-cost rows."""
        try:
            query_job = self.client.query(self._query_text())
            result = query_job.result(page_size=1000)
            records: list[dict[str, object]] = []
            observed_bytes = 0
            for row in result:
                record = dict(row.items()) if hasattr(row, "items") else dict(row)
                observed_bytes += len(
                    json.dumps(record, default=str, ensure_ascii=False).encode("utf-8")
                )
                enforce_size_limit(
                    observed_bytes,
                    self.max_bytes,
                    label="Google Cloud billing result",
                )
                records.append(record)
            dataframe = pd.DataFrame.from_records(records)
        except (CloudConnectionError, CloudDependencyError):
            raise
        except Exception as exc:
            raise CloudConnectionError(
                "Google Cloud could not query this billing export. Run gcloud auth "
                "application-default login or use a workload identity with BigQuery Job "
                "User and Data Viewer access."
            ) from exc
        if dataframe.empty:
            raise CloudConnectionError(
                "The Google Cloud billing export returned no rows for the selected lookback."
            )

        dataframe_bytes = int(dataframe.memory_usage(index=True, deep=True).sum())
        enforce_size_limit(
            dataframe_bytes,
            self.max_bytes,
            label="Google Cloud billing table in memory",
        )

        source_uri = (
            f"bigquery://{self.config.project_id.strip()}/"
            f"{self.config.dataset.strip()}/{self.config.table.strip()}"
        )
        loaded = LoadedTable(
            dataframe=dataframe,
            source_name=source_uri,
            file_format="bigquery",
            source_size_bytes=dataframe_bytes,
        )
        timestamp = utc_now()
        return CloudSyncResult(
            provider=self.provider,
            source_uri=source_uri,
            loaded_table=loaded,
            object_count=1,
            total_bytes=loaded.source_size_bytes or 0,
            latest_modified=timestamp,
            synced_at=timestamp,
        )
