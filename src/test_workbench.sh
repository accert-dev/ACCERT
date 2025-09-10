#!/bin/bash

echo "Testing workbench path detection..."
echo "OSTYPE: '$OSTYPE'"

case "$OSTYPE" in
  darwin*)    # macOS
    workbench_path="/Applications/Workbench-5.5.1.app/Contents"
    echo "Detected macOS - using: $workbench_path"
    ;;
  linux*)     # Linux (if you ever build a Linux bundle)
    workbench_path="/opt/Workbench-5.5.1"
    echo "Detected Linux - using: $workbench_path"
    ;;
  msys*|cygwin*)  # Git-bash or Cygwin on Windows
    # note: /c/... maps to C:\... in Git-bash/Cygwin
    workbench_path="/C:/Workbench-5.5.1"
    echo "Detected Windows (msys/cygwin) - using: $workbench_path"
    ;;
  *)
    echo "❌ unsupported OS: '$OSTYPE'"
    echo "Available paths to check:"
    echo "  - B:/Workbench-5.5.1.exe (if exists)"
    echo "  - C:/Workbench-5.5.1 (if exists)"
    exit 1
    ;;
esac

echo "Final workbench_path: $workbench_path"

# Test if path exists
if [ -e "$workbench_path" ]; then
    echo "✅ Path exists: $workbench_path"
else
    echo "❌ Path does not exist: $workbench_path"
    echo "Checking alternative paths..."
    
    # Check some common Windows paths
    if [ -e "/C/Workbench-5.5.1" ]; then
        echo "✅ Found: /C/Workbench-5.5.1"
    fi
    if [ -e "/B/Workbench-5.5.1.exe" ]; then
        echo "✅ Found: /B/Workbench-5.5.1.exe"
    fi
fi 