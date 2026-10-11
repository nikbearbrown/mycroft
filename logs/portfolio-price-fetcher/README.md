# Portfolio Visualization Agent: how to run the closed steps

`recipes/portfolio-price-fetcher.md` (steps 1, 3, 5) and `recipes/portfolio-dashboard.md` (step 1), in
sample mode. Python 3.9+ standard library only; no network, no keys. The parity check also needs `node`.
Run every command from the repository root.

## Run it

```bash
python3 scripts/tools/portfolio-price-fetcher-verify-provenance.py           # step 1, price fetcher
python3 scripts/tools/portfolio-dashboard-verify-provenance.py               # step 1, dashboard
python3 scripts/gigo/portfolio-price-fetcher-validate-data-shape.py          # step 3 (clean set)
python3 scripts/gigo/portfolio-price-fetcher-validate-data-shape.py --fixture-set defective   # exits 1 by design
python3 scripts/tools/portfolio-price-fetcher-run-approved-tools.py          # step 5 (reads step 3's output)
python3 scripts/tools/portfolio-price-fetcher-parity-check.py                # port vs the original JavaScript
python3 scripts/tools/portfolio-price-fetcher-self-test.py                   # every check, recorded
```

Add `--now 2026-10-10T00:00:00+00:00` to the two provenance scripts to reproduce the committed records
exactly.

## What each one does, and where it writes

| Script | Stops (exit 1) when | Writes |
|---|---|---|
| `portfolio-price-fetcher-verify-provenance.py` | the declared workflow is missing or unparseable; its nodes differ from the recipe's node table; the portfolio differs between *Define Portfolio* and *Calculate Metrics*; a fixture no longer matches `sample/manifest.json` | `logs/portfolio-price-fetcher-provenance-<date>.json` |
| `portfolio-dashboard-verify-provenance.py` | the same for the dashboard, or its *Call Portfolio Price Fetcher* node names another workflow | `logs/portfolio-dashboard-provenance-<date>.json` |
| `portfolio-price-fetcher-validate-data-shape.py` | any response breaks the contract (see the recipe's step 3); every finding is still reported | `data/verified/portfolio-price-fetcher/<set>/validated.json` and `validate-audit.md` |
| `portfolio-price-fetcher-run-approved-tools.py` | step 3 rejected anything, or a ticker is outside the portfolio; it writes nothing then | `data/verified/portfolio-price-fetcher/<set>/portfolio-summary.json` and `logs/portfolio-price-fetcher-run-approved-tools-<date>.json` |
| `portfolio-price-fetcher-parity-check.py` | the port and the original JavaScript differ on any compared field | stdout (`--json` to save) |
| `portfolio-price-fetcher-self-test.py` | any check does not behave as expected | `logs/portfolio-price-fetcher/self-test-results.{json,md}` |

## The sample corpus

`data/raw/portfolio-price-fetcher/sample/` holds Yahoo Finance chart responses shaped exactly as
*Calculate Metrics* reads them. **Every price is invented** and labelled "not market data" in its file.

- **`clean/`:** the workflow's own five tickers, each exercising one behaviour:
  - NVDA: a `toFixed` tie in the total
  - GOOGL: a null price that falls back to `previousClose`
  - META: a zero price that also falls back, because JavaScript's `||` treats 0 as missing
  - AMD: a loss
  - MSFT: a plain gain
- **`defective/`:** five catalogued defects, each naming the step that must catch it. The truncated
  response is stored as `.txt`, so the repository's conformance gate, which parses every `.json`, stays green.
- **`manifest.json`:** the SHA-256 of every file. Step 1 refuses fixtures that changed after it was frozen.

`data/raw/portfolio-price-fetcher/run-envelope.json` declares sample mode and the `as_of` timestamp that
stands in for the original's `new Date()`, so reruns are byte-identical.

## Not covered yet

- Price fetcher steps 2, 4 and 6 and the report-script mapping; dashboard steps 2–6 and its two script
  mappings. All are still `[TODO: DEV]`, and both recipes stay `DRAFT`.
- Live mode. There is no approval record, and the Yahoo Finance call is only a recorded handoff
  (`approved_for_live_action: false`).
