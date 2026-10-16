Analyze cluster signals and politician sector alpha profiles from the latest data.

Steps:
1. Run `venv/Scripts/python cluster_analyzer.py` to regenerate cluster_signals.json and politician_profiles.json
2. From `data/cluster_signals.json`, show:
   - Total clusters detected
   - Top 10 clusters by avg_alpha (ticker, sector, politicians, alpha, win rate, n)
   - Breakdown by sector: how many clusters are semiconductor vs cybersecurity vs healthcare vs general
3. From `data/politician_profiles.json`, show:
   - Top politicians ranked by overall_alpha (min 10 priced buys)
   - For top 5 politicians: their best sector and sector-specific alpha breakdown
   - Flag the BCR paradox: any politician with BCR > 0.9 but negative alpha?
4. State the key insight in one sentence: which sector + politician combination produces the most reliable signal

Format the cluster table as: Ticker | Sector | Politicians | Avg Alpha | Win% | n
