#!/usr/bin/env bash
# MotionGuard Dashboard Launcher for Linux / macOS
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================="
echo "    MotionGuard: Autonomous Incident Response AI"
echo "======================================================="
echo ""

if [ -f ".venv/bin/streamlit" ]; then
    echo "[OK] Using local .venv environment..."
    .venv/bin/streamlit run app.py
elif [ -f "venv/bin/streamlit" ]; then
    echo "[OK] Using local venv environment..."
    venv/bin/streamlit run app.py
elif command -v streamlit >/dev/null 2>&1; then
    echo "[OK] Using system streamlit..."
    streamlit run app.py
else
    echo "[!] Streamlit was not found. Installing requirements..."
    pip install -r requirements.txt
    python3 -m streamlit run app.py
fi
