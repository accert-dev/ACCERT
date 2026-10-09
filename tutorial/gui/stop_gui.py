"""Stop only an ACCERT GUI process recorded by the local launcher."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess

from crt_iat_gui import HOST, PORT, pid_file, resolve_gui_port


def _command_for_pid(pid: int) -> str:
    result = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True, check=False)
    return result.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stop the local ACCERT GUI without touching unrelated processes.")
    parser.add_argument("--port", type=int, default=None, help=f"GUI port (default: {PORT} or ACCERT_GUI_PORT).")
    args = parser.parse_args(argv)
    port = resolve_gui_port(args.port)
    marker = pid_file(port)
    if not marker.exists():
        print(f"No ACCERT GUI PID file found for port {port}.")
        return 0
    try:
        pid = int(marker.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        try:
            marker.unlink()
        except FileNotFoundError:
            pass
        print(f"Removed stale ACCERT GUI PID file for port {port}.")
        return 0

    command = _command_for_pid(pid)
    if "crt_iat_gui.py" not in command and "launch_gui.py" not in command:
        print(f"PID {pid} is not an ACCERT GUI process; it was not stopped.")
        return 1
    os.kill(pid, signal.SIGTERM)
    print(f"Stopping ACCERT GUI on {HOST}:{port} (PID {pid}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
