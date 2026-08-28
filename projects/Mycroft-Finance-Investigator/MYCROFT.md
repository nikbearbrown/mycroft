# Mycroft Integration — Finance Investigator

## Purpose

This project is the runnable sample implementation for an agentic monthly
performance investigation. It applies the preparation-versus-judgment boundary
from `chapters/06-monthly-variance-pack.md`.

## Canonical Contracts

- Recipe: `recipes/mycroft-finance-investigator.md`
- Conductor: `conductor/mycroft-finance-investigator.md`
- Raw data: `data/raw/mycroft-finance-investigator/`
- Verified data: `data/verified/mycroft-finance-investigator/`
- Human report template: `reports/templates/mycroft-finance-investigator.md`
- Status: `DRAFT`

## Labor Boundary

- Machines validate, reconcile, calculate, rank, flag, and attach source rows.
- The investigator plans which deterministic tools to run and surfaces missing
  evidence.
- Humans set production materiality, confirm causal explanations, judge
  adequacy, and authorize distribution.

The review gate is implemented in `mycroft_finance_investigator/review.py`.
Review requests are bound to the source run hash. A named human supplies the
decision; the recorder verifies cited evidence, prevents agent self-approval,
and writes a new artifact without overwriting an earlier decision.

The deterministic evaluation harness is implemented in
`mycroft_finance_investigator/evaluation.py`. It runs the baseline and six
adversarial cases in isolated temporary copies, compares observations with the
committed expectations in `evaluations/cases.json`, and emits a scorecard. It
reports coverage of named cases, not model confidence or production adequacy.

The scenario engine is implemented in
`mycroft_finance_investigator/scenario.py`. It binds a plan to the exact sample
run, applies amount or percent-of-actual assumptions, and preserves calculation
and plan lineage. Every output says `SIMULATION_NOT_FORECAST`, leaves
`recommendation` null, and records `HUMAN_REQUIRED` for the decision.

The audit-bundle handoff is implemented in
`mycroft_finance_investigator/bundle.py`. It validates the run-to-review,
run-to-scenario, case-to-evaluation, raw-data, and verified-data hashes before
packaging the complete evidence chain. The package includes source and verified
data, specifications, implementation, tests, logs, reports, the recipe, and the
conductor. A second command recomputes every packaged hash.

The bundle checksum proves integrity, not identity or adequacy. The generated
review view keeps the recipe `DRAFT`, reports
`BLOCKED_PENDING_HUMAN_REVIEW`, and leaves human attestation null.

The historical comparison is implemented in
`mycroft_finance_investigator/trend.py`. It accepts only ordered, unique periods
whose completed investigation logs and verified source hashes agree. It
recomputes EBITDA and category impacts, identifies recurrence using the
explicit demo threshold, and retains the source run and row references. It
cannot generate causation, forecasts, recommendations, or approval.

The investigator must never convert a numerical variance into a causal claim.
Its output may identify which customer, account, or department records move
with the variance, but the reason for that movement remains owner-required.

## Sample Classification

All included company and transaction records are synthetic. They are designed
to exercise the software and do not describe a real company, issuer, employee,
customer, or investment.

The committed sample review request remains `OPEN`. It is not a human decision
and does not promote the recipe.

The committed scenario plan is also synthetic and unapproved. Its values exist
to test arithmetic and disclosure behavior, not to represent a forecast or a
preferred business action.

The January-to-March history is synthetic and exists only to test historical
comparison controls. A repeated numerical pattern is not evidence of a
business cause or a prediction of a later period.
