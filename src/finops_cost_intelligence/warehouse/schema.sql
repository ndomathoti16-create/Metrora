CREATE TABLE IF NOT EXISTS ingestion_run (
    ingestion_id VARCHAR PRIMARY KEY,
    source_name VARCHAR NOT NULL,
    file_format VARCHAR NOT NULL,
    source_size_bytes BIGINT,
    rows_in BIGINT NOT NULL,
    rows_out BIGINT NOT NULL,
    ready_for_analysis BOOLEAN NOT NULL,
    overall_status VARCHAR NOT NULL,
    mapping_json VARCHAR NOT NULL,
    quality_report_json VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_cloud_cost (
    ingestion_id VARCHAR NOT NULL,
    source_file VARCHAR NOT NULL,
    source_row_number BIGINT NOT NULL,
    source_row_hash VARCHAR NOT NULL,
    usage_date DATE,
    service VARCHAR,
    cost DOUBLE,
    currency VARCHAR,
    provider VARCHAR,
    account_id VARCHAR,
    account_name VARCHAR,
    region VARCHAR,
    department VARCHAR,
    project VARCHAR,
    environment VARCHAR,
    resource_id VARCHAR,
    resource_name VARCHAR,
    usage_quantity DOUBLE,
    usage_unit VARCHAR,
    usage_type VARCHAR,
    cost_type VARCHAR,
    tags_json VARCHAR,
    PRIMARY KEY (ingestion_id, source_row_number)
);

CREATE TABLE IF NOT EXISTS quality_check_result (
    ingestion_id VARCHAR NOT NULL,
    check_name VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    severity VARCHAR NOT NULL,
    observed_value VARCHAR,
    expected_value VARCHAR,
    affected_rows BIGINT NOT NULL,
    detail VARCHAR NOT NULL,
    PRIMARY KEY (ingestion_id, check_name)
);
