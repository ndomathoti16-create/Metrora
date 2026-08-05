# Data dictionary

## Cloud billing input

The billing upload may use provider-specific names. The mapping screen converts it into `fact_cloud_cost`.

| Canonical field | Required | Meaning |
|---|---:|---|
| `usage_date` | Yes | Date assigned to the charge or usage |
| `service` | Yes | Cloud service or product family |
| `cost` | Yes | Monetary amount used for analysis |
| `currency` | No | Currency code; mixed currencies block analysis |
| `provider` | No | Cloud provider |
| `account_id` / `account_name` | No | Cloud account or subscription identity |
| `region` | No | Region or global scope |
| `department` | No | Owning department or cost center |
| `project` | No | Product, application, or workload |
| `environment` | No | Production, staging, development, or similar |
| `usage_quantity` / `usage_unit` | No | Provider usage measure |
| `usage_type` / `cost_type` | No | Provider charge classification |
| `tags_json` | No | Original tag payload preserved for lineage |

The application adds `ingestion_id`, `source_file`, `source_row_number`, and `source_row_hash` for lineage.

## Budget input

Minimum fields are `period_start`, `period_end`, `scope_type`, `scope_value`, `budget_amount`, and `currency`. Common aliases such as `month`, `budget`, `dimension`, and `value` are accepted. Supported scope types are total, service, account, department, project, environment, and region.

## Business metric input

Minimum fields are `metric_date`, `metric_name`, `metric_value`, and `unit`. The application aggregates duplicate rows to daily metric grain before calculating cost per unit. A user selects one metric explicitly; unrelated metrics are not silently combined.
