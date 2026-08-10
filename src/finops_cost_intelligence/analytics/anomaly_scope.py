"""Shared historical scope used by Metrora's anomaly surfaces."""

from __future__ import annotations

import pandas as pd

from .spend import filter_billing_data, prepare_daily_spend


def select_comparable_anomaly_history(
    dataframe: pd.DataFrame,
    *,
    maximum_window_days: int = 14,
) -> pd.DataFrame:
    """Return the latest two equal windows for a consistent anomaly scan.

    The Overview compares the newest period with its immediately preceding equal period.
    The anomaly surface uses that same historical slice so its headline count and its
    drill-down always reconcile.
    """
    daily = prepare_daily_spend(dataframe)
    if len(daily) < 2:
        return dataframe.copy()

    window_days = min(maximum_window_days, len(daily) // 2)
    if window_days < 1:
        return dataframe.copy()
    history_end = pd.Timestamp(daily["usage_date"].max()).normalize()
    history_start = history_end - pd.Timedelta(int((window_days * 2) - 1), unit="D")
    return filter_billing_data(
        dataframe,
        date_start=history_start,
        date_end=history_end,
    )
