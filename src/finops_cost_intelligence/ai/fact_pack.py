"""Build a versioned fact pack from deterministic analytical results."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from ..analytics.allocation import calculate_allocation_coverage
from ..analytics.budgets import calculate_budget_variance
from ..analytics.business_metrics import calculate_unit_economics
from ..analytics.spend import aggregate_spend, calculate_spend_summary
from ..anomalies import detect_spend_anomalies
from ..contracts.ai import Fact, FactPack
from ..contracts.anomaly import AnomalySummary
from ..contracts.forecasting import ForecastSummary
from ..contracts.normalization import NormalizedTable
from ..contracts.quality import QualityReport
from ..forecasting import forecast_daily_spend
from ..recommendations import generate_recommendations


def _fact(
    fact_id: str,
    label: str,
    value: Any,
    unit: str,
    evidence: str,
) -> Fact:
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        value = float(value) if isinstance(value, float) else int(value)
    return Fact(fact_id, label, value, unit, evidence)


def _add_forecast_facts(
    facts: list[Fact],
    dataframe: pd.DataFrame,
    caveats: list[str],
) -> ForecastSummary | None:
    try:
        _, forecast_summary = forecast_daily_spend(dataframe, horizon_days=14)
    except (ValueError, KeyError) as exc:
        caveats.append(f"Forecast unavailable: {exc}")
        return None
    facts.extend(
        [
            _fact(
                "forecast_total",
                "14-day forecast total",
                forecast_summary.forecast_total,
                "cost units",
                f"{forecast_summary.method} over {forecast_summary.horizon_days} future days",
            ),
            _fact(
                "forecast_method",
                "Forecast method",
                forecast_summary.method,
                "method",
                "Forecast method reported by the deterministic forecasting service",
            ),
            _fact(
                "forecast_residual_std",
                "Forecast residual standard deviation",
                forecast_summary.residual_std,
                "cost units",
                "Residual variation from the fitted historical model",
            ),
        ]
    )
    return forecast_summary


def _add_anomaly_facts(
    facts: list[Fact],
    dataframe: pd.DataFrame,
    caveats: list[str],
) -> AnomalySummary | None:
    try:
        _, anomaly_summary = detect_spend_anomalies(dataframe)
    except (ValueError, KeyError) as exc:
        caveats.append(f"Anomaly scan unavailable: {exc}")
        return None
    facts.append(
        _fact(
            "anomaly_count",
            "Meaningful anomaly count",
            anomaly_summary.anomaly_count,
            "rows",
            (
                f"{anomaly_summary.method}, {anomaly_summary.window_days}-day window, "
                f"threshold {anomaly_summary.threshold}"
            ),
        )
    )
    return anomaly_summary


def build_fact_pack(
    normalized: NormalizedTable,
    quality_report: QualityReport,
    *,
    dataframe: pd.DataFrame | None = None,
    budget_dataframe: pd.DataFrame | None = None,
    business_metrics_dataframe: pd.DataFrame | None = None,
    metric_name: str | None = None,
    filters: Mapping[str, Any] | None = None,
) -> FactPack:
    """Calculate all report facts from the selected canonical data.

    This function deliberately recomputes the small report fact set from the
    canonical rows instead of trusting values displayed by Streamlit widgets.
    """
    selected = (dataframe if dataframe is not None else normalized.dataframe).copy()
    facts: list[Fact] = []
    caveats: list[str] = []
    summary = calculate_spend_summary(selected, top_dimension="service")
    facts.extend(
        [
            _fact(
                "total_spend",
                "Total selected-period spend",
                summary.total_cost,
                summary.currency,
                "Sum of canonical cost values after the selected dashboard filters",
            ),
            _fact(
                "cost_row_count",
                "Selected billing row count",
                summary.row_count,
                "rows",
                "Number of canonical billing rows after the selected dashboard filters",
            ),
            _fact(
                "average_daily_spend",
                "Average daily spend",
                summary.average_daily_cost,
                summary.currency,
                f"Total spend divided by {summary.calendar_days} calendar day(s)",
            ),
        ]
    )
    if summary.date_start and summary.date_end:
        facts.extend(
            [
                _fact(
                    "period_start",
                    "Analysis start",
                    summary.date_start,
                    "date",
                    "Selected data period",
                ),
                _fact(
                    "period_end",
                    "Analysis end",
                    summary.date_end,
                    "date",
                    "Selected data period",
                ),
            ]
        )
    if "service" in selected.columns and not selected.empty:
        service_breakdown = aggregate_spend(selected, "service", top_n=1)
        if not service_breakdown.empty:
            facts.extend(
                [
                    _fact(
                        "top_service",
                        "Largest service by spend",
                        str(service_breakdown.iloc[0]["value"]),
                        "service",
                        "Ranked canonical service breakdown",
                    ),
                    _fact(
                        "top_service_share",
                        "Largest service share",
                        float(service_breakdown.iloc[0]["share_of_total"]),
                        "share",
                        (
                            "Largest service cost divided by total "
                            "selected-period cost"
                        ),
                    ),
                ]
            )

    try:
        allocation = calculate_allocation_coverage(selected)
        any_ownership = allocation.loc[allocation["field"].eq("any ownership field")].iloc[0]
        if pd.notna(any_ownership["cost_coverage"]):
            facts.append(
                _fact(
                    "allocation_cost_coverage",
                    "Positive cost with any ownership field",
                    float(any_ownership["cost_coverage"]),
                    "share",
                    "Positive-cost-weighted coverage across available ownership fields",
                )
            )
    except (ValueError, KeyError) as exc:
        caveats.append(f"Allocation coverage unavailable: {exc}")

    if budget_dataframe is not None:
        try:
            _, budget_summary = calculate_budget_variance(selected, budget_dataframe)
        except (ValueError, KeyError) as exc:
            caveats.append(f"Budget comparison unavailable: {exc}")
        else:
            facts.extend(
                [
                    _fact(
                        "budget_total",
                        "Supplied budget total",
                        budget_summary.budget_total,
                        "budget units",
                        "Sum of normalized budget rows",
                    ),
                    _fact(
                        "budget_actual_total",
                        "Actual cost matched to budget",
                        budget_summary.actual_total,
                        "cost units",
                        (
                            "Actual canonical cost matched to each budget "
                            "period and scope"
                        ),
                    ),
                    _fact(
                        "budget_variance_amount",
                        "Actual minus budget",
                        budget_summary.variance_amount,
                        "cost units",
                        "Actual matched cost minus supplied budget",
                    ),
                    _fact(
                        "budget_utilization",
                        "Budget utilization",
                        budget_summary.utilization_pct,
                        "share",
                        "Actual matched cost divided by supplied budget",
                    ),
                ]
            )

    if business_metrics_dataframe is not None and metric_name:
        try:
            _, unit_summary = calculate_unit_economics(
                selected, business_metrics_dataframe, metric_name
            )
        except (ValueError, KeyError) as exc:
            caveats.append(f"Business metric comparison unavailable: {exc}")
        else:
            facts.extend(
                [
                    _fact(
                        "business_metric_name",
                        "Selected business metric",
                        unit_summary.metric_name,
                        "metric",
                        "User-selected normalized business metric",
                    ),
                    _fact(
                        "business_metric_total",
                        "Business metric total",
                        unit_summary.total_metric_value,
                        "units",
                        "Sum of metric values at daily grain",
                    ),
                    _fact(
                        "cost_per_business_unit",
                        "Cost per business unit",
                        unit_summary.cost_per_unit,
                        "cost per unit",
                        (
                            "Total selected cost divided by selected business "
                            "metric total"
                        ),
                    ),
                ]
            )

    _add_forecast_facts(facts, selected, caveats)
    _add_anomaly_facts(facts, selected, caveats)
    recommendations = generate_recommendations(
        facts,
        quality_status=quality_report.overall_status,
        quality_ready=quality_report.ready_for_analysis,
    )
    return FactPack(
        schema_version="1.0",
        generated_at=datetime.now(UTC).isoformat(),
        ingestion_id=normalized.ingestion_id,
        source_name=normalized.source_name,
        period_start=summary.date_start,
        period_end=summary.date_end,
        filters=dict(filters or {}),
        quality_status=quality_report.overall_status,
        quality_ready=quality_report.ready_for_analysis,
        facts=tuple(facts),
        recommendations=recommendations,
        caveats=tuple(caveats),
    )
