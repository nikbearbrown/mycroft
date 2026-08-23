# Database setup

Supabase Postgres. Two layers, on purpose:

| Layer | Where | Size | What it is |
|---|---|---|---|
| Private holdings | `data/parquet/<quarter>/private_holdings.parquet` | ~22M rows / 14 quarters | Every Level 3 row without a real CUSIP. Local, DuckDB-queryable, rebuildable from the zips. |
| Universe holdings | Postgres `raw_holdings` | ~5,800 rows / 14 quarters | The universe v1 subset that entity resolution and marks consume. |

`plan.md` puts the whole private layer in `raw_holdings`. Measured, that is ~694,000
rows per quarter (`docs/feasibility.md` §5) — 22 million over 14 quarters, past what a
Supabase free tier holds. So the wide layer stays in Parquet, where it is still
re-runnable and still queryable, and Postgres carries the part the pipeline reads
repeatedly. The append-only invariant applies to both.

---

## 1. Get the connection string

**This is the step that has already cost this project time.** Supabase shows several
connection strings on one page and only one of them works with `psycopg2`.

1. Supabase dashboard → your project
2. **Project Settings → Database → Connection string → URI**
3. Copy the **URI**, which looks like:

```
postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

It does **not** look like `https://<project-ref>.supabase.co` — that is the REST API
URL, and `psycopg2` cannot use it. If `DATABASE_URL` starts with `https://`, every load
command will stop and tell you so rather than failing halfway through.

If the URI has `[YOUR-PASSWORD]` in it, substitute the database password. If the
password contains `@`, `:`, `/` or `?`, percent-encode it (`@` → `%40`).

Put it in `.env`:

```
DATABASE_URL=postgresql://postgres.abcdefgh:s3cret@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

`.env` is gitignored. Never commit it.

### Which port

| Port | Mode | Use it for |
|---|---|---|
| 5432 | session pooler | This project. Long-lived connections, full SQL, prepared statements. |
| 6543 | transaction pooler | Serverless. Does not support prepared statements; `psycopg2.extras.execute_values` misbehaves. |

Use **5432**.

## 2. Create the schema

```bash
python -m src.db.connect
```

Verifies the URL, applies `src/db/schema.sql`, and prints the tables it finds. Idempotent
— run it as often as you like. Expected output:

```
connected: PostgreSQL 15.x
tables: filings, funds, raw_holdings, runs
```

## 3. Load

```bash
python -m src.ingest.download_bulk 2026q2      # ~450 MB, resumable
python -m src.ingest.build_parquet --all       # 14 quarters -> Parquet
python -m src.db.load --all                    # Parquet -> Postgres
python scripts/reconcile.py --db               # the reconciliation table
```

Every step is idempotent, so the safe recovery from any failure is to run the same
command again:

- `funds` and `filings` upsert on their natural keys (`(cik, series_id)`, `accession`).
- `raw_holdings` is `ON CONFLICT DO NOTHING` on `(filing_id, holding_id)` — it is
  append-only, so a re-run must be a no-op on rows already present, never a rewrite.

## 4. Disk

The zips are ~450 MB each and expand to ~1.5 GB, of which `FUND_REPORTED_HOLDING.tsv`
is 910 MB. `build_parquet` therefore works one quarter at a time: extract only the five
TSVs the project reads, filter, write Parquet, delete the TSVs. Peak disk stays under
2 GB. Pass `--keep-tsv` to keep them for ad-hoc DuckDB work.

Fourteen quarters of zips are ~5.9 GB; the Parquet output is a few hundred MB. The zips
can be deleted once Parquet is built — `build_parquet` will tell you to re-download if
you ask for a quarter whose zip is gone.

## Schema

```
funds         (fund_id pk, cik, series_id, fund_name, family, first_seen, last_seen)
                unique (cik, series_id)
filings       (filing_id pk, fund_id fk, accession, form_type, period_end, filed_date,
               net_assets, source_url)   unique (accession)
raw_holdings  (raw_id pk, filing_id fk, holding_id, issuer_name, title_of_issue, cusip,
               lei, balance, units, currency, value_usd, pct_net_assets, asset_category,
               issuer_category, is_restricted, fair_value_level, price_per_share,
               company_provisional, is_spv, source_quarter, ingested_at)
                unique (filing_id, holding_id)
runs          (run_id pk, started_at, completed_at, periods_ingested, rows_scanned,
               rows_private, rows_universe, rows_null_price, excluded_by_cat,
               spv_count, complete, notes)
```

Two fields differ from `plan.md` and both are deliberate:

- **`price_per_share` is stored, not derived on read.** The arithmetic happens once, at
  ingest, under one null rule: `NULL` where balance is zero or absent, because a missing
  share count is not a zero price.
- **`company_provisional` is a label, not a decision.** It comes from the frozen name
  patterns in `src/ingest/universe.py`. Weeks 5–6 supersede it and record their reasoning
  in `match_decisions`; nothing downstream should treat it as resolved.

`period_end` is the DERA `REPORT_DATE` — the as-of date of the holdings — not
`REPORT_ENDING_PERIOD`, which is the fund's **fiscal year end**. Verified on 2026Q2:
BlackRock Funds files with a fiscal year end of 31-MAY-2026 carrying holdings as of
27-FEB-2026. Using the wrong one would scramble every propagation-lag measurement.

## What the bulk path cannot reach

The DERA sets are indexed by **filing** quarter, and filings lag their period by ~56
days. So the newest as-of date in the 2026Q2 set is **2026-04-30**, not 2026-06-30. The
$589.0095 Anthropic repricing verified by hand in Week 1 (period ends 5/29 and 5/31, filed
late July) sits in 2026Q3, which the SEC has not published — `2026q3_nport.zip` returns
HTTP 404. Reaching the current period needs the Week 3 live-EDGAR path. Bulk alone is
structurally about two months further behind than the quarter label suggests.
