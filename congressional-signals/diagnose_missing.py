import pandas as pd
import sys

# force utf-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/enriched_trades.csv', dtype=str).fillna('')
total = len(df)
has_price = df['price_at_trade'].apply(lambda x: x not in ('', 'nan', 'None') and bool(x))
missing = df[~has_price].copy()

print(f"Total trades:       {total}")
print(f"Has price:          {has_price.sum()}  ({has_price.sum()/total*100:.1f}%)")
print(f"Missing price:      {len(missing)}  ({len(missing)/total*100:.1f}%)")
print()

done = set()

cat1 = missing[missing['ticker'].str.strip() == ''].index
done.update(cat1)
print(f"[1] Blank ticker (bonds/bills/munis):     {len(cat1):4d}  ({len(cat1)/total*100:.1f}%)")

rem = missing[~missing.index.isin(done)]
cat3 = rem[rem['ticker'].str.contains(r'\d', na=False)].index
done.update(cat3)
print(f"[2] Digit in ticker (options/warrants):   {len(cat3):4d}  ({len(cat3)/total*100:.1f}%)")

rem = missing[~missing.index.isin(done)]
cat4 = rem[rem['ticker'].str.len() > 5].index
done.update(cat4)
print(f"[3] Ticker >5 chars (foreign/OTC):        {len(cat4):4d}  ({len(cat4)/total*100:.1f}%)")

rem = missing[~missing.index.isin(done)]
cat5 = rem[rem['transaction_date'].str.strip() == ''].index
done.update(cat5)
print(f"[4] Valid ticker, missing date:           {len(cat5):4d}  ({len(cat5)/total*100:.1f}%)  <-- scraper date bug (now fixed)")

rem = missing[~missing.index.isin(done)]
cat6 = rem.index
print(f"[5] Valid ticker+date, yfinance no data:  {len(cat6):4d}  ({len(cat6)/total*100:.1f}%)")

print()
print("--- CAT 5 DETAIL: yfinance misses ---")
rem_df = missing.loc[list(cat6)]
uniq = rem_df[['ticker','asset_name']].drop_duplicates('ticker')
print(uniq.to_string(index=False))

print()
print("--- SIGNAL VALIDITY: impact on BUY trades ---")
total_buys = (df['trade_type'].str.upper() == 'BUY').sum()
buy_missing = missing[missing['trade_type'].str.upper() == 'BUY']
print(f"Total BUY trades:            {total_buys}")
print(f"BUY trades missing price:    {len(buy_missing)}  ({len(buy_missing)/total_buys*100:.1f}%)")
print()
for label, cat in [
    ('Non-equity (bonds/bills)', cat1),
    ('Options/warrants', cat3),
    ('>5 char tickers', cat4),
    ('Missing date (old scrape)', cat5),
    ('yfinance gap', cat6),
]:
    n = len(set(cat) & set(buy_missing.index))
    if n > 0:
        print(f"  {label:<30} {n:3d} BUY trades  ({n/total_buys*100:.1f}%)")

print()
print("--- FIXABILITY ---")
fixable_date = len(set(cat5) & set(buy_missing.index))
fixable_yf   = len(set(cat6) & set(buy_missing.index))
non_equity   = len(set(cat1) & set(buy_missing.index))
print(f"  Non-equity (not a signal issue):   {non_equity}")
print(f"  Fixable by re-scraping dates:      {fixable_date}  (scraper date bug already patched)")
print(f"  Fixable by ticker normalisation:   {fixable_yf}  (BRK/B->BRK-B, ADR lookups)")
print(f"  True unresolvable gap:             {len(buy_missing) - non_equity - fixable_date - fixable_yf}")
