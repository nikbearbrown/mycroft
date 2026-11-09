"""Which fund complexes actually hold the universe? Measured, not assumed.

plan.md Week 2: "Check the four unverified fund complexes (Baillie Gifford,
Morgan Stanley, Neuberger, Invesco)." plan.md lists them as "unverified, worth
checking" -- so this answers the question with counts instead of promoting them
on reputation.

It also ranks every complex in the data, because the Week 1 holder list came
from EDGAR full-text search on one company. Fourteen quarters of bulk can say
who the holders really are.

    python scripts/check_fund_complexes.py
"""

import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.db.load import family_case_expr  # noqa: E402
from src.ingest.build_parquet import ALL_QUARTERS, PARQUET  # noqa: E402

FAMILY = family_case_expr()
REAL = "COMPANY IS NOT NULL AND COMPANY NOT LIKE '%FALSE POSITIVE%'"

# The four plan.md flags as unverified.
CANDIDATES = ["Baillie Gifford", "Morgan Stanley", "Neuberger Berman", "Invesco"]


def rule(title):
    print(f"\n{title}\n" + "=" * 92)


def main():
    files = [
        (PARQUET / q / "universe_holdings.parquet").as_posix()
        for q in ALL_QUARTERS
        if (PARQUET / q / "universe_holdings.parquet").exists()
    ]
    if not files:
        sys.exit("no universe Parquet -- run: python -m src.ingest.build_parquet --all")

    con = duckdb.connect()
    con.execute(f"CREATE VIEW u AS SELECT * FROM read_parquet([{', '.join(repr(f) for f in files)}])")

    rule("Every fund complex holding universe v1, ranked")
    rows = con.execute(f"""
        SELECT {FAMILY} AS family,
               count(*) AS rows,
               count(DISTINCT CIK) AS ciks,
               count(DISTINCT COMPANY) AS companies,
               count(DISTINCT PERIOD_END) AS period_ends,
               min(PERIOD_END) AS first_seen,
               max(PERIOD_END) AS last_seen
        FROM u WHERE {REAL}
        GROUP BY 1 ORDER BY rows DESC LIMIT 30
    """).fetchall()
    print(f"{'family':<34}{'rows':>7}{'CIKs':>6}{'cos':>5}{'ends':>6}  "
          f"{'first':<12}{'last':<12}")
    print("-" * 92)
    for fam, n, ciks, cos, ends, lo, hi in rows:
        print(f"{str(fam)[:32]:<34}{n:>7,}{ciks:>6}{cos:>5}{ends:>6}  "
              f"{str(lo):<12}{str(hi):<12}")

    rule("The four plan.md left unverified")
    for name in CANDIDATES:
        r = con.execute(f"""
            SELECT count(*), count(DISTINCT CIK), count(DISTINCT COMPANY),
                   min(PERIOD_END), max(PERIOD_END)
            FROM u WHERE {REAL} AND {FAMILY} = ?
        """, [name]).fetchone()
        verdict = "HOLDS THE UNIVERSE" if r[0] else "no universe positions"
        print(f"\n  {name:<20} {r[0]:>5,} rows  {r[1]} CIKs  {r[2]} companies   {verdict}")
        if r[0]:
            print(f"  {'':<20} {r[3]} .. {r[4]}")
            for c, n, ciks in con.execute(f"""
                SELECT COMPANY, count(*), count(DISTINCT CIK) FROM u
                WHERE {REAL} AND {FAMILY} = ?
                GROUP BY 1 ORDER BY 2 DESC
            """, [name]).fetchall():
                print(f"  {'':<22}{c[:40]:<42}{n:>5,} rows  {ciks} CIKs")

    rule("Holders NOT in the plan.md Week 1 list")
    known = {
        "Fidelity", "ARK", "T. Rowe Price", "BlackRock", "Capital Group", "Alger",
        "Franklin Templeton", "Nuveen", "New York Life", "Fundrise",
        "Private Shares Fund",
    }
    rows = con.execute(f"""
        SELECT {FAMILY} AS family, count(*) AS rows,
               count(DISTINCT CIK), count(DISTINCT COMPANY)
        FROM u WHERE {REAL}
        GROUP BY 1 ORDER BY rows DESC
    """).fetchall()
    new = [r for r in rows if r[0] not in known]
    print(f"  {len(new)} complexes in the data that Week 1's EDGAR-search list missed.")
    print(f"  Top 20 by row count:\n")
    print(f"  {'family':<48}{'rows':>7}{'CIKs':>6}{'cos':>5}")
    print("  " + "-" * 66)
    for fam, n, ciks, cos in new[:20]:
        print(f"  {str(fam)[:46]:<48}{n:>7,}{ciks:>6}{cos:>5}")

    rule("Verdict")
    print("  Counts only. Whether a complex belongs in the holder list is a")
    print("  judgment for a named human, recorded in docs/worklog.md (P4).")


if __name__ == "__main__":
    main()
