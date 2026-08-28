---
status: DRAFT
todos_open: 2
last_gate: null
attestation: null
recipe_version: 0.1.0
---

# Mycroft Finance Investigator

## Purpose

Turn approved monthly budget, actual, ledger, and operational-driver files into
a reconciled EBITDA bridge and evidence-linked investigation work surface. The
recipe computes and investigates; a named finance human owns materiality,
causal explanation, adequacy, and distribution.

## Required Reads

- `SNICKERDOODLE.md`
- `DATA_CONTRACT.md`
- `chapters/06-monthly-variance-pack.md`
- `projects/Mycroft-Finance-Investigator/MYCROFT.md`
- `data/raw/mycroft-finance-investigator/README.md`

## Inputs

| Input | Type | Source | Required |
|---|---|---|---|
| Provenance | JSON | Approved local sample or finance owner | Yes |
| Account mapping | CSV | Current-period finance mapping | Yes |
| Budget | CSV | Approved budget version | Yes |
| Actuals | CSV | Approved close output | Yes |
| Ledger | CSV | Approved GL detail | Yes |
| Customer drivers | CSV | Approved operational system | Yes for sample |
| Headcount drivers | CSV | Approved workforce system | Yes for sample |
| Materiality | Decimal amount | Named finance owner | Yes |

## Phase Gates

1. **Provenance gate — [TO].** Source classification, origin, period, entity,
   and permitted use must be explicit. Failure: stop before validation.
2. **Input conformance gate — [PA].** Required fields, unique keys, decimal
   amounts, categories, period, and entity must conform. Failure: reject the
   pack; do not repair silently.
3. **Reconciliation gate — [PA].** Actuals must tie to ledger by account;
   customer revenue must tie to revenue; headcount cost must tie to payroll;
   all accounts must be mapped. Failure: stop before variance calculations.
4. **Materiality gate — [IJ].** `[TODO: DEFINE]` A named finance owner must set
   the production dollar and percentage thresholds with reasoning. The included
   amount is demo-only.
5. **Evidence boundary gate — [IJ].** Every number must trace to a deterministic
   calculation and source reference. Operational driver records may prompt
   investigation but may not become causal explanations.
6. **Human release gate — [EI].** `[TODO: APPROVE]` A named finance reviewer
   must supply or approve causal explanations and record a distribution
   decision.

## Workflow

1. Validate provenance, schemas, keys, scope, mapping coverage, and control
   totals.
2. Write normalized records and a deterministic validation audit to the
   verified layer.
3. Calculate account and category variances using `actual - budget`.
4. Calculate each category's EBITDA performance impact and reconcile the
   impacts to total EBITDA variance.
5. Start the investigator with the human-provided question and threshold.
6. Let the investigator select category and driver tools based on observed
   material variances.
7. Produce a structured machine log and a separate human review report.
8. Run the committed baseline and adversarial control cases in isolated copies;
   fail if any observed result differs from its explicit expectation.
9. Apply explicit, unapproved exercise assumptions to the verified baseline;
   emit arithmetic sensitivities with lineage and no recommendation.
10. Validate the complete cross-artifact chain and package an immutable audit
    bundle containing data, specifications, implementation, tests, logs, and
    human-readable views.
11. Recompute the manifest, review-view, and packaged-artifact checksums before
    handoff.
12. Compare ordered historical runs only after verifying each run, scope, and
    source hash; report EBITDA movement and recurring material categories
    without causation, forecast, or recommendation.
13. Produce a run-bound review request with causal commentary blank and the
   human gate open.
14. Accept only a named human decision whose causal claims cite evidence from
   that exact run; record it as an append-only gate artifact.

## Implementation Map

| Responsibility | Implementation |
|---|---|
| Schema and control validation | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/validation.py` |
| Finance calculations | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/finance.py` |
| Observe-plan-act investigator | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/agent.py` |
| Human review gate | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/review.py` |
| Adversarial evaluation | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/evaluation.py` |
| Scenario sensitivities | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/scenario.py` |
| Audit-bundle handoff | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/bundle.py` |
| Historical comparison | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/trend.py` |
| Log and report rendering | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/reporting.py` |
| Local orchestration | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/cli.py` |
| Conformance and behavior tests | `projects/Mycroft-Finance-Investigator/tests/` |

## Output Contract

### Agent Log

Path: `logs/mycroft-finance-investigator-[RUN_ID].json`

Required fields: workflow, run ID, recipe version, mode, config, source hashes,
row counts, reconciliation observations, investigator policy, tool trace,
findings, evidence index, open human gate, and output status.

### Human Report

Path: `reports/generated/mycroft-finance-investigator-[RUN_ID].md`

Reader: FP&A analyst, finance manager, or controller.

Decision enabled: approve or replace materiality; provide evidence-backed
current-period explanations; approve, request changes, or block distribution.

Required sections: review status, question, verified mathematical findings,
investigation prompts, intentionally blank current explanation, evidence index,
agent trace, human decision, and did-not-test disclosures.

### Evaluation Scorecard

Paths: `logs/mycroft-finance-investigator-evaluation-[RUN_ID].json` and
`reports/generated/mycroft-finance-investigator-evaluation-[RUN_ID].md`.

Required fields: case specification hash, raw-source hashes, expected and
observed behavior per case, exact differences, aggregate matched/unexpected
counts, and a visible `PENDING_HUMAN_REVIEW` adequacy boundary.

### Scenario Decision Pack

Paths: `logs/mycroft-finance-investigator-scenarios-[RUN_ID].json` and
`reports/generated/mycroft-finance-investigator-scenarios-[RUN_ID].md`.

Required fields: exact baseline-run hash, scenario-plan hash, verified baseline
category amounts, assumption method/value/reasoning/source, calculation and
plan evidence, resulting EBITDA, `SIMULATION_NOT_FORECAST`, null
recommendation, and `HUMAN_REQUIRED` decision.

### Audit Bundle

Path: `reports/generated/mycroft-finance-investigator-audit-[RUN_ID]/`.

Required files: `manifest.json`, `manifest.sha256`, `REVIEW.md`, and the
`artifacts/` inventory. The manifest records original and bundled paths, byte
counts, and SHA-256 hashes. The review view must disclose that checksums are not
signatures, list every open human gate, and report
`BLOCKED_PENDING_HUMAN_REVIEW` while any gate remains open.

### Historical Comparison

Paths: `logs/mycroft-finance-investigator-trend-[RUN_ID].json` and
`reports/generated/mycroft-finance-investigator-trend-[RUN_ID].md`.

Required fields: ordered source periods and run IDs, exact run-log and verified
source hashes, per-period budget/actual/variance EBITDA, change from the prior
period, category impacts and recurrence counts,
`HISTORICAL_COMPARISON_NOT_FORECAST`, null causal explanation, forecast, and
recommendation, plus an open human gate.

## Stop Conditions

- Stop if provenance is missing or ambiguous.
- Stop if any required field is blank or malformed.
- Stop if the finance pack contains multiple periods or entities.
- Stop if an account is unmapped.
- Stop if actuals do not reconcile to ledger.
- Stop if driver control totals do not reconcile.
- Stop if the investigator exceeds its configured step limit.
- Stop if an evaluation case produces an unexpected result.
- Stop before treating an evaluation pass as confidence or production approval.
- Stop if a scenario plan does not bind to the exact baseline run.
- Stop if a category has duplicate assumptions or would become negative.
- Stop before presenting a sensitivity as a forecast, probability,
  recommendation, or approved plan.
- Stop if validation, review, evaluation, scenario, raw-data, or verified-data
  hashes do not form one consistent evidence chain.
- Stop rather than overwrite an existing audit bundle.
- Stop if a packaged manifest, review view, artifact size, or artifact hash
  changes after packaging.
- Stop before presenting a checksum as a human signature or attestation.
- Stop if historical periods are duplicated, unordered, or do not match their
  source-run entity and period.
- Stop if a verified historical source hash or recomputed EBITDA differs from
  its source run.
- Stop before treating recurrence as causation, forecast, or recommendation.
- Stop if a reviewer is unnamed or identifies as an agent.
- Stop if a causal explanation cites evidence absent from the source run.
- Stop if an approval lacks an accepted materiality decision or an
  evidence-backed causal explanation.
- Stop rather than overwrite a recorded review decision.
- Stop before presenting an operational driver as a causal explanation.
- Stop before distribution without a named human decision.
- Never post or propose a journal entry.

## Small-Run Command

```bash
cd projects/Mycroft-Finance-Investigator
python3 -m unittest discover -s tests -v
python3 -m mycroft_finance_investigator.cli all --run-id sample-2026-02
python3 -m mycroft_finance_investigator.cli evaluate \
  --output-log ../../logs/mycroft-finance-investigator-evaluation-week32.json \
  --output-report ../../reports/generated/mycroft-finance-investigator-evaluation-week32.md
python3 -m mycroft_finance_investigator.cli scenario \
  --output-log ../../logs/mycroft-finance-investigator-scenarios-week33.json \
  --output-report ../../reports/generated/mycroft-finance-investigator-scenarios-week33.md
python3 -m mycroft_finance_investigator.cli bundle \
  --bundle-id mycroft-finance-investigator-week34 \
  --output-dir ../../reports/generated/mycroft-finance-investigator-audit-week34
python3 -m mycroft_finance_investigator.cli verify-bundle \
  --bundle-dir ../../reports/generated/mycroft-finance-investigator-audit-week34
python3 -m mycroft_finance_investigator.cli trend \
  --output-log ../../logs/mycroft-finance-investigator-trend-week35.json \
  --output-report ../../reports/generated/mycroft-finance-investigator-trend-week35.md
```

Do not promote this recipe from `DRAFT` until both TODOs have the evidence
required by `SNICKERDOODLE.md`.

## Provenance

Designed and implemented as a local synthetic sample in Mycroft on 2026-07-26.
