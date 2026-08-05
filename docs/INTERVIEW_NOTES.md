# Interview notes

## Two-minute walkthrough

1. Upload a provider-style billing file and inspect its profile.
2. Review the suggested semantic mapping and apply it.
3. Show quality checks and source-to-canonical reconciliation before discussing any financial result.
4. Use the dashboard to identify the largest service driver and the period trend.
5. Add the budget and business-metric files to show budget variance, allocation coverage, and cost per unit.
6. Show the forecast, anomaly evidence, and evidence-backed recommendations.
7. Generate the executive HTML report and download the cleaned dataset and fact pack.

## Strong technical points

- The canonical model separates ingestion from analysis and preserves row-level lineage.
- Every displayed number is calculated in Python before the fact pack reaches the optional AI adapter.
- Quality checks distinguish blocking errors from reviewable warnings.
- Forecasting and anomaly detection expose their method, history, threshold, and limitations.
- Recommendations say “investigate” when billing-only evidence cannot prove a savings action.
- DuckDB provides the reproducible local path; S3 and Athena provide a realistic cloud extension.

## Honest limitations

The first release does not claim rightsizing, idle-resource deletion, commitment optimization, multi-currency conversion, or causal explanations without the required utilization, pricing, or operational evidence.
