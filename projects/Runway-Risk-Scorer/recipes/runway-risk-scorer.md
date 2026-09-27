---
recipe: runway-risk-scorer
status: SPECIFIED
recipe_version: 0.1.0
domain: company-intelligence / financial-signals
last_gate: 2026-08-28
attestation: null
todos_open: 2
owner: amruta
---

# Runway-Risk Scorer

Reads a company's **validated** funding and financial signals and produces a
**sourced runway-risk brief**, then **halts at a human gate**. It computes the
inputs to a runway-risk judgment; a human makes the judgment (P1).

## Company universe
Private, venture-funded AI vendors — the companies whose survival depends on
raising capital, so "runway risk" is meaningful. (Public, profitable companies
are out of scope: they have no runway risk in this sense.)

## The five metrics (mechanical — no verdict)
1. **total_raised** — sum of validated funding_round values (USD), with provenance
2. **months_since_last_raise** — months from run date to most recent funding event
3. **funding_stage_trend** — ordered sequence of reported stages (progression / stall)
4. **distress_indicators** — count of layoff / security_issue / executive_change signals
5. **signal_freshness** — age of the most recent validated signal

Every number cites its `signal_id` and `source_url` (P3). Missing data is
reported as UNKNOWN, never guessed. Unvalidated signals are dropped (P2).

## Steps (standard 6-step skeleton)
1. Verify provenance — confirm signal source/period.
2. Ingest declared inputs — load validated signals (sample first).
3. Validate data shape — required fields present.
4. Transform + compute the five metrics.
5. Run approved tools — read-only; no external writes.
6. Produce human report + machine JSON (two customers, P5).

## The gate (P1 / P4)
The recipe stops after producing the brief. A named human decides whether the
runway risk is acceptable and logs it. The recipe never: declares a vendor
safe/risky, recommends signing/dropping, invents a figure (P3), or writes to
the verified layer without validation (P2).

## Open TODOs
- [ ] TODO(DEFINE): confirm distress signal_types list is complete for the domain
- [ ] TODO(DEV): trailing-window backfill for months_since_last_raise
- [ ] TODO(DEV): signal-velocity delta metric
- [ ] TODO(DEV): source-freshness / dead-URL audit
- [ ] TODO(TEST): 3–5 deliberate break tests

## Lifecycle
DRAFT → SPECIFIED → RUNNABLE-SAMPLE (committed ceiling) → RUNNABLE-LIVE → VERIFIED.
RUNNABLE-LIVE and VERIFIED require live data and independent attestation and are
out of scope for the initial contribution.

## Data sources
- **Sample (now):** schema-matched synthetic set at `data/samples/sample_signals.json`.
- **Live (later, out of scope):** News + EDGAR ingest pipelines. Note: private AI
  startups have thin EDGAR coverage, so most live signals would be
  news/funding-announcement data, scored for confidence accordingly.
