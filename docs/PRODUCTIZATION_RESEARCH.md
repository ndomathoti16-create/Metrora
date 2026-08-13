# Metrora productization research

## Decision

Metrora's first downloadable release is a local, read-only FinOps decision workspace rather
than a cloud-control plane. It automatically reads scheduled provider billing exports, builds
one trusted cost model, and keeps every financial result traceable to source rows.

The hosted Streamlit site remains a product preview and synthetic demo. The Windows release
opens directly into the real workspace and stores its database and non-secret connection
profiles under the current user's local application-data directory.

## What finance, FinOps, and cloud teams need

The FinOps Foundation framework and current industry products converge on eight needs:

1. Automated, fresh cost ingestion across providers and adjacent technology vendors.
2. A normalized cost model, increasingly based on FOCUS, with source reconciliation.
3. Allocation to owners, applications, environments, cost centers, and business units.
4. Budget, forecast, and anomaly signals that lead to accountable action.
5. Unit economics that connect cloud cost to customers, revenue, transactions, or usage.
6. Governance controls, policy compliance, and an auditable review history.
7. Optimization recommendations supported by utilization or commitment evidence.
8. Executive communication that states the answer, impact, owner, evidence, and next step.

The 2026 FinOps Framework formalizes Executive Strategy Alignment: concise decision support,
shared accountability, business-relevant measures, clear decision rights, named owners, and
measured follow-through. That reinforces Metrora's decision register and evidence trail rather
than arguing for more decorative dashboards. Allocation quality, forecasting accuracy, anomaly
response, unit economics, and optimization outcomes remain the operating measures beneath that
executive layer.

## Provider ingestion design

### AWS

AWS Data Exports and CUR 2.0 deliver scheduled CSV.GZ or Parquet files to S3, potentially as
multiple chunks plus a manifest. Metrora lists the configured prefix, selects the latest run
directory, downloads every data chunk, combines them, and sends the result through the same
mapping and reconciliation pipeline used for uploads.

Authentication uses the standard boto3 credential chain: AWS IAM Identity Center/SSO profile,
environment credentials, or an attached IAM role. The minimum data permissions are
`s3:ListBucket` on the configured prefix and `s3:GetObject` on export files.

### Azure

Azure Cost Management creates recurring daily or monthly ActualCost or AmortizedCost exports
in Blob Storage. Metrora uses `DefaultAzureCredential`, so a user can authenticate with Azure
CLI during local use and a corporation can use managed identity in a managed environment.
The minimum role is Storage Blob Data Reader on the export container.

### Google Cloud

Google Cloud Billing exports standard or detailed cost data to BigQuery. Metrora queries a
standard export through Application Default Credentials, imports a configurable recent
history, and includes credits in the effective-cost calculation. The minimum roles are
BigQuery Job User and Data Viewer.

### Other providers and SaaS

CSV, Excel, Parquet, and FOCUS-shaped exports remain the portable integration path. FOCUS 1.3
extends the normalized specification across technology categories and makes both BilledCost and
EffectiveCost mandatory. Metrora proposes EffectiveCost for trend, forecast, and unit-economics
analysis, while keeping BilledCost available through mapping review for cash-basis and invoice
work. Standards-first expansion remains preferable to vendor-specific logic for every tool.

## Security and trust boundaries

- Connections are read-only.
- Cloud passwords, access keys, bearer tokens, and service-account files are never stored.
- Saved profiles contain only export locations and identity selectors.
- Source totals are reconciled after every refresh.
- A blocking quality result pauses planning and reporting.
- Metrora does not make changes to cloud resources.
- Rightsizing and savings claims require utilization, pricing, or commitment evidence; billing
  data alone is not treated as proof.

## Release scope

Included in the first desktop product release:

- portable Windows application with no local Python requirement;
- file, AWS S3, Azure Blob, and Google BigQuery sources;
- latest-export discovery, multi-file combination, refresh-on-open, and sync status;
- mapping, normalization, reconciliation, quality checks, analytics, forecast, anomaly review,
  budgets, allocation, unit economics, reports, and exports;
- local DuckDB persistence and non-secret connection profiles.

Post-release enterprise work:

- signed installer and automatic application updates;
- SSO, role-based access, shared workspaces, and immutable audit logs;
- background service scheduling when the desktop window is closed;
- Jira, Slack, Teams, and email action routing;
- Kubernetes, commitment, and utilization connectors for defensible optimization;
- policy-as-code and showback/chargeback workflows;
- managed deployment architecture, encryption controls, and security review.

## Primary sources

- FinOps Foundation Framework: <https://www.finops.org/framework/>
- FinOps Framework 2026 update: <https://www.finops.org/insights/2026-finops-framework/>
- Executive Strategy Alignment: <https://www.finops.org/framework/capabilities/executive-strategy-alignment/>
- FinOps allocation capability: <https://www.finops.org/framework/capabilities/allocation/>
- FinOps unit economics capability: <https://www.finops.org/framework/capabilities/unit-economics/>
- FOCUS 1.3: <https://focus.finops.org/focus-specification/v1-3/>
- AWS Data Exports delivery: <https://docs.aws.amazon.com/cur/latest/userguide/dataexports-export-delivery.html>
- Azure scheduled cost exports: <https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-improved-exports>
- Azure Blob passwordless Python access: <https://learn.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-python>
- Google Cloud Billing export: <https://cloud.google.com/billing/docs/how-to/export-data-bigquery-setup>
- PyInstaller: <https://pyinstaller.org/en/stable/>
