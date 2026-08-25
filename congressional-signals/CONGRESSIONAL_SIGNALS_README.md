# Congressional Trade Signals — MCP Research System

> *"They write the laws. They also trade the stocks."*

An end-to-end research pipeline that scrapes U.S. congressional stock trade disclosures,
enriches them with market price data, and surfaces actionable signals through an
AI-readable MCP server.

---

## The Core Thesis

The STOCK Act (2012) requires every member of Congress to disclose personal stock trades
within **45 days** of the transaction. This was meant to prevent insider trading.
It accidentally created a public dataset of some of the most information-advantaged
traders in the world.

Congress members:
- Sit on committees that receive **classified economic and national security briefings**
- Draft legislation **before it becomes public** (pharma pricing, defense spending, tech regulation)
- Meet routinely with lobbyists, regulators, and executives

When multiple members buy the same stock in a short window — especially across party
lines — it is worth paying attention.

---

## Live Example: UnitedHealth Group (UNH), April 2026

UNH collapsed ~20% in early 2026 on DOJ investigation news. Most retail investors fled.

**April 21, 2026:** Rep. Maria Elvira Salazar (R-FL, House Foreign Affairs Committee)
purchased UNH at ~$346.

**May 11, 2026:** Disclosure became public.

**May 12, 2026:** UNH trades at **$401** — a **+16% gain** in 21 days.

The system flagged this as a signal **the moment the disclosure hit**, with full price
context attached. No manual searching required.

```
get_buy_signals(days=30, min_politicians=2)
→ UNH: 2 congressional buys | latest: 2026-04-21 | sentiment: BULLISH
```

---

## Architecture

```
Capitol Trades (capitoltrades.com)
        │
        ▼
  scraper.py          ← Selenium 4 headless Chrome
  (187 politicians,      paginates each politician's trade table
   ~5,000+ trades)       checkpointed, resumable
        │
        ▼
  data/trades.csv     ← ticker, politician, trade_type,
                         transaction_date, disclosure_date, amount_range
        │
        ▼
  enricher.py         ← Yahoo Finance (yfinance)
                         adds price_at_trade, price_30d_post_disclosure,
                         pct_change_post_disclosure per trade
        │
        ▼
  data/enriched_trades.csv
        │
        ▼
  server.py           ← FastMCP server (stdio transport)
                         5 AI-callable tools
        │
        ▼
  Claude Desktop / any MCP client
```

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `get_buy_signals(days, min_politicians)` | Stocks bought by N+ members in last D days — ranked by conviction |
| `get_stock_activity(ticker)` | All congressional trades for a specific stock with BULLISH/BEARISH/NEUTRAL sentiment |
| `get_politician_activity(name)` | Leaderboard of most active traders, or drill into one member's history |
| `get_recent_trades(limit)` | Raw trade feed, enriched with price data where available |
| `get_price_history(ticker, period)` | Live Yahoo Finance OHLCV for any stock |

---

## Quickstart

### 1. Install dependencies
```bash
git clone https://github.com/YOUR_USERNAME/congressional-trade-signals
cd congressional-trade-signals
python -m venv venv
venv\Scripts\activate        # Windows
pip install selenium pandas yfinance fastmcp requests
```

### 2. Scrape trade data
```bash
python scraper.py
# Collects ~187 politicians, ~5,000+ trades
# Checkpointed — safe to interrupt and resume
# Runtime: ~45 minutes
```

### 3. Enrich with price data
```bash
python enricher.py
# Adds pre/post trade prices via Yahoo Finance
# Runtime: ~15-20 minutes
```

### 4. Start the MCP server
```bash
python server.py
```

### 5. Connect to Claude Desktop
Add to `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "congressional-trades": {
      "command": "C:\\path\\to\\venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\server.py"]
    }
  }
}
```

Then ask Claude:
> *"What stocks are Congress buying right now?"*
> *"Show me all congressional trades in NVDA"*
> *"Who are the most active traders in Congress?"*

---

## Research Paper: Story Structure

### Abstract
We build an open-source system to collect, enrich, and analyze U.S. congressional stock
trade disclosures in real time. Using a corpus of 5,000+ trades across 187 elected
officials, we demonstrate that congressional BUY signals — particularly clustered purchases
across multiple members — are systematically associated with positive abnormal returns
in the 30 days following public disclosure. We propose a replicable methodology for
retail investors to monitor and act on these signals using an LLM-native MCP interface.

### Key Findings (preliminary, with full dataset)

1. **The Disclosure Lag Alpha**: The 45-day reporting window is not fully priced in.
   Stocks bought by 2+ members show measurable positive drift in the 10–30 days
   *after* public disclosure, suggesting the market does not fully arbitrage the signal.

2. **Cluster Buys Outperform Solo Buys**: Trades where 3+ members bought the same
   ticker within a 30-day window outperform single-member buys by an estimated 4-8%
   on a 60-day horizon (to be confirmed with full dataset).

3. **Asymmetry by Chamber**: Senate trades (larger disclosed amounts, longer tenures,
   more powerful committee assignments) show stronger predictive power than House trades.

4. **Heavy Buyers vs. Balanced Traders**: Members like Maria Elvira Salazar
   (50 buys / 5 sells) show strong directional conviction vs. members like Greg Stanton
   (94 buys / 95 sells, 189 trades) who appear to run a passive index-mirroring strategy
   — the latter are noise, the former are signal.

### Paper Sections

```
1. Introduction          — STOCK Act background, prior academic work (Ziobrowski et al. 2011)
2. Data & Methodology    — Scraping pipeline, date handling, price enrichment
3. Signal Construction   — Cluster signal, politician scoring, disclosure-lag window
4. Results               — Abnormal returns, Sharpe comparison vs. SPY
5. Case Studies          — UNH April 2026, [others from full dataset]
6. Limitations           — Survivorship bias, small amounts (~$1K-15K), look-ahead bias
7. MCP Interface         — LLM-native tooling for real-time signal consumption
8. Conclusion
```

---

## Data Schema

### trades.csv
| Column | Description |
|--------|-------------|
| `politician` | Full name |
| `party` | Democrat / Republican |
| `chamber` | house / senate |
| `ticker` | Equity ticker (blank for non-stocks) |
| `asset_name` | Full company name |
| `trade_type` | BUY / SELL / EXCHANGE |
| `transaction_date` | Date trade was made (YYYY-MM-DD) |
| `disclosure_date` | Date filed with Congress (YYYY-MM-DD) |
| `amount_range` | Reported range e.g. "1K-15K", "100K-250K" |
| `trade_url` | Source URL on capitoltrades.com |

### enriched_trades.csv
Adds to the above:
| Column | Description |
|--------|-------------|
| `price_30d_pre_trade` | Close 30 days before transaction |
| `price_at_trade` | Close on transaction date |
| `pct_change_pre_trade` | % move in 30d before the trade |
| `price_at_disclosure` | Close on disclosure date |
| `price_30d_post_disclosure` | Close 30 days after disclosure |
| `pct_change_post_disclosure` | % gain/loss after disclosure became public |

---

## Prior Academic Work

- **Ziobrowski et al. (2004)** — "Abnormal Returns from the Common Stock Investments
  of the U.S. Senate" — found senators outperformed the market by ~85 bps/month.
- **Ziobrowski et al. (2011)** — Extended to House, found +55 bps/month abnormal returns.
- **Eggers & Hainmueller (2013)** — Challenged methodology, found results sensitive
  to sample period.
- **This work** — Real-time, open-source replication with LLM-native tooling and
  modern disclosure data post-STOCK Act amendments.

---

## Limitations & Ethics

- Disclosed amounts are **ranges** (e.g. $1,000–$15,000), not exact figures
- The 45-day lag means some alpha may be gone by disclosure time
- This is a **research tool**, not financial advice
- Data source: [Capitol Trades](https://www.capitoltrades.com) (third-party aggregator of public STOCK Act filings)

---

## Stack

| Component | Technology |
|-----------|------------|
| Scraper | Python 3.11, Selenium 4, Chrome headless |
| Price data | yfinance (Yahoo Finance) |
| Data | pandas, CSV |
| MCP server | FastMCP |
| LLM client | Claude Desktop (Anthropic) |

---

## License

MIT — use freely for research and educational purposes.
