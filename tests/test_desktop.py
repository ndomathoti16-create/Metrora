"""Unit coverage for the native desktop launcher's failure boundaries."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from finops_cost_intelligence import desktop


class _Process:
    def __init__(self, return_code: int | None = None) -> None:
        self.return_code = return_code

    def poll(self) -> int | None:
        return self.return_code


class _Response:
    status = 200

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def test_user_data_directory_honors_the_explicit_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    requested = tmp_path / "Metrora data"
    monkeypatch.setenv("METRORA_USER_DATA_DIR", str(requested))

    assert desktop._user_data_directory() == requested.resolve()


def test_child_command_uses_module_mode_during_development(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(sys, "executable", "python-test")

    assert desktop._child_command(8510) == [
        "python-test",
        "-m",
        "finops_cost_intelligence.desktop",
        "--streamlit-child",
        "8510",
    ]


def test_child_command_reuses_the_packaged_executable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", "Metrora.exe")

    assert desktop._child_command(8511) == ["Metrora.exe", "--streamlit-child", "8511"]


def test_wait_until_ready_accepts_a_healthy_local_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(desktop, "urlopen", lambda *_args, **_kwargs: _Response())

    desktop._wait_until_ready("http://127.0.0.1:8512", _Process(), timeout=0.1)


def test_wait_until_ready_reports_an_early_child_exit() -> None:
    with pytest.raises(RuntimeError, match="stopped before the window opened"):
        desktop._wait_until_ready("http://127.0.0.1:8513", _Process(1), timeout=0.1)
