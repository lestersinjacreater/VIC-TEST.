# Hackathon presentation guide

Target: 6 minutes plus questions. Everything shown is fictional.

## Before you present

1. `./scripts/dev.sh` and open http://localhost:5173 (or the Codespace
   URL) on a laptop and, ideally, a phone on the same Codespace URL.
2. My protection → Presenter tools → **Reset demo environment**.
3. Keep tabs open: Home, Guided demo, Scam network, Analytics.
4. Zoom the browser to 110–125% for the room.
5. Fallback: if the backend dies, the app shows the offline snapshot and
   keeps reports "Submitted locally". Say so and carry on.

## Script

### 1. The problem (45 s)

"Kenyans get fake reversal requests, fake customer-care calls and fake
Fuliza offers every week. Each one is handled alone: a customer
forwards one SMS to 333, a fraud team sees one number. Scammers reuse
the same links and the same wording across dozens of numbers. LINDA
connects those dots, on the customer's phone, and explains every
connection."

### 2. Guided demo (3 min) — `/demo`

Click **Reset and start**, then **Next** through the steps:

| Step | Say |
|---|---|
| Call | "A number we've never seen calls, claiming to be customer care." |
| Flags the call | "LINDA keeps two signals apart. The number is unknown — and unknown is not safe. But what the caller says scores very high: staff claim plus a code request." |
| SMS | "The same number texts a link and asks for the code." |
| Scan | "This runs on the phone. Every point of the score is explained, in English, Kiswahili or Sheng." |
| Link | "It never opens the link. It reads it: brand name on a domain that isn't Safaricom's." |
| Report | "Before sending, the customer sees exactly what is shared. No PIN, no contacts, an anonymous reference." |
| Response | "Every status is labelled simulated." Click **Fast-forward**. |
| Campaign | "The new number lands inside campaign C-02, next to six other numbers using the same link." |
| Why | "Shared URL, near-identical template. Similar-looking numbers are deliberately ignored — we never say two numbers are the same person." |
| Protect | Block the number. "Personal block, not a network block." |
| Dashboard | "And the customer's dashboard updates." |

### 3. The intelligence layer (1 min) — `/intel`

- Point at the line styles: solid = confirmed (simulated authorised
  source), dashed = community reports, dotted = model-inferred.
- Click **Watch a new number join a campaign**.
- Click the number `+254 700 000 145`: "It appears in two campaigns.
  LINDA says that may be a reused or compromised line, not one person."

### 4. Honest ML (30 s) — `/analytics`

"Rules first, then template similarity, then an explainable model. We
test on message families the model never saw: F1 is about 80%, not the
100% a random split gives. That's the honest number, on synthetic data."

### 5. Path to production (45 s) — `/integrations`

"The fraud-intelligence layer is behind one interface. Today it's a
labelled simulation. There is no public Safaricom fraud-report API, so
the Safaricom adapter is disabled and refuses to fake success. With an
agreement it plugs in without changing the app — and the customer still
sees exactly what is shared."

## Likely questions

**How is this different from fraud detection Safaricom already runs?**
Network-side systems see traffic; they don't sit with the customer at
the moment of decision. LINDA explains risk on the device, captures
consented, structured reports, and links them into campaigns a fraud
team can act on. It complements internal systems rather than
replacing them.

**Can it read my SMS and calls?** Not in the web demo. A native app
could, with explicit Android call-screening and SMS permissions,
processing on the device first.

**What stops people from mass-reporting an innocent number?** Rate
limits, per-device dedupe, three distinct reporters before "reported
scam", official contacts never auto-linked, and reports are always
shown as allegations.

**Is the model accurate?** It is evaluated on held-out template
families from synthetic data only. Real accuracy needs real, consented
data and Safaricom's ground truth.

**Data protection?** No accounts, hashed device IDs, automatic
redaction, 90-day retention, export and delete. A live version would need
a DPIA and data-sharing agreement under the Data Protection Act 2019.
