# Synthetic demo data

These files are deterministic, synthetic inputs for a portfolio walkthrough. They contain no cloud account, customer, or provider data.

Generate or refresh them from the repository root:

```powershell
python data/demo/generate_demo_data.py
```

Upload the files in this order:

1. `cloud_billing_demo.csv` as the billing source.
2. `budget_demo.csv` in the Budget variance tab.
3. `business_metrics_demo.csv` in the Business efficiency tab.

The data intentionally includes a compute-spend spike, incomplete ownership fields, a service-level February budget pressure signal, and Customers/Transactions metrics.
