"""The private-mark-to-public-price event study, ready before its data is.

`plan.md` week 8: "Fidelity marked Cerebras **Level 3 at $89.02** on
2026-03-31. BlackRock reports it **Level 1 at $236.99** on 2026-05-29 -- it
went public in between. That is a free, clean, private-mark-to-public-price
event study with no additional data collection: how far below the eventual
public price were the Level 3 marks, and how did that gap close as the IPO
approached?"

The estimate was right and the timing was wrong. A Level 1 mark in N-PORT **is**
the quoted market price -- that is what Level 1 means -- so no market-data
vendor is needed. But the Level 1 observation has a 2026-05-29 period end,
which sits in 2026Q3, and the SEC has not published that bulk set.

So this module is the harness. It runs today and reports "not yet observable"
with the reason; it produces the study the day `2026q3_nport.zip` is ingested
and `src.ingest.public_marks` has been run over it.

--------------------------------------------------------------------------
Three things it refuses to do
--------------------------------------------------------------------------
1. **It does not hardcode an IPO date.** The boundary is derived from the data:
   the first period end at which a company's filed rows stop being Level 3 and
   start being Level 1. A typed date is a number no filing produced (P3).

2. **It does not use plan.md's $236.99.** That figure lives in a planning
   document, not in a filing this project has ingested. When the filing
   arrives, the number comes from the filing.

3. **It does not compare a mark to a price on a different date and call the
   difference a discount** without saying so. A Level 1 mark is as of a fund's
   period end, and funds have staggered period ends, so what the study
   recovers is a price *path* around the boundary rather than one number.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# N-PORT reports period ends as '29-MAY-2026'. Postgres parses that with the
# right format string; storing the raw text and converting on read keeps the
# filed value intact in public_observations.
PERIOD_FMT = "DD-MON-YYYY"


def _rows(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, r)) for r in cur.fetchall()]


def public_observations(conn, company: str | None = None) -> list[dict]:
    """Every non-Level-3 observation captured for a universe company."""
    return _rows(conn, f"""
        SELECT company_provisional              AS company,
               fair_value_level                 AS level,
               to_date(period_end, '{PERIOD_FMT}') AS period_end,
               registrant,
               count(*)                         AS rows,
               min(price_per_share)::numeric(18,4) AS price_min,
               max(price_per_share)::numeric(18,4) AS price_max
          FROM public_observations
         WHERE company_provisional IS NOT NULL
           AND (%(company)s IS NULL OR company_provisional = %(company)s)
         GROUP BY 1, 2, 3, 4
         ORDER BY 1, 3, 2
    """, {"company": company})


def boundary(conn, company: str) -> dict:
    """The Level 3 -> Level 1 crossing, derived rather than typed.

    Returns the last period end at which the company was still marked Level 3
    and the first at which it is marked Level 1. Either may be missing; a
    missing Level 1 side is the normal state until the archive catches up.
    """
    last_private = _rows(conn, """
        SELECT max(m.period_end) AS period_end
          FROM marks m JOIN companies c ON c.company_id = m.company_id
         WHERE c.canonical_name = %(company)s
           AND m.price_per_share IS NOT NULL
    """, {"company": company})[0]["period_end"]

    first_public = _rows(conn, f"""
        SELECT min(to_date(period_end, '{PERIOD_FMT}')) AS period_end
          FROM public_observations
         WHERE company_provisional = %(company)s
           AND fair_value_level = '1'
    """, {"company": company})[0]["period_end"]

    return {
        "company": company,
        "last_level_3_period": str(last_private) if last_private else None,
        "first_level_1_period": str(first_public) if first_public else None,
        "crossed": first_public is not None,
        "gap_days": ((first_public - last_private).days
                     if first_public and last_private else None),
    }


def study(conn, company: str = "Cerebras Systems Inc.") -> dict:
    """The event study, or an honest account of why it cannot run yet."""
    private = _rows(conn, """
        SELECT m.period_end,
               count(DISTINCT f.family)               AS managers,
               min(m.price_per_share)::numeric(18,4)  AS price_min,
               max(m.price_per_share)::numeric(18,4)  AS price_max
          FROM marks m
          JOIN companies c ON c.company_id = m.company_id
          JOIN funds     f ON f.fund_id    = m.fund_id
         WHERE c.canonical_name = %(company)s
           AND m.price_per_share IS NOT NULL
         GROUP BY 1 ORDER BY 1
    """, {"company": company})

    public = [r for r in public_observations(conn, company) if r["level"] == "1"]
    edge = boundary(conn, company)

    if not public:
        return {
            "company": company,
            "runnable": False,
            "reason": "no Level 1 observation has been ingested for this company",
            "blocker": "The Level 1 marks have period ends after 2026-04-30, which is "
                       "the newest period end in the bulk archive. They sit in 2026Q3, "
                       "which the SEC has not published. Waiting is the chosen route; "
                       "the alternative was fetching the filings from EDGAR directly.",
            "unblocks_when": "2026q3_nport.zip is downloaded, built, and scanned with "
                             "`python -m src.ingest.public_marks 2026q3`",
            "boundary": edge,
            "private_leg": private,
            "private_first": private[0] if private else None,
            "private_last": private[-1] if private else None,
            "private_return": (round(float(private[-1]["price_max"])
                                     / float(private[0]["price_min"]) - 1, 4)
                               if private else None),
            "observations": [],
            "discounts": [],
        }

    # The reference price is the FIRST Level 1 observation: the earliest quoted
    # market price this project can see. Later ones give the path, not the
    # benchmark, because the market moves after an IPO for reasons that have
    # nothing to do with how the private marks were set.
    reference = min(public, key=lambda r: r["period_end"])
    reference_price = float(reference["price_min"])

    discounts = []
    for row in private:
        price = float(row["price_max"])
        discounts.append({
            "period_end": str(row["period_end"]),
            "managers": row["managers"],
            "level_3_price": price,
            "reference_level_1_price": reference_price,
            "discount": round(price / reference_price - 1, 4),
            "days_before_first_level_1": (reference["period_end"] - row["period_end"]).days,
        })

    return {
        "company": company,
        "runnable": True,
        "boundary": edge,
        "reference": {
            "period_end": str(reference["period_end"]),
            "registrant": reference["registrant"],
            "price": reference_price,
            "note": "the earliest Level 1 mark ingested; a Level 1 mark in N-PORT is "
                    "the quoted market price, so no market-data vendor is involved",
        },
        "private_leg": private,
        "observations": public,
        "discounts": discounts,
        "closing": (
            {"first": discounts[0], "last": discounts[-1],
             "narrowed_by": round(discounts[-1]["discount"] - discounts[0]["discount"], 4)}
            if len(discounts) > 1 else None),
        "caveats": [
            "A Level 1 mark is as of a fund's period end, not the IPO date, and funds "
            "have staggered period ends -- so this is a price path around the crossing, "
            "not a single before-and-after pair.",
            "Lock-up expiry can make the first post-IPO marks not cleanly comparable to "
            "the private ones.",
            "The discount is measured against the earliest Level 1 mark observed, which "
            "is not necessarily the IPO offer price.",
        ],
    }


def ready(conn) -> dict:
    """Which universe companies could support a study today."""
    rows = _rows(conn, """
        SELECT company_provisional AS company,
               fair_value_level    AS level,
               count(*)            AS rows
          FROM public_observations
         WHERE company_provisional IS NOT NULL
         GROUP BY 1, 2 ORDER BY 1, 2
    """)
    companies = sorted({r["company"] for r in rows if r["level"] == "1"})
    return {"companies_with_level_1": companies,
            "non_level_3_rows_by_company_and_level": rows,
            "any_runnable": bool(companies)}

def scan_summary(conn) -> dict:
    """What the public-lane scan covered and found.

    Reported rather than assumed: a section that says "no Level 1 rows exist"
    has to be able to say how many quarters it looked at, or it is an absence
    of evidence dressed as evidence of absence.
    """
    from src.ingest.build_parquet import ALL_QUARTERS

    rows = _rows(conn, """
        SELECT count(*)                            AS rows,
               count(DISTINCT source_quarter)      AS quarters_with_rows,
               count(DISTINCT company_provisional) AS companies
          FROM public_observations
    """)[0]
    by_level = _rows(conn, """
        SELECT fair_value_level AS level, count(*) AS rows
          FROM public_observations GROUP BY 1 ORDER BY 1
    """)
    return {
        "quarters_scanned": len(ALL_QUARTERS),
        "quarters_on_disk": list(ALL_QUARTERS),
        "rows": int(rows["rows"]),
        "companies": int(rows["companies"]),
        "by_level": by_level,
    }

# Instruments that carry a company's name and are not its shares. plan.md:
# "Bank debt, 144A bonds and other instruments priced per $100 of face value
# are excluded even when the issuer name matches."
NOT_SHARES = ("BANKDEBT", "BANK DEBT", "144A", "TERM LOAN", " TL ", "REVOLVER",
              "NOTES", "BOND")


def scan_quality(conn) -> dict:
    """What the public lane actually caught, sorted into three piles.

    This exists because the scan's headline is misleading on its own. Widening
    the fair value filter found 7,175 Level 1 rows -- and **every one of them
    is Coherent Corp**, a public company that the deliberate `%COHERE%` canary
    pattern matches. The Level 3 filter had been doing double duty as a
    precision filter, and removing it exposed the frozen name patterns to the
    entire public market.

    So the lane is reported in three piles and never as one number:

      false_positive  the issuer is not the company the pattern claims
      not_a_share     right company, wrong instrument -- bank debt and 144A
                      notes price per $100 of face, near $1.00 a unit
      candidate       a real equity observation of a universe company
    """
    rows = _rows(conn, """
        SELECT company_provisional AS company,
               fair_value_level    AS level,
               issuer_name,
               title_of_issue,
               count(*)            AS rows,
               min(price_per_share)::numeric(18,4) AS price_min,
               max(price_per_share)::numeric(18,4) AS price_max
          FROM public_observations
         GROUP BY 1, 2, 3, 4
    """)
    piles: dict = {"false_positive": [], "not_a_share": [], "candidate": []}
    for row in rows:
        blob = f"{row['issuer_name']} {row['title_of_issue'] or ''}".upper()
        if "FALSE POSITIVE" in (row["company"] or ""):
            piles["false_positive"].append(row)
        elif any(token in blob for token in NOT_SHARES):
            piles["not_a_share"].append(row)
        else:
            piles["candidate"].append(row)

    def total(pile):
        return sum(int(r["rows"]) for r in piles[pile])

    candidates_level_1 = [r for r in piles["candidate"] if r["level"] == "1"]
    return {
        "rows_total": sum(int(r["rows"]) for r in rows),
        "false_positive_rows": total("false_positive"),
        "not_a_share_rows": total("not_a_share"),
        "candidate_rows": total("candidate"),
        "candidate_level_1_rows": sum(int(r["rows"]) for r in candidates_level_1),
        "false_positive_issuers": sorted({r["issuer_name"]
                                          for r in piles["false_positive"]})[:8],
        "candidates": sorted(piles["candidate"],
                             key=lambda r: -int(r["rows"]))[:10],
        "verdict": ("no genuine Level 1 observation of a universe company exists "
                    "anywhere in the archive"
                    if not candidates_level_1 else
                    "at least one genuine Level 1 observation exists"),
    }
