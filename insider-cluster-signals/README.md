# insider-cluster-signals

Turns public SEC **Form 4** insider-trade disclosures into sourced **STRONG / WATCH / SKIP**
signals. Research only — no trades placed, no financial advice.

Extends Lakonishok & Lee (2001) — *Are Insider Trades Informative?* — into the 2024–2026
era with per-trade SPY benchmarking. Corporate-insider sibling of the `congressional-signals`
module: same cluster methodology (2+ insiders, same ticker, 30-day window), but a tighter
disclosure regime — Form 4s file within **2 business days** of the trade (vs. 45 days under
the STOCK Act), giving cleaner event windows.

All code lives under `insider-cluster-signals/` — no changes to existing repo files.

## Pipeline

```
fetcher.py -> parser.py -> price_fetcher.py -> enricher.py -> cluster_analyzer.py -> signal_scorer.py
(EDGAR;       (raw->verified  (Yahoo daily      (30d raw/SPY/    (2+ insiders, same       (Week 3:
 network       gate: validate  closes for        alpha returns,   ticker, 30-day window,   conviction ->
 caller #1)    or reject, P3)  P-tickers+SPY;    immature windows role-weighted, traces    STRONG/WATCH/
                               network #2)       marked, P6)      to accessions, P3)       SKIP)
```

Week 3 adds the scorer, the LangGraph state machine (conformance gate halts the run — P4),
and dual outputs: `logs/run_*.json` for agents, `reports/signal_report_*.md` for humans (P5).

## Status

Week 2 — analytics layer live. Data spine (fetch → validate) plus price enrichment
(30-day SPY-adjusted alpha, methodology mirrors the congressional sibling) and cluster
detection (role-weighted: officer 1.5 > director 1.0 > 10%-owner 0.75 > other 0.5).
21 unit tests. See `logs/RUN_LOG.md` for every live run and gate decision.

## How to run

```bash
cd insider-cluster-signals
python fetcher.py --date 2026-07-10 --limit 25   # pull Form 4s for a filing date
python parser.py                                  # validate raw XML -> data/verified/trades.json
python price_fetcher.py --start 2026-06-01        # Yahoo closes for P-tickers + SPY
python enricher.py                                # 30d SPY-adjusted alpha per market trade
python cluster_analyzer.py                        # detect >=2-insider 30-day buy clusters
python -m unittest discover tests                 # 21 tests
```

Stdlib only — no dependencies to install.

## Mycroft / SNICKERDOODLE compliance

| Principle | Implementation |
|---|---|
| P2 verified data | `fetcher.py` is the only network caller; `parser.py` is the raw→verified gate |
| P3 provenance | every record traces to an EDGAR accession; SHA-256 per fetched file; rejects carry reasons |
| P4 hard gates | validation failures reject records; pipeline conformance gate lands in Week 3 |
| P5 two customers | agent log + human report split (Week 3–4) |
| P6 recipe authority | `recipes/insider-cluster-signal-agent.md` (Week 4) |
| P7 append-only log | `logs/RUN_LOG.md` |
