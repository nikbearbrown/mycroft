# Mycroft Finance Investigator

A runnable, local-first MVP for investigating monthly budget-versus-actual
performance. It validates a synthetic finance pack, computes a deterministic
EBITDA bridge, and runs a single observe-plan-act investigator that selects
evidence tools based on the material variances it encounters.

The application explains the **mathematical bridge**, not business causation.
Current-period causal commentary remains owner-required and blank until a named
human approves it.

## Weeks 1–10 implemented

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
- **Week 7:** immutable audit bundles that verify cross-artifact lineage and
  package data, specifications, implementation, tests, logs, and human views.
- **Week 8:** hash-verified comparison of three monthly investigations,
  month-over-month EBITDA movement, recurring material variance detection, and
  separate machine and human-review trend reports.
- **Week 9:** a constrained supervisor that verifies the source chain, ranks
  recurring evidence gaps, delegates them to scoped finance specialists, and
  records every handoff without generating causal conclusions.
- **Week 10:** an exact specialist replay and review-follow-up loop that
  classifies evidence as verified, unsupported, or open and writes an
  append-only closure pack without pretending a synthetic exercise is approval.

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
python3 -m mycroft_finance_investigator.cli trend \
  --output-log ../../logs/mycroft-finance-investigator-trend-week35.json \
  --output-report ../../reports/generated/mycroft-finance-investigator-trend-week35.md
python3 -m mycroft_finance_investigator.cli orchestrate \
  --output-log ../../logs/mycroft-finance-investigator-routing-week36.json \
  --output-report ../../reports/generated/mycroft-finance-investigator-routing-week36.md
python3 -m mycroft_finance_investigator.cli follow-up \
  --output-log ../../logs/mycroft-finance-investigator-follow-up-week37.json \
  --output-report ../../reports/generated/mycroft-finance-investigator-follow-up-week37.md
python3 -m mycroft_finance_investigator.cli bundle \
  --bundle-id mycroft-finance-investigator-week34 \
  --output-dir ../../reports/generated/mycroft-finance-investigator-audit-week34
python3 -m mycroft_finance_investigator.cli verify-bundle \
  --bundle-dir ../../reports/generated/mycroft-finance-investigator-audit-week34
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

The bundle command is the reviewer handoff. Before writing anything, it checks
that the validation result equals the baseline run, the open review request is
bound to that run's SHA-256, all seven evaluation expectations matched, and the
scenario plan, verified files, and baseline hashes agree. It then packages 54
source, code, test, machine, and human artifacts with an integrity manifest.
Existing bundle directories are never overwritten. `verify-bundle` detects a
changed manifest, human view, or packaged artifact.

The checksum is deliberately not called a signature. It establishes file
integrity only; materiality, causation, test adequacy, scenario judgment, and
distribution remain open human decisions.

The trend command compares January, February, and March synthetic investigation
runs. It recomputes every period from verified files, checks each file against
the source-run hashes, and reports historical EBITDA movement and categories
that were materially adverse in at least two periods. Its output is labeled
`HISTORICAL_COMPARISON_NOT_FORECAST`; causal explanation, forecast,
recommendation, and distribution approval remain unset.

The orchestration command turns recurring categories into a prioritized
evidence-gap queue. A lineage specialist runs first; revenue, cost, and
workforce specialists have fixed category scopes and collect only deterministic
calculations or correlated records. A delegation limit is a hard stop, every
specialist result has a stable fingerprint, and all causal or approval work
remains with a human.

The follow-up command binds a synthetic review exercise to the exact Week 36
orchestration hash, verifies the routing plan and trend hashes, and replays all
specialist results. It can verify an unchanged evidence set, reject a causal
claim when only calculation or correlated records are cited, or keep a request
open when a required source is absent. Outputs are append-only and remain
`BLOCKED_PENDING_HUMAN_REVIEW`.

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
        +--> immutable audit bundle + integrity verification
        |
        +--> hash-verified multi-month trend comparison
        |
        +--> supervisor -> scoped evidence specialists
        |                         |
        |                         v
        +<-- exact replay + review-driven follow-up
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
