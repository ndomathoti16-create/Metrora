import pandas as pd
import pytest

from finops_cost_intelligence.anomalies import detect_spend_anomalies
from finops_cost_intelligence.contracts.analytics import AnalyticsInputError
from finops_cost_intelligence.contracts.forecasting import ForecastInputError
from finops_cost_intelligence.forecasting import forecast_daily_spend


def _daily_costs(values: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "usage_date": pd.date_range("2025-01-01", periods=len(values), freq="D"),
            "cost": values,
        }
    )


def test_forecast_uses_short_history_fallback_and_future_dates():
    data = _daily_costs([10.0, 20.0, 30.0])

    forecast, summary = forecast_daily_spend(data, horizon_days=4)

    assert summary.method == "rolling_mean"
    assert len(forecast) == 4
    assert forecast["usage_date"].min() == pd.Timestamp("2025-01-04")
    assert forecast["forecast_cost"].tolist() == [20.0] * 4
    assert (forecast["lower_bound"] >= 0).all()


def test_forecast_supports_long_history_and_returns_nonnegative_output():
    data = _daily_costs([100.0 + (index % 7) * 5 for index in range(35)])

    forecast, summary = forecast_daily_spend(data, horizon_days=7)

    assert summary.method in {"holt_winters_weekly", "holt_trend", "rolling_mean"}
    assert summary.history_end == "2025-02-04"
    assert len(forecast) == 7
    assert (forecast["forecast_cost"] >= 0).all()
    assert summary.forecast_total == pytest.approx(forecast["forecast_cost"].sum())


def test_forecast_rejects_invalid_horizon():
    with pytest.raises(ForecastInputError, match="between 1 and 90"):
        forecast_daily_spend(_daily_costs([10.0]), horizon_days=0)


def test_anomaly_detector_flags_spike_without_using_spike_in_baseline():
    data = _daily_costs([10.0] * 14 + [100.0] + [10.0, 10.0])

    diagnostics, summary = detect_spend_anomalies(data)

    assert summary.anomaly_count >= 1
    spike = diagnostics.loc[diagnostics["usage_date"].eq(pd.Timestamp("2025-01-15"))].iloc[0]
    assert bool(spike["is_anomaly"])
    assert spike["expected_cost"] == 10.0
    assert spike["direction"] == "increase"


def test_anomaly_detector_rejects_inconsistent_history_parameters():
    with pytest.raises(AnalyticsInputError, match="cannot exceed"):
        detect_spend_anomalies(_daily_costs([10.0] * 10), window_days=5, minimum_history_days=6)
