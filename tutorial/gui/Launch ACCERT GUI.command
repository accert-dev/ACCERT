#!/bin/zsh
set -e
cd "$(dirname "$0")/../.."

source "$(dirname "$0")/find_compatible_python.zsh"
if ! PYTHON=$(find_compatible_python); then
  osascript -e 'display alert "ACCERT GUI could not start" message "Python 3.10 or newer is required. Please install a compatible Python version." as critical'
  exit 1
fi

exec "$PYTHON" tutorial/gui/launch_gui.py
