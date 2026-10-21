#!/usr/bin/env bash
# Run all automated tests. Pass --e2e to include the browser tests.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Backend (pytest)"
cd "$ROOT/backend"
.venv/bin/pytest -p no:logging

echo "==> Frontend (vitest)"
cd "$ROOT/frontend"
npx vitest run

echo "==> Type check and build"
npm run build >/dev/null && echo "build ok"

if [[ "${1:-}" == "--e2e" ]]; then
  echo "==> End-to-end (Playwright)"
  npx playwright test
fi
