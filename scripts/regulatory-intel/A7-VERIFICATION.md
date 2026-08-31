# A7 — Mark-email-sent scoping: verification & measured evidence

**Date:** 2026-08-30 · **Workflow:** `workflow.dev.json` (`Mark email sent` node) · **DB:** local `mycroft_intelligence` @ `localhost:5431` (already running, not started for this check)

## The bug

The "Mark email sent" Postgres node re-derived its own copy of "what counts as high-priority"
instead of reading it from the node that actually built the email:

```sql
-- OLD
UPDATE regulatory_feeds
SET email_sent = TRUE, email_sent_at = NOW()
WHERE (urgency_score > 7 OR impact_level IN ('Critical', 'High'))
  AND email_sent = FALSE;
```

Meanwhile the node that actually decides what goes into the email ("High Priority Filter") uses a
different, narrower rule: `urgency_score > 6` only — no `impact_level` clause.

## Why the two rules disagree (not just a threshold typo)

`Keyword Analysis & Urgency Scoring` sets `impact_level` independently of the score for
enforcement/fraud hits:

```js
function determineImpactLevel(urgencyScore, isEnforcement, isFraud) {
  if (urgencyScore >= 9 || isFraud) return 'Critical';
  if (urgencyScore >= 7 || isEnforcement) return 'High';   // <-- bypasses the score
  if (urgencyScore >= 5) return 'Medium';
  return 'Low';
}
```

So an item with `urgency_score` as low as 5 or 6 can still get `impact_level = 'High'` or
`'Critical'` purely from an enforcement/fraud keyword match. "High Priority Filter"
(`urgency_score > 6`) would never select that row for an email — but the old "Mark email sent"
query (`impact_level IN ('Critical','High')`) would still match it and flip it to `email_sent = TRUE`.

## Live measurement (2026-08-30)

Query against the real `regulatory_feeds` table (not a simulation):

```sql
SELECT id, title, urgency_score, impact_level
FROM regulatory_feeds
WHERE impact_level IN ('Critical','High')
  AND urgency_score <= 6
  AND email_sent = FALSE
ORDER BY id;
```

**12 real rows matched**, as of 2026-08-30 — genuine SEC/FINRA/CFTC items that "High Priority
Filter" would never place in an email, but that the old query would flip to `email_sent = TRUE`
the next time it ran:

| id | title | urgency_score | impact_level |
|---|---|---|---|
| 112 | Sunshine Act Meetings; Open Commission Meeting Thursday, June 25, 2026 | 6 | High |
| 115 | Request for Comment on the Extension of Standard Futures Contracts to 24/7 Trading... | 6 | Critical |
| 153 | SEC Charges 21 Individuals With Alleged Wide-Reaching Insider Trading Scheme | 5 | Critical |
| 322 | Illinois investment advisor indicted in $4M Ponzi fraud scheme - InvestmentNews | 6 | Critical |
| 326 | SEC charges unregistered advisor with fraud over fake credentials, false AI trading claims | 6 | Critical |
| 338 | Hedge Clauses in Focus: The SEC Charges an Investment Adviser with Four Advisers Act Violations | 5 | High |
| 347 | SEC News Roundup: Private Funds Rule Compliance Date Set... | 5 | High |
| 356 | SEC Scorches New Mexico Investment Advisers for Allegedly Defrauding Elderly Clients | 6 | Critical |
| 364 | Requirement To Identify All Real Parties in Interest to a Third Party Request... | 6 | Critical |
| 483 | FINRA Expels BD Over Reg BI Violations - ThinkAdvisor | 5 | High |
| 555 | Order Providing Exemptive Relief To Facilitate Listing of Cash-Settled Futures... | 5 | High |
| 1008 | Order Under Section 36 of the Securities Exchange Act of 1934... | 5 | High |

**Honest caveats:**
- This is a live, growing table; 12 is the count *as of this query, 2026-08-30*, not a fixed constant.
- This proves the failure mode is real and currently latent in the data — it does **not** prove
  these specific 12 rows were ever actually mis-marked in the user's live n8n (that workflow is
  hand-built separately from `workflow.dev.json`; whether/when it last ran this exact query is
  unknown). The correct claim is forward-looking: under the old query, these rows *would* flip to
  `email_sent = TRUE` on the next run that matched this condition, without ever having been emailed.
- Some of the 12 (e.g., "Sunshine Act Meetings", the two CFTC/SEC exemptive-relief orders) are
  procedural/routine — consistent with the already-documented C1 keyword-scorer noise problem in
  `FINDINGS.md`. The clearest non-noise examples are rows 153, 322, 326, 356 (real SEC/FINRA
  enforcement actions).

## Fix

```sql
-- NEW
UPDATE regulatory_feeds
SET email_sent = TRUE, email_sent_at = NOW()
WHERE id = ANY($1::int[])
  AND email_sent = FALSE;
-- queryReplacement: $("High Priority Filter").all().map(i => i.json.id)
```

Scoping to the exact ids the email node emitted removes the drift entirely — the update can no
longer flip a row's `email_sent` flag based on a re-derived rule; it can only ever mark what the
email step actually saw.

## Verification method

Rolled-back transaction against the local DB: seeded rows matching the old blanket condition with
`email_sent = FALSE`, ran the new id-scoped query with an id list that deliberately excluded them,
confirmed they were left untouched (`email_sent` still `FALSE`) — proving the new query only
touches what's in its id list, not everything matching the old re-derived condition.
