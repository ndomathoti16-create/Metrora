"""Athena adapter for querying standardized Parquet data in S3."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import boto3
import pandas as pd
from botocore.exceptions import BotoCoreError, ClientError

from ..contracts.aws import AthenaQueryResult


class AthenaQueryError(RuntimeError):
    """Raised when an Athena query fails, times out, or returns malformed data."""


def _cell_value(cell: dict[str, Any]) -> object:
    return cell.get("VarCharValue")


class AthenaWarehouse:
    """Run bounded Athena queries and convert results to DataFrames."""

    def __init__(
        self,
        database: str,
        output_location: str,
        *,
        region: str = "us-east-1",
        client: Any | None = None,
        timeout_seconds: int = 120,
        poll_interval_seconds: float = 1.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not database.strip():
            raise AthenaQueryError("An Athena database is required.")
        if not output_location.strip().startswith("s3://"):
            raise AthenaQueryError("Athena output_location must be an s3:// URI.")
        if timeout_seconds <= 0:
            raise AthenaQueryError("timeout_seconds must be greater than zero.")
        if poll_interval_seconds < 0:
            raise AthenaQueryError("poll_interval_seconds cannot be negative.")
        self.database = database.strip()
        self.output_location = output_location.strip()
        self.client = client or boto3.client("athena", region_name=region)
        self.timeout_seconds = timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self.sleep = sleep

    def _wait_for_completion(self, query_execution_id: str) -> str:
        started = time.monotonic()
        while True:
            try:
                response = self.client.get_query_execution(
                    QueryExecutionId=query_execution_id
                )
            except (BotoCoreError, ClientError, OSError) as exc:
                raise AthenaQueryError("Could not read Athena query status.") from exc
            status = response.get("QueryExecution", {}).get("Status", {})
            state = str(status.get("State", "UNKNOWN"))
            if state in {"SUCCEEDED", "FAILED", "CANCELLED"}:
                if state != "SUCCEEDED":
                    reason = status.get("StateChangeReason", "No reason supplied")
                    raise AthenaQueryError(f"Athena query {state.lower()}: {reason}")
                return state
            if time.monotonic() - started >= self.timeout_seconds:
                raise AthenaQueryError(
                    f"Athena query {query_execution_id!r} timed out after "
                    f"{self.timeout_seconds} seconds."
                )
            self.sleep(self.poll_interval_seconds)

    def _read_results(self, query_execution_id: str) -> pd.DataFrame:
        rows: list[list[object]] = []
        column_names: list[str] | None = None
        next_token: str | None = None
        while True:
            kwargs: dict[str, object] = {"QueryExecutionId": query_execution_id}
            if next_token:
                kwargs["NextToken"] = next_token
            try:
                response = self.client.get_query_results(**kwargs)
            except (BotoCoreError, ClientError, OSError) as exc:
                raise AthenaQueryError("Could not read Athena query results.") from exc
            result_set = response.get("ResultSet", {})
            if column_names is None:
                column_info = result_set.get("ResultSetMetadata", {}).get("ColumnInfo", [])
                column_names = [str(column.get("Name", "column")) for column in column_info]
            rows.extend(
                [
                    [_cell_value(cell) for cell in row.get("Data", [])]
                    for row in result_set.get("Rows", [])
                ]
            )
            next_token = response.get("NextToken")
            if not next_token:
                break
        if not column_names:
            return pd.DataFrame()
        if rows and rows[0] == column_names:
            rows = rows[1:]
        normalized_rows = [row + [None] * (len(column_names) - len(row)) for row in rows]
        return pd.DataFrame(normalized_rows, columns=column_names)

    def query(self, sql: str) -> AthenaQueryResult:
        """Execute SQL in the configured database and return a DataFrame."""
        if not sql.strip():
            raise AthenaQueryError("Athena SQL cannot be empty.")
        try:
            response = self.client.start_query_execution(
                QueryString=sql,
                QueryExecutionContext={"Database": self.database},
                ResultConfiguration={"OutputLocation": self.output_location},
            )
            query_execution_id = str(response["QueryExecutionId"])
            state = self._wait_for_completion(query_execution_id)
            dataframe = self._read_results(query_execution_id)
        except AthenaQueryError:
            raise
        except (BotoCoreError, ClientError, OSError, KeyError, TypeError) as exc:
            raise AthenaQueryError("Could not start the Athena query.") from exc
        return AthenaQueryResult(
            query_execution_id=query_execution_id,
            state=state,
            output_location=self.output_location,
            dataframe=dataframe,
        )
