---
title: Audit record and review export
slug: f-audit
section: Features
order: 90
summary: Every compare run can be read as one audit record (JSON) or downloaded as a Markdown review, at the reader's scope, built from what the run recorded.
---

The audit record is the run reshaped for a reviewer: the figures, the checks, the grade
candidates, the decisions and the sources, in one object. It is a *view*: nothing is recomputed
and the stored record is not changed ([[validation/audit.py]], format `audit-v1`).

## Routes

| Route | Returns |
|---|---|
| `GET /api/runs/{id}/audit` | the audit record as JSON |
| `GET /api/runs/{id}/export.md` | the same as a Markdown review, downloaded as `review-<id>-<scope>.md` |

Both are served at the reader's scope like `GET /api/runs/{id}`, and only for compare runs (422
otherwise).

## What it holds

`metric_comparisons` (the figure rows), `structural_flags` (the checks), `primary_conflict_driver`,
`grade_candidates`, `consensus_grade` and its reason, `audit_recommendation`, `gate_status`,
`decisions`, `decided_grade`, and the source filings with their EDGAR index links.

- **Built after redaction.** The record is made from the run after scope redaction, so an
  investor's export carries only what an investor's read carries: no agent grade and no disputed
  value while a decision is pending.
- **The Markdown review** has a summary, the figures table, the checks, the grade candidates
  (labelled as model judgments), each decision with who, when and why, and the sources. Table
  cells are escaped and kept to one line.

## In the review app

"Download review" on a compare record downloads the Markdown at the viewer's scope; "Technical
details: the raw record" shows the JSON and offers "Download the audit record (JSON)"
([[web/frontend/src/views/RunDetail.tsx]]).

## Tested and observed

- **Tested** in [[tests/test_audit.py]]: the shape, that the stored record is unchanged, and that
  an investor export has no agent grade and no disputed value.
- **Observed** on 2026-09-27: the investor export of run `8ecb0922` downloaded from the new UI as
  `review-8ecb0922-investor.md` with no agent grade (`logs/RUN_LOG.md`, "B6 + U9").
