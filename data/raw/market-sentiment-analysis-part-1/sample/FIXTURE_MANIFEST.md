# Frozen Sample Fixture — Market Sentiment Analysis - Part 1

**Frozen at:** 2026-08-27T14:30:00Z · **Manifest version:** 1.0.0 · **Recipe:** `recipes/market-sentiment-analysis-part-1.md`
**Machine-readable twin:** `fixture-manifest.json` (that file is the source of truth; this is the human view)

> **Everything here is synthetic.** Payload *shapes* are copied from the source n8n workflow.
> Every *value* is invented. Ticker `FAKE` / "Fake Industries Inc." does not exist, no headline
> here was published anywhere, no Reddit post exists. **Nothing in this set is a market
> observation and nothing in it may be cited as evidence** (P3). The fictional ticker is
> deliberate: a fixture full of plausible NVDA prices is a fixture waiting to be quoted as real.
>
> Timestamps are pinned to `frozen_at`, never `now()`. The set does not rot, and re-running the
> validator next year must produce the same verdict.

## What is here

| File | Source | Rows | Defects |
|---|---|---|---|
| `clean/price-alpha-vantage.json` | Alpha Vantage `GLOBAL_QUOTE` | 1 quote | none |
| `clean/news-finnhub.json` | Finnhub `company-news` | 5 articles | none |
| `clean/reddit-wallstreetbets.json` | Reddit `search.json` | 4 submissions | none |
| `defective/price-alpha-vantage.json` | Alpha Vantage `GLOBAL_QUOTE` | 5 quotes | D01–D04 |
| `defective/news-finnhub.json` | Finnhub `company-news` | 8 articles | D05–D12 |
| `defective/reddit-wallstreetbets.json` | Reddit `search.json` | 6 submissions | D13–D17 |
| `defective/news-finnhub-unparseable.json.broken` | Finnhub `company-news` | n/a | D18 |

Each fixture is wrapped in the envelope the recipe's step 2 declares (`records`, `source_name`,
`source_type`, `fetched_at`, `sample_mode`, `rejects`) plus the raw-layer fields from the node
notes (`source_url_or_path`, `record_count`, `errors`), so steps 3 and 4 can consume them
directly. Inside the envelope, `records` holds the **verbatim upstream shape** — Alpha Vantage's
`{"Global Quote": {...}}`, Finnhub's flat article objects, Reddit's `data.children[]` of `t3`
submissions — because that is what the Aggregate node actually keys on.

In the defective price file, each defect sits on its **own record** (with `records[0]` as a clean
control). One defect per row means a validator that rejects a row early still has to find the
others; bundling them onto one record would let a single rejection hide four bugs.

## The 18 injected defects

| ID | Class | File | Locator | What is wrong |
|---|---|---|---|---|
| D01 | missing required field | `defective/price-…` | `records[1]."Global Quote"` | no `05. price` key; `parseFloat` would silently make the price **0** |
| D02 | type violation | `defective/price-…` | `records[2]…"10. change percent"` | literal `"N/A"`; `parseFloat` yields NaN into the price score |
| D03 | stale timestamp | `defective/price-…` | `records[3]…"07. latest trading day"` | `2024-03-15` — ~2.5 years stale, presented as current |
| D04 | duplicate | `defective/price-…` | `records[4]` = `records[0]` | `FAKE` quote twice; double-weights one ticker |
| D05 | duplicate | `defective/news-…` | `records[1].headline` = `records[0].headline` | syndicated copy: **different `id` and `url`, same headline** — what id-only dedupe misses |
| D06 | duplicate | `defective/news-…` | `records[2]` = `records[0]` | byte-identical repeat, same `id` |
| D07 | missing required field | `defective/news-…` | `records[3]` | no `headline`; aggregate would score the string `"undefined"` |
| D08 | missing required field | `defective/news-…` | `records[4].url` | `url` present but **`null`** — claim cannot be traced to a source |
| D09 | malformed row | `defective/news-…` | `records[5]` | row is a JSON **array**, not an object; `.get()` raises |
| D10 | stale timestamp | `defective/news-…` | `records[6].datetime` | epoch `1710507600` (2024-03-15) inside a 2-day window |
| D11 | type violation | `defective/news-…` | `records[7].datetime` | free text `"yesterday"` where an epoch int is required |
| D12 | count mismatch | `defective/news-…` | envelope `record_count` | declares **7**, actually holds **8** |
| D13 | duplicate | `defective/reddit-…` | `children[1]` = `children[0]` | same submission `id`, slightly different title |
| D14 | missing required field | `defective/reddit-…` | `children[2].data` | no `title`; aggregate would score `"undefined"` |
| D15 | malformed row | `defective/reddit-…` | `children[3].data` | `data` is a **string** — and it contains "to the moon", so naive substring sentiment scores it bullish |
| D16 | stale timestamp | `defective/reddit-…` | `children[4].data.created_utc` | epoch `1710523200` (2024-03-15) from a `t=day` query |
| D17 | type violation | `defective/reddit-…` | `children[5].data.score` | the word `"many"` where an integer is required |
| D18 | unparseable file | `…unparseable.json.broken` | whole file | truncated mid-object; exercises the `parse_errors` path |

**Why D18 is not named `.json`:** a truncated `*.json` under `data/raw/` would fail this recipe's
gate-3 test (`find … -name "*.json" -exec python3 -m json.tool`) **permanently**, and would also
trip `scripts/conformance.mjs`. The fixture would break the repo instead of testing the validator.
The `.json.broken` extension keeps it invisible to every glob; the validator must be pointed at it
explicitly.

## Field and freshness contract (the spec the validator asserts against)

No schema existed for this recipe, so this manifest defines one. This is the `[TODO: DEFINE]`
closure for the fixture set, not a promotion of anything to `data/verified/`.

**Required fields** — a field present with value `null` counts as **missing**, not present:

| Source | Required |
|---|---|
| price (`Global Quote`) | `01. symbol`, `05. price`, `06. volume`, `07. latest trading day`, `08. previous close`, `10. change percent` |
| news (article) | `id`, `datetime`, `headline`, `source`, `url` |
| reddit (`t3.data`) | `id`, `title`, `created_utc`, `score` |

**Identity keys for duplicate detection:**

| Source | Key |
|---|---|
| price | (`01. symbol`, `07. latest trading day`) |
| news | `id`, plus a separate near-duplicate pass on whitespace-normalised, case-folded `headline` |
| reddit | `id` |

*Counting rule:* a duplicate is every occurrence beyond the first. Three rows sharing one key
count as **2** duplicates — not 3, not 1.

**Freshness windows**, all measured from `frozen_at`:

| Source | Window | Matches |
|---|---|---|
| news | 2 days before `frozen_at` | the 2-day lookback in the Fetch News Headlines URL |
| reddit | 24 hours before `frozen_at` | `t=day` |
| price | `07. latest trading day` within 5 calendar days | tolerates weekends and holidays |

Anything outside its window is **stale and must be flagged, not silently dropped**.

## Expected totals a test can assert

| Measure | price | news | reddit |
|---|---|---|---|
| duplicates | 1 | 1 by `id`, 2 by headline | 1 |
| rows missing a required field | 1 | 2 | 1 |
| malformed rows | 0 | 1 | 1 |
| stale rows | 1 | 1 | 1 |
| type violations | 1 | 1 | 1 |

Plus 1 count mismatch, 1 unparseable file. **18 defects total.**

Which recipe-declared output field each defect should surface in — step 3 `missing_fields` /
`parse_errors` / `record_count`, step 4 `duplicates` / `rejects` / `flags` / `quality_notes` — is
recorded per defect in `fixture-manifest.json` under `expected_detection`.

One gap that surfaced while mapping this: **step 3's declared output contract has no field for a
type violation.** Its fields are `record_count`, `required_fields_present`, `missing_fields`,
`parse_errors`, `schema_version` — a value of the wrong type is none of those. D02, D11 and D17 are
therefore mapped to step 4 `flags`. Either step 3 needs a `type_errors` field or the recipe should
say type checking is step 4's job; right now it says neither.

## Clean-set invariants

Every `*.json` parses · every required field present and non-null · no identity key or headline
repeats · every timestamp inside its window · declared `record_count` equals the recount · no
credential values anywhere (only `${VAR}` placeholders) · no timestamp from `now()`.

## What this set does NOT test

- **Wrong-entity signals** — a row that is well-formed, fresh, unique and complete but belongs to
  a *different company*. This is the class that reached a finished brief (`logs/RUN_LOG.md#2026-08-26`)
  and no shape check catches it. Ticker `FAKE` is unambiguous by construction, which is exactly why
  this set cannot exercise it.
- **Upstream HTTP failure modes** — 401/403 on a bad key, 429 rate limit, timeout, empty 200 body.
  Envelope-level, not record-level; they belong in a second fixture set.
- **Encoding defects** — mojibake, lone surrogates, BOM. The source workflow JSON is itself
  cp1252-hostile UTF-8, so this is a live risk, not a theoretical one.
- **Volume** — the largest file holds 8 rows. Nothing tests pagination or the `limit=50` ceiling.
- **Whether the sentiment score is *right*.** The fixtures carry positive and negative keywords so
  the aggregate path runs deterministically, but this manifest asserts nothing about the resulting
  number. That is a human adequacy judgment (P1), not a conformance check.
