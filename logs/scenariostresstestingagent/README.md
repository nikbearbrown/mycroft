# Scenario Stress Testing Agent: how to run what was built (sample mode)

These are the checks and results for steps 1, 3 and 5 of `recipes/scenariostresstestingagent.md`, built 2026-10-25. Everything runs
on an invented corpus; **nothing calls Groq, Alpha Vantage or any other service**, and nothing is written outside this
recipe's own paths. Python 3.9+ standard library only; `node` is needed only for the parity check and the self-test's
parity-based breaks.

Run from the repository root, in this order:

| Step | Command | Expected |
|---|---|---|
| 1 verify provenance | `python3 scripts/tools/scenariostresstestingagent-verify-provenance.py` | exit 0: node table matches the workflow, connections match the wiring the port assumes, fixtures match their SHA-256 |
| 3 validate data shape | `python3 scripts/gigo/scenariostresstestingagent-validate-data-shape.py` | exit 0: 12 accepted |
| 3 on the defective set | `python3 scripts/gigo/scenariostresstestingagent-validate-data-shape.py --sample-dir data/raw/scenariostresstestingagent/sample/defective` | exit 1 **by design**: 10 of 10 rejected, each for its own reason (see `data/verified/scenariostresstestingagent/defective/validate-audit.md`) |
| 5 run approved tools | `python3 scripts/tools/scenariostresstestingagent-run-approved-tools.py` | exit 0: 11 stress-tested, 1 stopped at the Groq handoff |
| 5 on the defective set | `python3 scripts/tools/scenariostresstestingagent-run-approved-tools.py --sample-dir data/raw/scenariostresstestingagent/sample/defective --no-write` | exit 1: the tools refuse rejected data and write nothing |
| evidence: parity | `python3 scripts/tools/scenariostresstestingagent-parity-check.py` | exit 0: every node output identical to the original code, extracted from the workflow JSON at run time |
| evidence: self-test | `python3 scripts/tools/scenariostresstestingagent-self-test.py` | exit 0: every check as expected, including 12 deliberate breaks |

`--now <ISO time>` pins the timestamp (and the date in the log file name) for steps 1 and 5.

## What is in this folder

- `parity-results.json`: the per-request comparison with the original nodes (Validate Portfolio under node; Load_Template_Scenario, Save_Portfolio_Before_LLM and Stress_Test_Engine run as Python inside a small shim).
- `self-test-results.json` and `.md`: every check, what was expected, what was seen.
- Beside it, in `logs/`: `scenariostresstestingagent-provenance-2026-10-25.json` and `scenariostresstestingagent-run-approved-tools-2026-10-25.json`.

## Where the data is

- `data/raw/scenariostresstestingagent/sample/`: 12 clean and 10 defective requests, invented, with `manifest.json` (a SHA-256 per file, and a catalogue saying what each defect is and what the workflow does with it).
- `data/raw/scenariostresstestingagent/run-envelope.json`: declares sample mode.
- `data/verified/scenariostresstestingagent/{clean,defective}/`: the validator's `validated.json` and `validate-audit.md`; `clean/stress-results.json` from step 5.

## What is not covered

- Steps 2, 4 and 6, and the respond-to-webhook and human-report mappings, are still `[TODO: DEV]`.
- Parse_LLM_Response is not ported: it only runs after the Groq call. A request with a `custom_scenario` stops at that handoff.
- Live mode: no approval record exists; the Alpha Vantage request, the Groq call and the webhook reply are recorded as handoffs and never made.
- The finance in the engine is ported faithfully, not judged. Every portfolio in the corpus is invented.

## Later steps

This page describes steps 1, 3 and 5 as they were on 2026-10-25, so its "not covered" list above has since moved on. Steps 4 and 6 are in `README-steps-4-and-6.md` (2026-11-01, with a correction on 2026-11-02) and step 2, the last open `[TODO: DEV]`, in `README-step-2.md` (2026-11-09), with a transcript of all six steps run through the CLI in `full-sample-run-2026-11-09.md`.
