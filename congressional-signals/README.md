# Congressional Signal Intelligence

A Mycroft-compliant module that turns public U.S. congressional stock-trade disclosures
(STOCK Act filings) into sourced **STRONG / WATCH / SKIP** signals. Research only — no
trades placed, no financial advice. Extends Ziobrowski et al. (2004) into the post-STOCK
Act era (2023–2026) with per-trade SPY benchmarking.

## Thesis

Aggregate congressional trading is market beta (+0.24% BUY alpha vs SPY). The signal lives
in **cluster buys** — 2+ politicians buying the same ticker within 30 days — concentrated in
semiconductor / AI-infrastructure names (DDOG +68.94%, SNDK, MU, INTC alpha vs SPY), aligned
with active CHIPS Act and AI-regulation drafting. The value is the **skip rate**.

## Mycroft / SNICKERDOODLE compliance

| Principle | Implementation |
|-----------|----------------|
| P2 verified data | `data/raw/` (ingest) → `data/verified/` (gate-cleared); TOOL scripts read verified |
| P3 provenance | every signal carries a `source` tracing to a Capitol Trades filing |
| P4 hard gates | conformance gate halts pipeline on failure (G1) |
| P5 two customers | `logs/run_*.json` (agent) + `reports/signal_report_*.md` (human) |
| P6 recipe authority | `recipes/congressional-signal-agent.md` is canonical |
| P7 append-only log | `logs/RUN_LOG.md` |

See `recipes/congressional-signal-agent.md` for phase gates (G1–G6) and `DATA_CONTRACT.md`.

## Pipeline (LangGraph multi-agent)

```
conformance → cluster → scorer → research (LLM) → report
```

`langgraph_pipeline.py` is a 5-node LangGraph state machine. Gate failure halts; absence of
STRONG signals skips the research node. Research node uses Claude (langchain-anthropic) when
`ANTHROPIC_API_KEY` is set, else a rule-based fallback.

### Layers
- **INGEST** — `scraper.py` (Selenium, Capitol Trades) → `data/raw/`
- **GIGO** — `enricher.py` (yfinance), `market_adjusted.py` (SPY-matched), `conformance.py` → `data/verified/`
- **TOOL** — `cluster_analyzer.py`, `langgraph_pipeline.py`, `server.py` (FastMCP, 5 tools)

## Run

```bash
pip install -r requirements.txt
python langgraph_pipeline.py --no-llm   # rule-based, no API key
python langgraph_pipeline.py            # LLM research notes (needs ANTHROPIC_API_KEY)
```

## Current results (25 politicians, 5,409 trades, 4,166 priced)

Gate PASSED · 205 clusters · 9 STRONG / 174 WATCH / 22 SKIP · top STRONG: UNH (healthcare)
score 2.73, alpha +6.52%.
