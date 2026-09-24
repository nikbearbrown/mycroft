Run the full signal scoring pipeline on the latest enriched trades data.

Steps:
1. Run `venv/Scripts/python conformance.py` and report the skip rate and gate breakdown
2. Run `venv/Scripts/python signal_scorer.py` and show the STRONG/WATCH/SKIP summary
3. List the top 10 STRONG signals from `data/signal_log.json` with politician, ticker, score, cluster size, BCR, and alpha
4. Note how many signals are DRAFT (window still open) vs VERIFIED (result known)
5. Flag any STRONG signals in semiconductor or cybersecurity sectors — those are highest priority per the research thesis

Keep the output tight — a table for the top signals, one sentence summary of the skip rate.
