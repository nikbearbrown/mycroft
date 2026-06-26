import pandas as pd

df = pd.read_csv('data/enriched_trades.csv')
print(f'Total enriched rows: {len(df)}')
print(f'Rows with price_at_trade: {df["price_at_trade"].notna().sum()}')
print(f'Rows with post-disclosure return: {df["pct_change_post_disclosure"].notna().sum()}')
print()

buys  = df[(df['trade_type'].str.upper() == 'BUY')  & df['pct_change_post_disclosure'].notna()]
sells = df[(df['trade_type'].str.upper() == 'SELL') & df['pct_change_post_disclosure'].notna()]

print(f'BUY trades with full price data:  {len(buys)}')
print(f'SELL trades with full price data: {len(sells)}')
print()
print('Average 30d post-disclosure return:')
print(f'  BUY  trades: {buys["pct_change_post_disclosure"].mean():+.2f}%  (n={len(buys)})')
print(f'  SELL trades: {sells["pct_change_post_disclosure"].mean():+.2f}%  (n={len(sells)})')
print()

# Top 10 best individual buy trades
print('TOP 10 INDIVIDUAL BUY TRADES (by 30d post-disclosure return):')
cols = ['politician', 'ticker', 'asset_name', 'transaction_date', 'disclosure_date', 'pct_change_post_disclosure']
top10 = buys.nlargest(10, 'pct_change_post_disclosure')[cols]
print(top10.to_string(index=False))
print()

# Politician leaderboard
print('POLITICIAN LEADERBOARD — avg post-disclosure return on BUYs:')
pol = buys.groupby('politician')['pct_change_post_disclosure'].agg(
    avg_return='mean',
    trades='count',
    win_rate=lambda x: (x > 0).mean() * 100
).sort_values('avg_return', ascending=False)
print(pol.round(2).to_string())
print()

# Cluster signal performance — tickers bought by 2+ politicians
print('CLUSTER SIGNAL PERFORMANCE (tickers bought by 2+ politicians):')
eq = buys[buys['ticker'].str.isalpha() & buys['ticker'].str.len().between(1, 5)]
cluster = eq.groupby('ticker').agg(
    politicians=('politician', lambda x: list(set(x))),
    n_pols=('politician', lambda x: len(set(x))),
    avg_return=('pct_change_post_disclosure', 'mean'),
    asset_name=('asset_name', 'first')
).query('n_pols >= 2').sort_values('avg_return', ascending=False)
print(cluster[['asset_name', 'n_pols', 'avg_return']].round(2).to_string())
