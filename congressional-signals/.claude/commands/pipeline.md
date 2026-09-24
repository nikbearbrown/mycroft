Run the full enrichment and analysis pipeline after scraping. Use this after scraping new politicians.

Steps (run sequentially — each depends on the previous):
1. Run `venv/Scripts/python enricher.py` — adds price columns to trades.csv → enriched_trades.csv. Report how many rows were enriched and the coverage %.
2. Run `venv/Scripts/python market_adjusted.py` — adds spy_return_30d and abnormal_return columns. Report BUY alpha and SPY avg.
3. Run `venv/Scripts/python conformance.py` — validate the enriched data. Report skip rate and gate failures.
4. Run `venv/Scripts/python cluster_analyzer.py` — detect clusters and build politician sector profiles. Report top 5 clusters by alpha.
5. Run `venv/Scripts/python signal_scorer.py` — score all BUY trades. Report STRONG/WATCH/SKIP counts.
6. Summarize: how many politicians now in dataset, total trades, top new STRONG signals, and whether any semiconductor/AI cluster signals appeared.

If any step fails, stop and report the error — do not continue to the next step.
