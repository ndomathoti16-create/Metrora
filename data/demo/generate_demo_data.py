"""Generate safe, deterministic demo inputs for Metrora."""

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

SCENARIO_FILES = {
    "healthy": (
        "cloud_billing_healthy.csv",
        "budget_healthy.csv",
        "business_metrics_healthy.csv",
    ),
    "quality_risk": (
        "cloud_billing_quality_risk.csv",
        "budget_quality_risk.csv",
        "business_metrics_quality_risk.csv",
    ),
    "forecast_risk": (
        "cloud_billing_demo.csv",
        "budget_demo.csv",
        "business_metrics_demo.csv",
    ),
}


def _billing_table(rng: random.Random, scenario: str) -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=59, freq="D")
    rows: list[dict[str, object]] = []
    for index, usage_date in enumerate(dates):
        weekday_factor = 1.06 if usage_date.weekday() < 5 else 0.90
        for service, base_cost, department, project, environment in SERVICES:
            if scenario == "forecast_risk":
                late_days = max(index - 44, 0)
                trend_rate = 0.038 if service in {"Compute", "Database"} else 0.012
                trend_factor = 1.0 + late_days * trend_rate
                pulse_factor = 1.22 if 34 <= index <= 37 and service == "Compute" else 1.0
            else:
                trend_factor = 1.0 + index * 0.0008
                pulse_factor = 1.0
            noise = rng.gauss(0.0, base_cost * 0.025)
            cost = max(
                0.01,
                base_cost * weekday_factor * trend_factor * pulse_factor + noise,
            )
            is_unallocated = (
                scenario == "forecast_risk" and service == "Data Transfer" and index % 11 == 0
            )
            rows.append(
                {
                    "UsageStartDate": usage_date.strftime("%Y-%m-%d"),
                    "ProductName": service,
                    "UnblendedCost": round(cost, 2),
                    "Currency": "USD",
                    "AccountNumber": "acct-prod-001",
                    "AWSRegion": ("us-west-2" if service == "Data Transfer" else "us-east-1"),
                    "Dept": None if is_unallocated else department,
                    "ProjectName": None if is_unallocated else project,
                    "Env": environment,
                    "Usage": round(cost * 1.7, 2),
                    "Unit": "units",
                    "CostType": "Usage",
                }
            )
    billing = pd.DataFrame(rows)
    if scenario != "quality_risk":
        return billing

    # This source is intentionally deceptive in several different ways so the
    # quality workflow can demonstrate blocking errors and review-only warnings.
    billing["UnblendedCost"] = billing["UnblendedCost"].astype(object)
    billing.loc[2, "UsageStartDate"] = "not-a-date"
    billing.loc[9, "ProductName"] = None
    billing.loc[15, "UnblendedCost"] = "not-a-cost"
    billing.loc[24, "Currency"] = "EUR"
    billing.loc[30, "UnblendedCost"] = -18.50
    billing.loc[40:165, ["Dept", "ProjectName"]] = None
    return pd.concat([billing, billing.iloc[[6]].copy()], ignore_index=True)


def _budget_table(billing: pd.DataFrame, scenario: str) -> pd.DataFrame:
    working = billing.copy()
    working["_date"] = pd.to_datetime(working["UsageStartDate"], errors="coerce")
    working["_cost"] = pd.to_numeric(working["UnblendedCost"], errors="coerce")
    rows: list[dict[str, object]] = []
    for month_start, month_end in (
        ("2025-01-01", "2025-01-31"),
        ("2025-02-01", "2025-02-28"),
    ):
        month_mask = working["_date"].between(month_start, month_end)
        for service in [row[0] for row in SERVICES]:
            service_mask = month_mask & working["ProductName"].eq(service)
            actual = float(working.loc[service_mask, "_cost"].sum())
            factor = {
                "healthy": 1.14,
                "quality_risk": 1.10,
                "forecast_risk": 1.04,
            }[scenario]
            rows.append(
                {
                    "period_start": month_start,
                    "period_end": month_end,
                    "scope_type": "service",
                    "scope_value": service,
                    "budget_amount": round(actual * factor, 2),
                    "currency": "USD",
                }
            )
        total_actual = float(working.loc[month_mask, "_cost"].sum())
        total_factor = {
            "healthy": 1.12,
            "quality_risk": 1.08,
            "forecast_risk": 1.035,
        }[scenario]
        rows.append(
            {
                "period_start": month_start,
                "period_end": month_end,
                "scope_type": "total",
                "scope_value": "Total",
                "budget_amount": round(total_actual * total_factor, 2),
                "currency": "USD",
            }
        )
    return pd.DataFrame(rows)


def _business_metrics_table(rng: random.Random, scenario: str) -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=59, freq="D")
    rows: list[dict[str, object]] = []
    for index, usage_date in enumerate(dates):
        daily_growth = 18 if scenario == "healthy" else 8
        customers = 1200 + index * daily_growth + rng.randint(-15, 15)
        transactions = customers * 9 + rng.randint(-120, 120)
        rows.extend(
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
    return pd.DataFrame(rows)


def build_demo_tables(
    seed: int = 42,
    scenario: str = "forecast_risk",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return one deterministic billing, budget, and business-metric scenario."""
    if scenario not in SCENARIO_FILES:
        allowed = ", ".join(SCENARIO_FILES)
        raise ValueError(f"Unknown demo scenario {scenario!r}; choose one of: {allowed}.")
    rng = random.Random(seed)
    billing = _billing_table(rng, scenario)
    budget = _budget_table(billing, scenario)
    metrics = _business_metrics_table(rng, scenario)
    return billing, budget, metrics


def build_demo_scenarios(
    seed: int = 42,
) -> dict[str, tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]:
    """Build every checked-in scenario with stable, scenario-specific random streams."""
    return {
        scenario: build_demo_tables(seed=seed + offset, scenario=scenario)
        for offset, scenario in enumerate(SCENARIO_FILES)
    }


def write_demo_files(output_dir: Path) -> dict[str, Path]:
    """Write all demo CSVs and return their paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for scenario, tables in build_demo_scenarios().items():
        billing, budget, metrics = tables
        filenames = SCENARIO_FILES[scenario]
        for data_type, dataframe, filename in zip(
            ("billing", "budget", "business_metrics"),
            (billing, budget, metrics),
            filenames,
            strict=True,
        ):
            path = output_dir / filename
            dataframe.to_csv(path, index=False)
            paths[f"{scenario}_{data_type}"] = path
    paths["billing"] = output_dir / SCENARIO_FILES["forecast_risk"][0]
    paths["budget"] = output_dir / SCENARIO_FILES["forecast_risk"][1]
    paths["business_metrics"] = output_dir / SCENARIO_FILES["forecast_risk"][2]
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
