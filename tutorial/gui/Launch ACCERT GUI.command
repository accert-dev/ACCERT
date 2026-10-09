#!/bin/zsh
set -e
cd "$(dirname "$0")/../.."

if [[ -x /opt/anaconda3/envs/py312/bin/python ]]; then
  PYTHON=/opt/anaconda3/envs/py312/bin/python
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON=$(command -v python3.12)
else
  osascript -e 'display alert "ACCERT GUI could not start" message "Python 3.12 was not found. Install the project environment or ask IT for the configured ACCERT environment." as critical'
  exit 1
fi

exec "$PYTHON" tutorial/gui/launch_gui.py
