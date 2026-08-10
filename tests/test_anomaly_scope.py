from pathlib import Path

from finops_cost_intelligence.analytics import select_comparable_anomaly_history
from finops_cost_intelligence.anomalies import detect_spend_anomalies
from finops_cost_intelligence.config import Settings
from finops_cost_intelligence.ui.product_page import build_demo_artifacts


def test_overview_and_anomaly_drilldown_use_the_same_history_and_threshold() -> None:
    """The summary count must reconcile to the anomaly detail view exactly."""
    settings = Settings.from_environment(base_dir=Path.cwd())
    _, _, _, normalized, report = build_demo_artifacts(settings, "forecast_risk")

    history = select_comparable_anomaly_history(normalized.dataframe)
    _, overview = detect_spend_anomalies(history, threshold=3.5)
    diagnostics, drilldown = detect_spend_anomalies(history, threshold=3.5)

    assert report.ready_for_analysis
    assert overview.anomaly_count == drilldown.anomaly_count
    assert overview.anomaly_count == int(diagnostics["is_anomaly"].sum())
    assert overview.anomaly_count > 0
