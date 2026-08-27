# RUN_LOG — Congressional Signal Intelligence

Append-only execution history (SNICKERDOODLE P7). Concrete, dated, attributed.
Newest entries at top.

---

## 2026-06-26 — Full 64-politician run + enricher made resumable + bulk-SPY fix

**Fellow:** Ameya Deshmukh
**Recipe:** congressional-signal-agent

**Built / fixed:**
- `enricher.py` — now incremental & resumable (checkpoint every 200 rows, keyed on trade_url).
  Survives teardowns; restart skips already-enriched rows. Resolves repeated data loss.
- `market_adjusted.py` — replaced per-date SPY fetch (348 calls, rate-limited) with a single
  bulk SPY download + local nearest-prior lookup. 1 API call, no rate limiting.

**Commands:**
```
python enricher.py            # resumed 7209 → 9211
python market_adjusted.py
python cluster_analyzer.py
python langgraph_pipeline.py --no-llm
```

**Inputs:** `data/verified/enriched_trades.csv` — 9,211 trades, 64 politicians, 4,166 priced (45%)

**Result:** VERIFIED (rule-based mode), Gate PASSED
- Aggregate BUY alpha **+0.04%** (raw +2.61% vs SPY +2.56%); SELL alpha +0.15%. SPY avg +2.54%.
- Clusters: **425** · STRONG: **33** · WATCH: 352 · SKIP: 40
- Top cluster alpha: DDOG +68.94%, SNDK +51.17%, MRVL +31.68%, HUM +29.18%, MU +26.65%.
- Best politician signals: McCormick +5.25% (n=38, BCR 0.87), Tim Moore +4.25% (n=147, BCR 0.74).
- Semiconductor/AI thesis holds on the larger set; aggregate alpha near zero (rides beta).

**Open issues:** SPY null for disclosures whose 30-day window is still in the future (expected).

---

## 2026-06-25 — Mycroft compliance pass + LangGraph multi-agent pipeline

**Fellow:** Ameya Deshmukh
**Recipe:** congressional-signal-agent

**Built:**
- `langgraph_pipeline.py` — 5-node LangGraph state machine:
  conformance → cluster → scorer → research (LLM) → report.
  Conditional routing: gate failure halts; no STRONG signals skips research node.
- Two-tier data layer created: `data/raw/`, `data/verified/`.
- Recipe `recipes/congressional-signal-agent.md` authored to template (phase gates, output contract).
- `DATA_CONTRACT.md` and data-layer READMEs added.

**Commands:**
```
python langgraph_pipeline.py --no-llm
```

**Inputs:** `data/verified/enriched_trades.csv` (5,409 trades, 25 politicians, 4,166 priced)

**Outputs:**
- `logs/run_20260625_211251.json` (agent log, full provenance)
- `reports/signal_report_20260625_211251.md` (human brief)

**Result:** VERIFIED (rule-based mode)
- Gate: PASSED
- Clusters: 205 · STRONG: 9 · WATCH: 174 · SKIP: 22
- Top STRONG: UNH (healthcare) score 2.73 alpha +6.52%

**Open issues:**
- Enricher stalled mid-run on 9,211-row dataset (~row 2,313). 64-politician raw scrape
  complete in `data/raw/trades.csv`; re-enrichment pending.
- [TODO: DEV] migrate legacy scripts to read from `data/verified/` (copies synced for now).

---

## 2026-06-19 — Cluster analysis + conformance gate

**Fellow:** Ameya Deshmukh

**Built:** `cluster_analyzer.py`, `conformance.py`, `signal_scorer.py`.
3 Claude Code skills (`/pipeline`, `/score`, `/clusters`).

**Result:** VERIFIED. 205 clusters detected (89 positive alpha, 116 negative).
Semiconductor/cybersecurity concentration confirmed: SNDK +82.97%, DDOG +68.94%, MU +38.01%.

---

## 2026-06-12 — Dashboard + dataset expansion

**Fellow:** Ameya Deshmukh

**Built:** `dashboard.html` (Chart.js research dashboard). Scraper expanded 14 → 25 politicians.

**Result:** VERIFIED. Aggregate BUY alpha +0.24%. BCR paradox documented
(Doggett BCR 1.00 → −1.20% alpha). Tim Moore most robust: n=147, +4.25% alpha.

---

## 2026-06-09 — Market adjustment + paper draft

**Fellow:** Ameya Deshmukh

**Built:** `market_adjusted.py` (per-trade SPY-matched benchmark), `PAPER_DRAFT.md`,
`diagnose_missing.py`.

**Result:** VERIFIED. 14-politician run: BUY alpha −1.59% (raw +2.32% vs SPY +3.91%).
Cluster buys in semis survive adjustment (DDOG +68.94%). Aggregate = beta, signal = clusters.

---

## 2026-05-17 — Scraper + enricher (initial pipeline)

**Fellow:** Ameya Deshmukh

**Built:** `scraper.py` (Selenium, Capitol Trades, checkpoint/resume),
`enricher.py` (yfinance, 6 price columns), `server.py` (FastMCP, 5 tools).

**Result:** VERIFIED. First dataset: 14 politicians, 3,336 trades, 61% price coverage.
