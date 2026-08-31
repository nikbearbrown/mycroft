# Event envelope — the contract on the wire

Every message on `events.raw` / `events.validated` / `events.enriched` is one JSON object
with this shape. Producers MUST populate the required fields; consumers MUST ignore unknown
fields (forward compatible).

## Fields

| field | type | req | set by | notes |
|---|---|---|---|---|
| `event_key` | string | yes | ingest-gateway | **dedup key.** EDGAR accession number (`0000320193-26-000042`) for filings, atom `<id>` for the feed. Globally unique. |
| `source` | string | yes | ingest-gateway | `edgar_fts` \| `edgar_atom` \| `fred` \| `manual` |
| `form` | string | no | ingest-gateway | e.g. `8-K` |
| `ticker` | string | no | validation-svc (Week 2) | resolved from CIK; NULL until then |
| `cik` | string | no | ingest-gateway | zero-padded 10-digit where available |
| `company` | string | no | ingest-gateway | display name from the source |
| `title` | string | no | ingest-gateway | filing description / feed entry title |
| `url` | string | no | ingest-gateway | link to the primary document |
| `published_at` | string (RFC3339) | no | ingest-gateway | when the source says the event occurred/was filed |
| `fetched_at` | string (RFC3339) | yes | ingest-gateway | when the gateway pulled it |
| `raw` | object | yes | ingest-gateway | the unmodified source record (one FTS hit, or the atom entry as a map). Provenance — never trim it. |
| `event_type` | string | no | enrichment-svc (Week 2) | classified from the 8-K item codes; NULL in Week 1 |
| `signal` | object | no | enrichment-svc | see below |

## `signal` object (Week 2)

`{status: "pending_review", event_type, direction, magnitude, confidence, confidence_basis, rationale, passes}`
or `{status: "withheld", event_type, withheld_reason}`.

- **`confidence`** is **not a calibrated probability.** With the `deterministic` LLM provider it
  is a rule-table constant (`confidence_basis: "heuristic"`); with `anthropic` it is the model's
  own estimate (`confidence_basis: "model_estimate"`). Neither is validated against realized
  price moves until the Week-4 `outcome-grader`. Treat it as a coarse prior for ordering the
  review queue, not as a likelihood.
- **`direction`** ∈ `up | down | unclear`. The agent emits only `up`/`down`; `unclear` always
  routes to `withheld`.
- A **withheld** read is still a signal row (the agent looked and declined) — `withheld_reason`
  names why (self-consistency disagreement, unclear direction, low confidence, or verify-reject).

## Example (`events.raw`, Week 1)

```json
{
  "event_key": "0000320193-26-000042",
  "source": "edgar_fts",
  "form": "8-K",
  "cik": "0000320193",
  "company": "Apple Inc.",
  "title": "8-K - Entry into a Material Definitive Agreement",
  "url": "https://www.sec.gov/Archives/edgar/data/320193/000032019326000042/aapl-8k.htm",
  "published_at": "2026-08-28T00:00:00Z",
  "fetched_at": "2026-08-30T18:20:03Z",
  "raw": { "...": "the full efts hit" }
}
```

## Example (`events.enriched`, Week 1 — passthrough)

Same object, plus:

```json
  "event_type": null,
  "signal": { "status": "stub", "rationale": "passthrough — enrichment not implemented (Week 1)" }
```

## Kafka

- key = `event_key` (so all messages for one filing land on the same partition — matters once
  we reprocess).
- partitions: 3 (dev). Topics: `events.{raw,validated,enriched,actionable,deadletter}`.
