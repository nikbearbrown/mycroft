# Two-Week Progress Report — SEC Filings Financial Metrics Agent

**Fellow:** Asavari (Ash) Shejwal
**Program:** Humanitarians AI — Mycroft portfolio
**Period:** July 8 – July 24, 2026

---

## Summary

Over the past two weeks I took the **SEC Filings Financial Metrics Agent** from a
written proposal to a **working, verified, and properly-shipped Mycroft
contribution**. The tool retrieves SEC EDGAR filings, extracts standardized
financial metrics from XBRL data with full provenance, and validates them with
deterministic, rule-based checks — **no LLM in the critical path**. It is verified
against real filings (Microsoft FY2020–2025 and Apple FY2024) and runs fully
offline from a bundled sample. This work moved the recipe from **DRAFT →
SPECIFIED** (`recipe_version 0.2.0`, `todos_open: 0`).

---

## What I completed

### Week 1 (Jul 8–14) — scoping, research, architecture
- Authored the project proposal/vision defining objective, success criteria, and the "trust the data before you reason over it" thesis.
- Studied the Mycroft repo (governance model, recipe/conductor lifecycle, existing SEC pipeline) and the Mycroft Substack to identify the contribution gap.
- Set an engineering-first roadmap centered on the XBRL **concept-normalization** problem; chose deterministic extraction + rule-based validation over LLM automation.

### Week 2 (Jul 15–24) — build, validate, benchmark, ship, document
- **Extractor:** EDGAR client (ticker→CIK, `companyfacts`) with provenance-preserving caching; canonical-metric → `us-gaap` tag mapping that records which tag matched and flags unmapped metrics as `MISSING` (never guessed).
- **Derived metrics + report:** margins, ROE, ROA, current ratio, debt-to-equity, YoY growth per fiscal year, plus a human-readable Markdown report with a provenance appendix.
- **Validation:** six rule-based checks returning **PASS / FAIL / UNKNOWN** — accounting identity, margin bounds, cross-statement sum consistency, current-ratio sanity, unit consistency, and restatement flagging.
- **Benchmark harness:** scores extraction accuracy and coverage against a hand-verified golden set.
- **Offline `--sample` mode:** runs the full pipeline from a bundled fixture with zero network calls.
- **Custom-extension mapping:** a human-curated override map so company-specific XBRL labels can be resolved explicitly (still `MISSING`, never guessed, when unmapped).
- **Shipped as a Mycroft contribution:** DRAFT→SPECIFIED recipe, documented scripts package, `DATA_CONTRACT.md` registration, and two `RUN_LOG.md` entries — on a feature branch in my fork, ready for PR.
- **Fellowship video:** a Brutalist-style slide deck + narration script explaining the contribution.

---

## Engineering highlights

- **Concept normalization (the core problem):** "Net Sales" vs "Revenue from Contracts with Customers" vs company-specific tags — resolved deterministically with the matched tag recorded for every value.
- **Two fiscal-period bugs caught by verification, not assumption:** (1) grouping by the filing's `fy` field silently shifted every figure two years off — fixed by keying on period-end date; (2) a Q4-vs-full-year collision in restatement detection — fixed by keying on period start+end. Both found by sanity-checking against known values.
- **Uncertainty made explicit:** `UNKNOWN` is a first-class validation result, so the system surfaces what it can't judge instead of manufacturing confidence.

---

## Verification

| Check | Result |
|---|---|
| Golden-set benchmark (MSFT FY2023–25 + AAPL FY2024) | **8/8 match** within 0.5% |
| Accounting identity (Assets = Liabilities + Equity) | Balances **to the dollar** where data is complete |
| Validation run (Microsoft, all periods) | **0 FAIL** |
| Offline `--sample` run | Passes all checks with **zero network** |
| MSFT FY2025 revenue (spot check) | **$281.7B**, from the correct ASC 606 tag |

---

## Status

- **Recipe:** `SPECIFIED` · `recipe_version 0.2.0` · `todos_open: 0`
- **Runtime:** Python 3 standard library only (no install)
- **Footprint:** ~1,100 lines across a 10-module package + recipe, data-contract, run-log, benchmark, fixtures, and project docs.

---

## Documentation & links

Everything is documented in-repo on the branch `feature/sec-filings-metrics-agent`:

- **GitHub branch (live after push):** `https://github.com/Asavari24/mycroft/tree/feature/sec-filings-metrics-agent`
- **Project overview:** `projects/SEC-Filings-Financial-Metrics-Agent/README.md`
- **Recipe / spec:** `recipes/sec-filings-financial-metrics.yaml`
- **Code + usage:** `scripts/sec-filings-financial-metrics/README.md`
- **Run log (2 entries):** `logs/RUN_LOG.md`
- **Data contract entry:** `DATA_CONTRACT.md`
- **Benchmark report (generated):** `data/verified/sec-filings-financial-metrics/benchmark_report.md`

*(GitHub blob links resolve once the branch is pushed:
`https://github.com/Asavari24/mycroft/blob/feature/sec-filings-metrics-agent/<path>`.)*

---

## Next steps

1. Populate the custom-extension override map for real filers as encountered.
2. Expand the benchmark golden set with more companies and independently hand-verified figures.
3. Add quarterly (10-Q) derived ratios.
4. Promote the recipe SPECIFIED → RUNNABLE-SAMPLE with logged gate decisions.
