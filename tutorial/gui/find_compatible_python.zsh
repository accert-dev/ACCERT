#!/bin/zsh

# Print the first usable Python interpreter that satisfies pyproject.toml.
# This file is sourced by the macOS launchers, including when Finder provides
# a minimal PATH. Every candidate is validated by its runtime version.

find_compatible_python() {
  typeset -a candidates
  typeset -a command_names
  typeset candidate resolved command_name

  if [[ -n "${ACCERT_PYTHON:-}" ]]; then
    candidates+=("$ACCERT_PYTHON")
  else
    for candidate in \
      "$PWD/.venv/bin/python" \
      "$PWD/venv/bin/python" \
      "$PWD/env/bin/python" \
      "${0:A:h}/../../.venv/bin/python" \
      "${0:A:h}/../../venv/bin/python"; do
      candidates+=("$candidate")
    done

    command_names=(python3 python python3.12 python3.11 python3.10 python3.13 python3.14)
    for command_name in $command_names; do
      resolved=$(whence -p -- "$command_name" 2>/dev/null || true)
      [[ -n "$resolved" ]] && candidates+=("$resolved")
    done

    # Common macOS installation locations are fallback candidates for Finder,
    # whose PATH may omit Homebrew or the Python.org framework bin directory.
    candidates+=(
      /opt/homebrew/bin/python3
      /usr/local/bin/python3
      /Library/Frameworks/Python.framework/Versions/Current/bin/python3
      /usr/bin/python3
    )
  fi

  for candidate in $candidates; do
    [[ -x "$candidate" ]] || continue
    if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
      print -r -- "$candidate"
      return 0
    fi
  done
  return 1
}
