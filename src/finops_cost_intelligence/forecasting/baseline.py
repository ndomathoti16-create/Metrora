"""Daily cloud-spend forecasting with an auditable fallback baseline."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from ..analytics.spend import prepare_daily_spend
from ..contracts.forecasting import ForecastInputError, ForecastSummary


def _rolling_mean_forecast(values: pd.Series, horizon_days: int) -> tuple[pd.Series, str, float]:
    window = min(7, len(values))
    level = float(values.tail(window).mean())
    residuals = values - values.rolling(window, min_periods=1).mean()
    residual_std = float(residuals.std(ddof=1)) if len(residuals) > 1 else 0.0
    return pd.Series(level, index=range(horizon_days), dtype=float), "rolling_mean", residual_std


def forecast_daily_spend(
    dataframe: pd.DataFrame,
    *,
    horizon_days: int = 14,
) -> tuple[pd.DataFrame, ForecastSummary]:
    """Forecast future daily cost and return uncertainty bounds.

    A Holt-Winters model is used when enough history is available. Short or
    difficult histories use a trailing seven-day mean, keeping the output useful
    while making the modeling limitation explicit in the method label.
    """
    valid_horizon = (
        isinstance(horizon_days, int)
        and not isinstance(horizon_days, bool)
        and 1 <= horizon_days <= 90
    )
    if not valid_horizon:
        raise ForecastInputError("horizon_days must be an integer between 1 and 90.")
    daily = prepare_daily_spend(dataframe)
    if daily.empty:
        raise ForecastInputError("At least one valid billing day is required to forecast.")
    values = daily["cost"].astype(float).reset_index(drop=True)
    forecast_values: pd.Series
    method: str
    residual_std: float
    if len(values) >= 14:
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing

            use_weekly_seasonality = len(values) >= 28
            model = ExponentialSmoothing(
                values,
                trend="add",
                seasonal="add" if use_weekly_seasonality else None,
                seasonal_periods=7 if use_weekly_seasonality else None,
                initialization_method="estimated",
            )
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fitted = model.fit(optimized=True)
            forecast_values = pd.Series(fitted.forecast(horizon_days), dtype=float).reset_index(
                drop=True
            )
            method = "holt_winters_weekly" if use_weekly_seasonality else "holt_trend"
            residuals = values - pd.Series(fitted.fittedvalues).reset_index(drop=True)
            residual_std = float(residuals.std(ddof=1)) if len(residuals) > 1 else 0.0
        except (ValueError, TypeError, RuntimeError, np.linalg.LinAlgError):
            forecast_values, method, residual_std = _rolling_mean_forecast(values, horizon_days)
    else:
        forecast_values, method, residual_std = _rolling_mean_forecast(values, horizon_days)

    forecast_values = forecast_values.clip(lower=0.0)
    residual_std = max(0.0, residual_std)
    future_dates = pd.date_range(
        daily["usage_date"].max() + pd.Timedelta(value=1, unit="D"),
        periods=horizon_days,
        freq="D",
    )
    uncertainty = 1.96 * residual_std
    output = pd.DataFrame(
        {
            "usage_date": future_dates,
            "forecast_cost": forecast_values.to_numpy(),
            "lower_bound": (forecast_values - uncertainty).clip(lower=0.0).to_numpy(),
            "upper_bound": (forecast_values + uncertainty).to_numpy(),
        }
    )
    summary = ForecastSummary(
        method=method,
        history_start=daily["usage_date"].min().date().isoformat(),
        history_end=daily["usage_date"].max().date().isoformat(),
        horizon_days=horizon_days,
        forecast_total=float(output["forecast_cost"].sum()),
        residual_std=residual_std,
    )
    return output, summary
