from __future__ import annotations

import logging
import tempfile
import unittest
from pathlib import Path

from finops_cost_intelligence import __version__
from finops_cost_intelligence.config import ConfigurationError, Settings, validate_ai_base_url
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
                (Path(temporary_directory) / "data" / "metrora.duckdb").resolve(),
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

    def test_ai_base_url_requires_tls_for_remote_hosts(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "HTTPS"):
            validate_ai_base_url("http://example.com/v1")

    def test_ai_base_url_allows_a_local_development_endpoint(self) -> None:
        self.assertEqual(
            validate_ai_base_url("http://127.0.0.1:11434/v1/"),
            "http://127.0.0.1:11434/v1",
        )

    def test_ai_base_url_rejects_embedded_credentials(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "embedded credentials"):
            validate_ai_base_url("https://user:password@example.com/v1")


class FoundationTests(unittest.TestCase):
    def test_package_version_is_defined(self) -> None:
        self.assertEqual(__version__, "0.2.3")

    def test_logging_configuration_returns_project_logger(self) -> None:
        settings = Settings.from_environment({"LOG_LEVEL": "DEBUG"})
        logger = configure_logging(settings)

        self.assertEqual(logger.name, LOGGER_NAME)
        self.assertEqual(logger.getEffectiveLevel(), logging.DEBUG)


if __name__ == "__main__":
    unittest.main()
