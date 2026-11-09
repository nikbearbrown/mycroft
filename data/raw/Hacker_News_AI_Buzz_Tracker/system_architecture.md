# Hacker News AI Buzz Tracker: System Architecture

> Companion to `proposal.md`. This document specifies the **system architecture** for Phase 1: the component decomposition, the data flow between components, the interface contracts at each boundary, and the technology decisions with their rationale. The data schema and watchlist universe are specified separately in `data_architecture.md`.
>
> **This document reflects the implemented Phase-1 Week-4 build.** See `DATABASE_SETUP.md` for the storage schema.

## 1. Scope and architectural goals

Phase 1 delivers a **single n8n workflow** that runs once daily, end to end, with no LLM and no dashboard. The architecture is deliberately constrained to one orchestrator (n8n), one external read source (Hacker News Search API), one persistent store (Supabase Postgres), and one delivery channel (SMTP email). Every component is either a managed free tier or a no-key public API.

The architecture optimizes for four properties, in priority order:

1. **Determinism** — given the same stored history and the same Hacker News data, a run produces the same Buzz Scores. No randomness, no model calls in the scoring path.
2. **Graceful degradation** — a rate limit, an empty response, or a missing prior snapshot degrades to a defined, conservative output rather than failing the run.
3. **Separation of human and machine outputs** — the human digest (HTML email) and the machine signal (structured JSON in Postgres) are distinct artifacts produced from the same run.
4. **Reconfigurability without code change** — the watchlist, the trailing window (`windowHours=24`, configurable), and breakout thresholds are parameters, not hard-coded constants.

## 2. Component diagram

```
                          ┌──────────────────────────────────────────────────┐
                          │                  n8n Workflow                      │
                          │             (single daily execution)               │
                          │                                                    │
   ┌────────────┐  fires  │  ┌─────────────┐   ┌────────────────────────────┐ │
   │  Schedule  │────────►│  │  Watchlist   │   │   Loop (Split In Batches)  │ │
   │  Trigger   │  daily  │  │ (12 entities)│──►│   one iteration / entity   │ │
   └────────────┘         │  └─────────────┘   └─────────────┬──────────────┘ │
                          │                                  │ per entity      │
                          │                                  ▼                 │
   ┌────────────────┐     │                       ┌────────────────────┐       │
   │  Hacker News   │◄────┼───────────────────────│   HTTP Request     │       │
   │  Search API    │ GET │   stories (JSON)       │   (Algolia HN)     │       │
   │  (Algolia)     │────►│                        └─────────┬──────────┘       │
   └────────────────┘     │                                  ▼                  │
                          │                       ┌────────────────────┐        │
                          │                       │ Aggregate & Score  │        │
                          │                       │   (Code node)      │        │
                          │                       └─────────┬──────────┘        │
                          │            (after loop completes)│ scored entities  │
                          │                                  ▼                  │
   ┌────────────────┐     │   read prior run      ┌────────────────────┐        │
   │   Supabase     │◄────┼───────────────────────│ Get Previous Run   │        │
   │   Postgres     │────►│   prior leaderboard    │   (Postgres)       │        │
   │                │     │                        └─────────┬──────────┘        │
   │  hn_buzz_runs  │     │                                  ▼                   │
   │  (single table,│     │                       ┌────────────────────┐         │
   │   one row/run; │     │                       │  Compute Buzz +    │         │
   │   see DATABASE_│     │                       │  Velocity (Code)   │         │
   │   SETUP.md)    │     │                       └─────────┬──────────┘         │
            ▲             │                                  ▼                   │
            │  write run  │                       ┌────────────────────┐         │
            └─────────────┼───────────────────────│  Save Snapshot     │         │
                          │                        │ (Postgres, 1 row)  │        │
                          │                        └─────────┬──────────┘        │
                          │                                  ▼                   │
                          │                       ┌────────────────────┐         │
                          │                       │ Build Digest/Alert │         │
                          │                       │   (Code node)      │         │
                          │                       └─────────┬──────────┘         │
                          │                                  ▼                   │
   ┌────────────────┐     │   send HTML email     ┌────────────────────┐         │
   │  SendGrid SMTP │◄────┼───────────────────────│  Send Email (SMTP) │         │
   │  smtp.sendgrid │     │                        └────────────────────┘        │
   │  .net:587      │     │                                                       │
   └───────┬────────┘     └───────────────────────────────────────────────────--┘
           │ deliver
           ▼
   ┌────────────────┐                              ┌────────────────────────────┐
   │  Maintainer    │                              │  Mycroft Coordination Layer │
   │  inbox (digest │                              │  (consumes JSON signal from │
   │  + alerts)     │                              │   stored snapshot — Phase 1) │
   └────────────────┘                              └────────────────────────────┘
```

The error-handling path is a separate **Error Trigger** workflow wired via Settings → Error Workflow: any node failure (HTTP Request, the Postgres read/write steps) routes to a **Pipeline-Failure Alert** (a maintainer email with the `[HN Buzz ALERT]` prefix) rather than aborting silently. This alert is distinct from the entity breakout alert.

## 3. Components

| # | Component | n8n node type | Responsibility |
| --- | --- | --- | --- |
| C1 | Schedule Trigger | Schedule Trigger | Fire the workflow once per day at a fixed UTC time. |
| C2 | Watchlist | Set | Emit the v1 watchlist (12 entities from `watchlist.json`: `{entity, ticker, queryTerms[], frontPagePoints, breakoutThreshold}`) plus the run-level trailing window (`windowHours=24`). |
| C3 | Loop | Split In Batches | Iterate the watchlist so each entity is collected independently; isolates a per-entity failure to that entity. |
| C4 | Collector | HTTP Request | Query the Hacker News Search API (`search_by_date`) for one entity's query terms over the trailing 24-hour window. |
| C5 | Get Metrics | Code | Parse hits, dedupe by `objectID`, aggregate per entity, retain the top-3 stories, and compute the four scoring components and the 0–100 Buzz Score. |
| C6 | Get Previous Run | Postgres (select) | Load the most recent *complete* prior run to serve as the velocity baseline. |
| C7 | Compute Buzz + Velocity | Code | Compute acceleration vs. the previous complete run's base; evaluate the breakout threshold; mark cold-start and low-confidence entities. |
| C8 | Save Snapshot | Postgres (insert) | Persist the run as a single row (jsonb leaderboard + raw_metrics) in `hn_buzz_runs`. |
| C9 | Build Digest/Alert | Code | Render the ranked HTML digest and assemble breakout alert payloads. |
| C10 | Send Email | Send Email (SMTP) | Deliver the digest and any alerts via SendGrid SMTP. |

## 4. Data flow

A single run proceeds as a linear pipeline with one fan-out (the loop) and one fan-in (scoring runs per entity, velocity onward runs once over the full set):

1. **Trigger → Watchlist.** C1 fires; C2 emits 12 entity items + the 24-hour window config (a parallel *Get Day Ago Unix Time* step computes the window start).
2. **Watchlist → Collector (per entity).** C3 hands each entity to C4 (after an *Entity Term Pair* step). C4 issues a `search_by_date` query bounded by `created_at_i > now − 24h`.
3. **Collector → Score (per entity).** C5 receives raw hits, dedupes by `objectID`, aggregates, retains top-3 stories, and produces one **scored entity record** per watchlist entity.
4. **Fan-in → Read baseline.** After the loop completes, C6 reads the latest *complete* prior run to use as the single-run velocity baseline.
5. **Score + baseline → Velocity.** A *Merge* step joins current scores with the previous run; C7 computes the acceleration (velocity) term, applies the breakout threshold, and sets cold-start/low-confidence flags.
6. **Velocity → Store.** A *Build Run Row* step collapses the leaderboard to one row; C8 writes that single row (jsonb leaderboard + raw_metrics + `complete` boolean) to `hn_buzz_runs`.
7. **Store → Digest.** C9 builds the human HTML digest (ranked) and, on any breakout, the alert payloads from the now-persisted snapshot.
8. **Digest → Email.** C10 sends the digest (`[HN Buzz]`) and, separately, any breakout alerts (`[HN Buzz ALERT]`).
9. **Machine signal.** The stored snapshot in Postgres **is** the canonical machine output; the Mycroft coordination layer reads it directly (Phase 1) — no separate emission step.

The store-before-digest ordering is deliberate: the digest and alerts are rendered from persisted data so the human email can never describe a state that was not durably recorded.

## 5. Interface contracts

### 5.1 Collector → Hacker News Search API (C4 boundary)

- **Endpoint:** `GET https://hn.algolia.com/api/v1/search_by_date`
- **Auth:** none (no key).
- **Query params:** `query=<OR-joined terms>`, `tags=story`, `numericFilters=created_at_i>{windowStartEpoch}` (window start = now − 24h), `hitsPerPage=100`, paginated via `page`.
- **Response (consumed fields):** `hits[].objectID`, `hits[].title`, `hits[].url`, `hits[].points`, `hits[].num_comments`, `hits[].created_at_i`.
- **Failure modes:** HTTP 429 (rate limit) and 5xx → retry with backoff (see §6); persistent failure → the entity's collection is marked failed and the run is flagged `complete = false` (see §7).

### 5.2 Score node output contract (C5 → C6/C7)

One **scored entity record** per watchlist entity:

```json
{
  "entity": "NVIDIA",
  "ticker": "NVDA",
  "window_hours": 24,
  "story_count": 12,
  "engagement": { "points": 940, "comments": 612 },
  "front_page_count": 3,
  "components": { "volume": 26, "engagement": 24, "front_page": 15 },
  "base": 65,                       // volume + engagement + front_page (acceleration excluded)
  "buzz_score": 65,                 // base + acceleration, integer 0–100
  "low_confidence": false,          // story_count < 3
  "cold_start": false,              // entity absent from the previous complete run
  "top_stories": [ { "title": "...", "url": "https://...", "points": 410, "object_id": "..." } ]
}
```

Contract guarantees: `buzz_score` is an integer 0–100; `base = volume + engagement + front_page` (0–30 + 0–30 + 0–20) and is compared base-to-base across runs (acceleration excluded on both sides); `story_count` of 0 is a valid value (never null); `low_confidence=true` when `story_count < 3`; a `cold_start=true` entity forces `acceleration=0`.

### 5.3 Velocity node output contract (C7 → C8/C9)

Extends each scored record with:

```json
{
  "prev_base": 48,                 // base of this entity in the PREVIOUS COMPLETE RUN
  "velocity": 20,                  // acceleration points: 20 * clamp(delta/prev_base, -1.0, 2.0)
  "breakout": true                 // buzz_score >= breakoutThreshold (per-entity, 70 or 60)
}
```

Acceleration (the single `velocity` value) = `20 * clamp(delta / prev_base, -1.0, 2.0)`, where `delta = today_base − prev_base` and `prev_base` is the base of the entity in the **previous complete run** (not a trailing average). Negatives are allowed; the term range is **[−20, +40]**. Zero-denominator guard: `prev_base <= 0` → velocity `0`. There is a single signed `velocity` value — no `velocity_pct` and no `velocity_abs`.

Breakout is purely `buzz_score >= breakoutThreshold` (the per-entity threshold, 70 or 60) — there is no percentage-change or absolute-jump rule. If no prior complete run exists for an entity, it is a **cold start**: `velocity = 0` and `cold_start = true`, but the entity **can still break out** on base score alone if `buzz_score >= breakoutThreshold` (breakout is threshold-on-buzz-score, not velocity).

### 5.4 Store node contract (C8 → Postgres)

The write is a **single-row insert** into the one table `hn_buzz_runs` (jsonb `leaderboard` + `raw_metrics` + `complete` boolean + `window_hours` + `run_date` + `narratives` + `community_opinions`). Per-entity leaderboard rows live inside the `leaderboard` jsonb array; alerts are **not** persisted to a table — they fire as emails. There are no `hn_buzz_entity_scores` or `hn_buzz_alerts` tables. Schema is defined in `DATABASE_SETUP.md`. The run header carries a `complete` boolean; only `complete = true` runs are eligible as a future velocity baseline.

### 5.5 Machine signal contract (Postgres → Mycroft coordination layer)

The coordination layer consumes the latest **complete** run as a JSON signal:

```json
{
  "source": "hacker_news_buzz",
  "schema_version": "1.0",
  "run_date": "2026-07-02",
  "window_hours": 24,
  "complete": true,
  "entities": [
    { "entity": "NVIDIA", "ticker": "NVDA", "buzz_score": 65, "velocity": 20,
      "breakout": false, "low_confidence": false, "cold_start": false }
  ]
}
```

Field names are `entity`/`ticker`/`buzz_score`/`velocity`/`breakout`/`low_confidence`/`cold_start` — not `entity_id`, `velocity_pct`/`velocity_abs`, or `confidence`. This is a read against the stored snapshot in Phase 1; a pull HTTP endpoint is a later-phase deliverable. The email is never an ingestion path.

### 5.6 Email contract (C10 → SMTP)

- **Transport:** SendGrid SMTP, `smtp.sendgrid.net:587`, STARTTLS, username `apikey`, password = SendGrid API key (mail-send scope), stored as an n8n credential — never inline in workflow JSON.
- **Digest:** subject `[HN Buzz] Daily AI Buzz — <date>`; HTML body = ranked leaderboard. From `buzz-tracker@<project-domain>`; to `mali.om@northeastern.edu`.
- **Alert:** subject `[HN Buzz ALERT] <entity> breakout` (entity) or `[HN Buzz ALERT] pipeline failure` (operational); plain summary body.
- **Fallback:** Gmail SMTP + app password for the single Phase 1 recipient if SendGrid sender verification is incomplete at build time.

## 6. Cross-cutting concerns

- **Retries.** C4 and Postgres nodes use n8n's built-in retry-on-fail (3 attempts, exponential backoff) for transient 429/5xx/connection errors.
- **Idempotency.** A run is keyed by its UTC date; re-running the same day upserts on `run_date` rather than creating a duplicate baseline.
- **Secrets.** SendGrid API key, Supabase connection string, and any SMTP fallback credentials live in n8n credentials / environment, not in the exported workflow.
- **Time base.** All windows and run timestamps are UTC to keep the trailing-window boundary stable regardless of execution host.

## 7. Failure handling (architectural)

| Failure | Detection | Behavior |
| --- | --- | --- |
| Entity returns zero hits | `story_count == 0` | Valid data point; stored as a real zero (never null) → floored low-confidence score. Not an error. |
| One entity's collection fails | C4 exhausts retries | Run marked `complete = false`; that entity excluded from this run's velocity; the prior **complete** snapshot remains the baseline. |
| No prior complete run (cold start) | C6 returns empty | `velocity = 0` and `cold_start = true` per entity; entities can still break out on base score alone; surfaced in digest. |
| Storage write fails | C8 error | Pipeline-failure alert to maintainer; run not committed (no partial baseline). |
| API response shape changes | C5 schema guard | Pipeline-failure alert; run flagged `complete = false`. |

A partial snapshot (`complete = false`) is **never** used as the velocity baseline for the next run — reads filter `WHERE complete = true` — this is the central invariant protecting the velocity series from corruption.

## 8. Technology decisions

| Decision | Choice | Rationale | Alternatives rejected |
| --- | --- | --- | --- |
| Orchestrator | **n8n** | Visual, node-based, free self-host; matches Mycroft's existing workflow tooling; built-in scheduling, retries, and credential store. | Cron + script (no UI, no credential mgmt); Airflow (operationally heavy for one daily DAG). |
| Data source | **HN Search API (Algolia)** | No key, free, returns points/comments/timestamps directly; the canonical HN search backend. | HN Firebase API (no full-text search); scraping (fragile, ToS risk). |
| Collection mode | **`search_by_date`** with numeric time filter | Deterministic windowing on `created_at_i`; avoids relevance-ranking nondeterminism of `search`. | `search` (relevance-ordered, less reproducible). |
| Persistence | **Supabase Postgres** | Free tier; real SQL to select the latest complete run as the baseline; managed, no ops; one row per run with jsonb leaderboard payloads (single table `hn_buzz_runs`). | SQLite (no managed access for coordination layer); n8n static data (not queryable, size-limited). |
| Scoring | **Deterministic Code node** (no LLM) | Reproducibility is priority #1; LLM in the scoring path would break determinism. | LLM scoring (deferred to Phase 2 narrative layer, kept out of the score). |
| Email | **SendGrid SMTP** | 100/day free tier covers digest + alerts; SMTP relay drops into native node; no mail server. | SES (AWS account overhead); self-hosted SMTP (deliverability/ops burden). Gmail SMTP is the documented fallback. |
| Normalization universe | **Versioned watchlist (v1, frozen for Phase 1)** | Cross-entity log normalization requires a fixed universe for longitudinal comparability. | Dynamic watchlist (would silently reset baselines mid-series). |
| Acceleration comparison | **Base-vs-base** (compare `base = volume+engagement+front_page`, acceleration excluded on both sides) | The `base` is the purely measured signal. Comparing it avoids feeding an entity's prior acceleration back into today's — total-vs-total embeds yesterday's correction term in the value being differenced, so a spike's decaying acceleration reads as phantom velocity and the score oscillates around its base for weeks. | Total-vs-total (`buzz_score` diffed directly) — circular: differences a score against a version of itself, producing drift/ringing untethered from actual HN activity. |
| Human/machine output coupling | **Two independent renders of the persisted snapshot** (JSON signal and HTML digest built separately) | The JSON is a versioned contract (`schema_version`) the coordination layer parses and must change slowly; the digest is human presentation that restyles freely. They also differ in cardinality (signal is always the full snapshot; digest fires only on breakout). Separate renders keep a cosmetic email change from touching the machine contract, and a broken template from corrupting ingestion. | Derive the email from the JSON signal (single payload) — couples presentation to the contract, accretes display fields into the signal, and grafts conditional email logic onto an always-on data object. |

## 9. Phase boundaries (what this architecture defers)

The following are explicitly **out of scope** for the Phase 1 Week-4 build and are flagged for later phases: the free-LLM narrative/reception-tone layer (Week 7; the `narratives` column is reserved), the Community Opinion layer (Week 9; the `community_opinions` column is reserved), comment-level analysis, the Chart.js dashboard, the historical backfill, the signal-validation backtest (early Phase 2), and the coordination-layer **pull endpoint** (Phase 1 exposes the signal via the stored snapshot only). Score weights, the trailing-window length, and breakout thresholds are held fixed through Phase 1 and recalibrated against accumulated data afterward.
