# Scenario Stress Testing Agent: sample run `clean`, 2026-11-01

**Reader:** the domain lead or human boss responsible for accepting the `ScenarioStressTestingAgent` run.  
**Decision enabled:** approve the run for the next phase, request source or schema fixes, or block live execution.

## Run summary

- 12 request(s) read from the `clean` sample folder; 12 accepted at step 3, 0 rejected there.
- 11 stress-tested at step 5, 1 stopped at the Groq handoff; 11 reconciled on every step-4 check, 0 failed one, 0 duplicate group(s), 11 advisory flag(s).
- Stop conditions: 0 of 4 triggered; each is judged from evidence in the agent log.
- Mode **sample**: every request is invented; no Groq call, Alpha Vantage request, webhook reply, database write or credential was used.

## Purpose

ScenarioStressTestingAgent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to scenariostresstestingagent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source inventory

| Source | What it is | Where |
|---|---|---|
| the recipe | intent, steps, contracts (status `DRAFT`, version 0.3.1) | `recipes/scenariostresstestingagent.md` |
| sample corpus | 12 invented requests in `clean/` with a SHA-256 manifest | `data/raw/scenariostresstestingagent/sample/clean/` |
| run envelope | declares sample mode and that nothing live runs | `data/raw/scenariostresstestingagent/run-envelope.json` |
| the original workflow | the n8n workflow the recipe was converted from (read by step 1 only) | named in the recipe's Inputs and Provenance |

## Inputs used

- Step 3: `data/verified/scenariostresstestingagent/clean/validated.json`
- Step 5: `data/verified/scenariostresstestingagent/clean/stress-results.json`
- Step 4: `data/verified/scenariostresstestingagent/clean/quality-check.json`
- Step 1 log: `logs/scenariostresstestingagent-provenance-2026-10-25.json`
- Step 5 log: `logs/scenariostresstestingagent-run-approved-tools-2026-10-25.json`

## Phase-gate results

| Gate | Result | Evidence |
|---|---|---|
| 1 Source gate | PASS | the recipe and the sample folder `data/raw/scenariostresstestingagent/sample/clean/` exist; the sources are the invented sample corpus |
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

- Requests in: 12. Accepted: 12. Stress-tested: 11. Handed off, not run: 1.
- Risk levels over the 11 stress-tested requests: CRITICAL 7, HIGH 1, MODERATE 1, LOW 2.

## Rejects

- none

## Duplicates

- none found, by id or by content

## Flags

- `c02-rate-hike-mixed-book` **default-sector**: 50% of the book is in tickers the workflow's sector map does not list, so it gets the default tech_sector shock
- `c03-ai-regulation-outside-the-map` **default-sector**: 100% of the book is in tickers the workflow's sector map does not list, so it gets the default tech_sector shock
- `c04-chip-shortage-mostly-unmapped` **default-sector**: 90% of the book is in tickers the workflow's sector map does not list, so it gets the default tech_sector shock
- `c05-black-swan-two-names` **default-sector**: 100% of the book is in tickers the workflow's sector map does not list, so it gets the default tech_sector shock
- `c06-weights-sum-to-six-tenths` **rescaled**: the request's weights add to 0.6; the workflow rescaled them to 1.0
- `c07-weights-within-tolerance` **majority-holding**: OMNI is 50.5% of the book after rescaling, more than half
- `c07-weights-within-tolerance` **default-sector**: 50% of the book is in tickers the workflow's sector map does not list, so it gets the default tech_sector shock
- `c08-weights-sum-to-one-point-two` **rescaled**: the request's weights add to 1.2; the workflow rescaled them to 1.0
- `c09-scenario-type-absent` **scenario-defaulted**: no scenario_type in the request; the workflow runs the default, tech_crash
- `c10-custom-scenario-needs-the-llm` **handoff**: Groq chat call needed for a custom scenario: not approved, not made
- `c11-exactly-ten-percent` **on-threshold**: drawdown -10.0% sits within 0.05 points of the 10% line; the rule is 'above', so the level is LOW

## Typed TODOs

- Step 2 (Ingest declared inputs): `[TODO: DEV]` scripts/ingest/scenariostresstestingagent-ingest-inputs.py
- Script mapping: `scripts/tools/scenariostresstestingagent-respond-to-webhook.py`
- Script mapping: `scripts/tools/scenariostresstestingagent-produce-human-report.py`

## Human approvals

- None recorded. No approval record exists at `logs/gate-decisions/scenariostresstestingagent-approval.json`, so nothing live is approved, and a named human has not yet cleared the sample run for the next phase.

## Verified findings

- 11 of 11 stress results reconcile on all 14 step-4 checks: each position's shock re-derived from the workflow's own template shocks, losses and totals added up, drawdown and risk level re-derived, ordering and weights checked (`data/verified/scenariostresstestingagent/clean/quality-check.json`).
- Largest drawdown: `c01-tech-crash-semiconductor-heavy`, -78.0% under Tech Sector Crash (CRITICAL). Smallest: `c03-ai-regulation-outside-the-map`, -5.0% (LOW).
- The step-5 log's risk-level counts {'CRITICAL': 7, 'HIGH': 1, 'MODERATE': 1, 'LOW': 2} match the counts recomputed here from the results.
- Step 1's log: node table match True, workflow wiring match True, ported nodes ok True, fixtures ok True.

## Inferred findings

- These are readings of an invented sample, not claims about real portfolios and not a judgment of the template shocks or risk lines.
- Average drawdown by scenario in this sample (n in brackets): AI Regulation Announcement -5.0% (1); Aggressive Rate Hike -20.42% (3); Black Swan Event -35.0% (1); Semiconductor Supply Shock -31.07% (2); Tech Sector Crash -63.46% (4).
- 8 of 11 results sit within 5 points of a risk line (`c02-rate-hike-mixed-book`, `c03-ai-regulation-outside-the-map`, `c04-chip-shortage-mostly-unmapped`, `c05-black-swan-two-names`, `c07-weights-within-tolerance`, `c09-scenario-type-absent`, `c11-exactly-ten-percent`, `c12-growth-stack-rate-hike`); a small change in the shocks would move their level, so those levels should be read as soft.

## Decision recommendation

- **Approve for the next phase (sample mode only): YES.** Every accepted request reconciled, no duplicates, nothing rejected; the next phase is still a sample run, and a named human has to clear it.
- **Request source or schema fixes: NO.** None needed for the sample corpus.
- **Block live execution: YES.** No approval record exists; step 2 (ingest) is still open, the Alpha Vantage request, the Groq call and the webhook reply are only recorded handoffs, and the custom-scenario route stops at the handoff.
