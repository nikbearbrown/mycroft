# B2 — Source classification fix: verification & measured evidence

**Date:** 2026-08-30 · **Workflow:** `workflow.dev.json` (`Normalize Data` node, `identifySource()`)

## The bug

`identifySource()` labeled *every* `federalregister.gov` item as `'Federal Register - Securities'`
unless a narrow CFTC heuristic matched (link contains `commodity-futures`, or title contains
`cftc`). Two problems, both confirmed live:

1. **The CFTC heuristic never actually matches real CFTC items.** Federal Register document
   permalinks don't embed the agency slug (e.g.
   `federalregister.gov/documents/2026/08/26/2026-17416/swap-execution-facility-...`), and CFTC
   rule titles rarely say "CFTC" literally (e.g. "Swap Execution Facility Order Book Requirement
   for Permitted Transactions"). Live-tested: **12/12** items from the dedicated CFTC Regulations
   RSS feed were mislabeled `'Federal Register - Securities'`.
2. **The "securities+investment" term-search feed (labeled `Federal Register - Securities`) pulls
   in genuinely unrelated agencies** — the search is full-text, not agency-filtered. Live-tested:
   of 146 sampled items, 83 actually came from agencies like the Federal Communications Commission,
   Equal Employment Opportunity Commission, and the DOT Maritime Administration — all mislabeled
   `'Federal Register - Securities'`.

## The fix — read the real issuing agency instead of guessing

Every Federal Register RSS item carries a reliable `<dc:creator>` field naming the actual issuing
agency verbatim (e.g. `Commodity Futures Trading Commission`, `Securities and Exchange
Commission`) — already piped into the code as `creator`, but previously only checked via an
acronym substring (`includes('cftc')`, `includes('sec.gov')`) that never matches Federal
Register's spelled-out agency names, and only in a fallback block the `federalregister.gov`
branch's early `return` made unreachable anyway.

```js
if (lowerLink.includes('federalregister.gov')) {
  const lowerCreator = (creator || '').toLowerCase();
  if (lowerCreator.includes('commodity futures trading commission') || lowerLink.includes('commodity-futures') || lowerTitle.includes('cftc')) {
    return 'CFTC Regulations';
  }
  if (lowerCreator.includes('securities and exchange commission')) {
    return 'Federal Register - Securities';
  }
  if (lowerCreator.includes('financial industry regulatory authority')) {
    return 'FINRA Enforcement News';
  }
  // dc:creator reliably carries the issuing agency's full name (verified live 2026-08-30);
  // anything not SEC/CFTC/FINRA is a real non-financial agency, not "Securities"
  if (creator && creator !== 'Unknown') {
    return `Federal Register - ${creator}`;
  }
  return 'Unknown Source';
}
```

## Live verification (2026-08-30)

Extracted `identifySource()` (old and new versions) and ran both against live RSS pulls from all
5 feeds (script: ad hoc, not committed — see method below):

| Feed | Items sampled | Reclassified | Notes |
|---|---|---|---|
| Federal Register - Securities (term search) | 146 | **83** | Now labeled by real agency (FCC, EEOC, DOT-Maritime, etc.) instead of a blanket "Securities" |
| CFTC Regulations (dedicated feed) | 12 | **12** | 100% were mislabeled "Federal Register - Securities"; 100% now correctly "CFTC Regulations" |
| SEC Press Releases (native feed) | 25 | 0 | No change — already correctly classified via `sec.gov` link domain, unaffected by this fix |
| FINRA (Google News) | 100 | 0 | No change — classified via title heuristic, untouched by this fix |
| Investment Advisor Rules (Google News) | 100 | 0 | No change — same as above |

**Zero regressions** on the three feeds that were already classifying correctly.

## Scope — what this does NOT fix

- **The 21 "Unknown Source" items (Google News fallthrough)** are not addressed here: Google News
  RSS items carry no `dc:creator` (only a publisher `<source>` tag, e.g. "Mayer Brown" —
  irrelevant to agency classification) and their headlines sometimes don't literally contain
  "FINRA"/"SEC"/"investment adviser"/"CFTC"/"securities"/"commodity", so no reliable signal exists
  to close this gap without a fuzzier (and less verifiable) matching approach. Left open.
- **Noise from the loose "securities+investment" term search** (C1, frozen as the Layer-2
  benchmark baseline) is unchanged — this fix corrects the *label* on non-financial items, it does
  not filter them out.

## Verification method

Extracted the `identifySource()` function (old and new) into a standalone Node script; fetched all
5 live RSS feeds; ran both versions against every item and diffed the labels. No live DB write —
classification-only comparison.
