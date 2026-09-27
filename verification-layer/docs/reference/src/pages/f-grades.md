---
title: Grades and synthesis
slug: f-grades
section: Features
order: 60
summary: A separate model call reads each finished answer for a grade, direction and assumptions; a deterministic synthesis says why two agents' views differ and proposes a consensus only when one exists.
---

Two agents' free-text conclusions can't be compared on their overall view. The assessment turns
each view into data; the synthesis explains the difference between them. Neither decides
anything: a grade is **a model's judgment**, internal tier, and investors only ever see a grade a
human recorded.

## The assessment

An assessment is a small, closed-vocabulary object ([[core/assessment.py]]):

| Field | Allowed values |
|---|---|
| `grade` | `AAA`, `AA`, `A`, `BBB`, `BB`, `B`, `CCC` |
| `direction` | `buy`, `hold`, `sell` |
| `assumptions` | `revenue_growth_pct` (number), `margin_trend` (`expanding`, `stable`, `contracting`), `horizon_months` (number) |
| `key_metrics` | canonical metric names |
| `key_points` | up to three short strings |

A value outside the vocabulary is recorded as an issue and left out, never coerced: "A-" is not
turned into "A".

## Where it comes from: the extraction call

After an answer passes the ordinary two-block check, **one more call to the same model** reads the
finished answer and returns only the JSON object ([D-11](decisions.html#d-11)). This is "option 1",
chosen by a human on 2026-09-26 after asking the agent to write the block itself (directive
v1.6.0) cut format compliance to 2 of 10 live runs ([D-10](decisions.html#d-10)).

- **The prompt is versioned.** `assess-extract-v2` is recorded on every assessment as its source.
- **What the agent didn't write is removed** (`ground_in`): a key point or assumption whose figure
  isn't in the agent's own text is dropped with an issue, and a growth assumption must come from a
  forward-looking sentence. Version 1 had reported past growth as a forward assumption.
- **It never fails the run.** Every outcome has a status: `valid`, `partial`, `invalid_fields`,
  `invalid_json`, `unclosed`, `empty`, `absent`, `abstained` (the answer states no view, an honest
  outcome) or `extraction_failed`.
- **It runs only for ticker compares.** Subject compares have no company to grade, and chat runs
  get no extraction.

The extraction is traced as its own step (kind `extract`), and the raw reply is kept in the
attempt's `raw_output`.

## The synthesis

[[validation/divergence.py]] (policy `b5-v1`) reads the figure rows, the checks and both
assessments. It calls no model.

**Why the views differ**: `primary_conflict_driver` is the first of these that holds:

| Driver | When |
|---|---|
| `data` | a figure row is `MISMATCH` or `DIFFERENT_PERIODS` |
| `assumption` | both gave assumptions and they differ (growth more than 1 point apart, or a different margin trend or horizon) |
| `weighting` | both graded, and the grades or directions differ, with neither of the above: a residual, not a finding |
| `insufficient` | fewer than two grades |
| `none` | same grade and direction, no data conflict, no assumption difference |

**What each agent has behind it**: for each grade candidate, five counts, never weighted into a
score ([D-41](decisions.html#d-41)): figures that matched the filing, figures that contradicted it,
figures that couldn't be checked, figures with no backing, and failed hard checks.

**Consensus** is narrow: a consensus grade exists only when both agents graded, grade and
direction are equal, and no hard check failed for either. When they graded differently, the
synthesis sets `needs_decision`, and the [gate](f-gate.html) opens a `grade` item where a reviewer
sets the grade.

## Tested and observed

- **Tested** in [[tests/test_assessment.py]] and [[tests/test_synthesis.py]].
- **Observed live**: two grade conflicts on 2026-09-26 (AAPL `8ecb0922`, NVDA `9b1a9e0e`), both
  classed `assumption` by extraction v1, which the record then found wrong
  ([synthesis-thin-and-lexical](ledger.html#synthesis-thin-and-lexical)). v2 has few live runs.

## Limits

- The forward-looking test is a word list.
- A proposed consensus can't be confirmed as a published grade; only a disagreement opens a grade
  decision.
- The review app doesn't yet render the `abstained` and `extraction_failed` statuses specially
  (noted in [[web/frontend/src/components/Assessment.tsx]]).
