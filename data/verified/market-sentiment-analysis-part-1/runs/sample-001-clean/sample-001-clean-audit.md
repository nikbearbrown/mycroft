# Audit — Market Sentiment Analysis - Part 1 run `sample-001-clean`

**Inspected:** `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean`  ·  **Run date:** 2026-08-27  ·  **Frozen clock:** `2026-08-27T14:30:00+00:00`

> This audit reports what it found. It does not say "pass" — adequacy is the human gate (SNICKERDOODLE, verification stack layer 2).

## Records in, records out

| Stream | Seen | Passed shape | Duplicates removed | Final | Flags |
|---|---|---|---|---|---|
| news | 5 | 5 | 0 | 5 | 0 |
| price | 1 | 1 | 0 | 1 | 0 |
| reddit | 4 | 4 | 0 | 4 | 0 |

## What was withheld, and why

_None._

## What was flagged and kept

_None._

## Anomalies a shape check cannot catch

- **Wrong-entity signals.** A row that is well-formed, fresh, unique and complete but belongs to a different company. No check in this pipeline catches it; ticker `FAKE` is unambiguous by construction and cannot exercise it.
- **Whether the score is right.** This audit asserts nothing about the sentiment number. That is a human adequacy judgment (P1).
- **Upstream HTTP failures, encoding defects, volume.** Not covered by the fixture set.
