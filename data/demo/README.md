# Synthetic demo data

These files are deterministic, synthetic inputs for product testing. They contain no cloud
account, customer, or provider data.

Generate or refresh them from the repository root:

```powershell
python data/demo/generate_demo_data.py
```

The product page can open each scenario in one click. For manual upload testing, use each billing
file with the matching budget and business-metric files:

- **Healthy baseline:** `cloud_billing_healthy.csv`, `budget_healthy.csv`, and
  `business_metrics_healthy.csv`. The source is clean, stable, owned, and within plan.
- **Data needs review:** `cloud_billing_quality_risk.csv`, `budget_quality_risk.csv`, and
  `business_metrics_quality_risk.csv`. The source deliberately includes invalid required values,
  mixed currencies, duplicate rows, a negative value, and ownership gaps.
- **Hidden future risk:** `cloud_billing_demo.csv`, `budget_demo.csv`, and
  `business_metrics_demo.csv`. The current model reconciles and remains within the supplied
  budget, while late acceleration creates a material near-term forecast risk.

All scenarios use the same canonical column pattern so the outcome changes because of the data,
not because of a different user workflow.
