-- Replace the LOCATION value with an approved standardized S3 prefix.
-- The table matches the canonical Parquet output from the local application.

CREATE EXTERNAL TABLE IF NOT EXISTS fact_cloud_cost (
    ingestion_id string,
    source_file string,
    source_row_number bigint,
    source_row_hash string,
    usage_date date,
    service string,
    cost double,
    currency string,
    provider string,
    account_id string,
    account_name string,
    region string,
    department string,
    project string,
    environment string,
    resource_id string,
    resource_name string,
    usage_quantity double,
    usage_unit string,
    usage_type string,
    cost_type string,
    tags_json string
)
STORED AS PARQUET
LOCATION 's3://REPLACE_WITH_APPROVED_BUCKET/standardized/cloud_cost/';

CREATE OR REPLACE VIEW vw_monthly_service_spend AS
SELECT
    date_trunc('month', usage_date) AS month_start,
    service,
    currency,
    SUM(cost) AS total_cost,
    COUNT(*) AS cost_rows
FROM fact_cloud_cost
GROUP BY 1, 2, 3;
