import pandas as pd

df = pd.read_csv('data/trades.csv', dtype=str).fillna('')
print(f'Total trades: {len(df)}')
print(f'Politicians: {df["politician"].nunique()}')

eq_mask = df['ticker'].str.isalpha() & df['ticker'].str.len().between(1, 5)
print(f'Unique equity tickers: {df[eq_mask]["ticker"].nunique()}')
print()

# Politician profiles
print('=== POLITICIAN PROFILES ===')
for pol, g in df.groupby('politician'):
    buys  = (g['trade_type'].str.upper() == 'BUY').sum()
    sells = (g['trade_type'].str.upper() == 'SELL').sum()
    total = buys + sells
    ratio = round(buys / total * 100) if total > 0 else 0
    tickers = g[eq_mask.reindex(g.index, fill_value=False)]['ticker'].nunique()
    latest  = g['transaction_date'].max()
    print(f'{pol:<32} trades={len(g):4d}  buys={buys:4d}  sells={sells:4d}  buy%={ratio:3d}%  tickers={tickers:3d}  latest={latest}')

print()

# Most bought tickers
eq = df[eq_mask & (df['trade_type'].str.upper() == 'BUY')]
top = (
    eq.groupby('ticker')
    .agg(
        buy_count=('politician', 'count'),
        politicians=('politician', lambda x: len(set(x))),
        name=('asset_name', 'first'),
    )
    .sort_values('buy_count', ascending=False)
    .head(20)
)
print('=== TOP 20 MOST BOUGHT TICKERS ===')
print(top.to_string())

print()
print('=== CLUSTER SIGNALS (bought by 2+ politicians) ===')
print(top[top['politicians'] >= 2].to_string())

print()
# Sell signals
eq_sell = df[eq_mask & (df['trade_type'].str.upper() == 'SELL')]
top_sell = (
    eq_sell.groupby('ticker')
    .agg(
        sell_count=('politician', 'count'),
        politicians=('politician', lambda x: len(set(x))),
        name=('asset_name', 'first'),
    )
    .sort_values('sell_count', ascending=False)
    .head(10)
)
print('=== TOP 10 MOST SOLD TICKERS ===')
print(top_sell.to_string())

print()
# Date range of data
valid_dates = df[df['transaction_date'].str.len() == 10]['transaction_date']
print(f'Date range: {valid_dates.min()} to {valid_dates.max()}')
print(f'Trades with valid dates: {len(valid_dates)} / {len(df)}')
