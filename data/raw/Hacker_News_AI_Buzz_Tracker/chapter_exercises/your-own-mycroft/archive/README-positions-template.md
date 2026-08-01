# How to turn the templates into a real run

These are templates, not data — `book/positions.csv.template` and `benchmark/spy.csv.template` contain no real numbers, so `book/returns-vs-benchmark.md` correctly stays a halted-run record until they're filled in and saved as `book/positions.csv` / `benchmark/spy.csv` (without the `.template` suffix).

## positions.csv — a paper portfolio, no brokerage account needed

| Column | What goes here | Where to get it |
|---|---|---|
| ticker | Any ticker you're curious about (real holding or hypothetical) | — |
| entry_price | The price on the date you're pretending you bought | Any free quote site's historical price for that date (Yahoo Finance → ticker → Historical Data) |
| current_price | Today's price | Any free quote site's current quote |
| weight | What fraction of the paper portfolio this position is (weights across all rows should sum to 1) | You decide — e.g. equal-weight three positions at 0.333 each |

Example, filled in (illustrative numbers only — replace with real quotes before running):

```
ticker,entry_price,current_price,weight
META,600.00,715.00,0.40
AAPL,225.00,232.00,0.35
SPY,560.00,590.00,0.25
```

## spy.csv — the benchmark

| Column | What goes here | Where to get it |
|---|---|---|
| date | The two dates bracketing your period (the date matching your entry_price date, and today) | — |
| close | SPY's closing price on each of those two dates | Yahoo Finance → SPY → Historical Data, or stooq.com |

Example:

```
date,close
2026-01-15,560.00
2026-07-23,590.00
```

## Once both files are real

Ask me to re-run the Chapter 6 CLI exercise (Exercise 4) against `book/positions.csv` and `benchmark/spy.csv`. I'll compute each position's contribution, the total portfolio return, the benchmark return, and the active return, with the independent re-sum check the exercise requires — read-only against your two files, no brokerage connection, no trade suggested.
