# JSON signal contract (Week 11)

The machine-ingestible output for the Mycroft coordination layer. It is
**distinct from the email digest** (human-only) and from the full stored snapshot
(which also holds leaderboard internals, narratives, and raw metrics). The
coordination layer consumes *this* contract, never the email.

Produced by the `Code in Python` node from the run row; the same shape is served
by the pull endpoint (below).

## Schema 1.0 (current, shipped)

```json
{
  "source": "hacker_news_buzz",
  "schema_version": "1.0",
  "run_date": "2026-07-25",
  "window_hours": 24,
  "complete": true,
  "entities": [
    {
      "entity": "OpenAI",
      "ticker": null,
      "buzz_score": 72.3,
      "velocity": 5.1,
      "breakout": true,
      "low_confidence": false,
      "cold_start": false
    }
  ]
}
```

### Field semantics

| Field | Type | Meaning / consumer contract |
|---|---|---|
| `source` | string | Constant `"hacker_news_buzz"` — identifies the agent. |
| `schema_version` | string | Consumers pin on the major version; breaking changes bump it. |
| `run_date` | string (YYYY-MM-DD, UTC) | Window-start date of the run. |
| `window_hours` | int | Trailing window length (24). |
| `complete` | bool | `false` = partial run; consumers should skip/flag it. Partial runs are also excluded from the velocity baseline upstream. |
| `entities[]` | array | One object per watchlist entity, in leaderboard (buzz) order. |
| `entities[].entity` | string | Canonical entity name (join key). |
| `entities[].ticker` | string \| null | Public ticker, or `null` for private comparables (non-investable). |
| `entities[].buzz_score` | number 0–100 | Deterministic attention score. |
| `entities[].velocity` | number | Acceleration vs. previous run (−20…+40 range). |
| `entities[].breakout` | bool | Crossed its breakout threshold this run. |
| `entities[].low_confidence` | bool | Sparse entity (<3 stories); score on absolute floor. |
| `entities[].cold_start` | bool | No prior snapshot; velocity forced to 0. |

### Stability guarantees

- Field names are snake_case and stable within a major version.
- New **optional** fields may be added without a major bump; consumers must
  ignore unknown fields.
- `entity` + `run_date` uniquely identify a row.
- Order is by descending `buzz_score`; consumers should not rely on order for
  identity (join on `entity`).

## Schema 1.1 (proposed enrichment — additive, optional)

Adds the comment-grounded and qualitative layers already computed in the run row,
so the coordination layer can consume them without a second call. All additive;
`schema_version` becomes `"1.1"`. Consumers pinned on 1.0 ignore the new fields.

```json
{
  "schema_version": "1.1",
  "watchlist_version": "v1",
  "entities": [
    {
      "entity": "OpenAI",
      "buzz_score": 72.3,
      "narrative": { "theme": "launch", "tone": "bullish" },
      "community_opinion": {
        "sentiment": "mixed",
        "themes": ["reasoning", "pricing"],
        "comments_analyzed": 8,
        "low_confidence": false,
        "degraded": false
      }
    }
  ],
  "sector": {
    "narrative": "Discussion centered on pricing and open models.",
    "cross_entity_themes": ["pricing", "open models"],
    "degraded": false
  }
}
```

- `watchlist_version` is promoted to a top-level field so consumers know which
  normalization universe the scores belong to (a v1→v2 change is a clean break;
  scores are not comparable across it).
- `community_opinion` mirrors the analyzer output but **without** the free-text
  `summary`/`notableOpinions` (those stay in the human digest and the snapshot);
  the contract carries only the structured, machine-usable fields.

## Pull endpoint (Week 11 — canvas task)

A read path so the coordination layer can fetch the latest signal on demand
rather than waiting for a push.

- **Route:** `GET /webhook/signal` (Webhook node → Postgres read → respond).
- **Query:**
  ```sql
  SELECT run_date, window_hours, complete, watchlist_version,
         leaderboard, narratives, community_opinions, sector_narrative
  FROM hn_buzz_runs
  WHERE complete = true AND watchlist_version = 'v1'
  ORDER BY created_at DESC LIMIT 1;
  ```
  `sector_narrative` must be in the SELECT for the `sector` block to be non-degraded
  (requires the Week 11 migration `add column sector_narrative jsonb`).
- **Response:** the schema-1.x object above, `Content-Type: application/json`.
- **Empty state:** if no complete run exists, return `{ "complete": false,
  "entities": [] }` with 200, so consumers get a well-formed empty signal rather
  than an error.

This mirrors the existing `GET /webhook/dashboard` pattern (Webhook → read →
respond); only the transform differs (JSON contract instead of HTML). Wiring the
node is a human/canvas step — the JSON shape is fixed by this document.
