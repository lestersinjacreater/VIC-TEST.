# Integrations: real, simulated, and future

Research for this build was done on 21 October 2026 from Safaricom's
public pages. Nothing below claims access LINDA does not have.

## Summary

| Integration | Status in this build | What it does |
|---|---|---|
| Rule-based scanner and link checker | **Real**, runs locally | Explains risk in messages and links |
| Template similarity, model, graph clustering | **Real**, synthetic data only | Links reports to campaigns |
| `MockFraudIntelligenceProvider` | **Simulated** (default) | Receives reports, simulates review, simulated watchlist |
| `SafaricomFraudIntelligenceProvider` | **Disabled** | Placeholder for a future authorised integration |
| Safaricom SIM-swap check (Daraja) | **Not built** | Documented commercial API; noted for the roadmap |
| Google Safe Browsing | **Optional**, off by default | Link reputation when a server-side key is set |
| Official reporting channels | **Real guidance**, handoff only | The user forwards scam SMS to 333 themselves |

## Official reporting channels (handoff, verified)

What LINDA tells users, and why:

- **Forward the scam SMS to 333**, or text 333 with the number that
  contacted you. Safaricom's "Tips for staying safe" page says this gets
  numbers blocked and protects other customers.
  Source: https://safaricom.co.ke/fraud-awareness/tips-tricks and
  https://safaricom.co.ke/fraud-awareness/scams-extortion
- **Mistaken transactions:** forward the M-PESA message to **456**, or use
  Reverse Transaction in the M-PESA / mySafaricom app, or Zuri on
  WhatsApp. Source:
  https://safaricom.co.ke/media-center-landing/terms-and-conditions/m-pesa-reversal
- **Genuine calls** come from 0722 000 000 per Safaricom's guidance;
  staff never ask for your PIN; never dial codes a caller gives you.
- **Threats** go to the police.
- **\*234#** was not found described as a fraud-reporting channel on
  Safaricom's fraud-awareness pages, so LINDA does not present it as one.
  Verify before adding it.

A handoff is different from an in-app report: the user sends it from
their own phone, to Safaricom. A LINDA report goes only to LINDA's
simulated service. LINDA never sends an SMS to 333 or anywhere else.

## Safaricom developer APIs (what is actually documented)

The public Daraja portal (https://developer.safaricom.co.ke/apis)
documents **M-PESA payment APIs**. These move money; they are **not** a
fraud-reporting or fraud-intelligence API and give no access to fraud
reports, subscriber data or network-level intelligence.

A **SIM-swap check** ("Swap" API) is described in Daraja documentation
mirrors and press coverage as a commercial API returning the last SIM
swap date, aimed at banks. Reported onboarding: signed commercial
agreement, company registration, a connection fee and per-request
pricing. Treat these details as unconfirmed until Safaricom provides the
official contract. It could later power "your SIM was swapped recently"
warnings, with the customer's consent.

No public API was found for submitting fraud reports, reading
fraud-team watchlists, network-level blocking, or caller reputation.

## FraudIntelligenceProvider

`backend/app/providers/base.py`

```python
class FraudIntelligenceProvider(ABC):
    def describe(self) -> ProviderDescription: ...
    def submit_report(self, report: OutboundReport) -> SubmissionReceipt: ...
    def poll_status(self, provider_ref, ctx) -> list[StatusUpdate]: ...
    def lookup_indicator(self, kind, value, meta=None) -> IntelligenceSignal: ...
    def health(self) -> dict: ...
```

Errors: `ProviderUnavailable` (transient; the report stays
`submitted_locally` and is retried on the next status check) and
`ProviderNotConfigured` (missing approval, credentials or contract).

### What would be sent (`OutboundReport`)

`report_ref`, `report_type`, `indicator_kind`, `indicator` (normalised
number or domain), `category`, `submitted_at`, `reporter_reference`
(salted one-way hash), and only with consent `notes` and
`message_excerpt` (both redacted), plus `linked_campaign_hint`. Never: raw
device ID, name, contacts, location, call log, PIN, OTP, ID or card
numbers. Users see this list before every submission.

### Mock provider (default)

- Service: in-process simulation. Documentation: this file.
- Authentication: none. Approvals: none.
- Responses: receipt `SIM-XXXXXXXX`; `under_review_simulated` after
  `LINDA_SIM_REVIEW_AFTER_S`; `corroborated_simulated` (linked to a
  campaign or 3+ reporters) or `inconclusive` after
  `LINDA_SIM_OUTCOME_AFTER_S`. Never `confirmed_by_authorised_source`.
- Errors and retries: the outage switch (`POST /api/demo/outage`) makes
  calls raise `ProviderUnavailable`; reports wait and retry.
- Rate limits: none simulated.

### Safaricom provider (disabled)

- Enabled only with `LINDA_FRAUD_PROVIDER=safaricom` **and** all of
  `LINDA_SAFARICOM_FRAUD_API_BASE_URL`, `_CLIENT_ID`, `_CLIENT_SECRET`,
  `_AGREEMENT_REF`. Even then it raises `ProviderNotConfigured` until a
  developer implements the methods against the contract Safaricom
  supplies. It cannot fabricate a successful response (tested).
- Expected authentication: OAuth client credentials, as with Daraja
  (to be confirmed by contract).
- Approvals needed: partnership or commercial agreement, data-sharing
  agreement, DPIA under the Data Protection Act 2019, security review.
- Planned error handling: exponential backoff for transient errors,
  idempotent submission keyed on `report_ref`, reports kept locally
  until acknowledged.
- Rate limits: unknown until documented.

### What cannot be built without Safaricom approval

Sending reports to Safaricom's fraud team; receiving watchlists or fraud
signals; network-level number blocking; SIM-swap or any subscriber data;
automatic caller ID at network level.

## Google Safe Browsing (optional)

Set `LINDA_SAFE_BROWSING_API_KEY` to let the backend call the Lookup API
v4 (`threatMatches:find`). Only the link is sent. Failures fall back to
local checks. The code is unit-tested with a mocked transport but was not
exercised against the live service; confirm the current API version and
terms before enabling. A "not listed" result is never shown as "safe".

## Native capabilities (not in the web demo)

Automatic caller ID needs a native app: Android `CallScreeningService`
(role-based permission) or iOS Call Directory extensions. Automatic SMS
scanning would need Android SMS permissions, which Google Play restricts.
Both would process on the device first and be opt-in.
