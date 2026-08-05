"""Streamlit entry point for SpendArc."""

from finops_cost_intelligence.config import Settings
from finops_cost_intelligence.logging_utils import configure_logging
from finops_cost_intelligence.ui.app_shell import render_app_shell


def main() -> None:
    """Load settings, configure logging, and render the application shell."""
    settings = Settings.from_environment()
    settings.ensure_directories()
    configure_logging(settings)
    render_app_shell(settings)


if __name__ == "__main__":
    main()
