"""Load universe Parquet into funds / filings / raw_holdings. Idempotent.

Re-running a quarter must not duplicate or mutate anything: funds and filings
upsert on their natural keys, and raw_holdings does nothing on conflict, since
it is append-only and the source is immutable. So the safe recovery from any
failure is to run the same command again.

    python -m src.db.load 2026q2
    python -m src.db.load --all
"""

import argparse
import json
from pathlib import Path

import duckdb
import psycopg2.extras

from src.db.connect import apply_schema, connect
from src.ingest.build_parquet import ALL_QUARTERS, PARQUET

# Fidelity's dozen trusts and BlackRock's several are one decision-maker each,
# so dispersion has to be measured across families, not registrants. Anything
# unmatched keeps its registrant name and is reviewed rather than guessed.
FAMILIES = [
    # Order matters: first needle wins. The two Lincoln/Fidelity entries below
    # must stay in this order -- 'LINCOLN VARIABLE INSURANCE PRODUCTS TRUST' is
    # Lincoln Financial, while 'Variable Insurance Products Fund I-IV' are
    # Fidelity's VIP funds (CIKs 356494 / 831016 / 927384 / 720318, per
    # plan.md's holder table). Grouping them by the words they share would
    # split Fidelity's real footprint across five apparent families and
    # overstate the number of independent managers -- which is the exact
    # quantity the dispersion analysis depends on.
    ("LINCOLN", "Lincoln Financial"),
    ("FIDELITY", "Fidelity"), ("FMR", "Fidelity"),
    ("VARIABLE INSURANCE PRODUCTS FUND", "Fidelity"),
    ("BLACKROCK", "BlackRock"),
    ("T. ROWE", "T. Rowe Price"), ("T ROWE", "T. Rowe Price"),
    ("AMERICAN FUNDS", "Capital Group"), ("CAPITAL GROUP", "Capital Group"),
    ("NEW ECONOMY", "Capital Group"), ("GROWTH FUND OF AMERICA", "Capital Group"),
    ("ALGER", "Alger"),
    ("ARK ", "ARK"), ("ARK,", "ARK"),
    ("NEUBERGER", "Neuberger Berman"),
    ("MORGAN STANLEY", "Morgan Stanley"),
    ("BAILLIE", "Baillie Gifford"),
    ("INVESCO", "Invesco"),
    ("FRANKLIN", "Franklin Templeton"),
    ("NUVEEN", "Nuveen"),
    ("NEW YORK LIFE", "New York Life"), ("NYLIM", "New York Life"),
    ("FUNDRISE", "Fundrise"),
    ("PRIVATE SHARES", "Private Shares Fund"),
    ("VANGUARD", "Vanguard"),
    ("JPMORGAN", "JPMorgan"), ("J.P. MORGAN", "JPMorgan"),
    ("GOLDMAN", "Goldman Sachs"),
    ("WELLINGTON", "Wellington"),
    ("DESTINY TECH", "Destiny Tech100"), ("DXYZ", "Destiny Tech100"),
    ("BARON", "Baron Capital"),
    ("BRIGHTHOUSE", "Brighthouse"),
    ("MASSMUTUAL", "MassMutual"), ("MML ", "MassMutual"),
    ("BNY MELLON", "BNY Mellon"), ("DREYFUS", "BNY Mellon"),
    ("COATUE", "Coatue"),
    ("STEPSTONE", "StepStone"),
    ("SUNAMERICA", "SunAmerica"), ("SEASONS SERIES", "SunAmerica"),
    ("VOYA", "Voya"),
    ("LEGG MASON", "Franklin Templeton"),  # acquired by Franklin, 2020
]


def family_of(registrant_name: str) -> str:
    up = (registrant_name or "").upper()
    for needle, family in FAMILIES:
        if needle in up:
            return family
    return registrant_name or "(unknown)"


def family_case_expr(column: str = "REGISTRANT_NAME") -> str:
    """The same mapping as family_of(), as SQL.

    DuckDB's create_function() needs numpy, which this project does not
    otherwise require, so the rule is compiled to a CASE expression instead of
    registered as a UDF. One source of truth, two renderings -- and
    tests/test_families.py checks they agree.
    """
    arms = " ".join(
        f"WHEN upper({column}) LIKE '%{needle}%' THEN '{family}'"
        for needle, family in FAMILIES
    )
    return f"CASE {arms} ELSE coalesce({column}, '(unknown)') END"


def read_quarter(quarter: str):
    path = PARQUET / quarter / "universe_holdings.parquet"
    if not path.exists():
        raise SystemExit(
            f"{path} not found -- run: python -m src.ingest.build_parquet {quarter}"
        )
    con = duckdb.connect()
    rows = con.execute(f"""
        SELECT ACCESSION_NUMBER, HOLDING_ID, CIK, REGISTRANT_NAME, SERIES_NAME, SERIES_ID,
               NET_ASSETS, SUB_TYPE, FILED_DATE, PERIOD_END,
               ISSUER_NAME, ISSUER_TITLE, ISSUER_CUSIP, ISSUER_LEI,
               BALANCE, UNIT, CURRENCY_CODE, CURRENCY_VALUE, PCT_NET_ASSETS,
               ASSET_CAT, ISSUER_TYPE, IS_RESTRICTED_SECURITY, FAIR_VALUE_LEVEL,
               PRICE_PER_SHARE, COMPANY, IS_SPV, SOURCE_QUARTER
        FROM read_parquet('{path.as_posix()}')
    """).fetchall()
    con.close()
    return rows


def load_quarter(conn, quarter: str) -> dict:
    rows = read_quarter(quarter)
    cur = conn.cursor()

    # ----------------------------------------------------------- funds ----
    funds = {}
    for r in rows:
        cik, series_id, series_name, registrant = r[2], r[5], r[4], r[3]
        funds[(cik, series_id or "")] = (series_name or registrant, family_of(registrant))

    psycopg2.extras.execute_values(cur, """
        INSERT INTO funds (cik, series_id, fund_name, family)
        VALUES %s
        ON CONFLICT (cik, series_id) DO UPDATE
            SET fund_name = COALESCE(EXCLUDED.fund_name, funds.fund_name),
                family    = COALESCE(EXCLUDED.family, funds.family)
    """, [(cik, sid or "", name, fam) for (cik, sid), (name, fam) in funds.items()])

    cur.execute("SELECT cik, series_id, fund_id FROM funds")
    fund_ids = {(c, s or ""): fid for c, s, fid in cur.fetchall()}

    # --------------------------------------------------------- filings ----
    filings = {}
    for r in rows:
        acc, cik, series_id = r[0], r[2], r[5]
        filings[acc] = (
            fund_ids.get((cik, series_id or "")),
            r[7],                       # SUB_TYPE
            r[9],                       # PERIOD_END -- the holdings as-of date
            r[8],                       # FILED_DATE
            r[6],                       # NET_ASSETS
            f"https://www.sec.gov/Archives/edgar/data/{(cik or '').lstrip('0')}/"
            f"{acc.replace('-', '')}/primary_doc.xml",
        )

    psycopg2.extras.execute_values(cur, """
        INSERT INTO filings (accession, fund_id, form_type, period_end, filed_date,
                             net_assets, source_url)
        VALUES %s
        ON CONFLICT (accession) DO UPDATE
            SET fund_id    = COALESCE(EXCLUDED.fund_id, filings.fund_id),
                period_end = COALESCE(EXCLUDED.period_end, filings.period_end),
                filed_date = COALESCE(EXCLUDED.filed_date, filings.filed_date),
                net_assets = COALESCE(EXCLUDED.net_assets, filings.net_assets)
    """, [(acc, *vals) for acc, vals in filings.items()])

    cur.execute("SELECT accession, filing_id FROM filings")
    filing_ids = dict(cur.fetchall())

    # ---------------------------------------------------- raw_holdings ----
    # DO NOTHING, not DO UPDATE: raw_holdings is append-only, so a re-run must
    # be a no-op on rows that are already there rather than a silent rewrite.
    payload = [(
        filing_ids[r[0]], r[1], r[10], r[11], r[12], r[13], r[14], r[15], r[16],
        r[17], r[18], r[19], r[20],
        {"Y": True, "N": False}.get(r[21]),
        int(r[22]) if r[22] and str(r[22]).isdigit() else None,
        r[23], r[24], r[25], r[26],
    ) for r in rows]

    before = _count(cur, "raw_holdings")
    psycopg2.extras.execute_values(cur, """
        INSERT INTO raw_holdings (
            filing_id, holding_id, issuer_name, title_of_issue, cusip, lei,
            balance, units, currency, value_usd, pct_net_assets, asset_category,
            issuer_category, is_restricted, fair_value_level, price_per_share,
            company_provisional, is_spv, source_quarter)
        VALUES %s
        ON CONFLICT (filing_id, holding_id) DO NOTHING
    """, payload, page_size=500)
    inserted = _count(cur, "raw_holdings") - before

    # first_seen / last_seen follow from the filings actually loaded.
    cur.execute("""
        UPDATE funds f SET
            first_seen = sub.lo, last_seen = sub.hi
        FROM (SELECT fund_id, min(period_end) lo, max(period_end) hi
              FROM filings WHERE fund_id IS NOT NULL GROUP BY fund_id) sub
        WHERE f.fund_id = sub.fund_id
    """)

    conn.commit()
    cur.close()
    return {
        "quarter": quarter,
        "rows_read": len(rows),
        "funds": len(funds),
        "filings": len(filings),
        "holdings_inserted": inserted,
        "holdings_skipped": len(rows) - inserted,
    }


def _count(cur, table):
    cur.execute(f"SELECT count(*) FROM {table}")
    return cur.fetchone()[0]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("quarter", nargs="?")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    quarters = ALL_QUARTERS if args.all else [args.quarter]
    if quarters == [None]:
        ap.error("give a quarter or --all")

    conn = connect()
    apply_schema(conn)

    cur = conn.cursor()
    cur.execute("INSERT INTO runs (periods_ingested) VALUES (%s) RETURNING run_id",
                (quarters,))
    run_id = cur.fetchone()[0]
    conn.commit()

    print(f"run {run_id}")
    print(f"{'quarter':<10}{'read':>8}{'funds':>8}{'filings':>9}{'inserted':>10}{'skipped':>9}")
    print("-" * 54)

    totals = {"rows_read": 0, "holdings_inserted": 0}
    ok = True
    for q in quarters:
        try:
            rec = load_quarter(conn, q)
        except SystemExit as exc:
            print(f"{q:<10}SKIPPED -- {exc}")
            ok = False
            continue
        totals["rows_read"] += rec["rows_read"]
        totals["holdings_inserted"] += rec["holdings_inserted"]
        print(f"{rec['quarter']:<10}{rec['rows_read']:>8,}{rec['funds']:>8,}"
              f"{rec['filings']:>9,}{rec['holdings_inserted']:>10,}"
              f"{rec['holdings_skipped']:>9,}")

    # Roll the per-quarter reconciliation records into the run row, so the run
    # summary carries the scan counts and not just what landed.
    scanned = private = excluded = 0
    for q in quarters:
        rec_path = PARQUET / q / "reconciliation.json"
        if rec_path.exists():
            rec = json.loads(rec_path.read_text(encoding="utf-8"))
            scanned += rec["holding_rows_in"]
            private += rec["private_rows_out"]
            excluded += rec["excluded_by_asset_cat"]

    cur.execute("SELECT count(*) FROM raw_holdings WHERE price_per_share IS NULL")
    null_price = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM raw_holdings WHERE is_spv")
    spvs = cur.fetchone()[0]

    cur.execute("""
        UPDATE runs SET completed_at = now(), rows_scanned = %s, rows_private = %s,
               rows_universe = %s, rows_null_price = %s, excluded_by_cat = %s,
               spv_count = %s, complete = %s
        WHERE run_id = %s
    """, (scanned, private, totals["rows_read"], null_price, excluded, spvs, ok, run_id))
    conn.commit()

    print(f"\nrun {run_id}: complete={ok}  scanned={scanned:,}  private={private:,}  "
          f"universe={totals['rows_read']:,}  null-price={null_price:,}  SPV={spvs:,}")
    if not ok:
        print("run marked complete=false -- it is excluded from re-mark baselines")
    conn.close()


if __name__ == "__main__":
    main()
