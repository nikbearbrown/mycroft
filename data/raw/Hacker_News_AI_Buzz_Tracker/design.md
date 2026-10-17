# Hacker News AI Buzz Tracker — Design Document

> Week 1 design spec: data model, Buzz Score formula, HN Algolia API reference, and the planned
> workflow architecture. This is the design contract that Weeks 2–4 build against. No code yet.

**Author:** Om Mali
**Status:** Draft (Week 1) — design only

---

## 1. Overview

The agent tracks a configurable watchlist of AI entities on Hacker News, computes a deterministic
**Buzz Score (0–100)** per entity over a trailing window, compares it to the previous run to get
**buzz velocity**, stores the snapshot, and emails a ranked digest. It reads from one free,
no-key source (the HN Algolia Search API) and adds an LLM narrative layer in a later month.

The signal measures **attention, not direction** — heavy discussion of an outage and a celebrated
launch both score high. Distinguishing them is the LLM reception-tone layer's job (Month 2).

---

## 2. Data source — HN Algolia Search API

Free, no key, no signup. Base endpoint:

```
https://hn.algolia.com/api/v1/search_by_date?query={term}&tags=story&numericFilters=created_at_i>{since_unix}
```

### Key parameters

| Param | Purpose | Notes |
|-------|---------|-------|
| `query` | search term(s) | matched against title + url + text |
| `tags=story` | restrict to stories | excludes comments, polls, jobs |
| `numericFilters=created_at_i>{unix}` | trailing-window filter | `since_unix` = now − windowHours |
| `page` | pagination, 0-indexed | response reports `nbPages`, `nbHits` |
| `hitsPerPage` | results per page | default 20, request up to 100 wis not gauranteed |

`search_by_date` sorts newest-first (good for a trailing window). `search` (relevance-sorted) is
the alternative but less suited to time-bounded volume counting.

### Response shape (fields we use)

```jsonc
{
  "hits": [
    {
      "title": "OpenAI releases ...",
      "url": "https://...",
      "points": 412,
      "num_comments": 233,
      "created_at_i": 1749500000,   // unix seconds
      "objectID": "40123456"         // dedupe key + permalink id
    }
  ],
  "nbHits": 57,
  "nbPages": 3,
  "page": 0,
  "hitsPerPage": 20
}
```

Story permalink: `https://news.ycombinator.com/item?id={objectID}`.

### Computing the trailing window (PowerShell)

```powershell
$sinceUnix = [DateTimeOffset]::UtcNow.AddHours(-24).ToUnixTimeSeconds()
```

### API findings (Week 1 exploration — 2026-06-09)

Verified by hand against a live trailing-window query.

**Request**
```
https://hn.algolia.com/api/v1/search_by_date?query=Apple%20Intelligence&tags=story&numericFilters=created_at_i>1780443734
```

**Result:** HTTP 200, `nbHits: 6`, `nbPages: 1`, `hitsPerPage: 20`, `page: 0`,
`processingTimeMS: 10`. Trimmed top hit:

```jsonc
{
  "title": "Apple unveils innovative features and intelligence experiences across services",
  "url": "https://www.apple.com/newsroom/2026/06/apple-unveils-...",
  "author": "soheilpro",
  "points": 1,
  "num_comments": 0,
  "created_at": "2026-06-09T13:12:11Z",
  "created_at_i": 1781010731,
  "objectID": "48460690",
  "story_id": 48460690
}
```

**Confirmed**
- All fields the score depends on are present: `title`, `url`, `points`, `num_comments`,
  `created_at_i`, `objectID`. `created_at` (ISO string) and `author` also come for free.
- `tags=story` is echoed in `params`; results are stories only.
- The `numericFilters=created_at_i>{unix}` trailing-window filter works — every hit's
  `created_at_i` is greater than the supplied bound.
- Top-level `nbHits` (here 6) is the window count we use for the Volume component; `nbPages` tells
  us whether to paginate (here 1, so no pagination needed).
- `hitsPerPage` defaults to **20**. Each hit carries a `_highlightResult` block (matched-word
  highlighting with `<em>` tags) — **noise we ignore**; we read only the plain fields above.

**Implications for the build**
- Multi-term entities (e.g. "Apple Intelligence") work as a phrase query and matched on both title
  and url. Generic terms will pull adjacent stories — query-term precision matters (see Risks §7).
- Low-engagement reality check: even a relevant breaking story can sit at `points: 1`,
  `num_comments: 0` shortly after posting. Scoring must treat thin/early windows as a valid low
  baseline, not an error.
- For windows with `nbPages > 1`, page through with `page` until `page >= nbPages` (Week 2).

> Not yet exercised: explicit rate-limit / 429 behavior under rapid calls (the API is documented as
> generous and no key is required). Revisit during the Week 9 historical backfill when call volume
> is high.

---

## 3. Watchlist data model

Stored in `watchlist.json`, one object per entity:

```jsonc
{
  "entity": "NVIDIA",            // canonical display name + dedupe rollup key
  "ticker": "NVDA",             // null for private comparables
  "queryTerms": ["NVIDIA", "Nvidia", "CUDA"],  // OR'd / queried per term
  "frontPagePoints": 100,        // points threshold for "front page impact"
  "breakoutThreshold": 70        // Buzz Score that fires a breakout alert
}
```

Aliases (a company and its flagship model, e.g. Meta + Llama, Google + Gemini) roll up to **one**
entity so attention isn't split. Multi-term entities query each term and merge hits, deduping by
`objectID`.

### Watchlist v1 (12 entities)

The canonical list lives in `watchlist.json`; it is mirrored inline in the workflow's Watchlist node.

| Entity | Ticker | Sample query terms | frontPagePoints | breakoutThreshold |
|--------|--------|--------------------|-----------------|-------------------|
| NVIDIA | NVDA | NVIDIA, Nvidia, CUDA | 100 | 70 |
| OpenAI | — | OpenAI, ChatGPT, GPT-5, Sora | 100 | 70 |
| Microsoft (Copilot) | MSFT | Microsoft Copilot, GitHub Copilot | 100 | 70 |
| Google (Gemini) | GOOGL | Gemini, DeepMind, Google AI | 100 | 70 |
| Meta (Llama) | META | Llama, Meta AI | 100 | 70 |
| AMD | AMD | AMD, ROCm, Instinct MI300 | 100 | 70 |
| Palantir | PLTR | Palantir | 75 | 60 |
| Amazon (AWS AI) | AMZN | AWS Bedrock, Amazon Bedrock, Trainium | 100 | 70 |
| Apple (Apple Intelligence) | AAPL | Apple Intelligence | 75 | 60 |
| Tesla (AI/FSD) | TSLA | Tesla FSD, Tesla Optimus, Dojo | 100 | 70 |
| Anthropic | — | Anthropic, Claude | 75 | 60 |
| Mistral | — | Mistral AI, Mistral | 75 | 60 |

Private comparables (OpenAI, Anthropic, Mistral) carry `ticker: null` and are included for context.

---

## 4. Buzz Score model (deterministic, 0–100)

Four additive components. The LLM adds only the qualitative layer later; the score itself is fully
deterministic and reproducible.

| Component | Range | Input | Intent |
|-----------|-------|-------|--------|
| **Volume** | 0–30 | story count in window | how much is being posted |
| **Engagement** | 0–30 | total points + comments | how hard people are reacting |
| **Front-page impact** | 0–20 | # stories ≥ `frontPagePoints` | did anything actually break out |
| **Acceleration** | −20 → +40 | change vs. the previous run | is attention rising or falling |

```
base      = Volume + Engagement + FrontPage           // 0–80, this window in isolation
BuzzScore = base + Acceleration                        // clamped to [0, 100]
```

Acceleration is a signed run-over-run momentum term (negatives allowed) — see §4 velocity below
and `docs/scoring_logic.md` for the exact formula and the base-vs-base rationale.

### Normalization (log scale)

Raw counts are heavy-tailed — a single viral story can dominate. Each component is normalized on a
**log scale** across entities so a few front-page hits don't saturate the score. Sketch:

```
volumeScore     = 30 * clamp( log1p(storyCount)      / log1p(VOLUME_REF),     0, 1 )
engagementScore = 30 * clamp( log1p(points+comments) / log1p(ENGAGEMENT_REF), 0, 1 )
frontPageScore  = 20 * clamp( frontPageCount         / FRONTPAGE_REF,         0, 1 )
base            = volumeScore + engagementScore + frontPageScore
accelScore      = 20 * clamp( (base - prevBase) / prevBase, -1.0, 2.0 )   // prevBase from last run
```

Reference constants (`VOLUME_REF=30`, `ENGAGEMENT_REF=1000`, `FRONTPAGE_REF=5`) are calibration
knobs — the exact values and the full golden-fixture validation are the **Week 3** deliverable
(`scoring_logic.md`). This doc fixes the *shape* of the formula.

### Buzz Velocity (Week 4 — implemented)

Velocity is the acceleration component itself: the signed, bounded run-over-run change in an
entity's **base** score (volume+engagement+frontPage), measured against the **previous complete
run** — not against a trailing average.

```
prevBase = base of this entity in the previous run's leaderboard (or absent → cold start)
velocity = 20 * clamp( (base - prevBase) / prevBase, -1.0, 2.0 )   // 0 if prevBase <= 0 or cold start
```

Comparing base-to-base (excluding acceleration on both sides) keeps an entity's momentum from
compounding its own prior momentum. First run, or an entity unseen in the prior run, has no
`prevBase` → velocity **0**, `coldStart: true` (not an error). A trailing-average baseline
becomes possible after the Week 5 backfill and is a candidate refinement then.

### Edge cases the scoring must handle

- Zero-hit entity → all base components 0, low-confidence floor, Buzz Score 0 (valid, not an error).
- Empty / malformed API response → degrade gracefully, skip the term, keep the run alive.
- Missing prior snapshot / unseen entity → velocity = 0, `coldStart: true`.
- Missing LLM key (later months) → fall back to deterministic score + digest.

---

## 5. Storage schema (planned — table created Week 4)

Supabase Postgres. Documented now; not provisioned in Week 1.

```sql
create table hn_buzz_runs (
  id                 uuid default gen_random_uuid() primary key,
  created_at         timestamptz default now(),
  run_date           text,        -- window-start date (UTC)
  window_hours       int,         -- lookback window (default 24)
  complete           boolean default true,  -- false = partial run; excluded from velocity baseline
  leaderboard        jsonb,       -- ranked entities: score, velocity, components, top stories
  narratives         jsonb,       -- per-entity narrative, theme, tone (Week 7)
  community_opinions jsonb,       -- per-entity comment-grounded opinion (Week 9)
  raw_metrics        jsonb        -- volume, points, comments, front-page counts
);
```

- **One row per run** (not per entity); the whole leaderboard lives in the `leaderboard` jsonb.
- `complete` — `false` for a partial/failed run so it never becomes the next run's velocity baseline.
- `leaderboard` — ranked entities with scores, velocity, components, breakout flag, top stories.
- `narratives` / `community_opinions` — null until the Week 7 / Week 9 LLM layers land.
- `raw_metrics` — the underlying volume/points/comments/front-page counts for auditing scores.

See `DATABASE_SETUP.md` for the full setup, the read/insert queries, and verification steps.

---

## 6. Workflow architecture (target end state)

```
Schedule Trigger (daily, configurable)
  → Set: Watchlist (entity, query terms, ticker, thresholds)
  → Split In Batches (loop entities)
      → HTTP Request: HN Algolia search_by_date (trailing window filter)
  → Code: aggregate per-entity metrics + compute Buzz Score (0–100)
  → Postgres (Supabase): read previous snapshot
  → Code: compute Buzz Velocity vs. previous run
  → LLM node (Groq Llama 3.1 or Claude): narrative, theme, reception tone
  → Code: merge into ranked leaderboard
  → Postgres (Supabase): insert run snapshot
  → IF: any entity crosses an alert threshold
      → Send Email: HTML digest (top movers, scores, narratives)
  → (optional) Webhook: GET /webhook/dashboard serves HTML
```

### Build phasing (which weeks touch which nodes)

| Weeks | Nodes added |
|-------|-------------|
| **2** | Schedule Trigger, Watchlist Set, Split In Batches, HTTP Request, parse/dedupe/normalize Code |
| **3** | Buzz Score components in the Code node, log normalization, golden fixtures |
| **4** | Postgres read + insert, velocity Code node, simple ranked email digest |
| **5+** | LLM narrative node, richer HTML digest, alerts, dashboard webhook |

---

## 7. Known risks (from proposal.md)

- **Name ambiguity** — generic query terms pull unrelated stories; careful `queryTerms` + filtering
  is the main noise control.
- **Thin/empty windows** — small/private entities give jumpy scores; treat zero hits as a baseline.
- **Cold-start velocity** — needs history; early numbers are conservative until backfill (Month 3).
- **Score calibration** — weights and the points threshold are judgment calls; tune against real
  data before trusting the numbers.
- **Buzz ≠ direction** — high score = attention, not good news; reception-tone layer addresses this.
- **Single-source dependency** — if the HN API rate-limits or changes shape, collection stops;
  wrap requests in basic error handling.
