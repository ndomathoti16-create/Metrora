"""End-to-end smoke test for the simplified Metrora workspace."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from finops_cost_intelligence.ui.branding import METRORA_WORKSPACE_V2_CSS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "app.py"
DEMO_BILLING_PATH = PROJECT_ROOT / "data" / "demo" / "cloud_billing_demo.csv"


def test_public_product_page_renders_the_complete_scrolling_story() -> None:
    """The public site should combine the overview, workflow, and trust story."""
    app = AppTest.from_file(APP_PATH).run(timeout=30)
    assert not app.exception

    rendered_copy = " ".join(item.value for item in app.markdown)
    assert "One defensible path from raw export to recommendation." in rendered_copy
    assert "Numbers first. Narrative second." in rendered_copy
    assert app.button(key="product_demo_hero")


def test_shared_theme_exposes_keyboard_focus_and_accessible_icon_targets() -> None:
    """Regression guard for controls that Streamlit and Plotly render very small."""
    assert ":focus-visible" in METRORA_WORKSPACE_V2_CSS
    assert '[data-testid="stHeaderActionElements"] a' in METRORA_WORKSPACE_V2_CSS
    assert '[data-testid="stPlotlyChart"] .modebar-btn' in METRORA_WORKSPACE_V2_CSS
    assert "min-height: 1.5rem" in METRORA_WORKSPACE_V2_CSS


def test_workspace_headings_use_page_specific_anchors() -> None:
    """Workspace heading links must follow the selected destination."""
    source = (PROJECT_ROOT / "src/finops_cost_intelligence/ui/workspace_view.py").read_text(
        encoding="utf-8"
    )

    assert 'heading_id = page.lower().replace(" & ", "-").replace(" ", "-")' in source
    assert 'class="metrora-workspace-page-title" id="{escape(heading_id)}"' in source
    assert 'role="heading" aria-level="1">{escape(title)}</div>' in source


def test_guided_workspace_pages_render_without_errors() -> None:
    """The guided demo should open every primary workspace destination successfully."""
    app = AppTest.from_file(APP_PATH).run(timeout=30)
    assert not app.exception

    app.button(key="product_demo_hero").click().run(timeout=30)
    assert app.session_state["product_page"] == "Demo"
    app.button(key="product_demo_scenario_forecast_risk").click().run(timeout=30)
    assert not app.exception
    # The product and workspace intentionally share one dark visual system.
    assert app.session_state["dark_mode"] is True
    assert app.session_state["budget_table"] is not None
    assert app.session_state["business_metrics_table"] is not None
    assert {metric.label for metric in app.metric} >= {
        "Current window spend",
        "Change vs prior",
        "Next 14 days",
        "Anomalies to review",
    }

    expected_content = (
        ("top_workspace_nav_cost_explorer", "Total spend"),
        ("top_workspace_nav_plans_alerts", "Forecast"),
        ("top_workspace_nav_decisions", "Priority queue"),
        ("top_workspace_nav_reports", "The decision in one minute"),
        ("top_workspace_nav_connections", "Upload a file"),
        ("top_workspace_nav_advanced", "Automatic field mapping"),
        ("top_workspace_nav_home", "Current window spend"),
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


def test_desktop_mode_opens_real_workspace_and_restores_data_sources(monkeypatch) -> None:
    """The packaged app should skip the product site and preserve its workspace route."""
    monkeypatch.setenv("METRORA_DESKTOP", "1")
    app = AppTest.from_file(APP_PATH)
    app.query_params.update({"surface": "workspace", "page": "Connections"})
    app.run(timeout=30)

    assert not app.exception
    assert app.session_state["desktop_mode"] is True
    assert app.session_state["demo_authenticated"] is True
    assert app.session_state["workspace_page"] == "Connections"
    assert "Upload a file" in {item.label for item in app.tabs}
    assert "top_workspace_back_to_product" not in {item.key for item in app.button}


def test_one_upload_opens_a_complete_analysis_automatically() -> None:
    """A first-time user should not need a separate mapping or validation action."""
    app = AppTest.from_file(APP_PATH).run(timeout=30)
    app.button(key="product_demo_hero").click().run(timeout=30)
    app.button(key="product_demo_scenario_forecast_risk").click().run(timeout=30)
    app.button(key="top_workspace_new_analysis").click().run(timeout=30)

    content = DEMO_BILLING_PATH.read_bytes()
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


def test_refresh_restores_the_selected_demo_workspace_page() -> None:
    """A shared demo route should reconstruct the scenario and active workspace page."""
    app = AppTest.from_file(APP_PATH)
    app.query_params.update(
        {
            "surface": "workspace",
            "page": "Reports",
            "scenario": "forecast_risk",
        }
    )
    app.run(timeout=30)

    assert not app.exception
    assert app.session_state["demo_authenticated"] is True
    assert app.session_state["demo_scenario"] == "forecast_risk"
    assert app.session_state["workspace_page"] == "Reports"
    assert "The decision in one minute" in {item.value for item in app.subheader}


def test_hero_opens_the_scenario_chooser_not_a_preselected_workspace() -> None:
    """The public CTA must let visitors choose their own demo story first."""
    app = AppTest.from_file(APP_PATH).run(timeout=30)

    app.button(key="product_demo_hero").click().run(timeout=30)

    assert not app.exception
    assert app.session_state["product_page"] == "Demo"
    assert "demo_authenticated" not in app.session_state
    assert {
        "product_demo_scenario_healthy",
        "product_demo_scenario_quality_risk",
        "product_demo_scenario_forecast_risk",
    } <= {item.key for item in app.button}
