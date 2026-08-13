# sec-filings-financial-metrics

Deterministic extraction of standardized financial metrics from SEC EDGAR XBRL
data, with full provenance and rule-based validation. Implements the
[`sec-filings-financial-metrics`](../../recipes/sec-filings-financial-metrics.yaml)
recipe. **No LLM in the critical path** — retrieval, extraction, and validation
are plain, reproducible code.

## Package layout (`secfma/`)

| Module | Responsibility |
|---|---|
| `config.py` | URLs, SEC User-Agent, rate limit, and repo-root `data/` output paths |
| `edgar_client.py` | Polite, cached EDGAR client (ticker→CIK, `companyfacts`) |
| `concept_map.py` | Canonical metric → ordered candidate `us-gaap` tags (the core) |
| `extractor.py` | Extract metrics, tagging every value with provenance |
| `metrics.py` | Derived ratios (margins, ROE, ROA, current ratio, D/E, YoY growth) |
| `validation.py` | Rule-based checks returning PASS / FAIL / UNKNOWN |
| `report.py` | Human-readable Markdown report with a provenance appendix |
| `cli.py` | Command-line entry point |
| `benchmark.py` | Score extraction accuracy + coverage vs a hand-verified golden set |

## Usage

Run from the repo root (standard library only — nothing to install):

```bash
python3 -m scripts.sec-filings-financial-metrics.secfma.cli --ticker MSFT --report
# or, from inside the package dir:
cd scripts/sec-filings-financial-metrics && python3 -m secfma.cli --ticker MSFT --report
# score extraction against the hand-verified golden set:
python3 -m secfma.benchmark --report
# offline: run the whole pipeline from a bundled fixture (no network):
python3 -m secfma.cli --sample --report
```

## Inputs

- `--ticker` (required): US-listed stock ticker, e.g. `MSFT`.
- `--forms` (default `10-K 10-Q`): filing forms to include.
- `--validate`: run rule-based validation checks.
- `--report`: also write a Markdown report (implies `--validate`).

## Outputs

- `data/raw/sec-filings-financial-metrics/` — cached, unmodified SEC responses
  (each wrapped with a `_provenance` fetch timestamp + source URL).
- `data/verified/sec-filings-financial-metrics/<TICKER>_financial_metrics.json`
  — extracted + derived metrics, every value carrying its XBRL tag, accession,
  form, period, filed date, and source-filing URL.
- `data/verified/sec-filings-financial-metrics/<TICKER>_report.md` — human report.

These outputs are generated artifacts; do not commit them (keep them distinct
from source data per `DATA_CONTRACT.md`).

## Side effects

- **Network:** read-only HTTPS GETs to `sec.gov` / `data.sec.gov` public APIs,
  rate-limited to ~7/sec, with a descriptive User-Agent (SEC policy). No writes
  to any external system, no credentials, no LLM calls.
- **Disk:** writes only under `data/raw|verified/sec-filings-financial-metrics/`.

## Offline mode & custom extensions

- **`--sample`** runs the full pipeline against a bundled fixture
  (`secfma/fixtures/`, company `SMPL`) with zero network calls — for tests, demos, and CI.
- **Custom XBRL extensions:** when a metric has no matching `us-gaap` tag, the
  extractor consults `secfma/custom_extension_map.json` — a human-curated map of
  `CIK → {metric: {namespace, tag}}`. Unmapped metrics stay `MISSING` (flagged for a
  human), never guessed. The sample fixture demonstrates this by resolving
  `research_and_development` from a company-specific `smpl:` extension.

## Status

SPECIFIED. Verified against Microsoft (FY2020–2025) and Apple (FY2024): 8/8
golden-set match at 0.5% tolerance; balance sheet balances to the dollar; offline
sample run passes all checks. See the recipe's `known_issues` for remaining
improvements (populate the override map for real filers, expand the golden set,
quarterly ratios).
