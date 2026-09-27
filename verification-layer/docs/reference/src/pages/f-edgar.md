---
title: EDGAR data, lenses and filings
slug: f-edgar
section: Features
order: 30
summary: Where the agents' figures come from — one SEC companyfacts fetch read through two lenses, with every figure traceable to the filing it came from.
---

For a ticker compare, both agents reason over the company's own SEC filings, not the model's
memory. The data comes from one fetch and is read through two *lenses*: each agent sees a chosen
slice of the same payload.

## The fetch

[[datasources/edgar.py]] is the only data-egress module ([D-22](decisions.html#d-22)):

1. `lookup_cik` resolves the ticker to a CIK with SEC's ticker file.
2. `fetch_company_facts` downloads the company's XBRL `companyfacts` JSON **once**; both lenses
   read the same payload ([D-23](decisions.html#d-23)).
3. `select_fact` picks one value per concept and keeps its period and unit: the end date, the start
   date for duration figures, the form and the accession number ([D-24](decisions.html#d-24)).

Every fetch is injectable, so tests use a recorded payload
([[tests/fixtures/*|the fixtures]]) instead of the network. SEC asks every client to identify
itself; set `SEC_USER_AGENT`.

## Lenses

A lens is a `ConceptLens` value ([[producers/lens.py]]): a name, an agent id, a list of us-gaap
concepts, an optional header and a version ([D-26](decisions.html#d-26)). The lens decides what
the agent is shown and nothing else; the model call, the parser and the retry rules are the same
for every agent.

| Lens | Concepts | Version |
|---|---|---|
| `financial` ([[producers/financial.py]]) | `Assets`, `Revenues`, `NetIncomeLoss`, `EarningsPerShareDiluted` | v2 |
| `earnings` ([[producers/earnings.py]]) | `EarningsPerShareDiluted`, `EarningsPerShareBasic`, `OperatingIncomeLoss`, `NetIncomeLoss` | v2 |
| `bull` ([[producers/bull.py]]) | all six | v1 |
| `bear` ([[producers/bear.py]]) | all six | v1 |

## Pairings

A compare picks a pairing (`pairing` in the request; [[producers/__init__.py]]'s `PAIRINGS`):

- **`lenses`** (default): financial against earnings. They share two concepts, `NetIncomeLoss`
  and `EarningsPerShareDiluted`, and each sees two the other doesn't. The shared pair is where the
  agents can be compared directly ([D-28](decisions.html#d-28)). Originally the two sets were
  disjoint, which meant nothing could ever be corroborated ([D-27](decisions.html#d-27),
  superseded).
- **`bull_bear`**: both agents see the same six figures with opposite briefs, so any disagreement
  comes from interpretation, not data ([D-29](decisions.html#d-29)). This pairing has had few live
  runs ([bull-bear-unmeasured](ledger.html#bull-bear-unmeasured)).

The shared set is computed from the lens definitions (`shared_concepts`), never hard-coded in a
comparator.

## Figures located in the filing

A number in the companyfacts JSON is a value, not evidence a reader can check. So each figure
also carries the accession number of the filing it came from, and the review app can show the
figure **in the filing itself** ([D-25](decisions.html#d-25)):

- [[datasources/filings.py]] fetches the filing's primary document, parses its inline XBRL, finds
  the tagged fact with the same concept and period, and returns the surrounding table row or
  paragraph with the figure highlighted.
- It is lazy: nothing is fetched until a reviewer opens a figure (`GET /api/facts/excerpt`).
  Documents are cached gzipped in `web/data/filing_cache/`.
- It never fails loudly. `status` says what happened (`found`, `not_found`, `no_inline_xbrl`,
  `too_large`, `fetch_failed`, `not_in_index`), and the filing index link is returned either way.
- Coverage is limited to recent inline-XBRL primary documents
  ([filing-excerpt-coverage](ledger.html#filing-excerpt-coverage)).

## Where to look next

- How each lens writes its context string: [[producers/lens.py]].
- The recorded payloads and filing used by tests: [[tests/fixtures/*]].
- How the figures are compared once the agents answer: [Cross-agent comparison](f-compare.html).
