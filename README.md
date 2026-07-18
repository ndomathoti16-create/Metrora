# FinOps Cost Intelligence Platform

A local-first AI financial analytics application for cloud billing analysis, FinOps workflows, budget monitoring, forecasting, anomaly detection, and evidence-based recommendations.

The project is being built incrementally. Milestone 0 establishes the repository foundation; the analytical workflow will be added one milestone at a time.

## Current status

Milestone 3 is complete. The application accepts CSV, Excel (`.xlsx` and `.xls`), and Parquet uploads, profiles source structure, supports human-reviewed semantic mappings, normalizes data into the canonical cost model, runs deterministic quality checks, reconciles source and canonical totals, and persists runs to a local DuckDB warehouse. No real billing data or cloud credentials are required.

## Local setup

PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` if you want to customize local settings. The default configuration stores local application state under `data/`.

## Run the checks

```powershell
python -m unittest discover -s tests -v
finops-check
```

After installing the development extras, the recommended test command is:

```powershell
pytest
```

## Run the application shell

```powershell
streamlit run app.py
```

The current shell supports upload, profiling, semantic mapping, canonical normalization, quality checks, reconciliation, and local DuckDB persistence. Cost analytics, forecasting, and AI explanations arrive in later milestones.

## Ingestion behavior

The reader validates file type and configured size before parsing. It rejects missing paths, unsupported extensions, empty tables, malformed input, and missing format-specific parser dependencies with user-facing errors. The profiler reports row and column counts, null rates, unique counts, duplicate rows, all-null rows, raw numeric and datetime parse rates, sample values, and preview rows without mutating the loaded source.

## Mapping and normalization behavior

The detector ranks source columns for required fields (`usage_date`, `service`, and `cost`) and optional dimensions such as account, region, department, project, environment, usage, currency, and tags. Each suggestion includes a confidence level and explanation, and the Streamlit form requires a human review before applying it. Normalization standardizes dates, strings, currency codes, numeric values, and tags; adds ingestion and row-lineage fields; preserves every input row; and records conversion issues instead of silently dropping invalid values.

## Quality and warehouse behavior

Quality checks distinguish blocking errors from reviewable warnings. They cover row preservation, required-field completeness, normalization errors, currency consistency, exact duplicate canonical rows, negative costs, optional-field completeness, and source-to-canonical cost reconciliation. A run is marked ready for analysis only when no blocking check fails. DuckDB stores the canonical cost fact table, ingestion-run metadata, and individual quality-check results. Saving the same ingestion ID replaces its prior local version so repeated runs do not contaminate the warehouse.

## Project design

The complete scope, canonical data model, architecture, milestone gates, and portfolio presentation plan are documented in [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md).

## Data and privacy

Use synthetic or anonymized data for development. Do not commit cloud account identifiers, customer data, billing exports, access keys, or `.env` files.
