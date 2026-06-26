# DATA_CONTRACT — Congressional Signal Intelligence

Per SNICKERDOODLE P2 (verified data) and P3 (provenance). Defines where data lives,
how it is validated, and what may be trusted.

---

## Two-tier model

```
data/raw/        ← ingest outputs only. Unvalidated. Touched by INGEST scripts.
data/verified/   ← validated outputs only. Read by TOOL scripts. Gate-cleared.
```

**Rule:** nothing enters `data/verified/` without passing the conformance gate (G1).
TOOL scripts (`cluster_analyzer.py`, `langgraph_pipeline.py`, `server.py`) must read
from `data/verified/`. INGEST (`scraper.py`) writes only to `data/raw/`.

> Migration note: legacy scripts currently read `data/*.csv`; verified copies are synced.
> Full path migration tracked as `[TODO: DEV]` in the recipe.

---

## File contracts

| File | Layer | Producer | Required fields |
|------|-------|----------|-----------------|
| `trades.csv` | raw | scraper.py | politician, ticker, trade_type, transaction_date, disclosure_date, amount_range |
| `scraper_checkpoint.txt` | raw | scraper.py | one politician_id per line |
| `enriched_trades.csv` | verified | enricher + market_adjusted | raw fields + price_at_trade, price_at_disclosure, pct_change_post_disclosure, spy_return_30d, abnormal_return |
| `cluster_signals.json` | verified | cluster_analyzer.py | ticker, sector, cluster_size, politicians, avg_alpha, win_rate, source |
| `politician_profiles.json` | verified | cluster_analyzer.py | bcr, overall_alpha, best_sector, sector_alpha |
| `signal_log.json` / `run_*.json` | logs | langgraph_pipeline.py | full run state + provenance |

---

## Validation gates

| Check | Tool | Pass condition |
|-------|------|----------------|
| Schema conformance | `conformance.py` | required columns present, types parse |
| Price coverage | `market_adjusted.py` | ≥ 60% of equity trades priced |
| Provenance | recipe G3/G5 | every signal carries a `source` field tracing to capitoltrades.com filing |

## Quality notes

- ~23% of trades are non-equity (bonds, options) → no ticker → excluded from signals, not errors.
- SPY benchmark unavailable for disclosures whose 30-day window has not yet closed → expected nulls.
- Amount ranges (e.g. $1K–$15K), not exact values → returns are unweighted by capital.
