#!/usr/bin/env bash
# One-time setup: Python venv + packages, Node packages, database.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Backend"
cd "$ROOT/backend"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip >/dev/null
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m app.cli init

echo "==> Frontend"
cd "$ROOT/frontend"
npm install

echo
echo "Setup complete. Start LINDA with: ./scripts/dev.sh"
