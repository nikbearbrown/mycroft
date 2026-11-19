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

## Agent tool: `get_verified_financials`

Other Mycroft agents call this tool instead of asking a model for a financial figure. It wraps the same deterministic pipeline (`secfma/tool.py`), so no language model is involved.

```python
from secfma.tool import get_verified_financials, run_tool, TOOL_SPEC
get_verified_financials("MSFT", fiscal_year=2024, metrics=["revenue", "net_income"])
run_tool({"ticker": "MSFT", "fiscal_year": 2024})   # raw tool-call arguments from an agent
```

```bash
python3 -m secfma.tool --ticker MSFT --year 2024        # JSON to stdout
python3 -m secfma.tool --sample                          # offline, bundled fixture
python3 -m secfma.tool --spec                            # tool definition (input_schema)
python3 -m secfma.tool --openai-spec                     # same, OpenAI function format
```

**What a calling agent can rely on:**
- **Deterministic.** The same inputs and cached SEC data always give the same output (`method.llm_in_path` is `false`).
- **Never guesses.** A metric with no reliable source is `"status": "MISSING"` with `value: null` and a `reason`. Never 0.
- **Provenance on every value.** Each value carries `source_tag`, `tag_source` (`us-gaap` / `custom-extension` / `derived`), `accession`, `form`, `filed` and `source_url`.
- **Validation attached.** PASS / FAIL / UNKNOWN checks run on exactly the returned values. For example, a FAIL on the accounting identity tells the agent the balance sheet doesn't tie for that period.
- **Errors are data.** Failures come back as `{"ok": false, "error": {"type": ...}}`. The types are `invalid_argument`, `unknown_metric`, `ticker_not_found`, `fiscal_year_not_found`, `no_annual_data`, `fetch_failed` and `no_sample_fixture`.

Tests (offline, standard library only): `python3 -m unittest discover -s tests`

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
