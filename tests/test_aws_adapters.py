import io

import pandas as pd
import pytest

from finops_cost_intelligence.storage import S3Storage, S3StorageError
from finops_cost_intelligence.warehouse import AthenaQueryError, AthenaWarehouse


class _Body:
    def __init__(self, payload: bytes):
        self.payload = payload

    def read(self) -> bytes:
        return self.payload


class _FakeS3Client:
    def __init__(self):
        self.objects: dict[tuple[str, str], bytes] = {}

    def put_object(self, **kwargs):
        self.objects[(kwargs["Bucket"], kwargs["Key"])] = kwargs["Body"]

    def get_object(self, **kwargs):
        return {"Body": _Body(self.objects[(kwargs["Bucket"], kwargs["Key"])])}


class _FakeAthenaClient:
    def start_query_execution(self, **kwargs):
        self.sql = kwargs["QueryString"]
        return {"QueryExecutionId": "query-001"}

    def get_query_execution(self, **kwargs):
        assert kwargs["QueryExecutionId"] == "query-001"
        return {"QueryExecution": {"Status": {"State": "SUCCEEDED"}}}

    def get_query_results(self, **kwargs):
        assert kwargs["QueryExecutionId"] == "query-001"
        return {
            "ResultSet": {
                "ResultSetMetadata": {"ColumnInfo": [{"Name": "service"}, {"Name": "total_cost"}]},
                "Rows": [
                    {
                        "Data": [
                            {"VarCharValue": "service"},
                            {"VarCharValue": "total_cost"},
                        ]
                    },
                    {
                        "Data": [
                            {"VarCharValue": "Compute"},
                            {"VarCharValue": "12.5"},
                        ]
                    },
                ],
            }
        }


def test_s3_adapter_round_trips_parquet_with_injected_client():
    client = _FakeS3Client()
    storage = S3Storage("demo-bucket", client=client)
    frame = pd.DataFrame({"service": ["Compute"], "cost": [12.5]})

    uri = storage.upload_dataframe(frame, "standardized/demo.parquet")
    payload = storage.download_bytes("standardized/demo.parquet")
    round_trip = pd.read_parquet(io.BytesIO(payload))

    assert uri == "s3://demo-bucket/standardized/demo.parquet"
    pd.testing.assert_frame_equal(round_trip, frame)


def test_s3_adapter_rejects_unsafe_keys():
    with pytest.raises(S3StorageError, match="parent paths"):
        S3Storage("demo-bucket", client=_FakeS3Client()).uri("../secret.csv")


def test_athena_adapter_returns_dataframe_from_injected_client():
    client = _FakeAthenaClient()
    warehouse = AthenaWarehouse(
        "finops",
        "s3://demo-bucket/athena-results/",
        client=client,
        poll_interval_seconds=0,
    )

    result = warehouse.query("SELECT service, total_cost FROM vw_monthly_service_spend")

    assert result.query_execution_id == "query-001"
    assert result.state == "SUCCEEDED"
    assert result.dataframe.to_dict("records") == [{"service": "Compute", "total_cost": "12.5"}]
    assert client.sql.startswith("SELECT service")


def test_athena_adapter_validates_configuration():
    with pytest.raises(AthenaQueryError, match="s3://"):
        AthenaWarehouse("finops", "not-an-s3-location", client=_FakeAthenaClient())
