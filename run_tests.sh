#!/usr/bin/env bash
# MotionGuard Pytest Runner for Linux / macOS
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f ".venv/bin/pytest" ]; then
    echo "Using local .venv environment..."
    .venv/bin/pytest
elif [ -f "venv/bin/pytest" ]; then
    echo "Using venv environment..."
    venv/bin/pytest
else
    echo "Using system pytest..."
    python3 -m pytest
fi
