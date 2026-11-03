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
| `data/raw/form345/request_log.jsonl` | raw | `ingest.py`, G2 spot-check | one line per HTTP request: `ts`, `url`, `status`, `elapsed_ms` | yes |
| `data/raw/form345/<YYYY>q<N>/*` | raw | `ingest.py` (unzip) | SEC tables as extracted (8 `.tsv` files plus SEC's `FORM_345_metadata.json` and `FORM_345_readme.htm`), and `_EXTRACTED_FROM.json` (ZIP hash, member list) | no |
| `data/raw/parsed/form4_transactions.csv` | raw | `parse.py` | every Form 4 / 4-A non-derivative row joined to its submission and owner(s), plus `buy_class` (`qualifying_buy` or an exclusion reason) | no |
| `data/raw/prices/*.csv` | raw | `enrich.py` | daily adjusted close per ticker and SPY, with `fetched_at` | no |
| `data/verified/insider_buys.csv` | verified | `conformance.py` (on pass) | one row per qualifying buy: `accession_number`, `nonderiv_trans_sk`, `document_type`, `filing_date`, `trans_date`, `issuer_cik`, `issuer_name`, `ticker_as_filed`, `rptowner_cik`, `rptowner_name`, `relationship`, `title`, `role` (mapped), `shares`, `price`, `value_usd`, `shares_owned_after`, `direct_indirect`, `is_10b5_1`, `private_purchase_flag`, `amends_accession` (null if original), `source_quarter` | yes, if size allows; otherwise hash in manifest |
| `data/verified/conformance-audit.md` | verified | `conformance.py` | audit (findings, not pass/fail): rows in/out, exclusions by reason and code, amendments, blank symbols, late filings, joint filings, filing spot-check results | yes |
| `data/verified/enriched_buys.csv` | verified | `enrich.py` (on G3 pass) | `insider_buys.csv` fields + `entry_date`, `entry_price`, `exit_date`, `exit_price`, `stock_return`, `spy_return`, `abnormal_return`, `window_days`, `price_status` | yes |
| `data/verified/clusters.json` | verified | `signals.py` | per cluster: `issuer_cik`, `ticker`, `signal_date`, `members` (`rptowner_cik`, role, `value_usd`, `accession_numbers`), `score`, `label`, `label_reasons`, `abnormal_return` (null until the window closes) | yes |
| `logs/run_<run_id>.json` | logs | `langgraph_pipeline.py` | full graph state, append-only run log, input file hashes | yes |
| `reports/review_packet_<run_id>.md` | report | pipeline | pre-attestation packet, marked NOT ATTESTED | yes |
| `reports/signal_report_<run_id>.md` | report | pipeline, after G6 | attested report with filing links | yes |

---

## Validation gates

| Gate | Check | Tool | Pass condition |
|---|---|---|---|
| G1 | download integrity + fair access | `ingest.py --verify` | every requested quarter present; hash matches manifest; request log within rate; no unhandled 403/429 |
| G2 | schema, keys, dates, codes, buy-filter purity, CIKs present | `conformance.py` | all halting checks pass (exit 0) → `insider_buys.csv` written |
| G3 | price coverage + window rule | `enrich.py --check` | coverage ≥ minimum defined in the recipe; every unpriced row has a `price_status` reason |
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
- **Timeliness:** `TRANS_TIMELINESS` is `E` (early), `L` (late) or empty (on time). Late
  filings are kept. The lag is reported.
