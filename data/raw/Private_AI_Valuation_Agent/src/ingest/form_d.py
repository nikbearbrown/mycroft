"""Form D: round timing and amounts, joined on resolved identity.

`plan.md` week 9: "Form D join on resolved issuer identity, not name string --
dates and amounts only, never valuation, stated explicitly in the docs."

Both halves of that sentence are load-bearing, and the first one is the harder
one. This module exists in the shape it does because a name join is not merely
imprecise here -- it is wrong in a specific, quantified way.

--------------------------------------------------------------------------
Why a name join would have been wrong
--------------------------------------------------------------------------
Scanning the 2026Q1 issuer file for universe company names returns 85 rows.
Eighty-four of them are pooled investment vehicles. "Anthropic Jan 2026 a
Series of CGF2021 LLC", "SpaceX Tender Dec 2025 a Series of CGF2021 LLC",
"HII Cerebras V, a Series of HII Cerebras, LLC" -- these are feeders raising
money from accredited investors to buy existing shares on the secondary
market. Their `TOTALAMOUNTSOLD` is the feeder's raise, and has nothing to do
with a primary round by the company.

Summing them per company and calling the result "round timing and amounts"
would publish numbers that no universe company's filing produced. That is a
P3 violation with a plausible-looking table attached, which is the most
dangerous kind.

So the pipeline is three steps, and only the third is a join:

  1. **Name scan** -> `form_d_filings`. Every candidate, kept immutably,
     labelled `company_provisional`. This is a candidate pool.
  2. **Machine triage** on a filed fact, not an inference: the offering's own
     `ISPOOLEDINVESTMENTFUNDTYPE` flag. The filer declares itself a pooled
     vehicle; we do not guess from the name. In 2026Q1 this separates 84 from
     1 with no residue.
  3. **Human identity resolution** -> `company_identity`. A named reviewer
     affirms that a CIK *is* a company. Only then does anything join, and the
     join is `form_d_filings.cik = company_identity.cik`, never on a string.

Step 3 is also what makes the join *complete* rather than merely correct: once
a CIK is affirmed, every Form D that CIK ever filed is in scope, including the
ones whose entity name matches no pattern at all.

--------------------------------------------------------------------------
Never valuation
--------------------------------------------------------------------------
Form D carries no share count and no price per share. `TOTALOFFERINGAMOUNT`
and `TOTALAMOUNTSOLD` are dollars raised, and dollars raised divided by
nothing is not a valuation. There is no price column in `form_d_filings`, no
function here returns one, and `tests/test_form_d.py` fails if either changes.

--------------------------------------------------------------------------
Archive coverage
--------------------------------------------------------------------------
The SEC publishes these sets from 2014Q1 forward as a contiguous run, plus two
orphans (2008Q1, 2012Q1) with 2008Q2-2013Q4 absent. `QUARTERS` is the
contiguous run only, so that "no Form D before this date" is a statement about
the archive and not about the company.
"""

from __future__ import annotations

import csv
import io
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.ingest.download_bulk import DATA_DIR, download  # noqa: E402
from src.ingest.universe import (  # noqa: E402
    UNIVERSE_PATTERNS,
    WATCHLIST_PATTERNS,
)

BASE = "https://www.sec.gov/files/structureddata/data/form-d-data-sets"
SUFFIX = "_d.zip"

# The contiguous published run. 2008Q1 and 2012Q1 also exist as orphans; the
# quarters between them do not, so including them would make the earliest
# observed filing date depend on which orphan happened to contain a company.
QUARTERS = tuple(f"{y}q{n}" for y in range(2014, 2026) for n in range(1, 5)) + ("2026q1",)

# Patterns are reused from the N-PORT universe rather than redefined. They are
# the frozen Week 2 record of what a company is called, and Week 8 established
# that they over-match badly outside the Level 3 filter -- which is precisely
# why nothing here trusts a name match on its own.
_PATTERNS = [
    (canonical, pattern.strip("%"))
    for group in (UNIVERSE_PATTERNS, WATCHLIST_PATTERNS)
    for canonical, patterns in group.items()
    for pattern in patterns
]

POOLED_VEHICLE = "pooled_vehicle"
CANDIDATE_OPERATING = "candidate_operating"

# Names the issuer may have filed under previously. Checked as well as the
# current name because a company that renamed itself -- "OpenAI Group PBC" was
# "OpenAI OpCo, LLC" -- would otherwise be invisible in its older filings.
_NAME_FIELDS = (
    "ENTITYNAME",
    "ISSUER_PREVIOUSNAME_1", "ISSUER_PREVIOUSNAME_2", "ISSUER_PREVIOUSNAME_3",
    "EDGAR_PREVIOUSNAME_1", "EDGAR_PREVIOUSNAME_2", "EDGAR_PREVIOUSNAME_3",
)


def company_for(row: dict) -> str | None:
    """The provisional company label for one issuer row, or None.

    First match wins, exactly as `universe.company_case_expr` does for N-PORT,
    so the two lanes label a name the same way.
    """
    blob = " ".join(row.get(f) or "" for f in _NAME_FIELDS).upper()
    for canonical, pattern in _PATTERNS:
        if pattern in blob:
            return canonical
    return None


def _flag(value) -> bool | None:
    """Form D writes booleans as 'true'/'false' and leaves them blank."""
    if value is None or value == "":
        return None
    return value.strip().lower() == "true"


def _money(value):
    """A dollar figure, or None.

    `TOTALOFFERINGAMOUNT` legitimately reads 'Indefinite' for a fund with no
    cap. Coercing that to 0 would report a fund that raised nothing; coercing
    it to a number is impossible. It becomes NULL and `offering_is_indefinite`
    carries the fact.
    """
    if value is None:
        return None
    value = value.strip().replace(",", "").replace("$", "")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def is_indefinite(value) -> bool:
    return bool(value) and value.strip().lower() == "indefinite"


def _int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _date(value):
    """A filed date, across three formats the archive actually uses.

    The formats changed mid-archive and the first version of this function
    silently returned None for eleven years of filings. `FILING_DATE` is
    '2015-03-31 17:28:10' up to roughly 2020 and '30-SEP-2024' after it, while
    `SALE_DATE` is '2015-03-31'. A NULL filing date is indistinguishable from
    an absent one, so the bug read as "old filings have no date" rather than as
    a parser failure -- which is why the time component is stripped explicitly
    here instead of being left to a lucky format string.
    """
    if not value or not value.strip():
        return None
    text = value.strip().split()[0]          # drop any 'HH:MM:SS'
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text.upper() if "-" in text else text, fmt).date()
        except ValueError:
            continue
    return None


def _read(zf: zipfile.ZipFile, folder: str, name: str) -> list[dict]:
    text = zf.read(f"{folder}/{name}").decode("utf-8", "replace")
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def _folder(zf: zipfile.ZipFile) -> str:
    """The archive's internal directory, e.g. '2026Q1_d'. Case differs from the
    file name on disk, so it is read rather than constructed."""
    for name in zf.namelist():
        if name.endswith("/ISSUERS.tsv"):
            return name.rsplit("/", 1)[0]
    raise FileNotFoundError("no ISSUERS.tsv in archive")


def scan_quarter(quarter: str) -> list[dict]:
    """Every Form D issuer row in one quarter whose name matches the universe."""
    archive = DATA_DIR / f"{quarter}{SUFFIX}"
    if not archive.exists():
        archive = download(quarter, base=BASE, suffix=SUFFIX)

    with zipfile.ZipFile(archive) as zf:
        folder = _folder(zf)
        issuers = _read(zf, folder, "ISSUERS.tsv")
        offerings = {r["ACCESSIONNUMBER"]: r for r in _read(zf, folder, "OFFERING.tsv")}
        submissions = {r["ACCESSIONNUMBER"]: r
                       for r in _read(zf, folder, "FORMDSUBMISSION.tsv")}

    rows = []
    for issuer in issuers:
        company = company_for(issuer)
        if company is None:
            continue
        accession = issuer["ACCESSIONNUMBER"]
        offering = offerings.get(accession, {})
        submission = submissions.get(accession, {})

        pooled = _flag(offering.get("ISPOOLEDINVESTMENTFUNDTYPE"))
        previous = [issuer.get(f) for f in _NAME_FIELDS[1:] if (issuer.get(f) or "").strip()]

        rows.append({
            "source_quarter": quarter,
            "accession": accession,
            "issuer_seq_key": issuer.get("ISSUER_SEQ_KEY") or "1",
            "is_primary_issuer": (issuer.get("IS_PRIMARYISSUER_FLAG") or "").upper() == "YES",
            "cik": (issuer.get("CIK") or "").strip() or None,
            "entity_name": issuer["ENTITYNAME"],
            "previous_names": " | ".join(previous) or None,
            "entity_type": issuer.get("ENTITYTYPE") or None,
            "jurisdiction": issuer.get("JURISDICTIONOFINC") or None,
            "year_of_inc": issuer.get("YEAROFINC_VALUE_ENTERED") or None,
            "city": issuer.get("CITY") or None,
            "state_or_country": issuer.get("STATEORCOUNTRYDESCRIPTION") or None,
            "submission_type": submission.get("SUBMISSIONTYPE") or None,
            "filing_date": _date(submission.get("FILING_DATE")),
            "industry_group": offering.get("INDUSTRYGROUPTYPE") or None,
            "is_pooled_fund": pooled,
            "is_amendment": _flag(offering.get("ISAMENDMENT")),
            "previous_accession": offering.get("PREVIOUSACCESSIONNUMBER") or None,
            "date_of_first_sale": _date(offering.get("SALE_DATE")),
            "sale_yet_to_occur": _flag(offering.get("YETTOOCCUR")),
            "total_offering_amount": _money(offering.get("TOTALOFFERINGAMOUNT")),
            "total_amount_sold": _money(offering.get("TOTALAMOUNTSOLD")),
            "total_remaining": _money(offering.get("TOTALREMAINING")),
            "offering_is_indefinite": is_indefinite(offering.get("TOTALOFFERINGAMOUNT")),
            "is_equity_type": _flag(offering.get("ISEQUITYTYPE")),
            "is_debt_type": _flag(offering.get("ISDEBTTYPE")),
            "minimum_investment": _money(offering.get("MINIMUMINVESTMENTACCEPTED")),
            "investors_already": _int(offering.get("TOTALNUMBERALREADYINVESTED")),
            "company_provisional": company,
            "vehicle_class": POOLED_VEHICLE if pooled else CANDIDATE_OPERATING,
        })
    return rows


UPSERT = """
INSERT INTO form_d_filings
    (source_quarter, accession, issuer_seq_key, is_primary_issuer, cik, entity_name,
     previous_names, entity_type, jurisdiction, year_of_inc, city, state_or_country,
     submission_type, filing_date, industry_group, is_pooled_fund, is_amendment,
     previous_accession, date_of_first_sale, sale_yet_to_occur, total_offering_amount,
     total_amount_sold, total_remaining, offering_is_indefinite, is_equity_type,
     is_debt_type, minimum_investment, investors_already, company_provisional,
     vehicle_class)
VALUES (%(source_quarter)s, %(accession)s, %(issuer_seq_key)s, %(is_primary_issuer)s,
        %(cik)s, %(entity_name)s, %(previous_names)s, %(entity_type)s, %(jurisdiction)s,
        %(year_of_inc)s, %(city)s, %(state_or_country)s, %(submission_type)s,
        %(filing_date)s, %(industry_group)s, %(is_pooled_fund)s, %(is_amendment)s,
        %(previous_accession)s, %(date_of_first_sale)s, %(sale_yet_to_occur)s,
        %(total_offering_amount)s, %(total_amount_sold)s, %(total_remaining)s,
        %(offering_is_indefinite)s, %(is_equity_type)s, %(is_debt_type)s,
        %(minimum_investment)s, %(investors_already)s, %(company_provisional)s,
        %(vehicle_class)s)
ON CONFLICT (accession, issuer_seq_key) DO UPDATE SET
    filing_date          = EXCLUDED.filing_date,
    date_of_first_sale   = EXCLUDED.date_of_first_sale,
    is_pooled_fund       = EXCLUDED.is_pooled_fund,
    vehicle_class        = EXCLUDED.vehicle_class,
    company_provisional  = EXCLUDED.company_provisional,
    previous_names       = EXCLUDED.previous_names,
    total_offering_amount  = EXCLUDED.total_offering_amount,
    total_amount_sold      = EXCLUDED.total_amount_sold,
    total_remaining        = EXCLUDED.total_remaining,
    offering_is_indefinite = EXCLUDED.offering_is_indefinite
"""
# DO UPDATE rather than DO NOTHING, unlike raw_holdings. Both tables are
# projections of immutable source files, but this one is parsed rather than
# copied, and the first version of `_date` returned NULL for every filing
# before ~2020 because the archive switched date formats mid-run. With DO
# NOTHING, fixing that parser would have required truncating the table -- a
# destructive step to correct a non-destructive mistake. Re-running the ingest
# now converges instead. The natural key is the filed accession, so no row
# ever changes which filing it describes; only the parse of that filing is
# refreshed.


def load(conn, quarters=None) -> dict:
    """Scan and store, committing per quarter so progress is visible."""
    quarters = tuple(quarters) if quarters else QUARTERS
    found, inserted = 0, 0
    by_class: dict[str, int] = {}
    with conn.cursor() as cur:
        for quarter in quarters:
            rows = scan_quarter(quarter)
            for row in rows:
                cur.execute(UPSERT, row)
                inserted += cur.rowcount
                by_class[row["vehicle_class"]] = by_class.get(row["vehicle_class"], 0) + 1
            found += len(rows)
            conn.commit()
    return {"quarters": len(quarters), "rows_found": found,
            "rows_inserted": inserted, "by_class": by_class}


def candidates(conn) -> list[dict]:
    """Issuers that are NOT self-declared pooled vehicles: the human's queue.

    One row per CIK, not per filing. A company filing eight Form Ds is one
    identity question, and asking it eight times is the mistake Week 6's
    review queue exists to prevent.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT f.cik,
                   min(f.entity_name)                      AS entity_name,
                   string_agg(DISTINCT f.entity_type, ', ') AS entity_types,
                   string_agg(DISTINCT f.jurisdiction, ', ') AS jurisdictions,
                   string_agg(DISTINCT f.industry_group, ', ') AS industry_groups,
                   string_agg(DISTINCT f.company_provisional, ', ') AS provisional,
                   count(*)                                AS filings,
                   min(f.filing_date)                      AS first_filing,
                   max(f.filing_date)                      AS last_filing,
                   bool_or(i.cik IS NOT NULL)              AS already_decided
              FROM form_d_filings f
              LEFT JOIN company_identity i ON i.cik = f.cik
             WHERE f.vehicle_class = %s
             GROUP BY f.cik
             ORDER BY count(*) DESC, min(f.entity_name)
        """, (CANDIDATE_OPERATING,))
        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, r)) for r in cur.fetchall()]


def resolved(conn, company: str | None = None) -> list[dict]:
    """Form D filings joined on affirmed identity. The only join there is.

    Note what is absent: no price, no share count, no implied valuation. The
    columns are dates and dollars, which is the whole of what Form D says.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.canonical_name          AS company,
                   f.cik,
                   f.entity_name,
                   f.accession,
                   f.submission_type,
                   f.is_amendment,
                   f.filing_date,
                   f.date_of_first_sale,
                   f.total_offering_amount,
                   f.total_amount_sold,
                   f.offering_is_indefinite,
                   f.is_equity_type,
                   f.is_debt_type,
                   f.investors_already
              FROM form_d_filings f
              JOIN company_identity i ON i.cik = f.cik
              JOIN companies c        ON c.company_id = i.company_id
             WHERE i.verdict = 'operating_company'
               AND (%(company)s IS NULL OR c.canonical_name = %(company)s)
             ORDER BY c.canonical_name, f.date_of_first_sale NULLS LAST, f.filing_date
        """, {"company": company})
        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, r)) for r in cur.fetchall()]


def coverage(conn) -> dict:
    """What the scan holds, split the way the finding needs it split."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT vehicle_class, count(*) AS rows, count(DISTINCT cik) AS ciks
              FROM form_d_filings GROUP BY 1 ORDER BY 1
        """)
        by_class = [dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]
        cur.execute("""
            SELECT company_provisional AS company,
                   count(*) FILTER (WHERE vehicle_class = 'pooled_vehicle')     AS vehicles,
                   count(*) FILTER (WHERE vehicle_class = 'candidate_operating') AS candidates,
                   count(DISTINCT cik) AS ciks
              FROM form_d_filings GROUP BY 1 ORDER BY 2 DESC
        """)
        by_company = [dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]
        cur.execute("SELECT count(*), min(filing_date), max(filing_date) FROM form_d_filings")
        total, first, last = cur.fetchone()
    return {
        "quarters_scanned": len(QUARTERS),
        "first_quarter": QUARTERS[0],
        "last_quarter": QUARTERS[-1],
        "rows": int(total or 0),
        "first_filing_date": str(first) if first else None,
        "last_filing_date": str(last) if last else None,
        "by_class": by_class,
        "by_company": by_company,
        "archive_gap": "2008Q2-2013Q4 are not published by the SEC; 2008Q1 and "
                       "2012Q1 exist as orphans and are deliberately excluded so "
                       "that the earliest observed filing is a property of a "
                       "contiguous archive rather than of which orphan a company "
                       "happened to appear in.",
    }


def main() -> None:
    import argparse
    import json

    from src.db.connect import apply_schema, connect

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("quarters", nargs="*", help="default: the whole contiguous run")
    ap.add_argument("--coverage", action="store_true", help="report, do not load")
    args = ap.parse_args()

    conn = connect()
    apply_schema(conn)
    try:
        if args.coverage:
            print(json.dumps(coverage(conn), indent=2, default=str))
        else:
            print(json.dumps(load(conn, args.quarters or None), indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
