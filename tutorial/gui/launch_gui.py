"""Start or reuse the local ACCERT GUI and clean up its child process on exit."""

from __future__ import annotations

import argparse
import signal
import subprocess
import sys
import webbrowser
from pathlib import Path

from crt_iat_gui import HOST, PORT, gui_url, is_gui_running, resolve_gui_port


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Launch the local ACCERT GUI.")
    parser.add_argument("--port", type=int, default=None, help=f"Listening port (default: {PORT} or ACCERT_GUI_PORT).")
    args = parser.parse_args(argv)
    port = resolve_gui_port(args.port)
    url = gui_url(HOST, port)
    if is_gui_running(HOST, port):
        print(f"ACCERT GUI is already running at {url}; opening that instance.")
        webbrowser.open(url)
        return 0

    gui_script = Path(__file__).with_name("crt_iat_gui.py")
    process = subprocess.Popen([sys.executable, str(gui_script), "--port", str(port)])
    try:
        return process.wait()
    except KeyboardInterrupt:
        process.send_signal(signal.SIGTERM)
        try:
            return process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            return process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
