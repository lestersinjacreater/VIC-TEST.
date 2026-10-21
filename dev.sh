#!/usr/bin/env bash
# Start the backend (port 8000) and frontend (port 5173) together.
# Ctrl+C stops both.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT/backend"
.venv/bin/uvicorn app.main:app --port 8000 --no-access-log &
API_PID=$!
trap 'kill $API_PID 2>/dev/null || true' EXIT INT TERM

cd "$ROOT/frontend"
echo
echo "LINDA is starting:"
echo "  App: http://localhost:5173"
echo "  API: http://localhost:8000/docs"
echo
npx vite --port 5173 --host
