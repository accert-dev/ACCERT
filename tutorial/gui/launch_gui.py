"""One-click local ACCERT GUI launcher for macOS and terminal use."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

from crt_iat_gui import HOST, PORT, find_available_port, gui_url, is_gui_running, pid_file, resolve_gui_port


def _pid_command(pid: int) -> str:
    result = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True, check=False)
    return result.stdout.strip()


def _managed_pid(port: int) -> int | None:
    marker = pid_file(port)
    try:
        pid = int(marker.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None
    command = _pid_command(pid)
    return pid if "crt_iat_gui.py" in command else None


def _choose_existing_action(port: int, requested: str | None) -> str:
    if requested:
        return requested
    if not sys.stdin.isatty():
        return "reuse"
    print(f"An ACCERT GUI session is already running on {gui_url(HOST, port)}.")
    print("Choose: [R]euse it, [S]top and restart it, or start a [N]ew port.")
    choice = input("Selection [R]: ").strip().lower()
    return {"s": "restart", "n": "new"}.get(choice, "reuse")


def _stop_managed(port: int) -> bool:
    pid = _managed_pid(port)
    if pid is None:
        return False
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return True
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if not is_gui_running(HOST, port):
            return True
        time.sleep(0.1)
    return not is_gui_running(HOST, port)


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < (3, 12):
        print("ACCERT GUI requires Python 3.12 or newer. Use the provided macOS launcher or the py312 environment.")
        return 2
    parser = argparse.ArgumentParser(description="Launch the local ACCERT GUI.")
    parser.add_argument("--port", type=int, default=None, help="Optional fixed listening port.")
    parser.add_argument("--existing", choices=("reuse", "restart", "new"), help="Action when a managed session exists.")
    args = parser.parse_args(argv)

    requested_port = resolve_gui_port(args.port)
    port = requested_port
    if is_gui_running(HOST, port):
        action = _choose_existing_action(port, args.existing)
        if action == "reuse":
            url = gui_url(HOST, port)
            print(f"Reusing ACCERT GUI at {url}.")
            webbrowser.open(url)
            return 0
        if action == "restart":
            if not _stop_managed(port):
                print("The existing GUI is not managed by this launcher; it was not stopped.")
                return 2
        else:
            port = find_available_port(HOST, PORT + 1)
    elif args.port is None:
        # A non-ACCERT process may occupy the default port. Never stop it.
        try:
            port = find_available_port(HOST, PORT)
        except OSError as exc:
            print(f"ACCERT GUI could not find a free local port: {exc}")
            return 2

    gui_script = Path(__file__).with_name("crt_iat_gui.py")
    process = subprocess.Popen([sys.executable, str(gui_script), "--port", str(port)])
    try:
        return process.wait()
    except KeyboardInterrupt:
        process.send_signal(signal.SIGTERM)
        return process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
