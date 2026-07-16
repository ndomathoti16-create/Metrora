# FinOps Cost Intelligence Platform

A local-first AI financial analytics application for cloud billing analysis, FinOps workflows, budget monitoring, forecasting, anomaly detection, and evidence-based recommendations.

The project is being built incrementally. Milestone 0 establishes the repository foundation; the analytical workflow will be added one milestone at a time.

## Current status

Milestone 1 is complete. The application accepts CSV, Excel (`.xlsx` and `.xls`), and Parquet uploads, profiles source structure and parseability, and shows a read-only preview. No real billing data or cloud credentials are required.

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

The current shell supports upload and profiling. Semantic mapping, normalization, quality checks, analytics, forecasting, and AI explanations arrive in later milestones.

## Ingestion behavior

The reader validates file type and configured size before parsing. It rejects missing paths, unsupported extensions, empty tables, malformed input, and missing format-specific parser dependencies with user-facing errors. The profiler reports row and column counts, null rates, unique counts, duplicate rows, all-null rows, raw numeric and datetime parse rates, sample values, and preview rows without mutating the loaded source.

## Project design

The complete scope, canonical data model, architecture, milestone gates, and portfolio presentation plan are documented in [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md).

## Data and privacy

Use synthetic or anonymized data for development. Do not commit cloud account identifiers, customer data, billing exports, access keys, or `.env` files.
