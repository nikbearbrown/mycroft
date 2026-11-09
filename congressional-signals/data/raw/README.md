# data/raw/

**Unvalidated ingest outputs.** Written only by INGEST scripts (`scraper.py`).

Per SNICKERDOODLE P2: external sources are touched here and nowhere else.
Nothing in this folder may be treated as evidence until promoted to `data/verified/`
through the conformance gate (G1). See `../../DATA_CONTRACT.md`.

| File | Producer |
|------|----------|
| `trades.csv` | scraper.py — raw STOCK Act disclosures from Capitol Trades |
| `scraper_checkpoint.txt` | scraper.py — resume state (politician IDs done) |
