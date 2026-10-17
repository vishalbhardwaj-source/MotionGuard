#!/usr/bin/env bash
# MotionGuard Dashboard Launcher for Linux / macOS
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f ".venv/bin/streamlit" ]; then
    echo "Using local .venv environment..."
    .venv/bin/streamlit run app.py
elif [ -f "venv/bin/streamlit" ]; then
    echo "Using venv environment..."
    venv/bin/streamlit run app.py
else
    echo "Using system streamlit..."
    python3 -m streamlit run app.py
fi
