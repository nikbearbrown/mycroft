# "Unknown Source" investigation — partial fix, honest remainder

**Date:** 2026-08-30 · **Workflow:** `workflow.dev.json` (`Normalize Data` node, `identifySource()`)

## Starting point

After the B2 fix (see `B2-VERIFICATION.md`), 18 items across the two Google News feeds still fell
through to `'Unknown Source'` (live count 2026-08-30; `FINDINGS.md` from 2026-07-24 recorded 21 —
close, feed content changes daily). These items have no `dc:creator` (Google News RSS carries only
a publisher `<source>` tag, e.g. "Mayer Brown" — irrelevant to regulator classification), so the
`dc:creator` fix that solved B2 doesn't apply here.

## What was actually failing

Read every one of the 18 real titles live. They split into two groups:

1. **Recoverable — the title names the topic using a synonym the classifier didn't check for:**
   "adviser"/"advisor" alone (not the required two-word "investment adviser/advisor"), the "RIA"
   acronym (Registered Investment Adviser), "broker-dealer", or "Reg BI" (Regulation Best
   Interest — a broker-dealer rule, FINRA's domain). E.g. "What Are Exempt Reporting Advisers
   (ERAs)?", "The (New) Marketing Rule: Perspectives on RIA Compliance", "Managing broker-dealer
   compliance at scale", "Reg BI Cases Keep Increasing."
2. **Not recoverable from title alone:** generic overview pieces with no named regulator
   ("Financial Regulators: Who They Are and What They Do," "When Two Become One: Navigating the
   Complexities of Operational Integration," "De Minimis Exemptions By State"), or an item about a
   **different regulator entirely** — "FCA Decision Notice..." is the UK Financial Conduct
   Authority, not a US regulator this pipeline tracks. Labeling that "Unknown Source" is correct,
   not a bug.

## The fix — feed-agnostic secondary keywords, applied only to leftover items

```js
// inside the news.google.com branch, after the existing 4 checks
if (/\bria\b/.test(lowerTitle) || lowerTitle.includes('adviser') || lowerTitle.includes('advisor')) {
  return 'Investment Advisor Rules';
}
if (lowerTitle.includes('broker-dealer') || lowerTitle.includes('broker dealer') || /\breg\s?bi\b/.test(lowerTitle)) {
  return 'FINRA Enforcement News';
}
```

No feed-hint (i.e., no need to know which of the two Google News searches produced the item) —
these keywords are topically unambiguous regardless of which search surfaced them: an article
about broker-dealer compliance is FINRA's domain whether Google matched it under the "FINRA"
query or the "investment advisor" query.

## Live verification (2026-08-30)

Extracted the real `identifySource()` function from `workflow.dev.json` after the edit and ran it
against all 5 live feeds:

| Feed | Items | Unknown Source (before) | Unknown Source (after) |
|---|---|---|---|
| Federal Register - Securities (term search) | 146 | 0 | 0 |
| CFTC Regulations feed | 12 | 0 | 0 |
| SEC Press Releases | 25 | 0 | 0 |
| FINRA (Google News) | 100 | 6 | 4 |
| Investment Advisor (Google News) | 100 | 12 | 4 |
| **Total** | **383** | **18** | **8** |

**10 of 18 (56%) recovered, zero unexpected reclassifications** of items that were already
correctly labeled something other than `'Unknown Source'` — the new rules only ever fire on items
that would otherwise fall through.

## What's still open, and why this isn't a full close

The remaining 8 (listed above) are genuinely unclassifiable from title text alone without real
content analysis (reading the article body) or accepting a materially higher false-positive risk.
This was the explicitly-flagged tradeoff before starting this investigation — a fuzzier
NLP-style approach could chase these too, but at a lower confidence/higher risk-of-mislabeling
ratio than is worth taking on right now. Left open.
