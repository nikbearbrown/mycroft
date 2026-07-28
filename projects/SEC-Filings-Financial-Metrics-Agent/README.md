# SEC Filings Financial Metrics Agent

**Fellow:** Asavari (Ash) Shejwal · **Status:** Phase 1 (DRAFT → SPECIFIED)

Fellow contribution to the Mycroft finance portfolio. An open-source system that
retrieves SEC EDGAR filings, extracts standardized XBRL financial metrics,
validates and normalizes the data, and turns complex regulatory disclosures into
transparent, inspectable financial intelligence.

The guiding idea: **establish confidence in the underlying financial data before
any higher-level analysis takes place.** Success is measured not by predicting
markets but by reducing the effort required for students, researchers,
journalists, and individual investors to understand public disclosures — while
keeping every number traceable, reproducible, and explainable.

## What's here

- **Recipe:** [`recipes/sec-filings-financial-metrics.yaml`](../../recipes/sec-filings-financial-metrics.yaml) (DRAFT)
- **Code:** [`scripts/sec-filings-financial-metrics/`](../../scripts/sec-filings-financial-metrics/) — deterministic extractor, derived metrics, validation, and report generator (no LLM in the critical path)
- **`substack-drafts/`** — engineering-narrative write-ups of the design decisions
- **`benchmarks/golden_set.csv`** — hand-verified ground-truth stub for scoring extraction accuracy

## Delivered so far

- EDGAR XBRL client with provenance-preserving caching.
- Canonical-metric ↔ `us-gaap` tag mapping that records which tag matched every value (and flags custom extensions instead of guessing).
- Derived ratios per fiscal year: margins, ROE, ROA, current ratio, debt-to-equity, YoY growth — keyed by period-end date so 10-K comparative years are not mis-assigned.
- Rule-based validation returning PASS / FAIL / UNKNOWN (accounting identity + margin bounds implemented).
- Verified against Microsoft (FY2020–2025): correct revenue/net income; balance sheet balances to the dollar.

## Roadmap

1. Deepen validation — unit consistency, restatement dedupe, cross-statement sum checks.
2. Score extraction accuracy + coverage against `benchmarks/golden_set.csv` (include a company with a custom XBRL extension).
3. Document limitations and edge cases (`LIMITATIONS.md`).
4. Promote the recipe through the lifecycle (DRAFT → SPECIFIED → RUNNABLE-SAMPLE) with an offline sample mode and gate decisions logged.
