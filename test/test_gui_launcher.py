from __future__ import annotations

import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINDER = PROJECT_ROOT / "tutorial" / "gui" / "find_compatible_python.zsh"


def _fake_python(directory: Path, name: str, *, exit_code: int | None = None) -> Path:
    executable = directory / name
    result = "${FAKE_PYTHON_EXIT:-1}" if exit_code is None else str(exit_code)
    executable.write_text(
        "#!/bin/zsh\n"
        f"if [[ \"$1\" == \"-c\" ]]; then exit {result}; fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    return executable


def _run_finder(
    tmp_path: Path,
    *,
    exit_code: int,
    names: tuple[str, ...] = ("python3",),
    explicit_python: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    for name in names:
        _fake_python(tmp_path, name)
    env = os.environ.copy()
    env.update({"PATH": str(tmp_path), "FAKE_PYTHON_EXIT": str(exit_code)})
    if explicit_python is not None:
        env["ACCERT_PYTHON"] = str(explicit_python)
    return subprocess.run(
        ["/bin/zsh", "-c", f"source {FINDER!s}; find_compatible_python"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_finder_accepts_python3_when_python312_command_is_missing(tmp_path):
    result = _run_finder(tmp_path, exit_code=0)

    assert result.returncode == 0
    assert result.stdout.strip() == str(tmp_path / "python3")


def test_finder_accepts_python310(tmp_path):
    result = _run_finder(tmp_path, exit_code=0)

    assert result.returncode == 0
    assert result.stdout.strip().endswith("/python3")


def test_finder_prefers_first_compatible_runtime_when_multiple_exist(tmp_path):
    result = _run_finder(tmp_path, exit_code=0, names=("python3", "python3.12"))

    assert result.returncode == 0
    assert result.stdout.strip() == str(tmp_path / "python3")


def test_finder_skips_stale_virtual_environment(tmp_path):
    venv = tmp_path / ".venv" / "bin"
    venv.mkdir(parents=True)
    _fake_python(venv, "python", exit_code=1)
    result = _run_finder(tmp_path, exit_code=0)

    assert result.returncode == 0
    assert result.stdout.strip() == str(tmp_path / "python3")


def test_finder_reports_no_compatible_runtime(tmp_path):
    candidate = _fake_python(tmp_path, "stale-python", exit_code=1)
    result = _run_finder(tmp_path, exit_code=1, names=(), explicit_python=candidate)

    assert result.returncode != 0
    assert result.stdout == ""


def test_launcher_scripts_use_declared_python_minimum_and_no_personal_paths():
    launchers = [
        PROJECT_ROOT / "tutorial" / "gui" / "Launch ACCERT GUI.command",
        PROJECT_ROOT / "tutorial" / "gui" / "Stop ACCERT GUI.command",
        PROJECT_ROOT / "tutorial" / "gui" / "find_compatible_python.zsh",
        PROJECT_ROOT / "tutorial" / "gui" / "launch_gui.py",
        PROJECT_ROOT / "tutorial" / "gui" / "stop_gui.py",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in launchers)

    assert "/opt/anaconda3/" not in text
    assert "/Users/" not in text
    assert "Python 3.12 was not found" not in text
    assert "Python 3.10 or newer" in text


def test_necost_report_script_has_no_developer_workbook_path():
    script = PROJECT_ROOT / "tutorial" / "necost" / "ap1000_lcoe_scenarios.py"

    assert "/Users/" not in script.read_text(encoding="utf-8")
