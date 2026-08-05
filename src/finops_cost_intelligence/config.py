"""Application configuration with explicit validation and safe defaults."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


class ConfigurationError(ValueError):
    """Raised when an environment setting cannot be used safely."""


def _read_positive_int(raw_value: str, variable_name: str) -> int:
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(
            f"{variable_name} must be a whole number; received {raw_value!r}."
        ) from exc

    if value <= 0:
        raise ConfigurationError(f"{variable_name} must be greater than zero.")
    return value


def _resolve_path(raw_value: str, variable_name: str, base_dir: Path) -> Path:
    if not raw_value.strip():
        raise ConfigurationError(f"{variable_name} cannot be empty.")

    path = Path(raw_value).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


@dataclass(frozen=True)
class Settings:
    """Validated runtime settings for local development and later AWS integration."""

    app_env: str
    log_level: str
    data_dir: Path
    db_path: Path
    max_upload_mb: int
    ai_provider: str
    ai_model: str | None
    ai_api_key: str | None
    ai_base_url: str
    aws_region: str
    s3_bucket: str | None
    athena_database: str | None
    athena_output_location: str | None

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | None = None,
        *,
        base_dir: Path | None = None,
    ) -> Settings:
        """Build settings from environment variables without creating directories."""
        values = os.environ if environ is None else environ
        root = (base_dir or Path.cwd()).resolve()

        app_env = values.get("APP_ENV", "development").strip().lower()
        if app_env not in {"development", "test", "production"}:
            raise ConfigurationError("APP_ENV must be one of: development, test, production.")

        log_level = values.get("LOG_LEVEL", "INFO").strip().upper()
        if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ConfigurationError(
                "LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL."
            )

        data_dir = _resolve_path(values.get("DATA_DIR", "./data"), "DATA_DIR", root)
        db_path = _resolve_path(values.get("DB_PATH", "./data/spendarc.duckdb"), "DB_PATH", root)
        max_upload_mb = _read_positive_int(values.get("MAX_UPLOAD_MB", "200"), "MAX_UPLOAD_MB")

        ai_provider = values.get("AI_PROVIDER", "none").strip().lower()
        if not ai_provider:
            raise ConfigurationError("AI_PROVIDER cannot be empty.")

        def optional_value(name: str) -> str | None:
            value = values.get(name, "").strip()
            return value or None

        ai_base_url = values.get("AI_BASE_URL", "https://api.openai.com/v1").strip()
        if not ai_base_url:
            raise ConfigurationError("AI_BASE_URL cannot be empty.")

        aws_region = values.get("AWS_REGION", "us-east-1").strip()
        if not aws_region:
            raise ConfigurationError("AWS_REGION cannot be empty.")

        return cls(
            app_env=app_env,
            log_level=log_level,
            data_dir=data_dir,
            db_path=db_path,
            max_upload_mb=max_upload_mb,
            ai_provider=ai_provider,
            ai_model=optional_value("AI_MODEL"),
            ai_api_key=optional_value("AI_API_KEY"),
            ai_base_url=ai_base_url,
            aws_region=aws_region,
            s3_bucket=optional_value("S3_BUCKET"),
            athena_database=optional_value("ATHENA_DATABASE"),
            athena_output_location=optional_value("ATHENA_OUTPUT_LOCATION"),
        )

    def ensure_directories(self) -> None:
        """Create local runtime directories when the application is started."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
