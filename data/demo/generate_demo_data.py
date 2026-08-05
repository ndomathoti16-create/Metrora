"""Generate safe, deterministic demo inputs for the FinOps application."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import pandas as pd

SERVICES = (
    ("Compute", 110.0, "Engineering", "Customer Portal", "prod"),
    ("Storage", 34.0, "Engineering", "Customer Portal", "prod"),
    ("Database", 76.0, "Engineering", "Customer Portal", "prod"),
    ("Data Transfer", 24.0, "Finance", "Analytics", "prod"),
)


def build_demo_tables(seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return billing, budget, and business-metric demo tables.

    The data intentionally contains a compute spike, partial ownership coverage,
    a budget pressure signal, and business-volume growth so each dashboard section
    has something useful to show.
    """
    rng = random.Random(seed)
    dates = pd.date_range("2025-01-01", periods=59, freq="D")
    billing_rows: list[dict[str, object]] = []
    for index, usage_date in enumerate(dates):
        weekday_factor = 1.08 if usage_date.weekday() < 5 else 0.88
        spike_factor = 1.0 + (1.35 if 35 <= index <= 39 else 0.0)
        for service, base_cost, department, project, environment in SERVICES:
            noise = rng.gauss(0.0, base_cost * 0.04)
            cost = max(0.01, base_cost * weekday_factor * spike_factor + noise)
            is_unallocated = service == "Data Transfer" and index % 4 == 0
            billing_rows.append(
                {
                    "UsageStartDate": usage_date.strftime("%Y-%m-%d"),
                    "ProductName": service,
                    "UnblendedCost": round(cost, 2),
                    "Currency": "USD",
                    "AccountNumber": "acct-prod-001" if environment == "prod" else "acct-dev-001",
                    "AWSRegion": "us-east-1" if service != "Data Transfer" else "us-west-2",
                    "Dept": None if is_unallocated else department,
                    "ProjectName": None if is_unallocated else project,
                    "Env": environment,
                    "Usage": round(cost * 1.7, 2),
                    "Unit": "units",
                    "CostType": "Usage",
                }
            )
    billing = pd.DataFrame(billing_rows)

    billing["_date"] = pd.to_datetime(billing["UsageStartDate"])
    budget_rows: list[dict[str, object]] = []
    for month_start, month_end in (("2025-01-01", "2025-01-31"), ("2025-02-01", "2025-02-28")):
        month_mask = billing["_date"].between(month_start, month_end)
        for service in [row[0] for row in SERVICES]:
            service_mask = month_mask & billing["ProductName"].eq(service)
            actual = float(billing.loc[service_mask, "UnblendedCost"].sum())
            budget_factor = 0.88 if service == "Compute" and month_start == "2025-02-01" else 1.08
            budget_rows.append(
                {
                    "period_start": month_start,
                    "period_end": month_end,
                    "scope_type": "service",
                    "scope_value": service,
                    "budget_amount": round(actual * budget_factor, 2),
                    "currency": "USD",
                }
            )
        total_actual = float(billing.loc[month_mask, "UnblendedCost"].sum())
        budget_rows.append(
            {
                "period_start": month_start,
                "period_end": month_end,
                "scope_type": "total",
                "scope_value": "Total",
                "budget_amount": round(total_actual * 1.02, 2),
                "currency": "USD",
            }
        )
    budget = pd.DataFrame(budget_rows)

    metric_rows: list[dict[str, object]] = []
    for index, usage_date in enumerate(dates):
        customers = 1200 + index * 18 + rng.randint(-20, 20)
        transactions = customers * 9 + rng.randint(-150, 150)
        metric_rows.extend(
            [
                {
                    "metric_date": usage_date.strftime("%Y-%m-%d"),
                    "metric_name": "Customers",
                    "metric_value": customers,
                    "unit": "customers",
                },
                {
                    "metric_date": usage_date.strftime("%Y-%m-%d"),
                    "metric_name": "Transactions",
                    "metric_value": transactions,
                    "unit": "transactions",
                },
            ]
        )
    business_metrics = pd.DataFrame(metric_rows)
    return billing.drop(columns="_date"), budget, business_metrics


def write_demo_files(output_dir: Path) -> dict[str, Path]:
    """Write demo CSVs and return their paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    billing, budget, business_metrics = build_demo_tables()
    paths = {
        "billing": output_dir / "cloud_billing_demo.csv",
        "budget": output_dir / "budget_demo.csv",
        "business_metrics": output_dir / "business_metrics_demo.csv",
    }
    billing.to_csv(paths["billing"], index=False)
    budget.to_csv(paths["budget"], index=False)
    business_metrics.to_csv(paths["business_metrics"], index=False)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory in which the synthetic CSV files will be written.",
    )
    args = parser.parse_args()
    paths = write_demo_files(args.output_dir)
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
