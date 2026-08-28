# runway-risk-scorer

A financial-signal recipe for the Mycroft system. It reads a company's
**validated** funding and financial signals and produces a **sourced
runway-risk brief**, then **halts at a human gate**. It computes the inputs to a
runway-risk judgment; a human makes the judgment. The tool never declares a
vendor "safe" or "risky" — that separation between mechanical work and human
judgment is the core design principle (Snickerdoodle P1).

## What it computes

Five mechanical metrics, each citing its source (P3):

1. **Total raised** — sum of validated funding rounds
2. **Months since last raise** — time since the most recent funding event
3. **Funding-stage trend** — reported stage progression, or a stall
4. **Distress indicators** — count of layoffs / security issues / exec departures
5. **Signal freshness** — age of the most recent validated signal

Missing data is reported as UNKNOWN, never guessed. Unvalidated signals are
dropped (P2). Deciding whether any level is "dangerous" is the reviewer's call,
made at the human gate.

## Run it

```bash
# human-readable briefs for all companies
python scripts/runway_risk_score.py data/samples/sample_signals.json

# one company
python scripts/runway_risk_score.py data/samples/sample_signals.json --company harbor-ai

# also print machine-readable JSON
python scripts/runway_risk_score.py data/samples/sample_signals.json --json

# write one JSON file per company into reports/
python scripts/runway_risk_score.py data/samples/sample_signals.json --json-out reports
```

Each run prints a sourced brief per company and halts at the human gate. It
never issues a verdict.

## How it works (step skeleton)

```
STEP 1  ingest          load the signals file
STEP 2  validate_shape  drop malformed signals; drop unvalidated ones (P2)
STEP 3  score           compute the five metrics with provenance
STEP 4  report          human brief (customer 1) + machine JSON (customer 2, P5)
GATE    halt            never a verdict; a human decides (P1/P4)
```

## Layout

- `recipes/` — the recipe spec (frontmatter, steps, gate)
- `scripts/` — the runway scorer
- `data/samples/` — schema-matched synthetic signals (safe, offline)
- `data/verified/` — schema reference (real schema lives upstream)
- `logs/RUN_LOG.md` — dated run history (lifecycle evidence)
- `reports/` — generated briefs / JSON

## Current status

**Recipe lifecycle: SPECIFIED** (runs end-to-end on sample data; run logged).
Committed ceiling for this project is **RUNNABLE-SAMPLE**. VERIFIED is out of
scope — it needs live data and independent attestation.

## 5-week plan

| Week | Focus | Status |
|------|-------|--------|
| 1 | **Proposal & prototype.** Scope the scorer against the schema; build the prototype computing the five metrics with provenance; drop unvalidated signals; halt at the gate; run against a sample set. | Done |
| 2 | **Core pipeline to sample.** Split into named step scripts (ingest / validate-shape / score); add machine-readable JSON output; log a run. DRAFT → SPECIFIED. | Done |
| 3 | **Rigor metrics.** Add trailing-window backfill and signal-velocity delta. Commit a pre-registered validation note *before* re-running. | Planned |
| 4 | **Audit & RUNNABLE-SAMPLE.** Write a source-freshness audit; add 3–5 deliberate break tests; full sample run + conformance pass. SPECIFIED → RUNNABLE-SAMPLE. | Planned |
| 5 | **Attestation & PR.** Write the attestation record (Tested / Did-not-test / Broke-and-fixed); open a pull request into the upstream Mycroft repo. | Planned |

## Scope and honest limits

- **Company universe:** private, venture-funded AI vendors — the companies for
  which "runway risk" is meaningful.
- **A first-pass filter, not a financial model.** The metrics are a rough runway
  proxy. That roughness is why a human gate exists instead of an automated verdict.
- **Data:** sample runs use schema-matched synthetic data. A live version would
  draw on News and EDGAR ingest, with the caveat that private startups have thin
  EDGAR coverage, so most live signals would be news/funding data scored for
  confidence.

## Relationship to upstream Mycroft

Developed as a contribution to the Mycroft project. The upstream repo is
all-rights-reserved; this repo references its schema and governance rather than
redistributing them. Intended delivery is **fork + pull request** into the
upstream repo. See `GOVERNANCE.md`.