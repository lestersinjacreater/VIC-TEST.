"""Command-line helpers.

  python -m app.cli init       # run migrations and seed if empty
  python -m app.cli reset      # wipe and reseed demo data
  python -m app.cli train      # retrain the model, print metrics
  python -m app.cli snapshot ../frontend/src/data/snapshot.json
  python -m app.cli parity ../shared/scanner_parity.json
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path


def _init() -> None:
    from app.main import init_app_data

    init_app_data()
    print("Database migrated and seeded.")


def _reset() -> None:
    from app.db import session_factory
    from app.main import run_migrations
    from app.services import seed

    run_migrations()
    with session_factory()() as db:
        print("Reseeded:", seed.seed(db))


def _train() -> None:
    from app.ml import model

    m = model.train()
    print(json.dumps(m["evaluation"]["held_out_families"], indent=2))


def _snapshot(out: str) -> None:
    tmp = Path(tempfile.mkdtemp()) / "snap.db"
    os.environ["LINDA_DATABASE_URL"] = f"sqlite:///{tmp}"
    from app.config import get_settings

    get_settings.cache_clear()
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        def get(p: str):
            r = c.get(p)
            r.raise_for_status()
            return r.json()

        camps = get("/api/campaigns")
        scenario = get("/api/demo/scenario")
        demo_link = c.post("/api/intel/assess", json={
            "indicator_kind": "phone",
            "indicator": scenario["sms_sender"],
            "message_text": scenario["sms_text"],
        }).json()
        data = {
            "generated_at": datetime.now(UTC).isoformat(),
            "note": "Offline snapshot of synthetic demo data, bundled so "
                    "read-only screens still work without the backend.",
            "meta": get("/api/meta"),
            "dashboard": get("/api/dashboard"),
            "campaigns": camps,
            "campaign_details": {
                cm["id"]: get(f"/api/campaigns/{cm['id']}")
                for cm in camps["items"]
            },
            "graph": get("/api/graph"),
            "analytics": get("/api/analytics/summary"),
            "integrations": get("/api/integrations"),
            "demo_scenario": scenario,
            "demo_link": demo_link,
        }
    Path(out).write_text(json.dumps(data, separators=(",", ":")))
    print(f"Wrote {out} ({Path(out).stat().st_size // 1024} KB)")


def build_parity() -> dict:
    """Scores from the Python engines, used to prove the browser engines
    give identical results."""
    from app.detection.rulebook import sample_messages
    from app.detection.scanner import analyse_message
    from app.detection.urls import check_url
    from app.ml.corpus import generate

    texts = [s["text"] for s in sample_messages()]
    corpus = generate()
    texts += [s.text for s in corpus[::7]]
    messages = []
    for t in texts:
        r = analyse_message(t)
        messages.append({
            "text": t, "score": r["score"], "band": r["band"],
            "category": r["category"],
            "rules": sorted(x["id"] for x in r["reasons"]),
            "highlights": len(r["highlights"]),
        })
    urls = []
    for u in [
        "http://mpesa-care-verify.test/login", "bit.ly/x",
        "https://safaricorn-care.test/verify", "http://41.0.0.12/a",
        "https://login.example@fuliza-boost.test/",
        "https://safaricom.co.ke.account-update.test/signin",
        "https://www.safaricom.co.ke/personal/m-pesa",
        "https://m-pesa-bonus-claim-now.test/claim",
        "https://xn--safricom-9za.test/", "https://equlty-bank.test/login",
        "https://kra-refund-portal.test/verify", "ftp://x.test",
        "https://a.b.c.d.example/path?x=1", "not a url",
    ]:
        r = check_url(u)
        urls.append({"input": u, "valid": r.valid, "score": r.score,
                     "band": r.band, "flags": sorted(r.flags())})
    return {"messages": messages, "urls": urls}


def _parity(out: str) -> None:
    Path(out).write_text(json.dumps(build_parity(), indent=1,
                                    ensure_ascii=False))
    print(f"Wrote {out}")


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    if cmd == "init":
        _init()
    elif cmd == "reset":
        _reset()
    elif cmd == "train":
        _train()
    elif cmd == "parity" and len(argv) == 2:
        _parity(argv[1])
    elif cmd == "snapshot" and len(argv) == 2:
        _snapshot(argv[1])
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
