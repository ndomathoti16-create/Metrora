"""Deterministic service-level cost-driver diagnostics.

The routines in this module explain what the billing and usage records support.
They intentionally stop short of claiming an operational root cause because that
requires deployment, telemetry, pricing, or change-event evidence.
"""

from __future__ import annotations

import math

import pandas as pd

from ..contracts.analytics import AnalyticsInputError

DRIVER_COLUMNS = (
    "service",
    "recent_spend",
    "prior_spend",
    "change_amount",
    "change_pct",
    "direction",
    "driver_type",
    "explanation",
    "evidence_level",
    "usage_change_pct",
    "effective_rate_change_pct",
    "usage_unit",
    "usage_effect",
    "rate_mix_effect",
)


def _empty_driver_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=DRIVER_COLUMNS)


def _service_values(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip()
    return values.where(values.notna() & values.ne(""), "Unallocated").astype(str)


def _billing_only_explanation() -> tuple[str, str, str]:
    return (
        "Billing records identify this service as a spend driver, but comparable usage "
        "context is unavailable. Connect usage or deployment evidence to confirm root cause.",
        "Billing-only",
        "Low — billing only",
    )


def _usage_explanation(
    recent: pd.DataFrame,
    prior: pd.DataFrame,
) -> dict[str, object]:
    explanation, driver_type, evidence_level = _billing_only_explanation()
    result: dict[str, object] = {
        "driver_type": driver_type,
        "explanation": explanation,
        "evidence_level": evidence_level,
        "usage_change_pct": None,
        "effective_rate_change_pct": None,
        "usage_unit": None,
        "usage_effect": None,
        "rate_mix_effect": None,
    }
    if not {"usage_quantity", "usage_unit"}.issubset(recent.columns):
        return result

    combined_units = pd.concat(
        [recent["usage_unit"], prior["usage_unit"]], ignore_index=True
    ).astype("string")
    units = combined_units.str.strip().loc[lambda values: values.notna() & values.ne("")]
    unique_units = units.unique().tolist()
    if len(unique_units) != 1:
        return result

    recent_usage_values = pd.to_numeric(recent["usage_quantity"], errors="coerce").dropna()
    prior_usage_values = pd.to_numeric(prior["usage_quantity"], errors="coerce").dropna()
    if recent_usage_values.empty or prior_usage_values.empty:
        return result

    recent_usage = float(recent_usage_values.sum())
    prior_usage = float(prior_usage_values.sum())
    recent_cost = float(pd.to_numeric(recent["cost"], errors="coerce").sum())
    prior_cost = float(pd.to_numeric(prior["cost"], errors="coerce").sum())
    if (
        recent_usage <= 0
        or prior_usage <= 0
        or recent_cost < 0
        or prior_cost <= 0
    ):
        return result

    recent_rate = recent_cost / recent_usage
    prior_rate = prior_cost / prior_usage
    if not all(math.isfinite(value) for value in (recent_rate, prior_rate)) or prior_rate == 0:
        return result

    usage_change_pct = (recent_usage - prior_usage) / prior_usage
    rate_change_pct = (recent_rate - prior_rate) / prior_rate
    usage_effect = (recent_usage - prior_usage) * ((prior_rate + recent_rate) / 2)
    rate_mix_effect = (recent_rate - prior_rate) * ((prior_usage + recent_usage) / 2)
    effect_total = abs(usage_effect) + abs(rate_mix_effect)

    if effect_total <= 0.005:
        driver_type = "Stable usage and rate/mix"
        explanation = (
            "Usage and effective cost per usage unit were stable in the comparable windows. "
            "The remaining movement is immaterial at the service level."
        )
    elif usage_effect * rate_mix_effect < 0 and min(
        abs(usage_effect), abs(rate_mix_effect)
    ) > effect_total * 0.1:
        driver_type = "Offsetting usage and rate/mix"
        explanation = (
            "Usage and effective cost per usage unit moved in opposing directions. Inspect "
            "resource-level usage and pricing before assigning an operational root cause."
        )
    else:
        usage_share = abs(usage_effect) / effect_total
        rate_share = abs(rate_mix_effect) / effect_total
        if usage_share >= 0.7:
            driver_type = "Usage-driven"
            explanation = (
                "Usage movement was the dominant billing-observed factor; effective cost per "
                "usage unit was comparatively stable."
            )
        elif rate_share >= 0.7:
            driver_type = "Effective rate/mix-driven"
            explanation = (
                "Effective cost per usage unit was the dominant billing-observed factor. "
                "Pricing, discount, and resource-mix data are needed to separate the cause."
            )
        else:
            driver_type = "Combined usage and rate/mix"
            explanation = (
                "Usage and effective cost per usage unit moved together, supporting a combined "
                "billing explanation. Operational events are still needed to confirm root cause."
            )

    result.update(
        {
            "driver_type": driver_type,
            "explanation": explanation,
            "evidence_level": "Medium — billing + comparable usage",
            "usage_change_pct": usage_change_pct,
            "effective_rate_change_pct": rate_change_pct,
            "usage_unit": str(unique_units[0]),
            "usage_effect": usage_effect,
            "rate_mix_effect": rate_mix_effect,
        }
    )
    return result


def analyze_service_cost_drivers(
    dataframe: pd.DataFrame,
    *,
    recent_start: object,
    recent_end: object,
    prior_start: object,
    prior_end: object,
    top_n: int | None = 3,
) -> pd.DataFrame:
    """Rank service movements and explain the evidence-supported billing mechanism.

    Cost movement is decomposed into a usage effect and an effective cost-per-unit
    effect when one comparable usage unit is available for a service. The latter is
    deliberately labelled ``rate/mix`` because billing data alone cannot distinguish
    list-price changes, discounts, resource mix, credits, or commitment effects.
    """
    required = {"usage_date", "service", "cost"}
    missing = sorted(required.difference(dataframe.columns))
    if missing:
        raise AnalyticsInputError(
            "Cost-driver analysis requires canonical column(s): " + ", ".join(missing)
        )
    if top_n is not None and top_n < 1:
        raise AnalyticsInputError("top_n must be at least 1 or None.")
    if dataframe.empty:
        return _empty_driver_frame()

    working = dataframe.copy()
    working["usage_date"] = pd.to_datetime(working["usage_date"], errors="coerce").dt.normalize()
    working["cost"] = pd.to_numeric(working["cost"], errors="coerce")
    working["_service"] = _service_values(working["service"])
    working = working.dropna(subset=["usage_date", "cost"])
    if working.empty:
        return _empty_driver_frame()

    bounds = [pd.to_datetime(value, errors="coerce") for value in (
        recent_start,
        recent_end,
        prior_start,
        prior_end,
    )]
    if any(pd.isna(value) for value in bounds):
        raise AnalyticsInputError("Cost-driver comparison dates must be valid.")
    recent_start_ts, recent_end_ts, prior_start_ts, prior_end_ts = (
        pd.Timestamp(value).normalize() for value in bounds
    )
    if recent_end_ts < recent_start_ts or prior_end_ts < prior_start_ts:
        raise AnalyticsInputError("Cost-driver period end cannot precede its start.")

    recent = working.loc[
        working["usage_date"].between(recent_start_ts, recent_end_ts, inclusive="both")
    ].copy()
    prior = working.loc[
        working["usage_date"].between(prior_start_ts, prior_end_ts, inclusive="both")
    ].copy()
    if recent.empty and prior.empty:
        return _empty_driver_frame()

    def spend_by_service(period: pd.DataFrame, label: str) -> pd.DataFrame:
        return (
            period.groupby("_service", as_index=False)["cost"]
            .sum()
            .rename(columns={"_service": "service", "cost": label})
        )

    movers = spend_by_service(recent, "recent_spend").merge(
        spend_by_service(prior, "prior_spend"),
        on="service",
        how="outer",
    ).fillna(0.0)
    movers["change_amount"] = movers["recent_spend"] - movers["prior_spend"]
    movers["change_pct"] = movers.apply(
        lambda row: (
            float(row["change_amount"]) / float(row["prior_spend"])
            if float(row["prior_spend"]) != 0
            else None
        ),
        axis=1,
    )
    movers["absolute_change"] = movers["change_amount"].abs()
    movers = movers.loc[movers["absolute_change"].gt(0.005)].sort_values(
        ["absolute_change", "service"], ascending=[False, True]
    )
    if top_n is not None:
        movers = movers.head(top_n)

    rows: list[dict[str, object]] = []
    for _, mover in movers.iterrows():
        service = str(mover["service"])
        usage = _usage_explanation(
            recent.loc[recent["_service"].eq(service)],
            prior.loc[prior["_service"].eq(service)],
        )
        rows.append(
            {
                "service": service,
                "recent_spend": float(mover["recent_spend"]),
                "prior_spend": float(mover["prior_spend"]),
                "change_amount": float(mover["change_amount"]),
                "change_pct": mover["change_pct"],
                "direction": "increase" if float(mover["change_amount"]) > 0 else "decrease",
                **usage,
            }
        )
    return pd.DataFrame(rows, columns=DRIVER_COLUMNS)
