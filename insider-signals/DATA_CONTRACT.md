# DATA_CONTRACT — Insider Signal Intelligence

Per SNICKERDOODLE P2 (verified data) and P3 (provenance). Defines where data lives, how
it is validated, and what may be trusted. The recipe
(`recipes/insider-signal-agent.md`) is canonical for the pipeline. This file is
canonical for the data.

---

## Two-tier model

```
data/raw/        ← ingest and parse outputs only. Unvalidated. Written by ingest.py, parse.py, enrich.py (prices).
data/verified/   ← validated outputs only. Written only when conformance passes. Read by signals.py,
                   langgraph_pipeline.py, server.py.
```

**Rules**

- Nothing enters `data/verified/` without passing the G2 conformance gate.
- Only `ingest.py` (SEC), `enrich.py` (prices) and the G2 spot-check (sample of individual
  Form 4 filings) touch the network. Everything downstream reads local verified files.
- **Identity is a CIK, never a name.** Companies are `ISSUERCIK`, insiders are `RPTOWNERCIK`.
  Names and tickers are display fields (see the entity rule in the repo-root `DATA_CONTRACT.md`).
- Missing data is marked missing with a reason. It is never filled in or silently dropped.
- Large raw downloads stay out of git (see `.gitignore`). Provenance is kept by
  `manifest.json` (URL, time, SHA-256), which is committed, so anyone can re-download and
  check the same bytes.

---

## Source: SEC Insider Transactions Data Sets

- **Page:** https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets
- **Documentation:** https://www.sec.gov/files/insider_transactions_readme.pdf (table
  definitions and the Trans Code List; field names below are taken from it)
- **Coverage:** January 2006 → latest completed quarter (2026 Q3 as of 2026-11-03). Updated quarterly.
- **Format:** one ZIP per quarter; up to 8 tab-delimited, UTF-8 files; dates as `DD-MON-YYYY`.
- **SEC caveats:** data is "as filed", including amendments, and "may contain redundancies,
  inconsistencies, and discrepancies"; SEC "cannot guarantee the accuracy"; it is "not a
  substitute for such filings". Filings made after 5:30 pm ET on a quarter's last business
  day appear in the next quarter's data set.
- **Access rules:** User-Agent with contact info (`SEC_USER_AGENT`), at most 10 requests/second
  (this module defaults to 1/s), efficient downloads only. See the recipe's fair-access section.

### Fields used (from SEC's table definitions)

| Table | Key | Fields used |
|---|---|---|
| SUBMISSION | `ACCESSION_NUMBER` | `FILING_DATE`, `PERIOD_OF_REPORT`, `DATE_OF_ORIG_SUB`, `DOCUMENT_TYPE`, `ISSUERCIK`, `ISSUERNAME`, `ISSUERTRADINGSYMBOL`, `AFF10B5ONE` (added for 2023+; not in the readme, confirmed in the 2026 Q3 file with values `0`, `1`, `false`, `true` and blank) |
| REPORTINGOWNER | `ACCESSION_NUMBER` + `RPTOWNERCIK` | `RPTOWNERNAME`, `RPTOWNER_RELATIONSHIP` (OFFICER, DIRECTOR, TENPERCENTOWNER, OTHER), `RPTOWNER_TITLE`, `RPTOWNER_TXT` |
| NONDERIV_TRANS | `ACCESSION_NUMBER` + `NONDERIV_TRANS_SK` | `SECURITY_TITLE`, `TRANS_DATE`, `DEEMED_EXECUTION_DATE`, `TRANS_FORM_TYPE`, `TRANS_CODE`, `EQUITY_SWAP_INVOLVED`, `TRANS_TIMELINESS`, `TRANS_SHARES`, `TRANS_PRICEPERSHARE`, `TRANS_ACQUIRED_DISP_CD`, `SHRS_OWND_FOLWNG_TRANS`, `DIRECT_INDIRECT_OWNERSHIP`, `NATURE_OF_OWNERSHIP` |
| FOOTNOTES | `ACCESSION_NUMBER` + `FOOTNOTE_ID` | `FOOTNOTE_TXT` (read for private-purchase and 10b5-1 flags) |

DERIV_TRANS, DERIV_HOLDING, NONDERIV_HOLDING and OWNER_SIGNATURE are downloaded as part of
the ZIP but not used in v1.

---

## File contracts

| File | Layer | Producer | Contents / required fields | In git? |
|---|---|---|---|---|
| `data/raw/form345/<YYYY>q<N>_form345.zip` | raw | `ingest.py` | SEC ZIP, unchanged | no (re-downloadable) |
| `data/raw/form345/manifest.json` | raw | `ingest.py` | per quarter: `quarter`, `source_url`, `retrieved_at` (UTC ISO-8601), `sha256`, `bytes`, `http_status`, `user_agent_set` (bool; the value itself is not stored) | yes |
| `data/raw/form345/request_log.jsonl` | raw | `ingest.py` | one line per HTTP request: `ts`, `url`, `status`, `elapsed_ms` | yes |
| `data/raw/filings/<accession>.txt` + `.json` | raw | `conformance.py` (spot-check) | EDGAR full-submission text of each sampled filing, unchanged; sidecar with `url`, `sha256`, `bytes`, `retrieved_at`. Cached: never fetched twice | no (re-downloadable; URL and hash also in `conformance_summary.json`) |
| `data/raw/filings/request_log.jsonl` | raw | `conformance.py` (spot-check) | same format as INGEST's log. Kept separate so a spot-check 404 on one EDGAR path is not read by G1 as an unhandled status | yes |
| `data/raw/conformance/conformance-audit-FAILED-<ts>.md`, `conformance_summary-FAILED-<ts>.json` | raw | `conformance.py` (on failure) | the audit and summary of a run that did not promote; `data/verified/` is left unchanged | yes |
| `data/raw/form345/<YYYY>q<N>/*` | raw | `ingest.py` (unzip) | SEC tables as extracted (8 `.tsv` files plus SEC's `FORM_345_metadata.json` and `FORM_345_readme.htm`), and `_EXTRACTED_FROM.json` (ZIP hash, member list) | no |
| `data/raw/parsed/<YYYY>q<N>_form4_transactions.csv` | raw | `parse.py` | one row per Form 4 / 4-A non-derivative transaction (joint filings not duplicated; `owners` is a JSON list of every reporting owner with `cik`, `name`, `relationship`, `title`), plus `is_10b5_1` (plan / no_plan / unknown), `private_purchase_flag`, `espp_or_drip_flag`, `flag_evidence`, `footnote_mentions_10b5_1`, and `buy_class` (`qualifying_buy` or one exclusion reason). Columns: `parse.OUTPUT_COLUMNS` | no (rebuildable) |
| `data/raw/parsed/<YYYY>q<N>_parse_summary.json` | raw | `parse.py` | every count: funnel, rows by document type and code, exclusions by reason, flag counts, raw value distributions, review samples (accession + issuer only) | yes |
| `data/raw/parsed/<YYYY>q<N>_parse-audit.md` | raw | `parse.py` | human view of the summary (an audit: findings, not pass/fail) | yes |
| `data/raw/prices/<SYMBOL>.csv` | raw | `enrich.py` | daily bars from Yahoo Finance (yfinance, `auto_adjust=False`): `date`, `close`, `adj_close`, `volume`; one file per symbol with data, SPY included | no (re-downloadable) |
| `data/raw/prices/prices_manifest.json` | raw | `enrich.py` | per symbol requested: `status` (ok / no_data / fetch_error), `requested_start`, `requested_end` (exclusive), `fetched_at`, `error`, and for ok `rows`, `first_date`, `last_date`, `sha256` | yes |
| `data/raw/prices/splits_manifest.json` | raw | `enrich.py` | per symbol with a priced buy: `status`, `requested_start`, `requested_end` (exclusive), `fetched_at`, `error`, and for ok `splits` (list of `[date, ratio]`, Yahoo's Stock Splits; 2.0 = 2-for-1, 0.1 = 1-for-10). Used by Rule 9 | yes |
| `data/raw/prices/fetch_log.jsonl` | raw | `enrich.py` | one line per batch request: `ts`, `kind` (prices / splits), `batch`, `attempt`, `symbols`, `ok`, `failed`, `refused`, `reason`, `elapsed_ms` | yes |
| `data/raw/enrich/enrich-audit-FAILED-<ts>.md`, `enrich_summary-FAILED-<ts>.json` | raw | `enrich.py` (on failure) | audit and summary of a run that did not promote; `data/verified/` unchanged | yes |
| `data/verified/insider_buys.csv` | verified | `conformance.py` (on pass) | one row per qualifying buy, flagged buys included (`PRE_REGISTRATION.md` Rule 1). Columns: `conformance.VERIFIED_COLUMNS`: keys, dates, issuer, `owner_count`, `rptowner_ciks` / `rptowner_names` / `titles` (`;`-joined, every owner of a joint filing), `relationships`, `owners` (JSON), code, shares, price, `value_usd`, holdings, `trans_timeliness`, `is_10b5_1`, `private_purchase_flag`, `espp_or_drip_flag`, `flag_evidence`, `source_quarter`, `filing_index_url`. `amendment_match` (4/A: unique / resolved_rule_2a / multiple / none_in_study / no_date_of_orig_sub), `amends_accession` (the linked original), `repeats_original_buy` (`<accession>#<sk>` of the original buy it repeats, for Rule 2). Not yet included: `role` (needs TODO 7) | **no** (gitignored from 2026-11-04; ~45 MB for the study period). Its SHA-256 is recorded in `conformance_summary.json` (`insider_buys_sha256`) and `status.md`; rebuild with `parse.py` + `conformance.py` |
| `data/verified/conformance_summary.json` | verified | `conformance.py` (on pass) | every halting check, finding and spot-check row; `insider_buys_sha256` | yes |
| `data/verified/conformance-audit.md` | verified | `conformance.py` (on pass) | audit (findings, not pass/fail): halting-check table, rows in/out, exclusions by reason and code, Rule 1 counts, amendments, blank symbols, late filings and lag, joint filings, precision, filing spot-check results | yes |
| `data/verified/enriched_buys.csv` | verified | `enrich.py` (when its halting checks pass) | one row per verified buy, none dropped. `insider_buys.csv` columns + `symbol_used`, `price_status`, Rule 9 fields (`trade_ref_date`, `trade_ref_close_unadjusted`, `split_factor`, `filed_vs_close_ratio`, `filing_price_check`: ok / mismatch / not_checkable), `entry_date`, `entry_price`, `spy_entry_price`, and per window N ∈ {21, 63} (`PRE_REGISTRATION.md` Rule 7): `exit_date_Nd`, `exit_price_Nd`, `spy_exit_price_Nd`, `stock_return_Nd`, `spy_return_Nd`, `abnormal_return_Nd`, `window_status_Nd`. Columns: `enrich.ENRICHED_COLUMNS`. Status values are listed in `enrich.py` | **no** (gitignored, like `insider_buys.csv`); SHA-256 in `enrich_summary.json` (`enriched_buys_sha256`) |
| `data/verified/enrich_summary.json` | verified | `enrich.py` | halting checks, coverage, price_status and window counts by quarter, price range, fetch counts; no return statistics | yes |
| `data/verified/enrich-audit.md` | verified | `enrich.py` | audit (findings, not pass/fail) of the same; no return statistics | yes |
| `data/verified/clusters.json` | verified | `signals.py` | per cluster: `issuer_cik`, `ticker`, `signal_date`, `members` (`rptowner_cik`, role, `value_usd`, `accession_numbers`), `score`, `label`, `label_reasons`, `abnormal_return` (null until the window closes) | yes |
| `logs/run_<run_id>.json` | logs | `langgraph_pipeline.py` | full graph state, append-only run log, input file hashes | yes |
| `reports/review_packet_<run_id>.md` | report | pipeline | pre-attestation packet, marked NOT ATTESTED | yes |
| `reports/signal_report_<run_id>.md` | report | pipeline, after G6 | attested report with filing links | yes |

---

## Validation gates

| Gate | Check | Tool | Pass condition |
|---|---|---|---|
| G1 | download integrity + fair access | `ingest.py --verify` | every requested quarter present; hash matches manifest; request log within rate; no unhandled 403/429 |
| G2 | hash, required columns, keys, dates, codes, buy-filter purity, CIKs present | `conformance.py` | all halting checks pass (exit 0) → `insider_buys.csv` written; otherwise `data/verified/` unchanged. Date and code checks apply to the rows being promoted; anomalies elsewhere are audit findings |
| G3 | price coverage + window rule | `enrich.py` (promotion), `enrich.py --check` | input hash matches G2; SPY cached; cache consistent; every buy has a `price_status` and window statuses; entry/exit follow Rule 7 and returns recompute; Rule 9 fields recompute and every priced buy has split data; coverage ≥ 80% (Rule 8). Clearing G3 is the owner's logged decision |
| G4 | thresholds match pre-registration | `signals.py --check-prereg` | thresholds in code = `PRE_REGISTRATION.md` |

G5 and G6 concern the agent and the report; see the recipe.

---

## Quality notes (known before the first run)

- **Most Form 4 rows are not buys.** Grants (A), exercises (M, X, O), tax withholding (F) and
  sales (S) are excluded by code. The audit reports how many, per code.
- **Code P covers private as well as open-market purchases.** It cannot be split by code
  alone; flagged rows are handled by the recipe's private-purchase rule.
- **Amendments (4/A)** are separate submissions, linked by `DATE_OF_ORIG_SUB`. The original
  row is kept, and the amendment counts only from its own filing date onward.
- **Joint filings:** one accession can list several reporting owners. A transaction row is
  not duplicated per owner; the recipe defines how many insiders it counts as.
- **`RPTOWNER_TITLE` is free text** and must be mapped to roles. Unmapped titles are listed in the audit.
- **`RPTOWNER_RELATIONSHIP`** is comma-separated and mixed case in the 2026 Q3 file, e.g.
  `Officer`, `Director,Officer`, `TenPercentOwner`, `Director,Officer,TenPercentOwner`. The
  readme gives uppercase values. Map case-insensitively after splitting on commas.
- **Readme vs. file:** the file's SUBMISSION header has `FORM3_HOLDINGS_REPORTED` where the
  readme says `FORM3_HOLDING_REPORTED`. Treat the downloaded header as authoritative, and
  have G2 check the actual header against the fields this contract uses.
- **`ISSUERTRADINGSYMBOL`** is as filed. It may be blank, `NONE`, or out of date after a
  rename. Prices are fetched by this symbol, and failures are recorded, not guessed.
- **Prices come from yfinance**, which is not an authoritative source and is weak on
  delisted tickers. Delistings appear as missing prices, which is a survivorship risk that
  shows up in G3 coverage.
- **Shares and prices are rounded to 2 decimals in the data set** (found by the G2 spot-check,
  2026-11-04: 10 of 25 sampled buys differ from their filing only by rounding, e.g. a filed
  price of `0.006` is `0.01` in the data set). SEC's metadata does not say so. Low-priced buys
  are affected most (2026 Q3: 588 buys below $1.00, 92 at $0.05 or less). A filed price below
  $0.005 rounds to `0.00`, so some `p_price_missing_or_not_positive` exclusions may be real
  sub-cent buys. Not corrected. Decided 2026-11-04: sub-$1 buys are excluded from clustering by
  `PRE_REGISTRATION.md` Rule 4; at $1.00 and above rounding moves price by at most 0.5%, accepted.
- **Amendments can repeat their original's buy.** In 2026 Q3, 42 buys on 4/A filings have the
  same trade date, shares and price as a buy on their original. Both stay in verified;
  `repeats_original_buy` marks the repeat, and Rule 2 counts it once for clustering.
- **Timeliness:** `TRANS_TIMELINESS` is `E` (early), `L` (late) or empty (on time). Late
  filings are kept. The lag is reported.
