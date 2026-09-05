#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================================"
echo "🛰️  SATQUERY AI — SIH26167 DEMO PLATFORM LAUNCHER"
echo "========================================================"

cd "$ROOT_DIR"

# 1. Generate demo sample data if not present
if [ ! -f "$ROOT_DIR/data/samples/optical_single.png" ]; then
    echo "▶ Generating synthetic multi-spectral & SAR sample imagery..."
    .venv/bin/python data/generate_samples.py
fi

# 2. Start Backend API Server in background
echo "▶ Starting FastAPI Backend Server on http://localhost:8000 ..."
.venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# 3. Start Frontend
echo "▶ Starting Vite React Frontend on http://localhost:5173 ..."
cd "$ROOT_DIR/frontend"
npm run dev

wait $BACKEND_PID
