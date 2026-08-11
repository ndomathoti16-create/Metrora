"""Runtime paths that work in source checkouts and packaged desktop builds."""

from __future__ import annotations

import sys
from pathlib import Path


def application_root() -> Path:
    """Return the repository root or PyInstaller extraction directory."""
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root)
    return Path(__file__).resolve().parents[2]


def resource_path(*parts: str) -> Path:
    """Resolve one bundled, read-only application resource."""
    return application_root().joinpath(*parts)
