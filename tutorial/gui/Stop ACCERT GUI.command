#!/bin/zsh
set -e
cd "$(dirname "$0")/../.."

if [[ -x /opt/anaconda3/envs/py312/bin/python ]]; then
  PYTHON=/opt/anaconda3/envs/py312/bin/python
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON=$(command -v python3.12)
else
  osascript -e 'display alert "ACCERT GUI could not stop" message "Python 3.12 was not found." as critical'
  exit 1
fi

exec "$PYTHON" tutorial/gui/stop_gui.py
