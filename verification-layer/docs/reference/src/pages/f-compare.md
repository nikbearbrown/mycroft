---
title: Cross-agent comparison
slug: f-compare
section: Features
order: 40
summary: Two agents answer independently; every figure they cite is tagged with a metric and a period and compared figure by figure, with one status per metric.
---

Cross-agent validation runs two agents on the same subject, independently, and compares what
they concluded. It detects **numeric disagreement** between two conclusions. It does not detect
reasoning errors and it does not decide which agent is right ([D-30](decisions.html#d-30)).

## How a compare runs

[[validation/cross_validation.py]]'s `run_cross_agent_validation` runs both agents through the
[validation loop](f-validation-loop.html), on two threads by default, and assembles one
`cross_agent_comparison` block:

1. **Both agents answer.** Each gets its own context (its lens, or the shared subject context)
   and its own traced adapter. A halted agent means there is nothing to compare, and the status
   says so instead of reporting "no contradiction" ([D-31](decisions.html#d-31)).
2. **Figures are extracted** from each conclusion ([[validation/facts.py]]).
3. **Figures are compared** metric by metric: the `metric_comparisons` rows.
4. **A contradiction rule** decides `contradiction_flag` (below).
5. **Accounting checks** run ([Accounting checks](f-checks.html)).
6. **Grades are synthesised** ([Grades and synthesis](f-grades.html)).
7. **The run is stored** and the [decision gate](f-gate.html) is computed.

## Figures with a metric and a period

A bare string comparison can't say "both agents cite diluted EPS for Q3 FY26 and the values
differ". So each figure becomes a *canonical fact* ([D-32](decisions.html#d-32) covers the one
shared definition of "a number" in [[core/numeric.py]]):

- **The metric** is the nearest known alias in the same clause ("diluted EPS", "revenue",
  "operating margin"), with rules for per-share figures, ratios and percentage changes. A model's
  rating of itself ("confidence: 90%") is dropped: it is not a claim about the subject.
- **The period** is the nearest period expression in the sentence ("Q3 FY2026", "nine months
  ended", "fiscal 2025"), or `unknown`.
- Citation brackets and URLs are masked first, so digits in them never become figures.

## The statuses

Each metric gets exactly one row. The conditions are exact in [[validation/facts.py]]; in words:

| Status | Meaning | Gates? |
|---|---|---|
| `MATCH` | Both agents cite it, for compatible periods, within tolerance. | no |
| `MISMATCH` | Both cite it, for compatible periods, and the values differ beyond tolerance. The only two-sided conflict. | **yes** |
| `DIFFERENT_PERIODS` | Both cite it, but for periods that can't be compared. | no |
| `UNVERIFIABLE_PERIOD` | Only one side stated a period and nothing agrees. | no |
| `CITED_BY_ONE` | Only one agent cites a figure both were given (a shared lens concept). | no |
| `ONE_SIDED` | Only one agent cites a dollar or per-share figure not in both contexts. | no |
| `UNCORROBORATED` | Only one agent cites a figure of another kind, with no match on the other side. This is what catches the one confirmed fabrication in the corpus. | no (flags) |
| `DERIVED_OK` / `DERIVED_WRONG` | One agent states a ratio the system can recompute from that agent's own figures: within 2%, or not. | no |

Tolerances depend on the kind of figure: 0.5% for currency, half a cent for per-share, 0.1
points for percentage changes, 1% for derived and untagged figures, exact for years.

## Contradiction rules

`contradiction_flag` is a single yes/no the run carries. Which rule sets it is chosen per run
([D-34](decisions.html#d-34), [D-35](decisions.html#d-35)):

| Rule | Where | Default for |
|---|---|---|
| `concept_aware` | [[validation/concept_linkage.py]] | ticker compares with the `lenses` pairing |
| `canonical_facts` | [[validation/facts.py]] (flags on `MISMATCH` and `UNCORROBORATED`) | `bull_bear`, and subject compares (with years) |
| `symmetric_difference` | [[validation/cross_validation.py]] | the original v1 rule: the function's default for direct calls (scripts, tests); the web route always chooses one of the other two unless a request asks for it |

The flag is a summary. The rows are what a reviewer reads, and only `MISMATCH` rows open the gate.

## Tested and observed

- **Tested** in [[tests/test_facts.py]], [[tests/test_cross_validation.py]],
  [[tests/test_concept_linkage.py]] and [[tests/test_real_run_corpus.py]], which labels real stored
  runs and measures each rule against them.
- **Observed live** on 2026-09-24: an NVDA revenue row came out `DIFFERENT_PERIODS`, and AAPL, MSFT
  and GOOGL were flagged only by `UNCORROBORATED` rows (`logs/RUN_LOG.md`, "B1 + U2").

## Limits

- Tagging is lexical: an unrecognised phrasing stays untagged, and so is never compared or checked
  ([checks-lexical-coverage](ledger.html#checks-lexical-coverage)).
- `ONE_SIDED` also covers dollar figures neither agent was given; see the note in
  [[validation/facts.py]].
- Non-numeric claims (dates other than years, qualitative statements, causes) are out of scope.
