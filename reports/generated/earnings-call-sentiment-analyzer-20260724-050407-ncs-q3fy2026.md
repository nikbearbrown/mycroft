# Earnings Call Sentiment Analysis — Northstar Cloud Systems

## Review Status

- Run ID: `20260724-050407-ncs-q3fy2026`
- Recipe version: `0.1.0`
- Analyst: `[NOT YET ASSIGNED]`
- Review date: `[PENDING]`
- Decision: `[PENDING HUMAN REVIEW]`

This is a completed technical sample run, not an approved research finding. Northstar Cloud Systems is user-created synthetic data and is not a real issuer record.

## Source and Model

| Field | Value |
|---|---|
| Company | Northstar Cloud Systems |
| Ticker | NCS |
| Fiscal period | Q3 FY2026 |
| Transcript source | `data/raw/earnings-call-sentiment-analyzer/northstar-cloud-systems-q3-fy2026.txt` |
| Sample or real issuer record | User-created synthetic sample |
| Source hash | `b3f75b1f233281864121dbb5d5d372baf8e734c1c9c2670509b84c930e8ca14f` |
| Model | `ProsusAI/finbert`; immutable model revision was not recorded |
| Analysis timestamp | 2026-07-24 05:04:07–05:04:08 UTC |

Machine log: `logs/earnings-call-sentiment-analyzer-20260724-050407-ncs-q3fy2026.json`

## Scope

- Transcript sections analyzed: Q&A, prepared remarks, financial results, guidance, and unknown.
- Evidence chunks analyzed: 25.
- Named speakers detected: Maya Chen, Daniel Ortiz, Sarah Kim, Michael Torres, and Operator.
- Unknown speaker attributions: 2 of 25 chunks.
- Unknown section attributions: 4 of 25 chunks.
- Excluded or unreadable material: none reported by the worker.

## Tone Summary

These values are model judgments about language tone. Net tone is positive probability minus negative probability, averaged across the named cohort.

| Cohort | Net tone | Positive | Neutral | Negative | Evidence |
|---|---:|---:|---:|---:|---|
| Overall | +16.74% | 9 | 11 | 5 | 25 chunks |
| Prepared remarks | +20.39% | 2 | 0 | 2 | 4 chunks |
| Q&A | +12.33% | 4 | 7 | 2 | 13 chunks |
| Management | +37.53% | — | — | — | CEO and CFO chunks |
| Analysts | −26.69% | — | — | — | 4 analyst chunks |
| Guidance | +1.39% | 1 | 0 | 1 | 2 chunks |

## Prepared Remarks Versus Q&A

Prepared remarks scored +20.39% and Q&A scored +12.33%, a measured Q&A-minus-prepared difference of −8.05 percentage points. This is a descriptive model output; it does not establish why the language differs or whether either section is accurate.

Representative prepared evidence includes chunk 5, where Maya Chen describes revenue growth and durable demand (+93.85%), and chunk 8, where she describes below-plan European customer additions (−92.68%). Representative Q&A evidence includes chunk 23 on security-customer wins (+93.88%) and chunk 21 on RPO deceleration and shorter contracts (−92.04%).

## Management Versus Analyst Language

Management chunks averaged +37.53%; analyst chunks averaged −26.69%, a measured difference of 64.22 percentage points. This contrast is consistent with management responses containing constructive language and analyst questions raising potential weaknesses, but that explanation is an analyst hypothesis—not a machine-verified causal finding.

## Guidance and Risk-Language Signals

The two guidance chunks average +1.39%, which the UI categorizes as balanced. One guidance chunk is strongly positive and one strongly negative, so the near-zero average should not be read as uniform neutrality.

The dashboard's rule-based risk signal marks 2 of 25 chunks (8.0%) as elevated. The rule requires both a negative FinBERT label and a match against a fixed risk-term expression. In this run it matched the foreign-exchange “headwind” guidance in chunk 11 and “lower” contract duration/pacing language in chunk 21. This heuristic is a rule judgment; absence of a match would not establish absence of risk.

## Evidence Chunks

| Chunk | Section | Speaker | Role | Label | Net tone | Transcript evidence |
|---:|---|---|---|---|---:|---|
| 23 | Q&A | Maya Chen | CEO | Positive | +93.88% | Majority of security wins came from existing platform customers; 34 net-new security customers; improved win rates and feedback. |
| 5 | Prepared remarks | Maya Chen | CEO | Positive | +93.85% | Strong quarter, durable demand, and revenue growth ahead of the prior outlook. |
| 8 | Prepared remarks | Maya Chen | CEO | Negative | −92.68% | European customer additions were below internal plan amid longer procurement cycles. |
| 21 | Q&A | Daniel Ortiz | CFO | Negative | −92.04% | Renewal timing, shorter contract duration, and slower seat-expansion pace. |
| 11 | Guidance | Daniel Ortiz | CFO | Negative | −88.88% | Fourth-quarter outlook includes a two-point foreign-exchange headwind. |
| 14 | Q&A | Sarah Kim | Analyst | Neutral | −30.86% | Question about slower European customer additions and whether weakness continued. |

## Attribution and Parsing Gaps

- Unknown speakers: 2 chunks—the title and `OPERATOR INTRODUCTION` marker.
- Unknown sections: 4 chunks—the title, introduction marker, operator greeting, and recording notice.
- Suspected boundary errors: human review is still required; no machine-detected ordering gaps occurred.
- OCR or extraction issues: none; input was UTF-8 text.
- Corrections requested: decide whether front-matter/operator-introduction chunks should stay `UNKNOWN` or receive a dedicated metadata/introduction section.

## Verification Findings

- All five Compose services started; PostgreSQL, RabbitMQ, and backend health checks passed.
- The real sample upload queued and completed, with 25 chunks and 25 persisted sentiment rows.
- Every probability triplet sums to 1 within `1.10e-7`; every net score exactly equals positive minus negative.
- Chunk order, label counts, section counts, speaker counts, and summary means reconcile.
- Worker tests pass 9/9; frontend lint and production build pass.
- The backend Maven test lifecycle compiles 36 sources and succeeds, but reports no test sources.
- Invalid ticker metadata is rejected with HTTP 400.
- The transcript list, dashboard, evidence search, and upload page render and behave in the live browser.

## Correctness Issue Found During Verification — Resolved

At run time, the dashboard explanation said labels were Positive above +5%, Neutral from −5% to +5%, and Negative below −5%. Aggregate labels and chart colors use that threshold rule, but chunk evidence labels use FinBERT's highest-probability class. Three chunks in this run differ under the two rules, including chunk 14, whose highest class is Neutral even though its positive-minus-negative score is −30.86%. The UI copy was corrected before the feature-branch commit and now distinguishes “FinBERT class label” from “aggregate net-tone band.”

## Limitations

- FinBERT measures language tone, not truthfulness, valuation, earnings quality, or future returns.
- Transcript and speaker-attribution errors can materially change aggregates.
- Transcript-wide averages can hide section and speaker differences.
- Research-signal interpretations are model or rule judgments requiring human review.
- The Hugging Face model name is stored, but an immutable revision is not pinned or persisted.
- Backend and frontend automated test coverage is absent beyond worker tests, lint/build, API smoke checks, and this end-to-end run.

## Human Decision

### Tested

| Reviewed | Saw | Expected |
|---|---|---|
| `[PENDING]` | `[PENDING]` | `[PENDING]` |

### Did Not Test

- A real issuer transcript.
- Text-based PDF extraction in the full Compose stack.
- Failure recovery during queue or worker interruption.
- Multiple concurrent uploads and larger transcripts.
- Human adequacy of all speaker and section boundaries.

### Corrections or Follow-Up

- Assign a named analyst to review representative evidence and all unknown attributions.
- Define the acceptable unknown-attribution and labeled-corpus accuracy thresholds.
- Pin and persist the exact model revision.
- Add backend and frontend automated tests.

### Decision Enabled

Pending. A named human must choose: accept for bounded research use; request corrections; or block downstream use.
