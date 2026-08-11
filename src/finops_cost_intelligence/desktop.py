"""Native desktop launcher for the local Metrora Streamlit workspace."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from .runtime import resource_path

_DESKTOP_STREAMS: list[object] = []


def _user_data_directory() -> Path:
    """Return a writable per-user directory for local models and connection profiles."""
    override = os.environ.get("METRORA_USER_DATA_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "Metrora"


def _available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        candidate.bind(("127.0.0.1", 0))
        return int(candidate.getsockname()[1])


def _configure_desktop_environment() -> Path:
    data_root = _user_data_directory()
    data_root.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("APP_ENV", "production")
    os.environ["METRORA_DESKTOP"] = "1"
    os.environ.setdefault("DATA_DIR", str(data_root / "data"))
    os.environ.setdefault("DB_PATH", str(data_root / "data" / "metrora.duckdb"))
    return data_root


def _ensure_desktop_streams(data_root: Path) -> None:
    """Give no-console Windows builds writable streams for server diagnostics."""
    is_frozen = bool(getattr(sys, "frozen", False))
    if not is_frozen and sys.stdout is not None and sys.stderr is not None:
        return
    log_directory = data_root / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    stream = (log_directory / "desktop-service.log").open(
        "a",
        encoding="utf-8",
        buffering=1,
    )
    _DESKTOP_STREAMS.append(stream)
    sys.stdout = stream
    sys.stderr = stream


def _write_crash_report(exc: BaseException) -> Path | None:
    """Persist a readable local crash report without sending telemetry anywhere."""
    try:
        log_directory = _user_data_directory() / "logs"
        log_directory.mkdir(parents=True, exist_ok=True)
        report_path = log_directory / "desktop-crash.log"
        with report_path.open("a", encoding="utf-8") as report:
            report.write(f"\n[{datetime.now(UTC).isoformat()}] {type(exc).__name__}: {exc}\n")
            report.write("".join(traceback.format_exception(exc)))
        return report_path
    except OSError:
        return None


def _show_startup_error(report_path: Path | None) -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes

        detail = f"\n\nDetails were saved to:\n{report_path}" if report_path else ""
        ctypes.windll.user32.MessageBoxW(
            0,
            "Metrora could not start." + detail,
            "Metrora startup error",
            0x10,
        )
    except (AttributeError, OSError):
        return


def _run_streamlit_child(port: int) -> None:
    data_root = _configure_desktop_environment()
    _ensure_desktop_streams(data_root)

    from streamlit.web import bootstrap

    app_path = resource_path("app.py")
    if not app_path.is_file():
        raise RuntimeError(f"Packaged application entry point is missing: {app_path}")
    flags = {
        "global_developmentMode": False,
        "server_address": "127.0.0.1",
        "server_port": int(port),
        "server_headless": True,
        "server_fileWatcherType": "none",
        "browser_gatherUsageStats": False,
    }
    bootstrap.load_config_options(flag_options=flags)
    bootstrap.run(str(app_path), False, [], flags)


def _child_command(port: int) -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--streamlit-child", str(port)]
    return [
        sys.executable,
        "-m",
        "finops_cost_intelligence.desktop",
        "--streamlit-child",
        str(port),
    ]


def _wait_until_ready(url: str, process: subprocess.Popen, *, timeout: float = 45.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("The local Metrora service stopped before the window opened.")
        try:
            with urlopen(url, timeout=1.0) as response:
                if response.status < 500:
                    return
        except (URLError, OSError, TimeoutError):
            time.sleep(0.25)
    raise RuntimeError("Metrora did not finish starting within 45 seconds.")


def _launch_desktop() -> None:
    try:
        import webview
    except ImportError as exc:
        raise RuntimeError(
            'The desktop window dependency is missing. Install with "pip install -e '
            '.[desktop,cloud]".'
        ) from exc

    data_root = _configure_desktop_environment()
    log_directory = data_root / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    log_path = log_directory / "desktop-service.log"
    port = _available_port()
    base_url = f"http://127.0.0.1:{port}"
    workspace_url = f"{base_url}/?surface=workspace&page=Home"
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    with log_path.open("a", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            _child_command(port),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=creation_flags,
            env=os.environ.copy(),
        )
        try:
            _wait_until_ready(base_url, process)
            webview.create_window(
                "Metrora · Cloud FinOps Intelligence",
                workspace_url,
                width=1500,
                height=960,
                min_size=(1100, 720),
                background_color="#080d13",
            )
            webview.start(debug=False, private_mode=False)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


def main() -> None:
    """Start either the local Streamlit child or the native desktop shell."""
    is_child = len(sys.argv) >= 3 and sys.argv[1] == "--streamlit-child"
    try:
        if is_child:
            _run_streamlit_child(int(sys.argv[2]))
            return
        _launch_desktop()
    except Exception as exc:
        report_path = _write_crash_report(exc)
        if not is_child:
            _show_startup_error(report_path)
        raise


if __name__ == "__main__":
    main()
