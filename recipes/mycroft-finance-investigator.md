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
8. Produce a run-bound review request with causal commentary blank and the
   human gate open.
9. Accept only a named human decision whose causal claims cite evidence from
   that exact run; record it as an append-only gate artifact.

## Implementation Map

| Responsibility | Implementation |
|---|---|
| Schema and control validation | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/validation.py` |
| Finance calculations | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/finance.py` |
| Observe-plan-act investigator | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/agent.py` |
| Human review gate | `projects/Mycroft-Finance-Investigator/mycroft_finance_investigator/review.py` |
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

## Stop Conditions

- Stop if provenance is missing or ambiguous.
- Stop if any required field is blank or malformed.
- Stop if the finance pack contains multiple periods or entities.
- Stop if an account is unmapped.
- Stop if actuals do not reconcile to ledger.
- Stop if driver control totals do not reconcile.
- Stop if the investigator exceeds its configured step limit.
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
```

Do not promote this recipe from `DRAFT` until both TODOs have the evidence
required by `SNICKERDOODLE.md`.

## Provenance

Designed and implemented as a local synthetic sample in Mycroft on 2026-07-26.
