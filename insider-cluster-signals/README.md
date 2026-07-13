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
fetcher.py  ->  parser.py   ->  enricher.py  ->  cluster_analyzer.py  ->  signal_scorer.py
(EDGAR, the    (raw->verified   (prices +        (2+ insiders,           (role-weighted
 only network   gate: validate   SPY-matched      same ticker,            conviction ->
 caller, P2)    or reject, P3)   returns)         30-day window)          STRONG/WATCH/SKIP)
```

Weeks 3–4 add the LangGraph state machine (conformance gate halts the run — P4), the
recipe with lifecycle frontmatter, and dual outputs: `logs/run_*.json` for agents,
`reports/signal_report_*.md` for humans (P5).

## Status

Week 1 — data spine. `fetcher.py` and `parser.py` are live and verified against real
EDGAR data (see `logs/RUN_LOG.md`). Enrichment, clustering, and scoring are next.

## How to run

```bash
cd insider-cluster-signals
python fetcher.py --date 2026-07-10 --limit 25   # pull Form 4s for a filing date
python parser.py                                  # validate raw XML -> data/verified/trades.json
```

Stdlib only so far — no dependencies to install.

## Mycroft / SNICKERDOODLE compliance

| Principle | Implementation |
|---|---|
| P2 verified data | `fetcher.py` is the only network caller; `parser.py` is the raw→verified gate |
| P3 provenance | every record traces to an EDGAR accession; SHA-256 per fetched file; rejects carry reasons |
| P4 hard gates | validation failures reject records; pipeline conformance gate lands in Week 3 |
| P5 two customers | agent log + human report split (Week 3–4) |
| P6 recipe authority | `recipes/insider-cluster-signal-agent.md` (Week 4) |
| P7 append-only log | `logs/RUN_LOG.md` |
