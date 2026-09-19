"""The separate lane: universe-company holdings at ANY fair value level.

Week 8 found that `plan.md`'s Cerebras event study cannot be run, for two
reasons that look alike and are not:

  1. `PRIVATE_FILTER = "FAIR_VALUE_LEVEL = '3'"` means Level 1 rows never
     entered the pipeline. A filter, fixable here.
  2. The Level 1 observation's period end is 2026-05-29, which is in 2026Q3 --
     a bulk set the SEC has not published. Not fixable by any amount of code.

Only (2) binds. Widening the filter alone finds nothing, because the rows are
not in the archive at all. This module fixes (1) anyway, so that the study runs
the day (2) resolves.

--------------------------------------------------------------------------
Why this is a separate table and not a wider filter
--------------------------------------------------------------------------
`raw_holdings` is documented as the Level 3 private layer and 5,806 rows
reconcile against it through `match_decisions` and `marks`. Loosening
`PRIVATE_FILTER` in place would silently redefine every number downstream --
the re-mark rate, the dispersion, the panel. So the private layer is left
exactly as it is and public observations land in `public_observations`, which
nothing else reads.

The scan goes straight at the raw zips rather than the Parquet layer, because
the Parquet layer was itself built with the Level 3 filter. There is no way to
recover a Level 1 row from it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.ingest.build_parquet import (  # noqa: E402
    ALL_QUARTERS,
    DATA,
    READ_OPTS,
    extract_needed,
)
from src.ingest.universe import (  # noqa: E402
    company_case_expr,
    universe_match_expr,
)

# Every level except 3. Level 3 already has a home, and duplicating it here
# would give two answers to "what did this fund mark this at".
SCAN_SQL = """
SELECT s.REPORT_DATE                                   AS period_end_raw,
       s.ACCESSION_NUMBER                              AS accession,
       r.REGISTRANT_NAME                               AS registrant,
       h.ISSUER_NAME                                   AS issuer_name,
       h.ISSUER_TITLE                                  AS title_of_issue,
       h.ISSUER_CUSIP                                  AS cusip,
       h.FAIR_VALUE_LEVEL                              AS fair_value_level,
       h.IS_RESTRICTED_SECURITY                        AS is_restricted,
       h.ASSET_CAT                                     AS asset_category,
       h.CURRENCY_CODE                                 AS currency,
       try_cast(h.BALANCE AS DOUBLE)                   AS balance,
       try_cast(h.CURRENCY_VALUE AS DOUBLE)            AS value_usd,
       {company}                                       AS company_provisional
  FROM h
  JOIN s ON s.ACCESSION_NUMBER = h.ACCESSION_NUMBER
  LEFT JOIN r ON r.ACCESSION_NUMBER = h.ACCESSION_NUMBER
 WHERE {is_universe}
   AND coalesce(h.FAIR_VALUE_LEVEL, '') <> '3'
"""

UPSERT = """
INSERT INTO public_observations
    (source_quarter, accession, period_end, registrant, issuer_name, title_of_issue,
     cusip, fair_value_level, is_restricted, asset_category, currency,
     balance, value_usd, price_per_share, company_provisional)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (accession, issuer_name, title_of_issue, fair_value_level, balance)
DO NOTHING
"""


def scan_quarter(quarter: str) -> list[dict]:
    """Every universe-company holding in one quarter that is not Level 3."""
    src = extract_needed(quarter)
    con = duckdb.connect()
    for view, fname in (("h", "FUND_REPORTED_HOLDING.tsv"),
                        ("s", "SUBMISSION.tsv"),
                        ("r", "REGISTRANT.tsv")):
        con.execute(f"CREATE VIEW {view} AS SELECT * FROM "
                    f"read_csv('{(src / fname).as_posix()}', {READ_OPTS})")
    sql = SCAN_SQL.format(
        company=company_case_expr(),
        is_universe=universe_match_expr(include_watchlist=True),
    )
    cur = con.execute(sql)
    columns = [c[0] for c in cur.description]
    rows = [dict(zip(columns, r)) for r in cur.fetchall()]
    con.close()
    for row in rows:
        row["source_quarter"] = quarter
        balance, value = row.get("balance"), row.get("value_usd")
        row["price_per_share"] = (value / balance
                                  if balance not in (None, 0) and value is not None
                                  else None)
    return rows


def load(conn, quarters=None, keep_tsv: bool = False) -> dict:
    """Scan and store, one quarter at a time.

    Two things learned by getting them wrong on the first full run:

    * **Commit per quarter.** The first version committed once at the end, so a
      thirty-minute scan showed nothing at all until it finished and there was
      no way to tell progress from a hang.
    * **Delete the extracted TSVs.** `build_parquet` keeps peak disk under 2 GB
      by removing them after each quarter; this scanner did not, and left 15 GB
      of recoverable files behind after fourteen quarters.
    """
    import shutil

    quarters = quarters or ALL_QUARTERS
    found, inserted = [], 0
    with conn.cursor() as cur:
        for quarter in quarters:
            rows = scan_quarter(quarter)
            found.extend(rows)
            for row in rows:
                cur.execute(UPSERT, (
                    row["source_quarter"], row["accession"], row["period_end_raw"],
                    row["registrant"], row["issuer_name"], row["title_of_issue"],
                    row["cusip"], row["fair_value_level"], row["is_restricted"],
                    row["asset_category"], row["currency"], row["balance"],
                    row["value_usd"], row["price_per_share"],
                    row["company_provisional"],
                ))
                inserted += cur.rowcount
            conn.commit()
            if not keep_tsv:
                shutil.rmtree(DATA / f"{quarter}_nport", ignore_errors=True)
    conn.commit()
    by_level: dict = {}
    for row in found:
        level = row["fair_value_level"] or "(none)"
        by_level[level] = by_level.get(level, 0) + 1
    return {"quarters": len(quarters), "rows_found": len(found),
            "rows_inserted": inserted, "by_level": by_level}


def main() -> None:
    import argparse

    from src.db.connect import apply_schema, connect

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("quarters", nargs="*", help="default: every quarter on disk")
    ap.add_argument("--keep-tsv", action="store_true",
                    help="do not delete the extracted TSVs after each quarter")
    args = ap.parse_args()

    conn = connect()
    apply_schema(conn)
    try:
        print(load(conn, args.quarters or None, keep_tsv=args.keep_tsv))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
