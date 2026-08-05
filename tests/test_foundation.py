from __future__ import annotations

import logging
import tempfile
import unittest
from pathlib import Path

from finops_cost_intelligence import __version__
from finops_cost_intelligence.config import ConfigurationError, Settings
from finops_cost_intelligence.logging_utils import LOGGER_NAME, configure_logging


class SettingsTests(unittest.TestCase):
    def test_default_settings_are_safe_for_local_development(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            settings = Settings.from_environment(base_dir=Path(temporary_directory))

            self.assertEqual(settings.app_env, "development")
            self.assertEqual(settings.ai_provider, "none")
            self.assertEqual(settings.max_upload_mb, 200)
            self.assertEqual(
                settings.data_dir,
                (Path(temporary_directory) / "data").resolve(),
            )
            self.assertEqual(
                settings.db_path,
                (Path(temporary_directory) / "data" / "spendarc.duckdb").resolve(),
            )

    def test_ensure_directories_creates_runtime_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            settings = Settings.from_environment(base_dir=Path(temporary_directory))
            settings.ensure_directories()

            self.assertTrue(settings.data_dir.is_dir())
            self.assertTrue(settings.db_path.parent.is_dir())

    def test_invalid_upload_limit_is_rejected(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "MAX_UPLOAD_MB"):
            Settings.from_environment({"MAX_UPLOAD_MB": "not-a-number"})

    def test_invalid_environment_is_rejected(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "APP_ENV"):
            Settings.from_environment({"APP_ENV": "staging"})


class FoundationTests(unittest.TestCase):
    def test_package_version_is_defined(self) -> None:
        self.assertEqual(__version__, "0.1.0")

    def test_logging_configuration_returns_project_logger(self) -> None:
        settings = Settings.from_environment({"LOG_LEVEL": "DEBUG"})
        logger = configure_logging(settings)

        self.assertEqual(logger.name, LOGGER_NAME)
        self.assertEqual(logger.getEffectiveLevel(), logging.DEBUG)


if __name__ == "__main__":
    unittest.main()
