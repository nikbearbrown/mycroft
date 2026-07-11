# Database Setup (Supabase / Postgres)

The Hacker News AI Buzz Tracker stores **one row per run** in a single table,
`hn_buzz_runs`. Each row is a self-contained snapshot: the full ranked
leaderboard, per-entity raw metrics, and (later) narratives and community
opinions. The workflow reads back the most recent complete row to compute
buzz velocity, and inserts a new row at the end of each run.

This guide uses **Supabase** (free tier, hosted Postgres), but any Postgres
instance works — the SQL and the n8n Postgres node config are identical.

---

## 1. Create the database

### Option A — Supabase Cloud (recommended)

1. Go to [supabase.com](https://supabase.com) and sign up (GitHub login works).
2. **New Project** → name it, set a strong database password (save it), pick a
   nearby region. Wait ~2 minutes for provisioning.
3. Open **SQL Editor** and run the [schema](#2-schema) below.
4. Grab connection details from **Project Settings → Database → Connection
   info** (Host, Port, Database `postgres`, User, Password). You'll use these to
   create the n8n Postgres credential in step 3.

> Because n8n runs in Docker and Supabase is remote, the connection goes over
> the internet normally — no special container networking is needed.

### Option B — local Postgres

Any local Postgres (or a `postgres` service added to `docker-compose.yml`)
works. Run the schema below with `psql` or a GUI client. If Postgres runs in a
sibling container, the n8n host is the **container/service name**, not
`localhost`.

---

## 2. Schema

```sql
create table hn_buzz_runs (
  id                 uuid default gen_random_uuid() primary key,
  created_at         timestamptz default now(),
  run_date           text,        -- window-start date, YYYY-MM-DD (UTC)
  window_hours       int,         -- lookback window (default 24)
  watchlist_version  text default 'v1',  -- see watchlist governance in plan.md
  complete           boolean default true,  -- false = partial run; excluded from velocity baseline
  leaderboard        jsonb,       -- ranked entities: score, velocity, components, top stories
  narratives         jsonb,       -- per-entity narrative/theme/tone (added Week 7)
  community_opinions jsonb,       -- per-entity comment-grounded opinion (added Week 9)
  raw_metrics        jsonb        -- per-entity storyCount / points / comments / frontPage
);

-- The read query fetches the latest complete run; index for it.
create index if not exists hn_buzz_runs_recent
  on hn_buzz_runs (complete, created_at desc);
```

### Watchlist version guard (Week 5 — closes a real gap, not just documentation)

`watchlist_version` on `hn_buzz_runs` is not just a label — the previous-run
read query below filters on it, so a future watchlist bump (v1 → v2) cannot
be silently compared against pre-bump history by the velocity calculation.
Before this, `watchlist_version` existed only on `hn_buzz_runs_backfill` as
metadata; the live table had no such column and no version check, so the
Week 1 watchlist governance rule (treat a version bump as a clean break) was
unenforced for live runs. This must land before the Week 11 watchlist v2
expansion.

If `hn_buzz_runs` already exists without this column, migrate with:

```sql
alter table hn_buzz_runs add column watchlist_version text default 'v1';
```

### Backfill table (Week 5 — kept separate from `hn_buzz_runs`)

`backfill_history.py` writes to its own table, **not** `hn_buzz_runs`. The
live workflow's `Get Previous Run` query (below) picks the most recent row by
`created_at` (insert time), not `run_date`. A backfilled row inserted today
would have `created_at = now()` even though it represents a historical week —
so it would look like "the most recent run" and get used as the next live
run's velocity baseline, comparing a 24h daily window against a 168h weekly
one. A dedicated table makes that impossible and gives the Week 6 backtest a
single, unambiguous source for historical buzz.

```sql
create table hn_buzz_runs_backfill (
  id                uuid default gen_random_uuid() primary key,
  created_at        timestamptz default now(),
  run_date          text,        -- window-start date, YYYY-MM-DD (UTC)
  window_hours      int,         -- backfill chunk size in hours (168 = weekly)
  watchlist_version text,        -- e.g. "v1" — see watchlist governance in plan.md
  complete          boolean default true,
  leaderboard       jsonb,       -- same shape as hn_buzz_runs.leaderboard
  raw_metrics       jsonb
);

create index if not exists hn_buzz_runs_backfill_date
  on hn_buzz_runs_backfill (run_date);
```

The live workflow never reads this table and this table is never read by
`Get Previous Run` — the two are wired independently. Week 6's backtest
queries `hn_buzz_runs_backfill` directly by `run_date` for the historical
buzz series.

### Trailing baselines (Week 5 — `compute_trailing_baselines.py`)

One row per entity: the trailing average of raw metrics and buzz score across
the backfilled weeks, so velocity/the backtest have "this entity's typical
week" to compare against instead of cold-starting.

```sql
create table entity_baselines (
  id                    uuid default gen_random_uuid() primary key,
  computed_at           timestamptz default now(),
  entity                text,
  ticker                text,
  watchlist_version     text,
  weeks_used            int,     -- how many backfilled weeks fed this average
  avg_story_count       numeric,
  avg_total_points      numeric,
  avg_total_comments    numeric,
  avg_front_page_count  numeric,
  avg_buzz_score        numeric
);

create index if not exists entity_baselines_entity
  on entity_baselines (entity, computed_at desc);
```

Re-running `compute_trailing_baselines.py` inserts a fresh set of rows rather
than updating in place — `computed_at` + the index lets you always pull the
latest baseline per entity while keeping prior computations for comparison.

### Column notes

| Column | Purpose |
|---|---|
| `run_date` | Human-readable window-start date. Not unique — you may have multiple runs per day during testing. |
| `window_hours` | The trailing window the run covered (24 by default). |
| `watchlist_version` | The watchlist version this run was scored against (`v1`). The previous-run read query filters on this so a future version bump can't be compared against pre-bump history. |
| `complete` | `true` for a full run. A partial/failed run is written `false` (or not at all) so it never becomes the velocity baseline. |
| `leaderboard` | The ranked array the scoring node emits: `buzzScore`, `velocity`, `scoreComponents`, `breakout`, `topStory`, etc. This is what the next run reads back. |
| `narratives` | Null until Week 7 (LLM narrative layer). |
| `community_opinions` | Null until Week 9 (Community Opinion analyzer). |
| `raw_metrics` | Per-entity raw counts, keyed by entity name. |

---

## 3. Configure the n8n Postgres credential

In n8n → **Credentials → New → Postgres**, fill in the values from step 1:

| Field | Supabase value |
|---|---|
| Host | `db.<project-ref>.supabase.co` (or the pooler host) |
| Port | `5432` (direct) or `6543` (transaction pooler) |
| Database | `postgres` |
| User | `postgres` (or the pooler user) |
| Password | your project DB password |
| SSL | `require` (Supabase requires SSL) |

Use the same credential on both Postgres nodes below.

---

## 4. The two queries the workflow uses

### Read — `Get Previous Run` (runs before scoring)

Operation **Execute Query**:

```sql
SELECT run_date, leaderboard
FROM hn_buzz_runs
WHERE complete = true
  AND watchlist_version = 'v1'
ORDER BY created_at DESC
LIMIT 1;
```

- Returns **0 rows on the first ever run** → the scoring node treats every
  entity as cold-start (velocity 0). No special handling needed.
- Filtering `complete = true` guarantees a half-finished run never becomes the
  baseline for the next run.
- Filtering `watchlist_version = 'v1'` guarantees a future watchlist bump
  (v1 → v2) can't be silently compared against pre-bump history — update this
  literal when the watchlist version changes (Week 11).
- The returned row is merged into the scoring node's input; the scoring node
  looks up each entity in the previous `leaderboard` to compute acceleration.

### Insert — `Save Snapshot` (runs after scoring)

Operation **Execute Query** (parameterized — do **not** interpolate values into
the SQL string; JSON containing apostrophes will break it and is an injection
risk):

```sql
INSERT INTO hn_buzz_runs (run_date, window_hours, watchlist_version, leaderboard, raw_metrics, complete)
VALUES ($1, $2, $3, $4::jsonb, $5::jsonb, $6);
```

**Options → Query Parameters:**

```
{{ $json.run_date }}, {{ $json.window_hours }}, {{ $json.watchlist_version }}, {{ JSON.stringify($json.leaderboard) }}, {{ JSON.stringify($json.raw_metrics) }}, {{ $json.complete }}
```

- `JSON.stringify(...)` is correct here: Postgres receives text and `::jsonb`
  casts it. Apostrophes are safe because these are bound parameters.
- Leave **Continue On Fail = off** so a write failure propagates to the Error
  Trigger workflow rather than silently passing.

> **Why parameters, not string interpolation or the Insert operation?**
> Inline `'{{ ... }}'` breaks on any apostrophe in a story title
> (`Jamesob's guide` → SQL syntax error). The Insert operation validates jsonb
> columns as objects and rejects a stringified value. Execute Query +
> parameters + `::jsonb` avoids both pitfalls.

---

## 5. Verify

1. **First run** — trigger the workflow manually.
   - `Get Previous Run` returns 0 rows; every entity shows `coldStart: true`,
     `velocity: 0`.
   - `Save Snapshot` inserts one row. Confirm in Supabase:
     ```sql
     select id, run_date, complete, jsonb_array_length(leaderboard) as n_entities
     from hn_buzz_runs order by created_at desc limit 1;
     ```
2. **Second run** — trigger again.
   - `Get Previous Run` now returns the row from run 1.
   - Entities show `coldStart: false` and a **computed velocity** (non-zero once
     the underlying HN metrics differ between runs).
3. **Zero-hit entity** — an entity with no stories stores real zeros
   (`storyCount: 0`), is flagged `lowConfidence: true`, and is scored on the
   sparse floor rather than skipped.

Meeting "two consecutive runs with a correctly computed non-zero velocity" is
part of the Phase 1 exit criteria.

---

## 6. Verify the backfill (Week 5)

Run after `python backfill_history.py --days 90` (no `--dry-run`) has finished
inserting into `hn_buzz_runs_backfill`.

```sql
-- Row count and date range: expect ~13 rows spanning ~90 days, one per week.
select count(*) as n_weeks, min(run_date) as earliest, max(run_date) as latest
from hn_buzz_runs_backfill;

-- Entity coverage: every row should have all 12 watchlist entities.
select run_date, jsonb_array_length(leaderboard) as n_entities
from hn_buzz_runs_backfill
order by run_date;

-- Confirm the AMD query-pollution bug stayed fixed: story counts should look
-- like a normal watchlist entity (single digits to ~30/week), not 900+.
select run_date, raw_metrics->'AMD'->>'storyCount' as amd_story_count
from hn_buzz_runs_backfill
order by run_date;

-- Sanity check watchlist_version is stamped on every row (governance, plan.md).
select distinct watchlist_version from hn_buzz_runs_backfill;

-- Confirm hn_buzz_runs (the live table) was NOT touched by the backfill.
select count(*) from hn_buzz_runs;
```

Expect: ~13 rows, 12 entities per row, no gaps in `run_date`, AMD counts in the
same range as other mid-tier entities (not three digits), a single
`watchlist_version` value (`v1`), and the live `hn_buzz_runs` count unchanged
from before the backfill ran.
