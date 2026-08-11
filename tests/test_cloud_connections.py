from __future__ import annotations

import gzip
from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

from finops_cost_intelligence.connections import (
    AwsS3BillingConnector,
    AwsS3ExportConfig,
    AzureBlobBillingConnector,
    AzureBlobExportConfig,
    ConnectionProfile,
    ConnectionStore,
    GcpBigQueryBillingConnector,
    GcpBigQueryExportConfig,
)


class _Body:
    def __init__(self, payload: bytes):
        self.payload = payload

    def read(self) -> bytes:
        return self.payload


class _Paginator:
    def __init__(self, pages):
        self.pages = pages

    def paginate(self, **kwargs):
        assert kwargs["Bucket"] == "finops-exports"
        assert kwargs["Prefix"] == "cur"
        return self.pages


class _S3Client:
    def __init__(self, pages, objects):
        self.pages = pages
        self.objects = objects

    def get_paginator(self, name):
        assert name == "list_objects_v2"
        return _Paginator(self.pages)

    def get_object(self, **kwargs):
        return {"Body": _Body(self.objects[kwargs["Key"]])}


def _csv(rows: list[tuple[str, str, float]]) -> bytes:
    frame = pd.DataFrame(rows, columns=["UsageDate", "Service", "Cost"])
    return frame.to_csv(index=False).encode("utf-8")


def test_aws_connector_combines_only_latest_export_chunks():
    old = datetime.now(UTC) - timedelta(days=2)
    latest = datetime.now(UTC)
    pages = [
        {
            "Contents": [
                {"Key": "cur/old/part.csv.gz", "Size": 10, "LastModified": old},
                {"Key": "cur/new/part-1.csv.gz", "Size": 11, "LastModified": latest},
                {"Key": "cur/new/part-2.csv.gz", "Size": 12, "LastModified": latest},
                {"Key": "cur/new/manifest.json", "Size": 2, "LastModified": latest},
            ]
        }
    ]
    objects = {
        "cur/old/part.csv.gz": gzip.compress(_csv([("2026-01-01", "Old", 1.0)])),
        "cur/new/part-1.csv.gz": gzip.compress(
            _csv([("2026-02-01", "Compute", 10.0)])
        ),
        "cur/new/part-2.csv.gz": gzip.compress(
            _csv([("2026-02-01", "Storage", 5.0)])
        ),
    }
    connector = AwsS3BillingConnector(
        AwsS3ExportConfig(bucket="finops-exports", prefix="cur"),
        client=_S3Client(pages, objects),
    )

    result = connector.sync_latest()

    assert result.provider == "AWS"
    assert result.object_count == 2
    assert result.source_uri == "s3://finops-exports/cur/new"
    assert result.loaded_table.dataframe["Cost"].sum() == 15.0


class _Blob:
    def __init__(self, name: str, payload: bytes, modified: datetime):
        self.name = name
        self.size = len(payload)
        self.last_modified = modified


class _Download:
    def __init__(self, payload: bytes):
        self.payload = payload

    def readall(self):
        return self.payload


class _ContainerClient:
    def __init__(self, objects: dict[str, tuple[bytes, datetime]]):
        self.objects = objects

    def list_blobs(self, *, name_starts_with=None):
        return [
            _Blob(name, payload, modified)
            for name, (payload, modified) in self.objects.items()
            if not name_starts_with or name.startswith(name_starts_with)
        ]

    def download_blob(self, name):
        return _Download(self.objects[name][0])


def test_azure_connector_uses_latest_complete_export_directory():
    old = datetime.now(UTC) - timedelta(days=1)
    latest = datetime.now(UTC)
    objects = {
        "daily/old/part.csv": (_csv([("2026-01-01", "Old", 1.0)]), old),
        "daily/new/part.csv": (_csv([("2026-01-02", "Database", 8.0)]), latest),
    }
    connector = AzureBlobBillingConnector(
        AzureBlobExportConfig(
            account_url="https://costs.blob.core.windows.net",
            container="exports",
            prefix="daily",
        ),
        container_client=_ContainerClient(objects),
    )

    result = connector.sync_latest()

    assert result.provider == "Azure"
    assert result.object_count == 1
    assert result.loaded_table.dataframe["Service"].tolist() == ["Database"]
    assert result.source_uri.endswith("/exports/daily/new")


class _QueryResult:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def result(self):
        return self

    def to_dataframe(self):
        return self.dataframe


class _BigQueryClient:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.sql = ""

    def query(self, sql):
        self.sql = sql
        return _QueryResult(self.dataframe)


def test_gcp_connector_queries_credit_adjusted_cost():
    dataframe = pd.DataFrame(
        {
            "UsageStartDate": ["2026-01-01"],
            "ProductName": ["Compute Engine"],
            "EffectiveCost": [42.0],
        }
    )
    client = _BigQueryClient(dataframe)
    connector = GcpBigQueryBillingConnector(
        GcpBigQueryExportConfig(
            project_id="finops-demo-123",
            dataset="billing_export",
            lookback_days=90,
        ),
        client=client,
    )

    result = connector.sync_latest()

    assert result.loaded_table.dataframe["EffectiveCost"].sum() == 42.0
    assert "UNNEST(credits)" in client.sql
    assert "INTERVAL 90 DAY" in client.sql


def test_connection_store_persists_only_allowlisted_non_secret_fields(tmp_path):
    store = ConnectionStore(tmp_path / "connections.json")
    profile = ConnectionProfile.create(
        name="Finance AWS",
        provider="aws",
        settings={
            "bucket": "finops-exports",
            "prefix": "cur",
            "region": "us-east-1",
            "profile_name": "finops-readonly",
        },
        refresh_on_open=True,
    )
    store.save(profile)

    restored = store.active()

    assert restored == profile
    assert "secret" not in (tmp_path / "connections.json").read_text().casefold()


def test_connection_profile_rejects_secret_fields():
    with pytest.raises(ValueError, match="cannot store"):
        ConnectionProfile.create(
            name="Unsafe",
            provider="aws",
            settings={"bucket": "demo", "secret_access_key": "not-allowed"},
            refresh_on_open=False,
        )
