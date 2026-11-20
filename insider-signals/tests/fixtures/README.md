# Test fixtures — insider-signals

| File | What it is | Provenance |
|---|---|---|
| `sec_insider_dataset_page_trimmed.html` | SEC data-set page cut down to its ZIP links (both hosting-folder styles, one absolute href) and the readme link | Hrefs copied from https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets on 2026-11-03 |
| `form345_header_only.zip` | ZIP with SUBMISSION, REPORTINGOWNER, NONDERIV_TRANS header rows only — **no records** | Header rows copied from SEC's 2026 Q3 data set (`2026q3_form345.zip`, SHA-256 `a4e6a681…92c90f3`), downloaded 2026-11-03. The file's headers differ slightly from the readme (e.g. `FORM3_HOLDINGS_REPORTED`, `AFF10B5ONE`). INGEST never reads ZIP contents, so this exercises download, hash and extract with no invented data. |
| `parse_sample/` | SUBMISSION, REPORTINGOWNER, NONDERIV_TRANS, FOOTNOTES, DERIV_TRANS with 17 transaction rows built to hit every PARSE branch (each buy-filter failure, AFF10B5ONE variants, joint filing, private / ESPP / 10b5-1 footnotes, a Form 5 row) | Headers copied from the real 2026 Q3 files on 2026-11-03. **Rows are synthetic**: accessions `0000000000-26-0000NN`, CIKs 8000001–9000007, names "Owner …" / "Example Issuer …". |

Fixtures are inputs to offline tests only. They are not SEC data and are never promoted.
