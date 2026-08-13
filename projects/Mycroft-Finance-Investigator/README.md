# Mycroft Finance Investigator

A runnable, local-first MVP for investigating monthly budget-versus-actual
performance. It validates a synthetic finance pack, computes a deterministic
EBITDA bridge, and runs a single observe-plan-act investigator that selects
evidence tools based on the material variances it encounters.

The application explains the **mathematical bridge**, not business causation.
Current-period causal commentary remains owner-required and blank until a named
human approves it.

## Weeks 1–6 implemented

- **Week 1:** synthetic SaaS finance data, machine-readable schemas, provenance,
  raw-to-verified validation, and reconciliation checks.
- **Week 2:** deterministic account/category variance engine, materiality flags,
  EBITDA bridge, source-row lineage, and unit tests.
- **Week 3:** one stateful investigator, conditional tool selection, evidence
  ledger, machine log, and human review report.
- **Week 4:** run-bound human review requests, evidence-backed approval rules,
  agent self-approval prevention, and append-only gate decisions.
- **Week 5:** isolated planted-discrepancy cases for reconciliation failures,
  step-limit enforcement, self-approval prevention, and baseline regression.
- **Week 6:** run-bound scenario sensitivities with explicit assumptions,
  source lineage, exact EBITDA comparisons, and no generated recommendation.

## Quick start

From the repository root:

```bash
cd projects/Mycroft-Finance-Investigator
python3 -m unittest discover -s tests -v
python3 -m mycroft_finance_investigator.cli all
```

The `all` command:

1. validates `data/raw/mycroft-finance-investigator/`;
2. writes normalized records and a validation audit to
   `data/verified/mycroft-finance-investigator/`;
3. runs the local investigator;
4. writes a structured run log under `logs/` and a review report under
   `reports/generated/`.

No network access, API key, database, or model download is required.

## Useful commands

```bash
python3 -m mycroft_finance_investigator.cli validate
python3 -m mycroft_finance_investigator.cli investigate
python3 -m mycroft_finance_investigator.cli all --run-id demo-2026-02
python3 -m mycroft_finance_investigator.cli review-request \
  --output ../../logs/gate-decisions/demo-2026-02-review-request.json
python3 -m mycroft_finance_investigator.cli evaluate \
  --output-log ../../logs/mycroft-finance-investigator-evaluation-week32.json \
  --output-report ../../reports/generated/mycroft-finance-investigator-evaluation-week32.md
python3 -m mycroft_finance_investigator.cli scenario \
  --output-log ../../logs/mycroft-finance-investigator-scenarios-week33.json \
  --output-report ../../reports/generated/mycroft-finance-investigator-scenarios-week33.md
```

After a named finance reviewer completes a copy of the review request, record
it without overwriting prior decisions:

```bash
python3 -m mycroft_finance_investigator.cli record-review \
  --decision /path/to/human-completed-review.json \
  --output ../../logs/gate-decisions/demo-2026-02-review.json
```

`APPROVE` requires an approved or replaced materiality threshold and at least
one causal explanation backed by evidence from the source run. An agent name,
an unknown evidence reference, or an existing output path is a hard stop.

The sample materiality amount is a test fixture, not an approved business
policy. Reports remain `PENDING_HUMAN_REVIEW`.

The evaluation command mutates temporary copies—not source data—and compares
seven named observations with explicit expected outcomes. A passing scorecard
is evidence that those cases behaved as specified; it is not model confidence,
production certification, or a substitute for human adequacy review.

The scenario command applies explicit sample assumptions to the verified actual
baseline. Percentage assumptions mean percentage of the category's verified
actual amount. Each output is labeled `SIMULATION_NOT_FORECAST`, carries its
baseline and plan evidence, makes no recommendation, and requires a human
decision.

## Amount convention

Revenue and cost inputs are stored as non-negative amounts. Category mapping
determines EBITDA direction: revenue increases have positive performance impact,
while cost increases have negative performance impact. This keeps source files
readable and makes the sign transformation explicit in the finance engine.

## Architecture

```text
raw CSVs + provenance
        |
        v
schema validation + control reconciliations
        |
        v
verified normalized CSVs + validation audit
        |
        v
deterministic finance engine
        |
        v
single investigator (observe -> plan -> tool -> evidence)
        |
        +--> isolated adversarial evaluation
        |
        +--> deterministic scenario sensitivities
        |
        +--> structured machine log
        +--> human review report
        +--> OPEN review request
                    |
                    v
           named human decision
                    |
                    v
           append-only gate artifact
```

See `MYCROFT.md` for the canonical recipe, conductor, report, and lifecycle
links.
