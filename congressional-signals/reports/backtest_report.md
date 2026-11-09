# Backtest — Congressional Cluster Signal

**Source:** `enriched_trades.csv` · **Hold:** 30 days from disclosure · **Entry-time tiering:** cluster_size × max BCR (no look-ahead)

Strategy: enter each qualifying BUY at its disclosure date, hold 30 days. Alpha = return minus SPY over the identical window.

| Tier | n | Avg Return | SPY | **Alpha** | Win% |
|------|---|-----------|-----|-----------|------|
| STRONG | 815 | +2.47% | +2.24% | **+0.23%** | 50.3% |
| WATCH | 1212 | +3.14% | +2.61% | **+0.54%** | 50.6% |
| SKIP | 132 | +1.96% | +2.00% | **-0.04%** | 44.7% |
| SOLO | 3003 | +1.81% | +1.86% | **-0.05%** | 44.9% |
| ALL BUYS (copy everything) | 5162 | +2.23% | +2.10% | **+0.13%** | 47.1% |

**$10,000 equal-weighted across STRONG signals** → **$10,247** vs SPY **$10,224**.

**Alpha ordering STRONG ≥ WATCH ≥ SKIP holds:** False

### Caveats
- Small n on STRONG; in-sample; equal-weight, no transaction costs or slippage.
- Amount ranges (not exact sizes) — positions unweighted by capital deployed.
- Correlation, not proven causation. Research/education only — not financial advice.