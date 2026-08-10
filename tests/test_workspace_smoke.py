"""End-to-end smoke test for the simplified Metrora workspace."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_guided_workspace_pages_render_without_errors() -> None:
    """The guided demo should open every primary workspace destination successfully."""
    app = AppTest.from_file("app.py").run(timeout=30)
    assert not app.exception

    app.button(key="product_demo_hero").click().run(timeout=30)
    assert not app.exception
    # The product and workspace intentionally share one dark visual system.
    assert app.session_state["dark_mode"] is True
    assert {metric.label for metric in app.metric} >= {
        "Current window spend",
        "Change vs prior",
        "Next 14 days",
        "Anomalies to review",
    }

    expected_content = (
        ("workspace_nav_cost_explorer", "Total spend"),
        ("workspace_nav_plans_alerts", "Forecast"),
        ("workspace_nav_reports", "What leaders need to know"),
        ("workspace_nav_advanced", "Automatic field mapping"),
        ("workspace_nav_home", "Current window spend"),
    )
    for button_key, expected in expected_content:
        app.button(key=button_key).click().run(timeout=30)
        assert not app.exception
        visible_labels = (
            {item.value for item in app.subheader}
            | {item.label for item in app.metric}
            | {item.label for item in app.tabs}
        )
        assert expected in visible_labels


def test_one_upload_opens_a_complete_analysis_automatically() -> None:
    """A first-time user should not need a separate mapping or validation action."""
    app = AppTest.from_file("app.py").run(timeout=30)
    app.button(key="product_demo_hero").click().run(timeout=30)
    app.button(key="new_analysis").click().run(timeout=30)

    content = Path("data/demo/cloud_billing_demo.csv").read_bytes()
    app.file_uploader(key="billing_upload").upload(
        "billing.csv",
        content,
        "text/csv",
    ).run(timeout=30)

    assert not app.exception
    assert app.session_state["workspace_page"] == "Home"
    assert app.session_state["quality_report"].ready_for_analysis
    assert {metric.label for metric in app.metric} >= {
        "Current window spend",
        "Change vs prior",
        "Next 14 days",
        "Anomalies to review",
    }
