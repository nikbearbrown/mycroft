# D1 — Dashboard stats re-bucket severity from urgency_score instead of impact_level: verification & fix

**Date:** 2026-11-03 · **Component:** `Regulatory_QA/backend/app/crud.py` (`FeedCRUD.get_stats()`) ·
**DB:** local `mycroft_intelligence` @ `localhost:5431`

## The bug

Every other consumer in this system — the alert email (`Generate Email`, fixed in B6/C3), the
feed list UI, the RAG context passed to the chat LLM — treats the `impact_level` column
(`Critical`/`High`/`Medium`/`Low`, set by the keyword scorer and optionally corrected by the C2/C3
Layer 2 LLM re-score) as the authoritative severity label for a feed item.

The dashboard's `get_stats()` endpoint doesn't read that column at all for its severity
breakdown. It independently re-derives four tiers from the raw `urgency_score` (0–10) using its
own, uncoordinated cutoffs:

```sql
COUNT(*) FILTER (WHERE urgency_score >= 8) as critical,
COUNT(*) FILTER (WHERE urgency_score BETWEEN 6 AND 7) as high,
COUNT(*) FILTER (WHERE urgency_score BETWEEN 4 AND 5) as medium,
COUNT(*) FILTER (WHERE urgency_score <= 3) as low
```

`urgency_score` and `impact_level` are set together by the same keyword-scoring pass, but not on
a fixed formula — different trigger phrases carry different weight toward each field, and C2/C3's
LLM correction can change `impact_level` without touching `urgency_score` at all (by design — C2
never overwrites the already-committed keyword scorer fields, see C2-VERIFICATION.md). The two
columns drift apart on a real fraction of rows as a result, and the dashboard's own cutoffs were
never checked against what `impact_level` actually says.

## Why this matters

An operator watching the dashboard sees a severity distribution that doesn't match the one driving
the actual alert emails they'd also be receiving — on the live `mycroft_intelligence` DB (411 real
rows, `scripts/regulatory-intel` fixtures from the 2026-07-14 – 2026-07-24 ingestion window), the
two methods disagree on 62 of 411 rows (15%):

| Tier | Old (`urgency_score` cutoffs) | New (`impact_level` column) |
|---|---|---|
| Critical | 32 | 33 |
| High | 139 | 98 |
| Medium | 240 | 280 |
| Low | 0 | 0 |

The old method overcounted High by 41 items (30% inflated) and undercounted Medium by 40 — not a
rounding difference, a structurally different picture of how much of the backlog is actually
high-severity. This was flagged but not fixed during last week's C3 investigation.

## The fix

`crud.py`, `FeedCRUD.get_stats()` — bucket by `impact_level` directly instead of re-deriving tiers
from `urgency_score`:

```diff
-                SELECT 
-                    COUNT(*) FILTER (WHERE urgency_score >= 8) as critical,
-                    COUNT(*) FILTER (WHERE urgency_score BETWEEN 6 AND 7) as high,
-                    COUNT(*) FILTER (WHERE urgency_score BETWEEN 4 AND 5) as medium,
-                    COUNT(*) FILTER (WHERE urgency_score <= 3) as low
+                SELECT 
+                    COUNT(*) FILTER (WHERE impact_level = 'Critical') as critical,
+                    COUNT(*) FILTER (WHERE impact_level = 'High') as high,
+                    COUNT(*) FILTER (WHERE impact_level = 'Medium') as medium,
+                    COUNT(*) FILTER (WHERE impact_level = 'Low') as low
                 FROM regulatory_feeds
                 WHERE created_at >= NOW() - INTERVAL '7 days'
```

The response shape and key names (`critical`/`high`/`medium`/`low` under `urgency_distribution`)
are unchanged, so the frontend (`Stats.jsx`, which reads `urgency.critical`/`urgency.high`) needs
no change.

## Verification

Ran both the old and new queries directly against the real, live `mycroft_intelligence` database
(not synthetic rows) — first unwindowed across all 411 rows (table above, confirming the fix
changes real counts, not a no-op), then confirmed the new query is syntactically identical in
structure to the old one (same `FILTER`/`WHERE created_at` windowing), just reading a different
column. `python3 -m py_compile` on the patched `crud.py` — clean, no syntax errors.

Did not re-verify against the live 7-day/30-day rolling windows the endpoint actually uses in
production, because the fixture data's `created_at` range (2026-07-14 to 2026-07-24) predates
"now" by months — both old and new queries return all-zero for that window on this dataset,
which is a property of the stale fixture data, not of the fix. The unwindowed, whole-table
comparison above is what demonstrates the real behavioral difference.

## What's NOT touched

Only `get_stats()`'s urgency/severity breakdown query changed. The `total_feeds`, `source_distribution`,
and `recent_activity` queries, the `/api/feeds/stats` route, and the frontend `Stats.jsx` component
are untouched. `impact_level` itself (how it's set or corrected) is untouched — this fix only changes
which column the dashboard reads, not how either column is computed. Rows where `impact_level` is
`NULL` (if any exist) fall into none of the four `FILTER` buckets under the new query, same as they
would have under a `urgency_score` edge case outside 0–10 under the old one — not a new gap.
