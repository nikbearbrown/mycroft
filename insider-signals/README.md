# Insider Trading Signals

**Do open-market purchases by company insiders, especially several insiders buying
together, beat the market, and how many of them should simply be skipped?**

A planned, auditable research pipeline. It reads SEC Form 4 filings, keeps only real
open-market purchases, adjusts every return for the market (SPY), detects cluster buys
(2+ insiders at the same company within 30 days), and scores them **STRONG / WATCH / SKIP**.
No signal is reported until a named human has attested to the run.

> Mycroft module, modeled on [`congressional-signals/`](../congressional-signals/).
> Built as a Fellow at Humanitarians AI under the Snickerdoodle contract
> ([`SNICKERDOODLE.md`](../SNICKERDOODLE.md)). **Research only. Not financial advice. No trades are placed.**

## Status

**DRAFT. Spec and data contract only; no scripts yet.** See [`status.md`](status.md).

## Architecture (planned)

```
 INGEST              PARSE + GIGO                    ENRICH            SIGNALS / AGENT / REPORT
┌─────────────┐   ┌──────────────────────────┐   ┌─────────────┐   ┌────────────────────────────┐
│ingest.py    │ → │parse.py (trans codes;     │ → │enrich.py    │ → │signals.py (clusters, score) │
│SEC bulk     │   │ only open-market buys)    │   │prices, SPY  │   │langgraph_pipeline.py        │
│Form 3/4/5   │   │conformance.py (G2)        │   │abnormal ret │   │  → human attestation (G6)   │
│data sets    │   │                           │   │             │   │  → sourced report           │
└─────────────┘   └──────────────────────────┘   └─────────────┘   └────────────────────────────┘
 data/raw/  ─────────────────────────────────→  data/verified/  ──→  logs/ + reports/
```

Data source: SEC's **Insider Transactions Data Sets** (quarterly bulk files) for v1, with
a sample checked against individual Form 4 filings. The recipe explains why.

## Read in this order

| File | What |
|---|---|
| [`recipes/insider-signal-agent.md`](recipes/insider-signal-agent.md) | Canonical spec: stages, look-ahead rule, gates G1–G6, TODOs |
| [`DATA_CONTRACT.md`](DATA_CONTRACT.md) | Data locations, SEC fields used, validation rules |
| [`status.md`](status.md) | Current lifecycle state and next actions |
| [`_MANIFEST.md`](_MANIFEST.md) | Navigation map |
| [`logs/RUN_LOG.md`](logs/RUN_LOG.md) | Append-only history |

## Setup (once scripts exist)

```bash
pip install -r requirements.txt
export SEC_USER_AGENT="Your Name your-email@example.org"   # required by SEC fair-access rules
python -m unittest discover -s tests
```

## Author

**Gomathy S.** ([@GomathySelvamuthiah](https://github.com/GomathySelvamuthiah)) · Humanitarians AI Fellow

*Data: public SEC EDGAR filings and SEC's Insider Transactions Data Sets; prices via Yahoo
Finance. For research and education only.*
