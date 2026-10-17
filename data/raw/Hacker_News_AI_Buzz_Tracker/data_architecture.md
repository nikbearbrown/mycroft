# Hacker News AI Buzz Tracker: Data Architecture

> Companion to `proposal.md` and `system_architecture.md`. This document specifies the **data architecture** for Phase 1: the persistent schema (Supabase Postgres), the watchlist composition (the normalization universe), the fetch-window specification, and the consolidated resolution of the four flags raised in the proposal review (`/v1`). Where the system architecture describes how data *flows*, this document describes how data is *shaped, stored, and governed*.
>
> **Status:** this document reflects the implemented Phase-1 Week-4 build (the code is the source of truth). Later-phase fields (`narratives`, `community_opinions`) are present in the schema but null until their milestone.

## 1. Data domains

The system has four logical data domains:

1. **Configuration** — the watchlist and run-level parameters (fetch window, per-entity breakout thresholds). Versioned, human-owned, source-controlled.
2. **Raw collection** — Hacker News story hits per entity per run. Aggregated into `raw_metrics` and stored on the run row; individual hits are not persisted.
3. **Derived state** — per-entity Buzz Scores, components, velocity, and confidence flags, stored per run inside the `leaderboard` jsonb array. This is the historical series that acceleration depends on.
4. **Outputs** — the machine-ingestible JSON signal, the human HTML digest (rendered, not stored as a row), and a separate pipeline-failure error workflow.

## 2. Fetch window specification (FLAG-3, resolved)

`windowHours = 24` (default, configurable), exposed as a single run-level value and stored on each run row as `window_hours` (int) for provenance.

- **Collection bound:** each entity query filters `created_at_i > (now − 24h)`.
- **Baseline definition:** the acceleration baseline for an entity is its `base` score in the **previous complete run** — a single prior run, **not** a multi-day trailing average.
- **Cold-start bound:** acceleration is unavailable on run 1 (no prior complete run); the acceleration component is forced to `0` until at least one prior complete run exists, and the entity is flagged `coldStart`.
- **Rationale (owned opinion):** a 24-hour window matches the daily cadence — it captures the fresh day's HN activity while comparing directly against the immediately preceding complete run, keeping the signal sensitive to short surges rather than diluting them into a long trailing mean. Changing the window is a config edit, not a code change.

## 3. Watchlist composition (FLAG-1, resolved)

The watchlist **is** the normalization universe: cross-entity log normalization is computed over exactly these entities, so the set is frozen within a phase and versioned across phases. Query-term ambiguity is the highest-risk failure mode, so terms are deliberately specific and qualified.

**Watchlist v1 — 12 entities (frozen for Phase 1):**

| Entity | Ticker | Query terms (OR-matched) | Front-page points | Breakout threshold |
| --- | --- | --- | --- | --- |
| NVIDIA | NVDA | `NVIDIA`, `Nvidia`, `CUDA` | 100 | 70 |
| OpenAI | — (private) | `OpenAI`, `ChatGPT`, `GPT-5`, `Sora` | 100 | 70 |
| Microsoft (Copilot) | MSFT | `Microsoft Copilot`, `GitHub Copilot` | 100 | 70 |
| Google (Gemini) | GOOGL | `Gemini`, `DeepMind`, `Google AI` | 100 | 70 |
| Meta (Llama) | META | `Llama`, `Meta AI` | 100 | 70 |
| AMD | AMD | `AMD`, `ROCm`, `Instinct MI300` | 100 | 70 |
| Palantir | PLTR | `Palantir` | 75 | 60 |
| Amazon (AWS AI) | AMZN | `AWS Bedrock`, `Amazon Bedrock`, `Trainium` | 100 | 70 |
| Apple (Apple Intelligence) | AAPL | `Apple Intelligence` | 75 | 60 |
| Tesla (AI/FSD) | TSLA | `Tesla FSD`, `Tesla Optimus`, `Dojo` | 100 | 70 |
| Anthropic | — (private) | `Anthropic`, `Claude` | 75 | 60 |
| Mistral | — (private) | `Mistral AI`, `Mistral` | 75 | 60 |

- **`entity`** (the display name) is the stable key used across the leaderboard, `raw_metrics`, and the coordination-layer signal.
- **Governance:** static within Phase 1; additions/removals only at a version boundary (v1 → v2), which creates a normalization discontinuity (historical scores valid within a version, not compared across the boundary). Owner: project maintainer (`mali.om@northeastern.edu`).
- **Private entities** (no ticker: OpenAI, Anthropic, Mistral) carry `ticker: null` and are included for context.

### 3.1 Watchlist record (configuration schema)

Each entry in the source-controlled `watchlist.json` matches this shape (one object per entity):

```json
{
  "entity": "NVIDIA",
  "ticker": "NVDA",
  "queryTerms": ["NVIDIA", "Nvidia", "CUDA"],
  "frontPagePoints": 100,
  "breakoutThreshold": 70
}
```

`breakoutThreshold` is a per-entity integer buzz-score cutoff (70 or 60, §5); `frontPagePoints` is the per-entity points threshold used to count front-page stories. Both are edited in `watchlist.json` without code change. Private entities set `ticker: null`. There is no `entity_id`, `investable`, or `aliases` field.

## 4. Persistent schema (Supabase Postgres)

**One table**, one row per run. Per-entity results, narratives, opinions, and raw aggregates all live in jsonb columns on that row — there is no separate per-entity scores table and no separate alerts table. The watchlist lives in source control (`watchlist.json`), not the database. See `DATABASE_SETUP.md` for full setup detail.

### 4.1 `hn_buzz_runs` — one row per run

```sql
create table hn_buzz_runs (
  id                 uuid default gen_random_uuid() primary key,
  created_at         timestamptz default now(),
  run_date           text,        -- window-start date (UTC, YYYY-MM-DD)
  window_hours       int,         -- lookback window (default 24)
  complete           boolean default true,  -- false = partial run; excluded from velocity baseline
  leaderboard        jsonb,       -- ranked entities (array): score, velocity, components, breakout, topStory(ies)
  narratives         jsonb,       -- per-entity narrative/theme/tone (Week 7, null until then)
  community_opinions jsonb,       -- per-entity comment-grounded opinion (Week 9, null until then)
  raw_metrics        jsonb        -- {entityName: {storyCount, totalPoints, totalComments, frontPageCount}}
);
```

- **`complete`** is a boolean: a partial/failed run is written with `complete = false` (or not written at all), and all reads filter `WHERE complete = true`. There is no `status` text column.
- **`leaderboard`** is the per-entity leaderboard (formerly a separate table). Each array element carries the entity name, `ticker`, buzz `score`, `velocity` (= the acceleration score), the four scoring components, `breakout`, the confidence flags (`lowConfidence`, `coldStart`), and the entity's top story/stories.
- **`raw_metrics`** holds the collected aggregates keyed by entity name: `{ storyCount, totalPoints, totalComments, frontPageCount }`. Individual story hits are not persisted.
- **`narratives`** / **`community_opinions`** are later-phase columns (Week 7 and Week 9); they exist in the schema but are `null` in the Week-4 build.

### 4.2 Reading and writing runs

- **Read previous complete run** (for the acceleration baseline):
  `SELECT run_date, leaderboard FROM hn_buzz_runs WHERE complete = true ORDER BY created_at DESC LIMIT 1;`
- **Insert** a run with a parameterized `INSERT` that casts the jsonb parameters with `$3::jsonb` / `$4::jsonb` (etc.), passing `JSON.stringify(value)` for each jsonb column.

### 4.3 Alert & failure records

There is **no** persisted alerts table. Breakout notifications are derived on-the-fly from the current run's leaderboard (`breakout = true`) and emailed as the HTML digest. Pipeline failures are handled by a separate n8n **Error Trigger** workflow (§7 / §8), not by an alerts row.

## 5. Breakout thresholds (FLAG-2, resolved — provisional)

Breakout is a single per-entity **absolute score cutoff**. An entity breaks out when, in the same run:

- `buzzScore ≥ breakoutThreshold`

where `breakoutThreshold` is the entity's value from `watchlist.json` — **70** for high-profile entities and **60** for the quieter ones (Palantir, Apple, Anthropic, Mistral). There is no percentage-velocity rule, no absolute-jump tripwire, and no `velocity_pct` / `velocity_abs` combination.

Constraints:

- **Confidence handling:** low-confidence entities (`storyCount < 3`) are flagged `lowConfidence`. The code does not currently confidence-gate breakouts, but a low-confidence breakout should be treated cautiously downstream.
- **Provisional status:** the `70 / 60` cutoffs are heuristics — set now for the discipline of a defined, testable rule, held fixed through Phase 1 for comparability, and recalibrated against accumulated data later. They are expected to be wrong on first pass and are editable per entity in `watchlist.json`.

## 6. Scoring data rules

**Buzz Score** ∈ `[0, 100]` = `base + acceleration`, where `base = volume + engagement + frontPage`.

- **volume** (0–30) `= 30 · clamp( log1p(storyCount) / log1p(30) )`
- **engagement** (0–30) `= 30 · clamp( log1p(points + comments) / log1p(1000) )`
- **frontPage** (0–20) `= 20 · clamp( frontPageCount / 5 )`
- **Sparse floor** (`storyCount < 3` → `lowConfidence`): `volume = 30·clamp(storyCount/3)`, `engagement = 30·clamp(engagement/50)`, `frontPage = 0`.
- **Acceleration** (`[−20, +40]`) `= 20 · clamp( delta / prevBase, −1.0, 2.0 )`, where `prevBase` is the entity's `base` in the **previous complete run** and `delta = today_base − prevBase`. Negatives are allowed. Guard: `prevBase ≤ 0` → `acceleration = 0`.
- **Cold start** (entity absent from the previous complete run): `acceleration = 0` and `coldStart = true`.
- The per-entity **`velocity`** value equals the acceleration score.
- **Log normalization** (via `log1p`) keeps a few viral stories from dominating volume and engagement.
- **Zero hits:** stored as a real `0`, yielding a floored low-confidence score — never null, never skipped.

## 7. Email delivery data (FLAG-4, resolved)

Delivery configuration (transport, not stored in Postgres):

- **Provider/transport:** SendGrid SMTP, `smtp.sendgrid.net`, port `587`, STARTTLS.
- **Credentials:** n8n SMTP credential — username `apikey`, password = SendGrid API key scoped to mail-send only; key held as an environment-level secret, never inline in workflow JSON.
- **From:** `buzz-tracker@<project-domain>` (verified sender; SendGrid single-sender verified address as setup fallback).
- **To (Phase 1):** `mali.om@northeastern.edu`.
- **Subject prefixes:** `[HN Buzz]` (breakout digest) vs `[HN Buzz ALERT]` (pipeline failure) so they are filterable.
- **Fallback:** Gmail SMTP + app password for the single Phase 1 recipient if SendGrid sender verification is incomplete at build time.
- **Free-tier headroom:** 100 emails/day comfortably covers one daily digest plus occasional alerts.

**Two distinct email paths:**

- **Breakout digest** — the HTML email is sent only when at least one entity breaks out (`breakout = true`). Human-only; never an ingestion path.
- **Pipeline failure** — a **separate n8n Error Trigger workflow** (wired via *Settings → Error Workflow*) emails the maintainer with the workflow name, failed node, error message, and execution URL. This is distinct from breakout alerting and is not persisted as an alerts row.

## 8. Machine-ingestible signal (data contract)

The Mycroft coordination layer consumes the JSON signal built by the **"Build JSON Signal"** Code node (also the latest **complete** run in Postgres). Canonical shape:

```json
{
  "source": "hacker_news_buzz",
  "schema_version": "1.0",
  "run_date": "2026-06-12",
  "window_hours": 24,
  "complete": true,
  "entities": [
    {
      "entity": "NVIDIA",
      "ticker": "NVDA",
      "buzz_score": 65,
      "velocity": 17,
      "breakout": true,
      "low_confidence": false,
      "cold_start": false
    }
  ]
}
```

Keys are the flat per-entity fields shown above (`entity`, `ticker`, `buzz_score`, `velocity`, `breakout`, `low_confidence`, `cold_start`) — there is no `entity_id`, `velocity_pct`, `velocity_abs`, or `confidence` field. The HTML email is for humans only and is never an ingestion path. A pull HTTP endpoint serving this same shape is a later-phase deliverable; in Phase 1 the stored snapshot is the interface.

## 9. Flag resolution summary

| Flag | Topic | Resolution | Location |
| --- | --- | --- | --- |
| FLAG-1 | Watchlist composition | 12 entities (9 ticker + 3 private), specific query terms, per-entity `frontPagePoints` and `breakoutThreshold`; v1 frozen for Phase 1. | §3, §3.1 |
| FLAG-2 | Breakout thresholds | Per-entity absolute cutoff `buzzScore ≥ breakoutThreshold` (70 or 60); editable in `watchlist.json`; recalibrated post-Phase 1. | §5 |
| FLAG-3 | Fetch window | `24 hours` (`windowHours`, configurable), owned rationale; stored as `window_hours` on each run. | §2 |
| FLAG-4 | Email delivery | SendGrid SMTP `:587` STARTTLS, credentialed API key, verified from-address, maintainer to-address, Gmail fallback. | §7 |
