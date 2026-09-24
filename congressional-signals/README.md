# Congressional Trade Signals

**Do U.S. congressional stock trades beat the market — and can a retail investor act on them?**

An end-to-end, auditable research pipeline that collects public STOCK Act disclosures,
market-adjusts every trade against the S&P 500, detects multi-politician *cluster* buys,
and scores them into **STRONG / WATCH / SKIP** signals — exposed both as a research dataset
and as a live MCP server.

> Research project extending Ziobrowski et al. (2004, 2011) into the post-STOCK Act era.
> Built as a Fellow at [Humanitarians AI](https://github.com/Humanitariansai) under the
> Mycroft verified-intelligence framework. **Research only — not financial advice. No trades are placed.**

---

## The headline finding

In aggregate, congressional BUY trades beat the market by only **+0.24%** after per-trade
SPY adjustment — most members simply ride market beta. The real signal is concentrated in
**cluster buys**: when 2+ politicians independently buy the same ticker within 30 days,
especially in semiconductors and AI infrastructure under active legislative oversight,
those clusters show **+17% to +68% alpha** above SPY.

**The value of the system is the skip rate** — it filters out ~95% of trades as noise.

---

## Architecture

```
 INGEST            GIGO (validate)             TOOL (analyze, read verified only)
┌─────────┐   ┌──────────────────────┐   ┌─────────────────────────────────────┐
│scraper  │ → │enricher              │ → │cluster_analyzer → langgraph_pipeline │
│(Selenium│   │(yfinance prices)     │   │(cluster detect)  (5-node multi-agent)│
│Capitol  │   │market_adjusted       │   │                                      │
│Trades)  │   │(SPY per-trade alpha) │   │           server.py (MCP, 5 tools)   │
└─────────┘   └──────────────────────┘   └─────────────────────────────────────┘
 data/raw/  ───────────────────────────→  data/verified/  ──→  logs/ + reports/
```

### The LangGraph multi-agent pipeline (`langgraph_pipeline.py`)

```
conformance ──(fail)──→ END          hard data gate: never analyze garbage
     │
     ↓
 cluster ──→ scorer ──(0 STRONG)──→ report      skip the LLM when nothing to explain
                 │
              (STRONG>0)
                 ↓
            research (Claude) ──→ report         LLM thesis note per strong signal
```

Shared typed state with an **append-only run-log reducer** — every number in the final
report traces back through the graph to its source filing (provenance).

---

## Quick start

```bash
pip install -r requirements.txt

python scraper.py              # 1. INGEST  — scrape Capitol Trades → data/raw/trades.csv
python enricher.py             # 2. GIGO    — add yfinance prices (resumable, checkpointed)
python market_adjusted.py      # 3. GIGO    — per-trade SPY-matched alpha
python cluster_analyzer.py     # 4. TOOL    — detect clusters + politician sector profiles
python langgraph_pipeline.py --no-llm   # 5. TOOL — score signals, write log + report
```

Open `dashboard.html` in any browser for the interactive research dashboard.

### As an MCP server (Claude Desktop)

`server.py` exposes 5 natural-language tools: `get_price_history`, `get_recent_trades`,
`get_buy_signals`, `get_stock_activity`, `get_politician_activity`.

---

## Methodology highlights

- **Per-trade market adjustment** — each trade's return has SPY's return over the *identical*
  30-day window subtracted. Stricter than the aggregate benchmarking in prior literature.
- **Returns measured from disclosure date**, not transaction date — the moment a retail
  investor could realistically have known. No look-ahead.
- **Cluster = temporal co-occurrence**, not ML clustering: 2+ distinct politicians buying the
  same ticker in a 30-day sliding window.
- **Two-factor score** = cluster size × max buy-conviction ratio (BCR), validated against
  out-of-sample market-adjusted alpha.

---

## Repo layout

| Path | What |
|------|------|
| `scraper.py` | Selenium scraper for Capitol Trades (checkpoint/resume) |
| `enricher.py` | yfinance price enrichment (incremental, resumable) |
| `market_adjusted.py` | per-trade SPY alpha |
| `cluster_analyzer.py` | cluster detection + politician sector profiles |
| `langgraph_pipeline.py` | 5-node LangGraph multi-agent signal pipeline |
| `server.py` | FastMCP server (5 tools) |
| `dashboard.html` | interactive research dashboard (Chart.js) |
| `PAPER_DRAFT.md` | working paper |
| `recipes/`, `DATA_CONTRACT.md`, `logs/RUN_LOG.md` | Mycroft framework compliance |

---

## Author

**Ameya Deshmukh** — [@Ameya-Deshmukh26](https://github.com/Ameya-Deshmukh26)
deshmukh.amey@northeastern.edu · Northeastern University

## License

MIT — see [LICENSE](LICENSE).

*Data sourced from public STOCK Act disclosures via [Capitol Trades](https://www.capitoltrades.com)
and price data via Yahoo Finance. This project is for research and educational purposes only
and does not constitute financial advice.*
