# Prioritised future upgrades

## Now (before or right after the hackathon)

1. **Native Android shell** with `CallScreeningService` caller labels and
   opt-in SMS scanning, reusing the TypeScript rulebook on-device
   (React Native or a WebView wrapper).
2. **Native-speaker review** of all Kiswahili and Sheng text and rules;
   add more Sheng variants.
3. **Real-world rule tuning** with consented, anonymised samples; track
   false positives on legitimate M-PESA and bank messages.

## Next (with a Safaricom partner)

4. **Authorised integration**: implement `SafaricomFraudIntelligenceProvider`
   against an agreed contract — report submission, status callbacks,
   idempotency, backoff, audit logs.
5. **Confirmed indicators**: replace the simulated watchlist with signed,
   expiring indicators from the fraud team; show real
   "Confirmed by authorised source" status only from that feed.
6. **SIM-swap warnings** via the Daraja SIM-swap check, with customer
   consent, before high-risk actions.
7. **Consent and DPIA package**: consent records, retention schedule,
   data-sharing agreement, ODPC registration where required.

## Later

8. **Better models**: multilingual embeddings for template similarity,
   calibrated probabilities, active learning from analyst decisions.
9. **Analyst console**: campaign triage, merge/split campaigns, evidence
   export for law enforcement.
10. **Push alerts** for campaign matches and report updates.
11. **Accessibility and reach**: USSD/SMS-only check flow for feature
    phones; voice explanations.
12. **Operational hardening**: distributed rate limiting (Redis),
    observability, load tests, penetration test.
