# FinOps Cost Intelligence Platform

A local-first AI financial analytics application for cloud billing analysis, FinOps workflows, budget monitoring, forecasting, anomaly detection, and evidence-based recommendations.

The project is being built incrementally, with deterministic calculations kept separate from the Streamlit presentation layer.

## Current status

Milestones 0–6 are complete. The application accepts CSV, Excel (`.xlsx` and `.xls`), and Parquet uploads, profiles source structure, supports human-reviewed semantic mappings, normalizes data into the canonical cost model, runs deterministic quality checks, reconciles source and canonical totals, and persists runs to a local DuckDB warehouse. It then calculates filterable spend KPIs, budget variance, allocation coverage, business unit economics, daily forecasts, and explainable anomalies. No real billing data or cloud credentials are required.

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

The current shell supports upload, profiling, semantic mapping, canonical normalization, quality checks, reconciliation, local DuckDB persistence, core spend analysis, optional budget/business-metric uploads, forecasting, and anomaly detection. AI explanations, exports, and AWS S3/Athena integration remain future milestones.

## Ingestion behavior

The reader validates file type and configured size before parsing. It rejects missing paths, unsupported extensions, empty tables, malformed input, and missing format-specific parser dependencies with user-facing errors. The profiler reports row and column counts, null rates, unique counts, duplicate rows, all-null rows, raw numeric and datetime parse rates, sample values, and preview rows without mutating the loaded source.

## Mapping and normalization behavior

The detector ranks source columns for required fields (`usage_date`, `service`, and `cost`) and optional dimensions such as account, region, department, project, environment, usage, currency, and tags. Each suggestion includes a confidence level and explanation, and the Streamlit form requires a human review before applying it. Normalization standardizes dates, strings, currency codes, numeric values, and tags; adds ingestion and row-lineage fields; preserves every input row; and records conversion issues instead of silently dropping invalid values.

## Quality and warehouse behavior

Quality checks distinguish blocking errors from reviewable warnings. They cover row preservation, required-field completeness, normalization errors, currency consistency, exact duplicate canonical rows, negative costs, optional-field completeness, and source-to-canonical cost reconciliation. A run is marked ready for analysis only when no blocking check fails. DuckDB stores the canonical cost fact table, ingestion-run metadata, and individual quality-check results. Saving the same ingestion ID replaces its prior local version so repeated runs do not contaminate the warehouse.

## Analytics behavior

Core spend KPIs and charts use the same inclusive date and dimension filters. Spend is calculated from the canonical `cost` field and is broken down by available service, account, department, project, environment, region, provider, and cost type dimensions. Missing dimensions are shown as unavailable rather than inferred.

Optional budget files are normalized from common headers and compared by inclusive period and scope. Allocation coverage reports both row coverage and positive-cost-weighted coverage; positive spend is the denominator so credits do not distort tagging percentages. Optional business metrics are joined at daily grain to calculate cost per unit.

Forecasts use Holt-Winters when enough history is available and a trailing-mean fallback for short histories. Anomalies use a prior rolling median/MAD baseline, so the observed day is not used to calculate its own expectation. Forecast methods, history windows, thresholds, and uncertainty bounds are displayed with the results.

All analytics are calculated in Python before any future AI summarization layer. The AI layer will receive structured facts and caveats rather than raw authority to invent financial values.

## Project design

The complete scope, canonical data model, architecture, milestone gates, and portfolio presentation plan are documented in [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md).

## Data and privacy

Use synthetic or anonymized data for development. Do not commit cloud account identifiers, customer data, billing exports, access keys, or `.env` files.
