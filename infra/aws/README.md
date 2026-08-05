# AWS deployment notes

This directory contains the optional cloud extension. It is intentionally documentation-first: no resource is created automatically and no account-specific values are committed.

Recommended sequence:

1. Create an S3 bucket with versioning, encryption, lifecycle rules, and separate `raw/`, `standardized/`, `exports/`, and `athena-results/` prefixes.
2. Create an Athena database and workgroup with a query-result location under `athena-results/`.
3. Run [athena_schema.sql](athena_schema.sql) after replacing the example location with the approved standardized prefix.
4. Add the Glue crawler or explicit catalog table needed for the chosen Parquet layout.
5. Configure the application through environment variables or a managed deployment secret store.
6. Test with the synthetic demo inputs before considering real billing data.

The Python adapters are intentionally injectable for tests: `S3Storage` accepts a client and `AthenaWarehouse` accepts a client, timeout, and sleep function.
