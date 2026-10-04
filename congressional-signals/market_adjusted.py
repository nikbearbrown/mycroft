"""
market_adjusted.py
Recomputes all post-disclosure returns as market-adjusted (alpha) by subtracting
SPY's actual return over the exact same 30-day window for each individual trade.

Raw return:            (price_30d_post_disclosure / price_at_disclosure) - 1
SPY return (matched):  (SPY_30d_after_disclosure / SPY_at_disclosure) - 1
Abnormal return:       raw_return - spy_return
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ── SPY price cache ──────────────────────────────────────────────────────────
_spy_cache: dict[str, float] = {}

def get_spy_close(date_str: str) -> float | None:
    """Get SPY closing price on or just before a given date."""
    if not date_str or len(date_str) != 10:
        return None
    if date_str in _spy_cache:
        return _spy_cache[date_str]
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        start = (dt - timedelta(days=7)).strftime("%Y-%m-%d")
        end   = (dt + timedelta(days=1)).strftime("%Y-%m-%d")
        df = yf.download("SPY", start=start, end=end, progress=False, auto_adjust=True)
        if df.empty:
            _spy_cache[date_str] = None
            return None
        price = float(df["Close"].iloc[-1])
        _spy_cache[date_str] = price
        return price
    except Exception:
        _spy_cache[date_str] = None
        return None


def compute_spy_return(disclosure_date: str) -> float | None:
    """SPY return over the same 30-day window used for post-disclosure return."""
    spy_at  = get_spy_close(disclosure_date)
    if not spy_at:
        return None
    post_dt = (datetime.strptime(disclosure_date, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
    spy_post = get_spy_close(post_dt)
    if not spy_post:
        return None
    return round((spy_post - spy_at) / spy_at * 100, 4)


# ── Main ─────────────────────────────────────────────────────────────────────
df = pd.read_csv('data/enriched_trades.csv', dtype=str).fillna('')

# Only rows with a valid post-disclosure return
df['pct_change_post_disclosure'] = pd.to_numeric(df['pct_change_post_disclosure'], errors='coerce')
valid = df[df['pct_change_post_disclosure'].notna() & (df['disclosure_date'].str.len() == 10)].copy()

print(f"Rows with post-disclosure return: {len(valid)}")
print("Fetching SPY prices for each unique disclosure date...")

unique_dates = valid['disclosure_date'].unique()
print(f"Unique disclosure dates: {len(unique_dates)}")

# Pre-fetch all SPY prices (one API call per unique date pair)
spy_returns = {}
for i, d in enumerate(sorted(unique_dates)):
    r = compute_spy_return(d)
    spy_returns[d] = r
    if (i+1) % 20 == 0:
        print(f"  {i+1}/{len(unique_dates)} dates processed...")

print(f"SPY returns computed for {sum(v is not None for v in spy_returns.values())} / {len(unique_dates)} dates")
print()

# Map SPY return onto each trade
valid['spy_return_30d'] = valid['disclosure_date'].map(spy_returns)
valid['abnormal_return'] = (valid['pct_change_post_disclosure'] - valid['spy_return_30d']).round(4)

# Save enriched file with new columns
df_out = df.copy()
df_out['spy_return_30d'] = None
df_out['abnormal_return'] = None
df_out.loc[valid.index, 'spy_return_30d'] = valid['spy_return_30d']
df_out.loc[valid.index, 'abnormal_return'] = valid['abnormal_return']
df_out.to_csv('data/enriched_trades.csv', index=False)
print("Saved updated enriched_trades.csv with spy_return_30d and abnormal_return columns")
print()

# ── Results ──────────────────────────────────────────────────────────────────
buys  = valid[(valid['trade_type'].str.upper() == 'BUY')  & valid['abnormal_return'].notna()]
sells = valid[(valid['trade_type'].str.upper() == 'SELL') & valid['abnormal_return'].notna()]

print("=" * 55)
print("MARKET-ADJUSTED RETURNS (Abnormal Return = Raw - SPY)")
print("=" * 55)
print(f"{'':30} {'Raw':>8}  {'SPY':>8}  {'Alpha':>8}")
print(f"  BUY  trades (n={len(buys):4d})          "
      f"{buys['pct_change_post_disclosure'].mean():>+7.2f}%  "
      f"{buys['spy_return_30d'].mean():>+7.2f}%  "
      f"{buys['abnormal_return'].mean():>+7.2f}%")
print(f"  SELL trades (n={len(sells):4d})          "
      f"{sells['pct_change_post_disclosure'].mean():>+7.2f}%  "
      f"{sells['spy_return_30d'].mean():>+7.2f}%  "
      f"{sells['abnormal_return'].mean():>+7.2f}%")
print()

# Politician leaderboard — market adjusted
print("POLITICIAN LEADERBOARD (market-adjusted, BUYs only):")
print(f"{'Politician':<30} {'Raw':>8}  {'Alpha':>8}  {'Win%':>6}  {'n':>4}")
print("-" * 62)
pol = buys.groupby('politician').agg(
    raw=('pct_change_post_disclosure', 'mean'),
    alpha=('abnormal_return', 'mean'),
    win_rate=('abnormal_return', lambda x: (x > 0).mean() * 100),
    n=('abnormal_return', 'count')
).sort_values('alpha', ascending=False)

for name, row in pol.iterrows():
    print(f"  {name:<28} {row['raw']:>+7.2f}%  {row['alpha']:>+7.2f}%  {row['win_rate']:>5.1f}%  {int(row['n']):>4}")

print()

# Cluster signals — market adjusted
print("CLUSTER SIGNAL ALPHA (2+ politicians, same ticker):")
print(f"{'Ticker':<8} {'Company':<35} {'Pols':>4}  {'Raw':>8}  {'Alpha':>8}")
print("-" * 65)
eq = buys[buys['ticker'].str.isalpha() & buys['ticker'].str.len().between(1,5)]
cluster = eq.groupby('ticker').agg(
    n_pols=('politician', lambda x: len(set(x))),
    raw=('pct_change_post_disclosure', 'mean'),
    alpha=('abnormal_return', 'mean'),
    name=('asset_name', 'first')
).query('n_pols >= 2').sort_values('alpha', ascending=False)

for ticker, row in cluster.head(20).iterrows():
    print(f"  {ticker:<6} {row['name'][:33]:<33} {int(row['n_pols']):>4}  {row['raw']:>+7.2f}%  {row['alpha']:>+7.2f}%")

print()
print("BOTTOM 10 CLUSTER SIGNALS (worst alpha):")
for ticker, row in cluster.tail(10).iterrows():
    print(f"  {ticker:<6} {row['name'][:33]:<33} {int(row['n_pols']):>4}  {row['raw']:>+7.2f}%  {row['alpha']:>+7.2f}%")

print()
avg_spy = valid['spy_return_30d'].mean()
print(f"Average SPY 30d return across all disclosure windows: {avg_spy:+.2f}%")
