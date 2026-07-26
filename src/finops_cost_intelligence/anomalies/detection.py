"""Leakage-safe robust anomaly detection for daily cloud spend."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..analytics.spend import prepare_daily_spend
from ..contracts.analytics import AnalyticsInputError
from ..contracts.anomaly import AnomalySummary


def detect_spend_anomalies(
    dataframe: pd.DataFrame,
    *,
    window_days: int = 14,
    threshold: float = 3.5,
    minimum_history_days: int = 7,
) -> tuple[pd.DataFrame, AnomalySummary]:
    """Flag daily spend changes against a prior rolling median and MAD.

    The one-day shift is intentional: a day is never used to calculate its own
    expected value, so the detector does not leak the observation into its baseline.
    """
    if not isinstance(window_days, int) or window_days < 3:
        raise AnalyticsInputError("window_days must be an integer of at least 3.")
    if not isinstance(minimum_history_days, int) or minimum_history_days < 3:
        raise AnalyticsInputError("minimum_history_days must be an integer of at least 3.")
    if minimum_history_days > window_days:
        raise AnalyticsInputError("minimum_history_days cannot exceed window_days.")
    if threshold <= 0:
        raise AnalyticsInputError("threshold must be greater than zero.")
    daily = prepare_daily_spend(dataframe)
    if daily.empty:
        return pd.DataFrame(), AnomalySummary(
            method="rolling_median_mad",
            threshold=threshold,
            window_days=window_days,
            minimum_history_days=minimum_history_days,
            anomaly_count=0,
        )
    values = daily["cost"].astype(float)
    prior = values.shift(1)
    baseline = prior.rolling(window_days, min_periods=minimum_history_days).median()
    deviations = (prior - baseline).abs()
    mad = deviations.rolling(window_days, min_periods=minimum_history_days).median()
    robust_scale = mad * 1.4826
    standard_scale = prior.rolling(window_days, min_periods=minimum_history_days).std(ddof=1)
    scale = robust_scale.where(robust_scale > 0, standard_scale)
    history_count = prior.rolling(window_days, min_periods=minimum_history_days).count()
    score = (values - baseline).div(scale)
    zero_scale = scale.fillna(0).eq(0)
    score = score.mask(zero_scale & baseline.notna() & values.ne(baseline), np.inf)
    score = score.fillna(0.0)
    valid = history_count.ge(minimum_history_days) & baseline.notna()
    is_anomaly = valid & score.abs().ge(threshold)
    output = daily.assign(
        expected_cost=baseline,
        absolute_change=values - baseline,
        change_pct=(values - baseline).div(baseline.abs().where(baseline.abs().gt(0))),
        anomaly_score=score,
        is_anomaly=is_anomaly,
        direction=np.where(values >= baseline, "increase", "decrease"),
        severity=np.where(score.abs().ge(5), "high", "medium"),
    )
    output.loc[~valid, "severity"] = "insufficient_history"
    output.loc[~is_anomaly, "severity"] = "normal"
    anomalies = output.loc[output["is_anomaly"]].copy().reset_index(drop=True)
    summary = AnomalySummary(
        method="rolling_median_mad",
        threshold=threshold,
        window_days=window_days,
        minimum_history_days=minimum_history_days,
        anomaly_count=len(anomalies),
    )
    return output, summary
