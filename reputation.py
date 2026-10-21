"""Optional external URL reputation lookups.

Off by default. When LINDA_SAFE_BROWSING_API_KEY is set, the backend
can ask Google Safe Browsing (Lookup API v4) about a link. The key
stays server-side. This path was not exercised against the live
service in this build; check Google's current API version and terms
before enabling it.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings

SB_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"


def reputation_status() -> dict[str, Any]:
    configured = bool(get_settings().safe_browsing_api_key)
    return {
        "id": "google_safe_browsing",
        "configured": configured,
        "detail": "Configured (server-side key)." if configured else
        "Not configured. Only LINDA's local heuristics are used.",
    }


def check_reputation(
    url: str, client: httpx.Client | None = None
) -> dict[str, Any]:
    key = get_settings().safe_browsing_api_key
    if not key:
        return {
            "source": "not_configured",
            "detail": "No external reputation service is configured.",
        }
    body = {
        "client": {"clientId": "linda-demo", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": [
                "MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE",
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    own = client is None
    client = client or httpx.Client(timeout=5.0)
    try:
        resp = client.post(SB_URL, params={"key": key}, json=body)
        resp.raise_for_status()
        matches = resp.json().get("matches", [])
    except (httpx.HTTPError, ValueError) as exc:
        return {
            "source": "google_safe_browsing",
            "error": True,
            "detail": f"Reputation lookup failed ({type(exc).__name__}). "
                      "Local checks still apply.",
        }
    finally:
        if own:
            client.close()
    if matches:
        kinds = sorted({m.get("threatType", "UNKNOWN") for m in matches})
        return {
            "source": "google_safe_browsing",
            "listed": True,
            "detail": "Listed by Google Safe Browsing: " + ", ".join(kinds),
        }
    return {
        "source": "google_safe_browsing",
        "listed": False,
        "detail": "Not on Google Safe Browsing lists. That is not proof "
                  "the link is safe.",
    }
