"""Build a versioned fact pack from deterministic analytical results."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from ..analytics.allocation import calculate_allocation_coverage
from ..analytics.budgets import calculate_budget_variance
from ..analytics.business_metrics import calculate_unit_economics
from ..analytics.drivers import analyze_service_cost_drivers
from ..analytics.spend import (
    aggregate_spend,
    calculate_spend_summary,
    prepare_daily_spend,
)
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


def _add_period_comparison_facts(
    facts: list[Fact],
    dataframe: pd.DataFrame,
    caveats: list[str],
    *,
    currency: str,
) -> tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp, int] | None:
    """Compare the latest window with the immediately preceding equal window."""
    try:
        daily = prepare_daily_spend(dataframe)
    except (ValueError, KeyError) as exc:
        caveats.append(f"Comparable-period trend unavailable: {exc}")
        return None
    if len(daily) < 2:
        caveats.append(
            "Comparable-period trend unavailable: at least two calendar days are required."
        )
        return None

    window_days = min(14, len(daily) // 2)
    if window_days < 1:
        return None
    recent = daily.tail(window_days)
    prior = daily.iloc[-(window_days * 2) : -window_days]
    if prior.empty:
        return None
    recent_cost = float(recent["cost"].sum())
    prior_cost = float(prior["cost"].sum())
    change_amount = recent_cost - prior_cost
    change_pct = change_amount / prior_cost if prior_cost else None
    recent_start = pd.Timestamp(recent["usage_date"].min())
    recent_end = pd.Timestamp(recent["usage_date"].max())
    prior_start = pd.Timestamp(prior["usage_date"].min())
    prior_end = pd.Timestamp(prior["usage_date"].max())
    evidence = (
        f"Latest {window_days}-day window ({recent_start.date().isoformat()} to "
        f"{recent_end.date().isoformat()}) compared with the preceding {window_days}-day "
        f"window ({prior_start.date().isoformat()} to {prior_end.date().isoformat()})"
    )
    facts.extend(
        [
            _fact(
                "comparison_window_days",
                "Comparable trend window",
                window_days,
                "days",
                evidence,
            ),
            _fact(
                "recent_period_start",
                "Latest comparison-period start",
                recent_start.date().isoformat(),
                "date",
                evidence,
            ),
            _fact(
                "recent_period_end",
                "Latest comparison-period end",
                recent_end.date().isoformat(),
                "date",
                evidence,
            ),
            _fact(
                "prior_period_start",
                "Prior comparison-period start",
                prior_start.date().isoformat(),
                "date",
                evidence,
            ),
            _fact(
                "prior_period_end",
                "Prior comparison-period end",
                prior_end.date().isoformat(),
                "date",
                evidence,
            ),
            _fact(
                "recent_period_spend",
                "Latest comparable-period spend",
                recent_cost,
                currency,
                evidence,
            ),
            _fact(
                "prior_period_spend",
                "Prior comparable-period spend",
                prior_cost,
                currency,
                evidence,
            ),
            _fact(
                "spend_change_amount",
                "Latest period spend change",
                change_amount,
                currency,
                "Latest comparable-period spend minus prior comparable-period spend",
            ),
        ]
    )
    if change_pct is not None:
        facts.append(
            _fact(
                "spend_change_pct",
                "Latest period spend change rate",
                change_pct,
                "share",
                "Latest comparable-period change divided by prior comparable-period spend",
            )
        )
    else:
        caveats.append(
            "Comparable-period percentage change is unavailable because prior spend was zero."
        )
    return recent_start, recent_end, prior_start, prior_end, window_days


def _add_service_mover_facts(
    facts: list[Fact],
    dataframe: pd.DataFrame,
    comparison: tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp, int] | None,
    *,
    currency: str,
) -> None:
    """Add service movements and the strongest explanation supported by the source."""
    if comparison is None or "service" not in dataframe.columns or dataframe.empty:
        return
    recent_start, recent_end, prior_start, prior_end, window_days = comparison
    try:
        movers = analyze_service_cost_drivers(
            dataframe,
            recent_start=recent_start,
            recent_end=recent_end,
            prior_start=prior_start,
            prior_end=prior_end,
            top_n=3,
        )
    except (ValueError, KeyError):
        return
    evidence = f"Service totals in the latest {window_days} days versus the preceding period"
    for rank, (_, row) in enumerate(movers.iterrows(), start=1):
        prefix = f"service_mover_{rank}"
        facts.extend(
            [
                _fact(
                    f"{prefix}_name",
                    f"Service mover {rank}",
                    str(row["service"]),
                    "service",
                    evidence,
                ),
                _fact(
                    f"{prefix}_direction",
                    f"Service mover {rank} direction",
                    str(row["direction"]),
                    "direction",
                    evidence,
                ),
                _fact(
                    f"{prefix}_recent_spend",
                    f"Service mover {rank} latest spend",
                    float(row["recent_spend"]),
                    currency,
                    evidence,
                ),
                _fact(
                    f"{prefix}_prior_spend",
                    f"Service mover {rank} prior spend",
                    float(row["prior_spend"]),
                    currency,
                    evidence,
                ),
                _fact(
                    f"{prefix}_change_amount",
                    f"Service mover {rank} change",
                    float(row["change_amount"]),
                    currency,
                    evidence,
                ),
                _fact(
                    f"{prefix}_driver_type",
                    f"Service mover {rank} billing driver type",
                    str(row["driver_type"]),
                    "classification",
                    "Deterministic classification from comparable cost and usage records",
                ),
                _fact(
                    f"{prefix}_explanation",
                    f"Service mover {rank} explanation",
                    str(row["explanation"]),
                    "explanation",
                    "Evidence-bounded explanation; not an operational root-cause claim",
                ),
                _fact(
                    f"{prefix}_evidence_level",
                    f"Service mover {rank} evidence level",
                    str(row["evidence_level"]),
                    "confidence",
                    "Billing-only evidence is low; comparable billing and usage is medium",
                ),
            ]
        )
        if pd.notna(row["usage_change_pct"]):
            facts.append(
                _fact(
                    f"{prefix}_usage_change_pct",
                    f"Service mover {rank} usage change rate",
                    float(row["usage_change_pct"]),
                    "share",
                    "Comparable-period usage quantity change for one consistent usage unit",
                )
            )
        if pd.notna(row["effective_rate_change_pct"]):
            facts.append(
                _fact(
                    f"{prefix}_effective_rate_change_pct",
                    f"Service mover {rank} effective rate or mix change",
                    float(row["effective_rate_change_pct"]),
                    "share",
                    (
                        "Change in cost divided by usage quantity; this can include price, "
                        "discount, commitment, credit, and resource-mix effects"
                    ),
                )
            )


def _add_forecast_facts(
    facts: list[Fact],
    dataframe: pd.DataFrame,
    caveats: list[str],
    *,
    currency: str,
) -> ForecastSummary | None:
    try:
        forecast, forecast_summary = forecast_daily_spend(dataframe, horizon_days=14)
    except (ValueError, KeyError) as exc:
        caveats.append(f"Forecast unavailable: {exc}")
        return None
    facts.extend(
        [
            _fact(
                "forecast_total",
                "14-day forecast total",
                forecast_summary.forecast_total,
                currency,
                f"{forecast_summary.method} over {forecast_summary.horizon_days} future days",
            ),
            _fact(
                "forecast_horizon_days",
                "Forecast horizon",
                forecast_summary.horizon_days,
                "days",
                "Number of future calendar days in the deterministic forecast",
            ),
            _fact(
                "forecast_lower_total",
                "14-day forecast lower bound",
                float(forecast["lower_bound"].sum()),
                currency,
                "Sum of daily lower uncertainty bounds from the deterministic forecast",
            ),
            _fact(
                "forecast_upper_total",
                "14-day forecast upper bound",
                float(forecast["upper_bound"].sum()),
                currency,
                "Sum of daily upper uncertainty bounds from the deterministic forecast",
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
                currency,
                "Residual variation from the fitted historical model",
            ),
        ]
    )
    daily = prepare_daily_spend(dataframe)
    if len(daily) >= forecast_summary.horizon_days:
        comparable_actual = float(daily.tail(forecast_summary.horizon_days)["cost"].sum())
        change_amount = forecast_summary.forecast_total - comparable_actual
        facts.extend(
            [
                _fact(
                    "forecast_comparison_actual",
                    "Most recent 14-day actual spend",
                    comparable_actual,
                    currency,
                    "Actual spend over the same number of days as the forecast horizon",
                ),
                _fact(
                    "forecast_change_amount",
                    "Forecast change versus recent actual",
                    change_amount,
                    currency,
                    "14-day forecast total minus the most recent 14-day actual spend",
                ),
            ]
        )
        if comparable_actual:
            facts.append(
                _fact(
                    "forecast_change_pct",
                    "Forecast change rate versus recent actual",
                    change_amount / comparable_actual,
                    "share",
                    "Forecast change divided by the most recent 14-day actual spend",
                )
            )
    else:
        caveats.append(
            "Forecast-to-recent comparison is unavailable because fewer than 14 historical "
            "calendar days are selected."
        )
    return forecast_summary


def _add_anomaly_facts(
    facts: list[Fact],
    dataframe: pd.DataFrame,
    caveats: list[str],
    *,
    currency: str,
) -> AnomalySummary | None:
    try:
        diagnostics, anomaly_summary = detect_spend_anomalies(dataframe)
    except (ValueError, KeyError) as exc:
        caveats.append(f"Anomaly scan unavailable: {exc}")
        return None
    facts.append(
        _fact(
            "anomaly_count",
            "Meaningful anomaly count",
            anomaly_summary.anomaly_count,
            "days",
            (
                f"{anomaly_summary.method}, {anomaly_summary.window_days}-day window, "
                f"threshold {anomaly_summary.threshold}"
            ),
        )
    )
    anomalies = diagnostics.loc[diagnostics["is_anomaly"]].copy()
    if anomalies.empty:
        return anomaly_summary
    increases = anomalies.loc[anomalies["absolute_change"].gt(0)].copy()
    decreases = anomalies.loc[anomalies["absolute_change"].lt(0)].copy()
    facts.extend(
        [
            _fact(
                "anomaly_increase_count",
                "Upward anomaly count",
                len(increases),
                "days",
                "Flagged days with actual spend above the prior rolling baseline",
            ),
            _fact(
                "anomaly_decrease_count",
                "Downward anomaly count",
                len(decreases),
                "days",
                "Flagged days with actual spend below the prior rolling baseline",
            ),
            _fact(
                "anomaly_estimated_increase_total",
                "Spend above baseline on upward anomaly days",
                float(increases["absolute_change"].sum()),
                currency,
                (
                    "Sum of actual daily spend above each flagged day's rolling baseline; "
                    "this is investigation impact, not confirmed waste or savings"
                ),
            ),
        ]
    )
    ranked = (
        increases
        if not increases.empty
        else anomalies.assign(_rank_change=anomalies["absolute_change"].abs())
    )
    sort_column = "absolute_change" if not increases.empty else "_rank_change"
    top = ranked.sort_values(sort_column, ascending=False).iloc[0]
    top_date = pd.Timestamp(top["usage_date"])
    facts.extend(
        [
            _fact(
                "top_anomaly_date",
                "Largest flagged change date",
                top_date.date().isoformat(),
                "date",
                "Flagged date with the largest upward deviation, or largest absolute deviation",
            ),
            _fact(
                "top_anomaly_actual_spend",
                "Largest flagged date actual spend",
                float(top["cost"]),
                currency,
                "Canonical daily spend on the largest flagged date",
            ),
            _fact(
                "top_anomaly_expected_spend",
                "Largest flagged date baseline",
                float(top["expected_cost"]),
                currency,
                "Prior rolling median baseline for the largest flagged date",
            ),
            _fact(
                "top_anomaly_change_amount",
                "Largest flagged date difference",
                float(top["absolute_change"]),
                currency,
                "Actual daily spend minus the prior rolling baseline",
            ),
            _fact(
                "top_anomaly_direction",
                "Largest flagged date direction",
                str(top["direction"]),
                "direction",
                "Direction of the largest flagged daily change",
            ),
            _fact(
                "top_anomaly_severity",
                "Largest flagged date severity",
                str(top["severity"]),
                "severity",
                "Severity assigned by the deterministic anomaly detector",
            ),
        ]
    )
    if "service" in dataframe.columns:
        dates = pd.to_datetime(dataframe["usage_date"], errors="coerce").dt.normalize()
        day = dataframe.loc[dates.eq(top_date.normalize())]
        if not day.empty:
            service = aggregate_spend(day, "service", top_n=1).iloc[0]
            facts.extend(
                [
                    _fact(
                        "top_anomaly_largest_service",
                        "Largest service on the top flagged date",
                        str(service["value"]),
                        "service",
                        "Largest service by canonical spend on the top flagged date",
                    ),
                    _fact(
                        "top_anomaly_largest_service_spend",
                        "Largest service spend on the top flagged date",
                        float(service["cost"]),
                        currency,
                        "Canonical spend for the largest service on the top flagged date",
                    ),
                ]
            )
    return anomaly_summary


def _add_quality_facts(facts: list[Fact], quality_report: QualityReport) -> None:
    nonpassing = [check for check in quality_report.checks if check.status != "pass"]
    facts.extend(
        [
            _fact(
                "quality_status",
                "Data-quality status",
                quality_report.overall_status,
                "status",
                "Overall result of the deterministic data-quality checks",
            ),
            _fact(
                "quality_exception_count",
                "Data-quality exception count",
                len(nonpassing),
                "checks",
                "Number of quality checks that did not return pass",
            ),
        ]
    )
    difference = quality_report.reconciliation.absolute_difference
    if difference is not None:
        facts.append(
            _fact(
                "reconciliation_difference",
                "Source-to-canonical reconciliation difference",
                difference,
                "cost units",
                "Absolute difference between source-derived and canonical cost totals",
            )
        )


def _deduplicate(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


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
            _fact(
                "calendar_days",
                "Selected calendar days",
                summary.calendar_days,
                "days",
                "Inclusive number of calendar days in the selected billing period",
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
        service_breakdown = aggregate_spend(selected, "service", top_n=3)
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
                        "top_service_cost",
                        "Largest service spend",
                        float(service_breakdown.iloc[0]["cost"]),
                        summary.currency,
                        "Canonical spend for the largest service in the selected period",
                    ),
                    _fact(
                        "top_service_share",
                        "Largest service share",
                        float(service_breakdown.iloc[0]["share_of_total"]),
                        "share",
                        ("Largest service cost divided by total selected-period cost"),
                    ),
                    _fact(
                        "top_three_service_share",
                        "Top three services share",
                        float(service_breakdown["share_of_total"].sum()),
                        "share",
                        (
                            "Combined canonical spend for the three largest services "
                            "divided by total spend"
                        ),
                    ),
                ]
            )

    comparison = _add_period_comparison_facts(
        facts,
        selected,
        caveats,
        currency=summary.currency,
    )
    _add_service_mover_facts(
        facts,
        selected,
        comparison,
        currency=summary.currency,
    )

    try:
        allocation = calculate_allocation_coverage(selected)
        any_ownership = allocation.loc[allocation["field"].eq("any ownership field")].iloc[0]
        if pd.notna(any_ownership["cost_coverage"]):
            facts.extend(
                [
                    _fact(
                        "allocation_cost_coverage",
                        "Positive cost with any ownership field",
                        float(any_ownership["cost_coverage"]),
                        "share",
                        "Positive-cost-weighted coverage across available ownership fields",
                    ),
                    _fact(
                        "unallocated_positive_spend",
                        "Positive spend without an ownership field",
                        float(any_ownership["positive_cost"])
                        - float(any_ownership["allocated_positive_cost"]),
                        summary.currency,
                        (
                            "Positive canonical spend without account, department, project, "
                            "or environment ownership"
                        ),
                    ),
                ]
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
                        summary.currency,
                        "Sum of normalized budget rows",
                    ),
                    _fact(
                        "budget_actual_total",
                        "Actual cost matched to budget",
                        budget_summary.actual_total,
                        summary.currency,
                        ("Actual canonical cost matched to each budget period and scope"),
                    ),
                    _fact(
                        "budget_variance_amount",
                        "Actual minus budget",
                        budget_summary.variance_amount,
                        summary.currency,
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
            if budget_summary.budget_total:
                facts.append(
                    _fact(
                        "budget_variance_pct",
                        "Actual-versus-budget variance rate",
                        budget_summary.variance_amount / budget_summary.budget_total,
                        "share",
                        "Actual-minus-budget variance divided by supplied budget",
                    )
                )
    else:
        caveats.append(
            "No budget data was supplied; budget status and forecast-to-budget risk "
            "are unavailable."
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
                        ("Total selected cost divided by selected business metric total"),
                    ),
                ]
            )
    else:
        caveats.append(
            "No business metric was selected; revenue, customer, transaction, and "
            "unit-economics context is unavailable."
        )

    _add_forecast_facts(
        facts,
        selected,
        caveats,
        currency=summary.currency,
    )
    _add_anomaly_facts(
        facts,
        selected,
        caveats,
        currency=summary.currency,
    )
    _add_quality_facts(facts, quality_report)
    caveats.append(
        "Potential savings are not quantified because billing data alone does not prove "
        "rightsizing, utilization, commitment, or rate-optimization value."
    )
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
        caveats=_deduplicate(caveats),
    )
