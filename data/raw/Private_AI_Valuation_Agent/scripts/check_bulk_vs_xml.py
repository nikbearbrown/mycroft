"""Does the DERA bulk data behave like the raw XML?

This is the Week 1 de-risking test. Everything verified by hand came from
primary_doc.xml. If the bulk TSVs normalize the CUSIP placeholder or the
restricted flag differently, the filter logic has to change again -- so check
before building an ingest pipeline on top of it.

Three questions:
  1. Do the Anthropic rows we verified appear in the bulk, with the same values?
  2. How many rows does each candidate filter keep across the whole quarter?
  3. What does the private universe actually look like at quarter scale?

    python scripts/check_bulk_vs_xml.py data/2026q2_nport
"""

import json
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "week1_verified_marks.json"

UNIVERSE = {
    "Anthropic": "%ANTHROPIC%",
    "Databricks": "%DATABRICKS%",
    "OpenAI": "%OPENAI%",
    "xAI": "%X.AI%",
    "Anduril": "%ANDURIL%",
    "Figure AI": "%FIGURE AI%",
    "Cohere": "%COHERE%",
    "Perplexity": "%PERPLEXITY%",
    "Groq": "%GROQ%",
    "Scale AI": "%SCALE AI%",
    "SpaceX": "%SPACE EXPLORATION%",
    "Cerebras": "%CEREBRAS%",
}


def rule(title):
    print(f"\n{title}\n" + "=" * 78)


def main():
    quarter_dir = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "data/2026q2_nport")
    holdings = (quarter_dir / "FUND_REPORTED_HOLDING.tsv").as_posix()
    submission = (quarter_dir / "SUBMISSION.tsv").as_posix()

    con = duckdb.connect()
    # all_varchar: never let type inference reinterpret a placeholder like
    # '000000000' as the integer 0 -- the exact string is the thing under test.
    con.execute(f"""
        CREATE VIEW h AS SELECT * FROM read_csv('{holdings}',
            delim='\t', header=true, all_varchar=true, quote='', ignore_errors=true);
        CREATE VIEW s AS SELECT * FROM read_csv('{submission}',
            delim='\t', header=true, all_varchar=true, quote='', ignore_errors=true);
    """)

    total = con.execute("SELECT count(*) FROM h").fetchone()[0]
    subs = con.execute("SELECT count(*) FROM s").fetchone()[0]
    print(f"2026Q2 bulk: {total:,} holding rows across {subs:,} submissions")

    # ------------------------------------------------------------------ Q1
    rule("Q1. Do the hand-verified Anthropic rows appear, with the same values?")

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["positions"]
    by_acc = {}
    for p in fixture:
        by_acc.setdefault(p["accession"], []).append(p)

    rows = con.execute("""
        SELECT ACCESSION_NUMBER, ISSUER_NAME, ISSUER_TITLE, ISSUER_CUSIP, ISSUER_LEI,
               BALANCE, CURRENCY_VALUE, ASSET_CAT, IS_RESTRICTED_SECURITY, FAIR_VALUE_LEVEL
        FROM h WHERE upper(ISSUER_NAME) LIKE '%ANTHROPIC%'
        ORDER BY ACCESSION_NUMBER, ISSUER_TITLE
    """).fetchall()
    print(f"Anthropic rows in bulk 2026Q2: {len(rows)} "
          f"across {len({r[0] for r in rows})} submissions\n")

    print(f"{'accession':<24}{'cusip':<12}{'restr':<7}{'lvl':<5}{'cat':<5}{'price':>11}  title")
    print("-" * 110)
    matched = mismatched = 0
    for acc, name, title, cusip, lei, bal, val, cat, restr, lvl in rows:
        if acc not in by_acc:
            continue
        price = float(val) / float(bal) if float(bal) else None
        exp = next((p for p in by_acc[acc] if p["title"].upper() == (title or "").upper()), None)
        flag = ""
        if exp:
            same = (
                abs(float(bal) - exp["balance"]) < 0.01
                and abs(float(val) - exp["valUSD"]) < 0.01
                and (cusip or "") == exp["cusip"]
                and (restr or "") == exp["isRestrictedSec"]
                and int(lvl) == exp["fairValLevel"]
            )
            flag = "  <- matches XML" if same else "  <- DIFFERS FROM XML"
            matched += same
            mismatched += not same
        print(f"{acc:<24}{cusip or '(null)':<12}{restr or '-':<7}{lvl or '-':<5}"
              f"{cat or '-':<5}{price:>11.4f}  {(title or '')[:40]}{flag}")

    print(f"\n  exact matches to hand-verified XML: {matched}   mismatches: {mismatched}")

    # ------------------------------------------------------------------ Q2
    rule("Q2. Filter behaviour across the full quarter")

    stats = con.execute("""
        SELECT
          count(*) FILTER (WHERE FAIR_VALUE_LEVEL='3') AS level3,
          count(*) FILTER (WHERE IS_RESTRICTED_SECURITY='Y') AS restricted,
          count(*) FILTER (WHERE ISSUER_CUSIP='N/A') AS cusip_na,
          count(*) FILTER (WHERE ISSUER_CUSIP='000000000') AS cusip_zeros,
          count(*) FILTER (WHERE IS_RESTRICTED_SECURITY='Y'
                             AND FAIR_VALUE_LEVEL='3'
                             AND ISSUER_CUSIP='N/A') AS plan_filter,
          count(*) FILTER (WHERE FAIR_VALUE_LEVEL='3'
                             AND (ISSUER_CUSIP IN ('N/A','000000000','0','')
                                  OR ISSUER_CUSIP IS NULL
                                  OR IS_RESTRICTED_SECURITY='Y')) AS corrected_filter
        FROM h
    """).fetchone()
    labels = ["FAIR_VALUE_LEVEL = 3", "IS_RESTRICTED_SECURITY = Y", "CUSIP = 'N/A'",
              "CUSIP = '000000000'", "plan.md filter (3-field AND)", "corrected filter"]
    for label, n in zip(labels, stats):
        print(f"  {label:<34}{n:>12,}  ({n/total*100:.3f}% of quarter)")

    print("\n  CUSIP placeholder variants actually present:")
    for cusip, n in con.execute("""
        SELECT ISSUER_CUSIP, count(*) FROM h
        WHERE FAIR_VALUE_LEVEL='3'
          AND (ISSUER_CUSIP IS NULL OR length(trim(ISSUER_CUSIP))<9
               OR ISSUER_CUSIP IN ('N/A','000000000'))
        GROUP BY 1 ORDER BY 2 DESC LIMIT 12
    """).fetchall():
        print(f"    {str(cusip)[:24]:<26}{n:>10,}")

    # ------------------------------------------------------------------ Q3
    rule("Q3. The private AI universe at quarter scale")

    print(f"{'company':<14}{'rows':>7}{'funds':>8}{'titles':>8}{'level3':>8}  price range")
    print("-" * 78)
    for company, pattern in UNIVERSE.items():
        r = con.execute(f"""
            SELECT count(*), count(DISTINCT ACCESSION_NUMBER),
                   count(DISTINCT ISSUER_TITLE),
                   count(*) FILTER (WHERE FAIR_VALUE_LEVEL='3'),
                   min(TRY_CAST(CURRENCY_VALUE AS DOUBLE)/NULLIF(TRY_CAST(BALANCE AS DOUBLE),0)),
                   max(TRY_CAST(CURRENCY_VALUE AS DOUBLE)/NULLIF(TRY_CAST(BALANCE AS DOUBLE),0))
            FROM h WHERE upper(ISSUER_NAME) LIKE '{pattern}'
        """).fetchone()
        rng = f"{r[4]:,.2f} - {r[5]:,.2f}" if r[4] is not None else "-"
        print(f"{company:<14}{r[0]:>7,}{r[1]:>8,}{r[2]:>8,}{r[3]:>8,}  {rng}")

    print("\n  Largest Level 3 private holders this quarter (by distinct private positions):")
    for name, n in con.execute("""
        SELECT s.REGISTRANT_NAME, count(*) AS n
        FROM h JOIN s USING (ACCESSION_NUMBER)
        WHERE h.FAIR_VALUE_LEVEL='3'
          AND (h.ISSUER_CUSIP IN ('N/A','000000000') OR h.ISSUER_CUSIP IS NULL)
        GROUP BY 1 ORDER BY n DESC LIMIT 12
    """).fetchall():
        print(f"    {name[:52]:<54}{n:>6,}")


if __name__ == "__main__":
    main()
