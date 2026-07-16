"""Small diagnostic command for validating the local project foundation."""

from __future__ import annotations

from .config import Settings


def main() -> int:
    """Validate configuration and print a safe local status summary."""
    settings = Settings.from_environment()
    print("FinOps Cost Intelligence foundation is configured.")
    print(f"Environment: {settings.app_env}")
    print(f"Data directory: {settings.data_dir}")
    print(f"Database path: {settings.db_path}")
    print(f"AI provider: {settings.ai_provider}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
