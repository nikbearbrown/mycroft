# F1 — Dashboard severity stats zeroed out by a stale hardcoded time window: verification & fix

**Date:** 2026-11-19 · **Component:** `Regulatory_QA/backend/app/crud.py` (`FeedCRUD.get_stats()`) ·
**DB:** local `mycroft_intelligence` @ `localhost:5431`

## The bug

D1 (2026-11-03) fixed *which column* `get_stats()`'s severity breakdown reads
(`impact_level` instead of re-derived `urgency_score` cutoffs). It left untouched a second,
separate defect in the same query, flagged at the time as an open issue and never closed: the
`urgency_distribution` query is filtered to `created_at >= NOW() - INTERVAL '7 days'`, and
`source_distribution` to 30 days — while `total_feeds` is an unwindowed `COUNT(*)`, and
`list_feeds()` (which backs `FeedList.jsx`'s panel, including "Select All", see E1-VERIFICATION.md)
applies no date filter at all.

The fixture data's `created_at` range is 2026-07-14 to 2026-07-24. Today is 2026-11-19 — four
months past that range — so both windowed queries return zero rows, unconditionally, on every
single page load.

## Why this matters

Live, on the real `mycroft_intelligence` DB (411 rows):

| Query | Critical | High | Medium | Low |
|---|---|---|---|---|
| Old (`WHERE created_at >= NOW() - INTERVAL '7 days'`) | 0 | 0 | 0 | 0 |
| New (unwindowed) | 33 | 98 | 280 | 0 |

The stats cards show "Total Feeds: 411, Critical: 0, High Priority: 0" while the feed list panel
directly below — same page, same data, `list_feeds`'s default top-100 slice — renders 24
Critical- and 8 High-tagged items a user can click and select right now. This is reached with
*zero clicks*, on the default page load, not an edge case: the dashboard summary flatly
contradicts the list sitting next to it, for as long as the fixture data stays older than 7/30
days (i.e. indefinitely, since nothing re-ingests it).

## The fix

`crud.py`, `FeedCRUD.get_stats()` — drop the 7-day filter on the severity-count query so it reads
the same unwindowed population as `total_feeds` and `list_feeds`:

```diff
             cursor.execute("""
                 SELECT
                     COUNT(*) FILTER (WHERE impact_level = 'Critical') as critical,
                     COUNT(*) FILTER (WHERE impact_level = 'High') as high,
                     COUNT(*) FILTER (WHERE impact_level = 'Medium') as medium,
                     COUNT(*) FILTER (WHERE impact_level = 'Low') as low
                 FROM regulatory_feeds
-                WHERE created_at >= NOW() - INTERVAL '7 days'
             """)
```

`source_distribution`'s 30-day window and `recent_activity`'s 14-day window are left as-is —
`recent_activity` is explicitly a time series (a windowed trend is the point), and
`source_distribution` is a lower-stakes breakdown not directly contradicted by an adjacent,
always-visible list the way the severity snapshot is. Only the severity-count query, which sits
directly above the always-unwindowed feed list, is changed.

## Verification

Ran both the old and new `urgency_distribution` queries directly against the live DB: old
returns 0/0/0/0 (confirmed via `MIN(created_at)=2026-07-14`, `MAX(created_at)=2026-07-24`,
both outside any 7/30-day window from today), new returns 33/98/280/0 — matching D1's own
verified unwindowed `impact_level` counts exactly, confirming this is a time-window defect, not
a data-integrity issue. Separately replicated `list_feeds`'s actual default ordering
(`ORDER BY created_at DESC, urgency_score DESC`, `limit=100`, no date filter) to confirm the
top-100 slice the frontend renders contains real Critical/High rows, demonstrating the two
panels' live disagreement concretely rather than just by query-text inspection.
`python3 -m py_compile` on the patched `crud.py` — clean.

## What's NOT touched

`total_feeds`, `source_distribution`, `recent_activity`, and the `/api/feeds/stats` route are
untouched. D1's `impact_level`-bucketing fix is untouched — this only removes the time window
around it. `list_feeds()` and the frontend (`FeedList.jsx`, `Stats.jsx`, `App.jsx`) are untouched
— this fix makes the stats query match data the frontend already shows unwindowed, not the other
way around.
