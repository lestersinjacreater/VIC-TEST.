# API reference

Base path `/api`. Interactive OpenAPI docs: http://localhost:8000/docs.

Every request that touches personal reports sends
`X-Linda-Client: <random device id>` (8–64 letters, digits or dashes).
The server stores only a salted hash of it.

Errors always look like:

```json
{"error": {"code": "invalid_phone",
           "message": "Enter a Kenyan mobile number...",
           "details": null}}
```

Common codes: `validation_error` (422), `invalid_phone`, `invalid_url`,
`missing_client` (400), `rejected` (400, honeypot), `rate_limited` (429),
`not_found` (404), `consent_required` (400), `demo_only` (403),
`internal_error` (500).

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness and provider health |
| GET | `/meta` | Mode, exact disclaimer, provider, versions |
| POST | `/scan` | Server-side scan + model second opinion (needs `consent: true`) |
| POST | `/links/check` | Link heuristics; optional reputation lookup |
| POST | `/indicators/lookup` | Caller/indicator classification with evidence |
| POST | `/intel/assess` | Preview campaign links for a number and/or message (not saved) |
| GET | `/campaigns` | Campaign list |
| GET | `/campaigns/{id}` | Campaign detail, indicators, provenance, timeline |
| GET | `/graph` | Network graph (`campaign`, `min_confidence`, `brands`, `reports`) |
| GET | `/graph/clusters` | Connected clusters, shared indicators, centrality |
| POST | `/reports/preview` | Exactly what would be shared, without saving |
| POST | `/reports` | Submit a report (dedupe, rate limit, link, hand to provider) |
| GET | `/reports` | This device's reports (statuses refreshed) |
| GET | `/reports/{ref}` | One report (only for the device that made it) |
| POST | `/reports/{ref}/advance` | Demo only: jump the simulated review to its outcome |
| GET | `/analytics/summary` | All analytics, labelled simulated |
| GET | `/ml/metrics` | Model training and evaluation metrics |
| GET | `/integrations` | Every integration, real or simulated, with details |
| GET | `/dashboard` | Home screen summary |
| GET | `/demo/scenario` | Scripted call and SMS for the guided demo |
| POST | `/demo/reset` | Demo only: restore seed data |
| POST | `/demo/outage` | Demo only: `{"enabled": true}` simulates a provider outage |
| GET | `/me/export` | Everything the backend holds for this device |
| DELETE | `/me/data` | Delete this device's reports |

## Examples

### Look up a number

```bash
curl -s -X POST localhost:8000/api/indicators/lookup \
  -H 'Content-Type: application/json' \
  -d '{"kind":"phone","value":"0700000141"}'
```

```json
{
  "display": "+254 700 000 141",
  "classification": "verified_campaign_indicator",
  "classification_label": "Campaign indicator (simulated verification)",
  "reason": "Linked to a campaign by a simulated authorised source...",
  "report_count": 6,
  "distinct_reporters": 6,
  "campaigns": [{"campaign_id": "C-02", "provenance": "confirmed_simulated",
                 "confidence": 0.92}],
  "evidence": [...],
  "last_updated": "2026-10-20T...",
  "external_signal": {"found": true, "simulated": true,
                      "source_label": "Simulated fraud-team watchlist (demo data)"}
}
```

Classifications: `trusted`, `unknown`, `suspicious`, `reported_scam`
(3+ distinct reporters), `verified_campaign_indicator`.

### Submit a report

```bash
curl -s -X POST localhost:8000/api/reports \
  -H 'Content-Type: application/json' \
  -H 'X-Linda-Client: my-test-device-01' \
  -d '{"report_type":"sms","indicator":"0700000199",
       "category":"otp_pin_harvest",
       "message_text":"Send the code to http://mpesa-care-verify.test/x",
       "share_message":true}'
```

Body fields: `report_type` (`call|sms|url`), `indicator`, `category`,
`notes` (≤ 500), `message_text` (≤ 1000), `share_message`, `share_notes`,
`website` (honeypot, leave empty).

Response (abridged):

```json
{
  "ref": "LR-7KQ2M9XA",
  "status": "received_by_demo_service",
  "status_label": "Received by demo service",
  "simulated": true,
  "provider": "mock",
  "provider_ref": "SIM-1A2B3C4D",
  "linked_campaign_id": "C-02",
  "link": {
    "linked": true, "confidence": 0.988,
    "summary": "Likely part of C-02 (...) with 99% confidence.",
    "evidence": [{"type": "shared_url", "weight": 0.85, "strong": true, ...},
                 {"type": "similar_template", "weight": 0.9, ...}],
    "ignored_signals": ["Number prefix or sequence similarity ...", "..."]
  },
  "events": [{"status": "submitted_locally", ...},
             {"status": "received_by_demo_service", "simulated": true, ...}],
  "duplicate": false
}
```

A repeat of the same indicator or message from the same device within
24 hours returns the original report with `"duplicate": true`.

### Check a link

```bash
curl -s -X POST localhost:8000/api/links/check \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://safaricorn-care.test/verify"}'
```

Returns `score`, `band`, `flags` and every check with `triggered`,
`weight` and `detail`, plus `source: "local_heuristic"` and
`reputation.source` (`not_configured` unless a key is set).
