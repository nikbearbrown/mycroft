# Audit — Market Sentiment Analysis - Part 1 run `sample-001-defective`

**Inspected:** `data/verified/market-sentiment-analysis-part-1/runs/sample-001-defective`  ·  **Run date:** 2026-08-27  ·  **Frozen clock:** `2026-08-27T14:30:00+00:00`

> This audit reports what it found. It does not say "pass" — adequacy is the human gate (SNICKERDOODLE, verification stack layer 2).

## Records in, records out

| Stream | Seen | Passed shape | Duplicates removed | Final | Flags |
|---|---|---|---|---|---|
| news | 8 | 5 | 3 | 3 | 2 |
| price | 5 | 4 | 1 | 3 | 2 |
| reddit | 6 | 4 | 1 | 3 | 2 |

## What was withheld, and why

| Stream | Locator | Reason | Action |
|---|---|---|---|
| news | `records[3]` | missing_required_field | row withheld from the verified layer; never defaulted |
| news | `records[4]` | missing_required_field | row withheld from the verified layer; never defaulted |
| news | `records[5]` | malformed_row | row withheld from the verified layer |
| price | `records[1]."Global Quote"` | missing_required_field | row withheld from the verified layer; never defaulted |
| reddit | `records[0].data.children[2].data` | missing_required_field | row withheld from the verified layer; never defaulted |
| reddit | `records[0].data.children[3].data` | malformed_row | row withheld from the verified layer |

## What was flagged and kept

| Stream | Locator | Flag | Value |
|---|---|---|---|
| news | `records[6]` | stale_timestamp | `1710507600` |
| news | `records[7]` | type_violation | `yesterday` |
| price | `records[2]."Global Quote"` | type_violation | `N/A` |
| price | `records[3]."Global Quote"` | stale_timestamp | `2024-03-15` |
| reddit | `records[0].data.children[4].data` | stale_timestamp | `1710523200` |
| reddit | `records[0].data.children[5].data` | type_violation | `many` |

## Anomalies a shape check cannot catch

- **Wrong-entity signals.** A row that is well-formed, fresh, unique and complete but belongs to a different company. No check in this pipeline catches it; ticker `FAKE` is unambiguous by construction and cannot exercise it.
- **Whether the score is right.** This audit asserts nothing about the sentiment number. That is a human adequacy judgment (P1).
- **Upstream HTTP failures, encoding defects, volume.** Not covered by the fixture set.
