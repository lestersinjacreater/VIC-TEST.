# LINDA — Scam intelligence that connects the dots

LINDA is a mobile-first scam protection and fraud-intelligence demo for
Kenyan consumers. It checks suspicious messages, links and numbers,
explains what looks wrong, and connects scam attempts that share links,
wording or reports into campaigns — with every link labelled by how sure
LINDA is and why.

> **Demo only.** All phone numbers, campaigns, reports, links and
> verification outcomes are fictional or simulated. LINDA does not
> monitor calls or SMS, does not connect to Safaricom, M-PESA or any
> mobile network, and never sends anything to 333 or an authority. It is
> not a Safaricom product. See [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md).

## Quick start

You need **Python 3.11+** and **Node.js 22** (20.19+ also works).

```bash
./scripts/setup.sh     # venv, packages, database, seed data
./scripts/dev.sh       # API on :8000, app on :5173
```

Open http://localhost:5173. The first visit shows onboarding; choose
**Start guided demo** for the three-minute story.

### GitHub Codespaces (no installs on your machine)

Open the repo in a Codespace. `.devcontainer/devcontainer.json` runs
`scripts/setup.sh` automatically. Then run `./scripts/dev.sh`; port 5173
opens in the browser.

### Manual commands

```bash
# Backend
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m app.cli init
.venv/bin/uvicorn app.main:app --port 8000

# Frontend (second terminal)
cd frontend
npm install
npx vite --port 5173
```

On Windows use `.venv\Scripts\python` in place of `.venv/bin/python`.

### PostgreSQL (optional)

SQLite is the default and needs no setup. To use PostgreSQL:

```bash
docker compose up -d db
export LINDA_DATABASE_URL=postgresql+psycopg://linda:linda@localhost:5432/linda
cd backend && .venv/bin/python -m app.cli init
```

Migrations are managed with Alembic (`backend/migrations`). The full test
suite was run against both SQLite and PostgreSQL 16.

## Tests

```bash
./scripts/test.sh          # pytest + vitest + type check + build
./scripts/test.sh --e2e    # also Playwright browser tests
```

Individually:

```bash
cd backend && .venv/bin/pytest -p no:logging
cd frontend && npx vitest run
cd frontend && npx playwright install chromium && npx playwright test
```

Playwright starts its own backend (fresh database) and frontend on ports
8011 and 5181. If Chromium can't be downloaded, set
`PW_CHROMIUM_PATH=/path/to/chrome`.

## Configuration

Copy `.env.example` to `backend/.env`. Every setting has a safe default.
Secrets are read only by the backend and are never sent to the browser.

| Setting | Default | Purpose |
|---|---|---|
| `LINDA_DATABASE_URL` | SQLite file | Database connection |
| `LINDA_FRAUD_PROVIDER` | `mock` | `mock` (simulated) or `safaricom` (disabled placeholder) |
| `LINDA_SAFE_BROWSING_API_KEY` | empty | Optional link reputation lookups |
| `LINDA_CLIENT_SALT` | demo value | Salt for hashing device IDs; change for shared deploys |
| `LINDA_REPORT_RETENTION_DAYS` | 90 | Auto-deletion of user reports |
| `LINDA_SIM_REVIEW_AFTER_S` / `_OUTCOME_AFTER_S` | 6 / 14 | Simulated review pacing |

## What's inside

```
linda/
├── shared/                 One rulebook for both engines
│   ├── scam_rules.json       Message heuristics (EN, Kiswahili, Sheng)
│   ├── url_rules.json        Link heuristics, brand allowlist
│   ├── sample_messages.json  Fictional samples (also test cases)
│   ├── url_cases.json        Link test cases
│   └── scanner_parity.json   Proof the TS and Python engines agree
├── backend/                FastAPI + SQLAlchemy + Alembic
│   ├── app/detection/        Scanner and link checker (Python mirror)
│   ├── app/ml/               Corpus, model, template similarity,
│   │                         campaign linker, NetworkX graph
│   ├── app/providers/        FraudIntelligenceProvider, mock,
│   │                         disabled Safaricom adapter, reputation
│   ├── app/services/         Reports, indicators, campaigns,
│   │                         analytics, seed data
│   ├── app/routers/api.py    REST API (OpenAPI at /docs)
│   ├── migrations/           Alembic
│   └── tests/                pytest
├── frontend/               React + TypeScript + Vite + Tailwind
│   ├── src/features/         One folder per module
│   ├── src/lib/detection/    In-browser scanner and link checker
│   ├── src/data/snapshot.json Offline fallback of demo data
│   └── e2e/                  Playwright
├── docs/                   Architecture, API, integrations, demo
└── scripts/                setup, dev, test
```

## Features

| Module | Where |
|---|---|
| Onboarding and privacy | `/onboarding`, `/privacy` |
| Home dashboard with universal check box | `/` |
| Caller lookup and incoming-call simulator | `/calls` |
| SMS scam scanner (on-device) | `/scan` |
| Link checker (on-device, never opens links) | `/links` |
| Reporting wizard with "what will be shared" preview | `/report`, `/reports` |
| Scam-network explorer and campaign pages | `/intel` |
| Analytics and model evaluation | `/analytics` |
| Personal blocklist, safe list, alerts, history, export, delete | `/protection` |
| Learn (English and Kiswahili) | `/learn` |
| Guided hackathon demo with replay | `/demo` |
| Integrations: real vs simulated | `/integrations` |

## Regenerating derived files

```bash
cd backend
.venv/bin/python -m app.cli parity ../shared/scanner_parity.json
.venv/bin/python -m app.cli snapshot ../frontend/src/data/snapshot.json
.venv/bin/python -m app.cli train   # model artifacts (auto on first run)
.venv/bin/python -m app.cli reset   # restore seed data
```

Run `parity` after changing any rule; both test suites fail otherwise.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — diagram, data flow, security
- [API](docs/API.md) — endpoints and examples
- [Integrations](docs/INTEGRATIONS.md) — what is real, what is simulated, what needs approval
- [Demo script](docs/DEMO_SCRIPT.md) — hackathon presentation guide
- [Roadmap](docs/ROADMAP.md) — prioritised future upgrades

## Screenshots

| Home | Scanner | Guided demo (mobile) |
|---|---|---|
| ![Home](docs/screenshots/home.png) | ![Scanner](docs/screenshots/scanner.png) | ![Demo](docs/screenshots/demo-campaign-link-mobile.png) |
