#!/usr/bin/env python3
"""Desktop entry point for the local Windows app build."""

from __future__ import annotations

import os
import logging
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Optional
from urllib.request import urlopen


APP_NAME = "AI Video Transcriber"


def _base_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def _user_data_dir() -> Path:
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / APP_NAME
    return Path.home() / f".{APP_NAME.lower().replace(' ', '-')}"


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _configure_desktop_logging(data_dir: Path) -> None:
    log_dir = data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    handlers: list[logging.Handler] = [
        logging.FileHandler(log_dir / "desktop.log", encoding="utf-8")
    ]
    stderr = getattr(sys, "stderr", None)
    if stderr is not None and not getattr(sys, "frozen", False):
        handlers.append(logging.StreamHandler(stderr))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=handlers,
        force=True,
    )


def _prepare_environment(base_dir: Path, port: int) -> None:
    backend_dir = base_dir / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    data_dir = _user_data_dir()
    _configure_desktop_logging(data_dir)

    temp_dir = data_dir / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("HOST", "127.0.0.1")
    os.environ["PORT"] = str(port)
    os.environ.setdefault("PRODUCTION_MODE", "true")
    os.environ.setdefault("AI_VIDEO_TRANSCRIBER_TEMP_DIR", str(temp_dir))
    os.environ.setdefault("WHISPER_MODEL_SIZE", "medium")

    bundled_bin = base_dir / "bin"
    if bundled_bin.exists():
        os.environ["PATH"] = str(bundled_bin) + os.pathsep + os.environ.get("PATH", "")


def _wait_for_server(url: str, timeout_seconds: float = 30.0) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Optional[Exception] = None
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=1.0) as response:
                if response.status < 500:
                    return
        except Exception as exc:
            last_error = exc
            time.sleep(0.2)
    raise RuntimeError(f"Server did not start in time: {last_error}")


def main() -> None:
    base_dir = _base_dir()
    port = _find_free_port()
    _prepare_environment(base_dir, port)

    import uvicorn
    import webview

    from main import app

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        access_log=False,
        reload=False,
    )
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    url = f"http://127.0.0.1:{port}"
    _wait_for_server(url)

    webview.create_window(APP_NAME, url, width=1180, height=820, min_size=(900, 650))
    try:
        webview.start()
    finally:
        server.should_exit = True
        server_thread.join(timeout=5)


if __name__ == "__main__":
    main()
