# Scenario Stress Testing Agent: sample run `defective`, 2026-11-01

**Reader:** the domain lead or human boss responsible for accepting the `ScenarioStressTestingAgent` run.  
**Decision enabled:** approve the run for the next phase, request source or schema fixes, or block live execution.

## Run summary

- 10 request(s) read from the `defective` sample folder; 0 accepted at step 3, 10 rejected there.
- 0 stress-tested at step 5, 0 stopped at the Groq handoff; 0 reconciled on every step-4 check, 0 failed one, 0 duplicate group(s), 0 advisory flag(s).
- Stop conditions: 0 of 4 triggered; each is judged from evidence in the agent log.
- Mode **sample**: every request is invented; no Groq call, Alpha Vantage request, webhook reply, database write or credential was used.

## Purpose

ScenarioStressTestingAgent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to scenariostresstestingagent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source inventory

| Source | What it is | Where |
|---|---|---|
| the recipe | intent, steps, contracts (status `DRAFT`, version 0.3.1) | `recipes/scenariostresstestingagent.md` |
| sample corpus | 10 invented requests in `defective/` with a SHA-256 manifest | `data/raw/scenariostresstestingagent/sample/defective/` |
| run envelope | declares sample mode and that nothing live runs | `data/raw/scenariostresstestingagent/run-envelope.json` |
| the original workflow | the n8n workflow the recipe was converted from (read by step 1 only) | named in the recipe's Inputs and Provenance |

## Inputs used

- Step 3: `data/verified/scenariostresstestingagent/defective/validated.json`
- Step 5: no stress results for this folder (nothing was accepted)
- Step 4: `data/verified/scenariostresstestingagent/defective/quality-check.json`
- Step 1 log: `logs/scenariostresstestingagent-provenance-2026-10-25.json`
- Step 5 log: `logs/scenariostresstestingagent-run-approved-tools-2026-10-25.json`

## Phase-gate results

| Gate | Result | Evidence |
|---|---|---|
| 1 Source gate | PASS | the recipe and the sample folder `data/raw/scenariostresstestingagent/sample/defective/` exist; the sources are the invented sample corpus |
| 2 Scope gate | PASS | `run-envelope.json` parses and declares mode `sample`, live_calls False, network False, database_writes False |
| 3 Data-shape gate | PASS | 29 JSON file(s) under the raw and verified folders parse |
| 4 Script-readiness gate | PASS | 5 of 6 step scripts exist; step(s) 2 still carry a typed `[TODO: DEV]` |
| 5 Approval gate | NOT NEEDED (sample mode) | no live call, external write or credential was requested; the approval record `logs/gate-decisions/scenariostresstestingagent-approval.json` does not exist, so live execution stays blocked |
| 6 Report gate | PASS | the agent log has its 16 required fields and the report its 15 sections |

## Steps completed

| Step | Name | Status | Script |
|---|---|---|---|
| 1 | Verify provenance | closed | `scripts/tools/scenariostresstestingagent-verify-provenance.py` |
| 2 | Ingest declared inputs | OPEN (`[TODO: DEV]`) | `scripts/ingest/scenariostresstestingagent-ingest-inputs.py` |
| 3 | Validate data shape | closed | `scripts/gigo/scenariostresstestingagent-validate-data-shape.py` |
| 4 | Transform and quality check | closed | `scripts/gigo/scenariostresstestingagent-transform-quality-check.py` |
| 5 | Run approved tools | closed | `scripts/tools/scenariostresstestingagent-run-approved-tools.py` |
| 6 | Produce human report | closed | `scripts/tools/scenariostresstestingagent-produce-human-report.py` |

## Records seen

- Requests in: 10. Accepted: 0. Stress-tested: 0. Handed off, not run: 0.
- Risk levels over the 0 stress-tested requests: CRITICAL 0, HIGH 0, MODERATE 0, LOW 0.

## Rejects

- `d01-portfolio-missing` at step 3: Portfolio must have holdings array (the node's own rule)
- `d02-holdings-missing` at step 3: Portfolio must have holdings array (the node's own rule)
- `d03-holding-without-ticker` at step 3: Each holding must have a ticker (the node's own rule)
- `d04-holdings-is-an-object` at step 3: portfolio.holdings is not iterable (the node's own rule); holdings is a dict, not an array (gate addition)
- `d05-weight-is-a-string` at step 3: holding 0 (NVDA) has a weight that is not a number ('0.5'): JavaScript would join it as text (gate addition)
- `d06-all-weights-zero` at step 3: weights total 0.0: rescaling by a zero total gives NaN weights (gate addition)
- `d07-negative-weight` at step 3: holding 1 (AMD) has a negative weight (-0.3): the engine would treat it as a short position without saying so (gate addition)
- `d08-unknown-scenario-type` at step 3: scenario_type 'meltdown' is not one of ['ai_regulation', 'black_swan', 'chip_shortage', 'rate_hike', 'tech_crash']: the workflow would silently run tech_crash (gate addition)
- `d09-empty-holdings` at step 3: holdings is empty: nothing to stress-test (gate addition)
- `d10-weight-missing` at step 3: holding 1 (AMD) has no weight: the node counts it as 0 and the engine then fails on it (gate addition)

## Duplicates

- none found, by id or by content

## Flags

- none

## Typed TODOs

- Step 2 (Ingest declared inputs): `[TODO: DEV]` scripts/ingest/scenariostresstestingagent-ingest-inputs.py
- Script mapping: `scripts/tools/scenariostresstestingagent-respond-to-webhook.py`
- Script mapping: `scripts/tools/scenariostresstestingagent-produce-human-report.py`

## Human approvals

- None recorded. No approval record exists at `logs/gate-decisions/scenariostresstestingagent-approval.json`, so nothing live is approved, and a named human has not yet cleared the sample run for the next phase.

## Verified findings

- No request was accepted, so no stress result exists to verify.
- Step 1's log: node table match True, workflow wiring match True, ported nodes ok True, fixtures ok True.
- 10 of 10 requests were rejected at step 3 with a reason each; none reached the stress-test chain.

## Inferred findings

- These are readings of an invented sample, not claims about real portfolios and not a judgment of the template shocks or risk lines.
- Nothing ran, so there is nothing to read.

## Decision recommendation

- **Approve for the next phase (sample mode only): NO.** This folder holds requests the gate rejects on purpose; nothing ran, so there is nothing to approve.
- **Request source or schema fixes: YES.** 10 reject(s), 0 failed check(s), 0 duplicate group(s) are listed above.
- **Block live execution: YES.** No approval record exists; step 2 (ingest) is still open, the Alpha Vantage request, the Groq call and the webhook reply are only recorded handoffs, and the custom-scenario route stops at the handoff.
