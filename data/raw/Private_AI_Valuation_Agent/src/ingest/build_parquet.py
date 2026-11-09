"""Turn a quarter's DERA bulk zip into two Parquet files, then clean up.

The zips are ~450 MB each and expand to ~1.5 GB, of which FUND_REPORTED_HOLDING
is 910 MB on its own. Fourteen quarters extracted at once is ~21 GB, so this
works one quarter at a time: pull out only the five TSVs that are needed,
filter, write Parquet, delete the TSVs. Peak disk stays under 2 GB.

Two outputs per quarter, deliberately different widths:

  private_holdings.parquet   every Level 3 row without a real CUSIP, or flagged
                             restricted -- ~700k rows/qtr, ~20 MB. This is the
                             re-runnable raw layer. A universe v2 must be
                             answerable from it without re-downloading.

  universe_holdings.parquet  the same rows narrowed to universe v1 issuers and
                             equity-ish asset categories -- ~1,000 rows/qtr.
                             This is what the database and entity resolution
                             consume.

Both carry the fund and filing context joined on, so nothing downstream needs
the TSVs again.

    python -m src.ingest.build_parquet 2026q2
    python -m src.ingest.build_parquet --all
    python -m src.ingest.build_parquet 2026q2 --keep-tsv
"""

import argparse
import json
import shutil
import sys
import time
import zipfile
from pathlib import Path

import duckdb

from src.ingest.universe import (
    ASSET_CATS,
    PARQUET_NET,
    PRIVATE_FILTER,
    SPV_EXPR,
    company_case_expr,
    universe_match_expr,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
PARQUET = DATA / "parquet"

# Of the 30 TSVs in a quarter's zip these are the only ones this project reads.
NEEDED = [
    "SUBMISSION.tsv",
    "REGISTRANT.tsv",
    "FUND_REPORTED_INFO.tsv",
    "FUND_REPORTED_HOLDING.tsv",
    "IDENTIFIERS.tsv",
]

# all_varchar: never let type inference reinterpret a placeholder. '000000000'
# must stay the string '000000000', not become the integer 0 -- the exact
# spelling is what distinguishes a missing CUSIP from a real one.
READ_OPTS = "delim='\t', header=true, all_varchar=true, quote='', ignore_errors=true"


def extract_needed(quarter: str) -> Path:
    """Unzip only the five TSVs this project uses. Returns the directory."""
    archive = DATA / f"{quarter}_nport.zip"
    if not archive.exists():
        sys.exit(f"{archive} not found -- run: python -m src.ingest.download_bulk {quarter}")

    dest = DATA / f"{quarter}_nport"
    dest.mkdir(exist_ok=True)

    with zipfile.ZipFile(archive) as zf:
        present = set(zf.namelist())
        missing = [n for n in NEEDED if n not in present]
        if missing:
            sys.exit(f"{quarter}: zip is missing {missing} -- schema drift, stop and look")
        for name in NEEDED:
            target = dest / name
            if target.exists():
                continue
            zf.extract(name, dest)
    return dest


def build(quarter: str, keep_tsv: bool = False) -> dict:
    """Filter one quarter to Parquet. Returns the reconciliation record."""
    started = time.time()
    src = extract_needed(quarter)
    out = PARQUET / quarter
    out.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    for view, fname in [
        ("h", "FUND_REPORTED_HOLDING.tsv"),
        ("s", "SUBMISSION.tsv"),
        ("r", "REGISTRANT.tsv"),
        ("f", "FUND_REPORTED_INFO.tsv"),
    ]:
        path = (src / fname).as_posix()
        con.execute(f"CREATE VIEW {view} AS SELECT * FROM read_csv('{path}', {READ_OPTS})")

    total_rows = con.execute("SELECT count(*) FROM h").fetchone()[0]
    total_subs = con.execute("SELECT count(*) FROM s").fetchone()[0]

    # ---------------------------------------------------------------- joined
    # One row per holding, with its filing and fund context attached. A
    # registrant can appear more than once per accession in REGISTRANT.tsv, so
    # the join is deduplicated first -- otherwise holdings multiply silently.
    con.execute(f"""
        CREATE VIEW ctx AS
        SELECT s.ACCESSION_NUMBER, s.SUB_TYPE, s.FILING_DATE,
               s.REPORT_ENDING_PERIOD, s.REPORT_DATE,
               r.CIK, r.REGISTRANT_NAME, r.LEI AS REGISTRANT_LEI,
               f.SERIES_NAME, f.SERIES_ID, f.NET_ASSETS
        FROM s
        LEFT JOIN (SELECT * FROM (
                     SELECT *, row_number() OVER (PARTITION BY ACCESSION_NUMBER) AS rn
                     FROM r) WHERE rn = 1) r USING (ACCESSION_NUMBER)
        LEFT JOIN (SELECT * FROM (
                     SELECT *, row_number() OVER (PARTITION BY ACCESSION_NUMBER) AS rn
                     FROM f) WHERE rn = 1) f USING (ACCESSION_NUMBER)
    """)

    select_cols = f"""
        h.ACCESSION_NUMBER, h.HOLDING_ID,
        ctx.CIK, ctx.REGISTRANT_NAME, ctx.REGISTRANT_LEI,
        ctx.SERIES_NAME, ctx.SERIES_ID,
        TRY_CAST(ctx.NET_ASSETS AS DOUBLE) AS NET_ASSETS,
        ctx.SUB_TYPE,
        -- DERA writes dates as DD-MON-YYYY strings. Parse them here, once. Left
        -- as text they sort alphabetically, which puts 30-APR before 31-MAR --
        -- and propagation lag is measured in days between period ends, so a
        -- string sort would silently invert the project's headline output.
        TRY_STRPTIME(ctx.FILING_DATE, '%d-%b-%Y')::DATE AS FILED_DATE,
        -- Two date fields, and they are not interchangeable:
        --   REPORT_ENDING_PERIOD is the fund's FISCAL YEAR end (31-DEC-2026,
        --     31-OCT-2026) -- useful for grouping a family, useless as a mark date.
        --   REPORT_DATE is the as-of date of the holdings themselves.
        -- period_end must be REPORT_DATE. Verified 2026Q2: BlackRock Funds files
        -- fiscal-year-end 31-MAY-2026 carrying holdings as of 27-FEB-2026.
        TRY_STRPTIME(ctx.REPORT_ENDING_PERIOD, '%d-%b-%Y')::DATE AS FISCAL_YEAR_END,
        TRY_STRPTIME(ctx.REPORT_DATE, '%d-%b-%Y')::DATE AS PERIOD_END,
        h.ISSUER_NAME, h.ISSUER_TITLE, h.ISSUER_CUSIP, h.ISSUER_LEI,
        TRY_CAST(h.BALANCE AS DOUBLE) AS BALANCE,
        h.UNIT, h.OTHER_UNIT_DESC, h.CURRENCY_CODE,
        TRY_CAST(h.CURRENCY_VALUE AS DOUBLE) AS CURRENCY_VALUE,
        TRY_CAST(h.PERCENTAGE AS DOUBLE) AS PCT_NET_ASSETS,
        h.ASSET_CAT, h.ISSUER_TYPE, h.INVESTMENT_COUNTRY,
        h.IS_RESTRICTED_SECURITY, h.FAIR_VALUE_LEVEL,
        -- Never divide by an absent or zero balance: a missing share count is
        -- not a zero price. NULLIF makes the row survive with a null price,
        -- which is what the error-handling rule in plan.md requires.
        TRY_CAST(h.CURRENCY_VALUE AS DOUBLE)
            / NULLIF(TRY_CAST(h.BALANCE AS DOUBLE), 0) AS PRICE_PER_SHARE,
        '{quarter}' AS SOURCE_QUARTER
    """

    # ------------------------------------------------- wide private layer
    private_path = (out / "private_holdings.parquet").as_posix()
    con.execute(f"""
        COPY (SELECT {select_cols}
              FROM h LEFT JOIN ctx USING (ACCESSION_NUMBER)
              WHERE {PARQUET_NET})
        TO '{private_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    private_rows = con.execute(
        f"SELECT count(*) FROM read_parquet('{private_path}')"
    ).fetchone()[0]

    # ------------------------------------------------- narrow universe layer
    universe_path = (out / "universe_holdings.parquet").as_posix()
    con.execute(f"""
        COPY (SELECT {select_cols},
                     {company_case_expr()} AS COMPANY,
                     {SPV_EXPR} AS IS_SPV
              FROM h LEFT JOIN ctx USING (ACCESSION_NUMBER)
              WHERE {PRIVATE_FILTER}
                AND {universe_match_expr(include_watchlist=True)}
                AND (h.ASSET_CAT IN {ASSET_CATS} OR h.ASSET_CAT IS NULL))
        TO '{universe_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    universe_rows = con.execute(
        f"SELECT count(*) FROM read_parquet('{universe_path}')"
    ).fetchone()[0]

    # Rows the asset-category allow-list threw away. Counted, never silent --
    # if this number ever jumps, a real category is being dropped.
    excluded_by_cat = con.execute(f"""
        SELECT count(*) FROM h
        WHERE {PRIVATE_FILTER}
          AND {universe_match_expr(include_watchlist=True)}
          AND h.ASSET_CAT IS NOT NULL AND h.ASSET_CAT NOT IN {ASSET_CATS}
    """).fetchone()[0]

    null_price = con.execute(f"""
        SELECT count(*) FROM read_parquet('{universe_path}')
        WHERE PRICE_PER_SHARE IS NULL
    """).fetchone()[0]

    period_ends, earliest, latest = con.execute(f"""
        SELECT count(DISTINCT PERIOD_END), min(PERIOD_END), max(PERIOD_END)
        FROM read_parquet('{universe_path}')
    """).fetchone()

    con.close()

    if not keep_tsv:
        shutil.rmtree(src, ignore_errors=True)

    record = {
        "quarter": quarter,
        "holding_rows_in": total_rows,
        "submissions_in": total_subs,
        "private_rows_out": private_rows,
        "universe_rows_out": universe_rows,
        "excluded_by_asset_cat": excluded_by_cat,
        "universe_null_price": null_price,
        "distinct_period_ends": period_ends,
        # The as-of window this filing quarter actually delivers. Because the
        # DERA sets are indexed by FILING quarter and filings lag the period by
        # ~56 days, latest_period_end runs roughly two months behind the
        # quarter label -- 2026Q2 tops out at 2026-04-30, not 2026-06-30.
        "earliest_period_end": str(earliest) if earliest else None,
        "latest_period_end": str(latest) if latest else None,
        "seconds": round(time.time() - started, 1),
    }
    (out / "reconciliation.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


ALL_QUARTERS = [
    f"{y}q{q}" for y in range(2023, 2027) for q in range(1, 5)
][:14]  # 2023Q1 .. 2026Q2 -- the window decided in docs/worklog.md


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("quarter", nargs="?", help="e.g. 2026q2")
    ap.add_argument("--all", action="store_true", help="every quarter 2023Q1-2026Q2")
    ap.add_argument("--keep-tsv", action="store_true", help="do not delete extracted TSVs")
    args = ap.parse_args()

    quarters = ALL_QUARTERS if args.all else [args.quarter]
    if not quarters or quarters == [None]:
        ap.error("give a quarter or --all")

    print(f"{'quarter':<10}{'rows in':>12}{'private':>10}{'universe':>10}"
          f"{'cat-excl':>10}{'null px':>9}{'secs':>7}")
    print("-" * 68)
    for q in quarters:
        rec = build(q, keep_tsv=args.keep_tsv)
        print(f"{rec['quarter']:<10}{rec['holding_rows_in']:>12,}"
              f"{rec['private_rows_out']:>10,}{rec['universe_rows_out']:>10,}"
              f"{rec['excluded_by_asset_cat']:>10,}{rec['universe_null_price']:>9,}"
              f"{rec['seconds']:>7.1f}")


if __name__ == "__main__":
    main()
