# Congressional Signal Intelligence Agent — Recipe

> Mycroft recipe. Canonical specification for the congressional-trade signal pipeline.
> Governed by `SNICKERDOODLE.md` (P1–P8). Recipe supersedes scripts where they disagree (P6).

---

## Purpose & Overview

Turn public U.S. congressional stock-trade disclosures (STOCK Act filings) into a sourced
**STRONG / WATCH / SKIP** decision per ticker. The value is the **skip rate**: most
congressional trades are market beta and are filtered out. The residual high-signal set —
cross-party cluster buys in sectors under active legislative oversight — is the research output.

- **Domain owner / approver:** Ameya Deshmukh (Fellow), Prof. Nik Bear Brown (PI)
- **Outputs reviewed by:** human gate before any signal is marked `VERIFIED`
- **This is research, not financial advice.** No trades are placed.

---

## Source Inventory

| Source | Type | Layer | Notes |
|--------|------|-------|-------|
| capitoltrades.com | Live web (Selenium) | `data/raw/` | STOCK Act disclosures; no API, JS-rendered |
| Yahoo Finance (yfinance) | Live API | `data/raw/` → `data/verified/` | Per-trade OHLCV + SPY benchmark |
| SECTOR_MAP | Static config | in-code | GICS-inspired ticker → sector map |

Only INGEST steps touch external sources (P2). TOOL steps read **only** from `data/verified/`.

---

## Inputs & Dependencies

| Input | Required | Approval gate |
|-------|----------|---------------|
| `data/raw/trades.csv` | yes | conformance pass |
| `data/verified/enriched_trades.csv` | yes | GIGO promotion |
| `ANTHROPIC_API_KEY` | optional | enables LLM research node; falls back to rule-based |

---

## Phase Gates

Lifecycle: `DRAFT → SPECIFIED → RUNNABLE-SAMPLE → RUNNABLE-LIVE → VERIFIED`

| Gate | Test command | Human capacity | Pass condition |
|------|--------------|----------------|----------------|
| G1 Conformance | `python conformance.py` | [TO] technical owner | required columns present, exit 0 |
| G2 GIGO promote | `python market_adjusted.py` | [PF] proof of fitness | priced coverage ≥ 60%, raw→verified written |
| G3 Cluster detect | `python cluster_analyzer.py` | [IJ] interpretive judgment | clusters.json regenerated |
| G4 Score | `python langgraph_pipeline.py --no-llm` | [PA] policy/approval | STRONG/WATCH/SKIP counts logged |
| G5 Research | `python langgraph_pipeline.py` | [EI] external interface | notes generated, provenance attached |
| G6 Attest | human review of report | [PA] | signal state DRAFT→VERIFIED |

Capacity labels: [TO] technical owner · [PF] proof-of-fitness · [PA] policy/approval ·
[IJ] interpretive judgment · [EI] external-interface.

---

## Steps

1. **INGEST — scrape disclosures**
   `scraper.py` → `data/raw/trades.csv`
   Labor: AI executes, human approves scope. Selenium, checkpoint/resume.

2. **GIGO — price enrich**
   `enricher.py` → `data/verified/enriched_trades.csv`
   Labor: AI executes. Adds 6 price columns via yfinance.

3. **GIGO — market adjust**
   `market_adjusted.py` → adds `spy_return_30d`, `abnormal_return`
   Labor: AI executes. Per-trade SPY-matched window. Gate G2.

4. **TOOL — cluster + profiles**
   `cluster_analyzer.py` → `data/verified/cluster_signals.json`, `politician_profiles.json`
   Labor: AI executes, human interprets sector concentration (G3).

5. **TOOL — multi-agent scoring**
   `langgraph_pipeline.py` → `logs/run_*.json` + `reports/signal_report_*.md`
   Graph: conformance → cluster → scorer → research(LLM) → report.
   Labor: AI executes, human gate before VERIFIED (G4–G6).

---

## Output Contract (P5 — two customers, twice)

| Customer | Artifact | Location |
|----------|----------|----------|
| Agent / audit | structured JSON, full provenance + run_log | `logs/run_*.json` |
| Human / domain | readable signal brief, decision-ready | `reports/signal_report_*.md` |

Required report sections: Signal Summary table · Strong Signals (ticker, sector,
politicians, score, alpha, win rate, **source**, signal state) · provenance footer.

Every finding traces: report → log → script → recipe → source (P3). No invented numbers.

---

## Stop Conditions

- Conformance gate (G1) fails → HALT, do not enrich.
- `ANTHROPIC_API_KEY` missing → research node degrades to rule-based notes (not a halt).
- Priced coverage < 60% → HALT at G2, flag data-quality issue.
- Any signal written as `VERIFIED` without a logged human attestation → contract violation (P4/P8).

---

## CLI Reference

```bash
# Full pipeline (after scrape + enrich)
python langgraph_pipeline.py --no-llm      # rule-based notes, no key needed
python langgraph_pipeline.py               # LLM research notes (needs ANTHROPIC_API_KEY)

# Individual gates
python conformance.py                      # G1
python market_adjusted.py                  # G2
python cluster_analyzer.py                 # G3
```

---

## [TODO]

- [TODO: DEV] Migrate legacy scripts (`server.py`, `cluster_analyzer.py`, `signal_scorer.py`)
  to read canonically from `data/verified/` rather than `data/`. Currently copies are synced.
- [TODO: DEV] Wire `conformance.py` as a hard pre-commit gate via `.claude/hooks/`.
- [TODO: DATA SOURCE] Add per-row provenance URL note for trades with missing tickers.
- [TODO: DEFINE] Statistical significance threshold for STRONG (t-test / bootstrap).
- [TODO: REPORT FIELD] Add sector-adjusted benchmark (XSD ETF) column to verified output.
