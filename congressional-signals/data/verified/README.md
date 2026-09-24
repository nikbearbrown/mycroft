# data/verified/

**Validated, gate-cleared data only.** Read by TOOL scripts
(`cluster_analyzer.py`, `langgraph_pipeline.py`, `server.py`).

Per SNICKERDOODLE P2/P3: every file here has passed the conformance gate (G1) and
carries provenance back to a `data/raw/` source. See `../../DATA_CONTRACT.md`.

| File | Producer | Gate |
|------|----------|------|
| `enriched_trades.csv` | enricher + market_adjusted | G2 (coverage ≥ 60%) |
| `cluster_signals.json` | cluster_analyzer.py | G3 |
| `politician_profiles.json` | cluster_analyzer.py | G3 |
| `signal_log.json` | langgraph_pipeline.py | G4 |
| `conformance_report.json` | conformance.py | G1 |
