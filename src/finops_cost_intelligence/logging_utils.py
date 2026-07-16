"""Logging setup shared by the CLI and Streamlit entry points."""

from __future__ import annotations

import logging

from .config import Settings

LOGGER_NAME = "finops_cost_intelligence"


def configure_logging(settings: Settings) -> logging.Logger:
    """Configure a concise application logger and return the project logger."""
    log_level = getattr(logging, settings.log_level)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(log_level)
    logger.debug("Logging configured for %s environment.", settings.app_env)
    return logger
