"""The per-fund exposure map and the per-company timeline.

`plan.md` week 9: "Build the per-fund exposure map and the per-company
timeline. Deliverable: enriched timelines with entry cost where available,
plus the exposure map."

Two views of the same panel, aimed at two different questions:

* **Exposure map** — *who is holding this, and how much of their fund is it?*
  One row per (fund family, company), with position value, share of net
  assets, and how long they have held. `pct_net_assets` comes from the filing
  itself; it is not value divided by a net-asset figure this project computed.

* **Timeline** — *what happened to this company, in order?* Marks from
  N-PORT, entry dates and costs from the N-CSR footnote, and round dates from
  Form D where an identity has been affirmed. Three sources, each labelled,
  never blended into one number.

--------------------------------------------------------------------------
What the timeline refuses to do
--------------------------------------------------------------------------
It is very tempting, holding an entry cost and a current mark, to divide and
publish a return. The reason this module does not:

The N-CSR footnote gives cost for a *position*, which is a number of shares
bought across one or more dates. N-PORT gives a price per share on a period
end. Dividing one by the other is only a return if the share count has not
changed — and Week 7 found seven confirmed splits and blocked 301 marks for
exactly that reason. Where the footnote gives both a cost and a value for the
same position on the same date, that ratio is a **filed** fact and is reported
as `cost_to_value`. Anything else would be a number no filing produced (P3).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


# Travels with every timeline. A module-level constant rather than a literal
# inside the function so that a test can read it: an unreadable disclaimer is
# one nobody notices deleting.
NOT_COMPUTED = (
    "A return from N-CSR cost against an N-PORT price. The cost is for a "
    "position whose share count may have changed -- Week 7 confirmed seven "
    "splits and blocked 301 marks. Where a single filed row carries both cost "
    "and value, cost_to_value is reported instead.",
    "Any company-level valuation. Neither source carries shares outstanding, "
    "so there is no arithmetic from these tables to a company value.",
    "A per-share price from Form D. Form D reports dollars offered and "
    "dollars sold, and no share count at all.",
)


def _rows(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, r)) for r in cur.fetchall()]


def exposure_map(conn, company: str | None = None) -> list[dict]:
    """One row per (fund family, company): size, share of fund, tenure.

    Built from the latest period end each family reported for that company,
    not from the whole history, because "how exposed is this manager" is a
    question about now. `first_period` and `periods_held` carry the history.

    Blended and unpriced marks are counted in `positions` but contribute no
    price; a blended mark has no published price by design (Week 7).
    """
    return _rows(conn, """
        WITH latest AS (
            SELECT m.company_id, f.family, max(m.period_end) AS period_end
              FROM marks m JOIN funds f ON f.fund_id = m.fund_id
             GROUP BY 1, 2
        )
        SELECT co.canonical_name                              AS company,
               co.status                                      AS coverage_status,
               l.family                                       AS manager,
               l.period_end                                   AS as_of,
               count(*)                                       AS positions,
               count(DISTINCT m.fund_id)                      AS funds,
               sum(m.value_usd)::numeric(20,2)                AS value_usd,
               sum(m.balance)::numeric(20,2)                  AS shares,
               max(rh.pct_net_assets)                         AS max_pct_net_assets,
               min(hist.first_period)                         AS first_period,
               max(hist.periods_held)                         AS periods_held
          FROM latest l
          JOIN marks m      ON m.company_id = l.company_id
                           AND m.period_end = l.period_end
          JOIN funds f      ON f.fund_id = m.fund_id AND f.family = l.family
          JOIN companies co ON co.company_id = l.company_id
          LEFT JOIN LATERAL (
              SELECT min(m2.period_end) AS first_period,
                     count(DISTINCT m2.period_end) AS periods_held
                FROM marks m2 JOIN funds f2 ON f2.fund_id = m2.fund_id
               WHERE m2.company_id = l.company_id AND f2.family = l.family
          ) hist ON TRUE
          LEFT JOIN LATERAL (
              SELECT max(r.pct_net_assets) AS pct_net_assets
                FROM raw_holdings r
                JOIN match_decisions d ON d.raw_id = r.raw_id
               WHERE d.company_id = l.company_id
                 AND r.filing_id = m.filing_id
          ) rh ON TRUE
         WHERE (%(company)s IS NULL OR co.canonical_name = %(company)s)
         GROUP BY 1, 2, 3, 4
         ORDER BY 1, 7 DESC NULLS LAST
    """, {"company": company})


def price_history(conn, company: str) -> list[dict]:
    """The N-PORT leg: price per share by period end, across managers.

    Guarded exactly as Week 8's findings are -- a blocked mark never enters a
    published series, so the same panel cannot say two different things in two
    different reports.
    """
    return _rows(conn, """
        SELECT m.period_end,
               count(DISTINCT f.family)                AS managers,
               count(*)                                AS marks,
               min(m.price_per_share)::numeric(18,4)   AS price_min,
               max(m.price_per_share)::numeric(18,4)   AS price_max,
               sum(m.value_usd)::numeric(20,2)         AS value_usd
          FROM marks m
          JOIN funds f      ON f.fund_id = m.fund_id
          JOIN companies co ON co.company_id = m.company_id
         WHERE co.canonical_name = %(company)s
           AND m.price_per_share IS NOT NULL
           AND NOT m.change_blocked
         GROUP BY 1 ORDER BY 1
    """, {"company": company})


def entries(conn, company: str) -> list[dict]:
    """The N-CSR leg: when a fund bought in, and what it paid.

    `cost_to_value` is computed only where the same filed row carries both a
    position cost and a position value. It is a ratio of two numbers from one
    table in one filing, which is a filed fact -- unlike cost against an
    N-PORT mark, which would silently assume the share count never changed.
    """
    rows = _rows(conn, """
        SELECT l.registrant, l.fund_name, l.form_type, l.report_date,
               l.issuer_name_raw, l.acquisition_date_raw,
               l.acquisition_date_first, l.acquisition_date_last,
               l.acquisition_date_is_range, l.cost_usd, l.cost_basis_scope,
               l.value_usd, l.pct_net_assets, l.source_url
          FROM restricted_lots l
          JOIN companies c ON c.canonical_name = l.company_provisional
         WHERE c.canonical_name = %(company)s
         ORDER BY l.acquisition_date_first NULLS LAST, l.registrant
    """, {"company": company})
    for row in rows:
        cost, value = row["cost_usd"], row["value_usd"]
        row["cost_to_value"] = (
            round(float(value) / float(cost), 4)
            if row["cost_basis_scope"] == "position" and cost and value else None)
    return rows


def rounds(conn, company: str) -> list[dict]:
    """The Form D leg: dates and amounts, for affirmed identities only.

    Returns nothing until a named human has affirmed a CIK for this company.
    That is the intended behaviour, not a missing feature: the alternative is
    joining on the issuer name, which would attribute every SPV that raised
    money to buy the company's shares to the company itself.
    """
    return _rows(conn, """
        SELECT f.filing_date, f.date_of_first_sale, f.submission_type,
               f.is_amendment, f.total_offering_amount, f.total_amount_sold,
               f.offering_is_indefinite, f.is_equity_type, f.is_debt_type,
               f.investors_already, f.entity_name, f.cik, f.accession
          FROM form_d_filings f
          JOIN company_identity i ON i.cik = f.cik
          JOIN companies c        ON c.company_id = i.company_id
         WHERE i.verdict = 'operating_company'
           AND c.canonical_name = %(company)s
         ORDER BY coalesce(f.date_of_first_sale, f.filing_date), f.accession
    """, {"company": company})


def timeline(conn, company: str) -> dict:
    """All three legs for one company, labelled by source and never merged."""
    marks = price_history(conn, company)
    lots = entries(conn, company)
    offerings = rounds(conn, company)

    with_cost = [r for r in lots if r["cost_basis_scope"] == "position"]
    return {
        "company": company,
        "n_port": {
            "source": "N-PORT monthly holdings, Level 3 private positions",
            "periods": len(marks),
            "first_period": str(marks[0]["period_end"]) if marks else None,
            "last_period": str(marks[-1]["period_end"]) if marks else None,
            "series": marks,
        },
        "n_csr": {
            "source": "Reg S-X 12-12 restricted-securities footnote "
                      "(N-CSR / N-CSRS)",
            "lots": len(lots),
            "with_position_cost": len(with_cost),
            "earliest_entry": min((r["acquisition_date_first"] for r in lots
                                   if r["acquisition_date_first"]), default=None),
            "entries": lots,
        },
        "form_d": {
            "source": "Form D, joined on an affirmed CIK in company_identity",
            "filings": len(offerings),
            "note": ("empty until a named human affirms an operating-company "
                     "CIK for this company; a name join would attribute SPV "
                     "raises to the company"
                     if not offerings else
                     "dates and amounts only. Form D carries no share count "
                     "and no price, so no valuation is derivable from it"),
            "offerings": offerings,
        },
        "not_computed": list(NOT_COMPUTED),
    }


# The two sources are filed by different parties for different reasons: the
# issuer files Form D because it sold securities, the fund files N-CSR because
# it owns them. Neither cites the other. So agreement between them is evidence
# rather than tautology -- and disagreement has to be read carefully, which is
# what the window below is for.
CORROBORATION_WINDOWS = (0, 7, 31)


def corroboration(conn) -> dict:
    """Do fund acquisition dates land on filed round dates?

    Restricted to acquisitions that fall **inside** a company's Form D filing
    window, and that restriction is the whole methodological point. SpaceX
    stopped filing Form D in July 2022; 22 of its 28 acquisition dates come
    after that. Measuring those against the nearest round gives gaps of 873,
    911, 1090 and 1293 days, and every one of those numbers is the distance to
    the end of the archive rather than anything about when a fund bought. Put
    them in the denominator and a real 56% agreement reads as 33%.

    Date ranges are excluded: a position built over three years has no single
    acquisition date to compare, and picking an endpoint would manufacture the
    match or the miss.
    """
    rows = _rows(conn, """
        WITH fd AS (
          SELECT i.company_id,
                 min(coalesce(f.date_of_first_sale, f.filing_date)) AS first_round,
                 max(coalesce(f.date_of_first_sale, f.filing_date)) AS last_round
            FROM company_identity i
            JOIN form_d_filings f ON f.cik = i.cik
           WHERE i.verdict = 'operating_company'
           GROUP BY 1)
        SELECT co.canonical_name                      AS company,
               l.acquisition_date_first               AS acquired,
               min(abs(l.acquisition_date_first
                       - coalesce(f.date_of_first_sale, f.filing_date))) AS gap_days,
               count(DISTINCT l.registrant)           AS registrants
          FROM restricted_lots l
          JOIN companies co        ON co.canonical_name = l.company_provisional
          JOIN fd                  ON fd.company_id = co.company_id
          JOIN company_identity i  ON i.company_id = co.company_id
                                  AND i.verdict = 'operating_company'
          JOIN form_d_filings f    ON f.cik = i.cik
         WHERE l.acquisition_date_first BETWEEN fd.first_round AND fd.last_round
           AND NOT l.acquisition_date_is_range
         GROUP BY 1, 2
         ORDER BY 1, 2
    """)
    outside = _rows(conn, """
        WITH fd AS (
          SELECT i.company_id,
                 min(coalesce(f.date_of_first_sale, f.filing_date)) AS first_round,
                 max(coalesce(f.date_of_first_sale, f.filing_date)) AS last_round
            FROM company_identity i
            JOIN form_d_filings f ON f.cik = i.cik
           WHERE i.verdict = 'operating_company'
           GROUP BY 1)
        SELECT co.canonical_name AS company,
               fd.first_round, fd.last_round,
               count(DISTINCT l.acquisition_date_first) FILTER (
                   WHERE l.acquisition_date_first NOT BETWEEN fd.first_round
                                                          AND fd.last_round)
                                                     AS dates_outside_window,
               count(DISTINCT l.acquisition_date_first) AS dates_total
          FROM fd
          JOIN companies co ON co.company_id = fd.company_id
          LEFT JOIN restricted_lots l
                 ON l.company_provisional = co.canonical_name
                AND l.acquisition_date_first IS NOT NULL
                AND NOT l.acquisition_date_is_range
         GROUP BY 1, 2, 3 ORDER BY 1
    """)

    counted = len(rows)
    hits = {w: sum(1 for r in rows if r["gap_days"] is not None
                   and int(r["gap_days"]) <= w)
            for w in CORROBORATION_WINDOWS}
    return {
        "dates_in_window": counted,
        "hits": hits,
        "share": {w: round(n / counted, 4) if counted else None
                  for w, n in hits.items()},
        "pairs": rows,
        "by_company": outside,
        "method": (
            "One row per (company, acquisition date) where the date falls "
            "inside that company's Form D filing window and is not a range. "
            "gap_days is the distance to the nearest filed round."),
        "caveat": (
            "Agreement is evidence, not proof of causation: a fund buying on "
            "the day an issuer reports first sale is consistent with "
            "participating in that round, and also with a secondary purchase "
            "that happened to settle the same day. What it is not is "
            "circular -- neither filing cites the other."),
    }


def summary(conn) -> dict:
    """Coverage of both new lanes, per company, for the findings report."""
    return {
        "exposure": _rows(conn, """
            SELECT co.canonical_name AS company,
                   count(DISTINCT f.family) AS managers,
                   count(DISTINCT m.fund_id) AS funds,
                   max(m.period_end) AS latest_period
              FROM marks m
              JOIN funds f ON f.fund_id = m.fund_id
              JOIN companies co ON co.company_id = m.company_id
             GROUP BY 1 ORDER BY 2 DESC
        """),
        "entry_dates": _rows(conn, """
            SELECT company_provisional AS company,
                   count(*) AS lots,
                   count(DISTINCT registrant) AS registrants,
                   count(*) FILTER (WHERE cost_basis_scope = 'position') AS position_cost,
                   count(*) FILTER (WHERE cost_basis_scope = 'fund_total') AS fund_total_cost,
                   min(acquisition_date_first) AS earliest_entry,
                   max(acquisition_date_last)  AS latest_entry
              FROM restricted_lots
             WHERE company_provisional IS NOT NULL
             GROUP BY 1 ORDER BY 2 DESC
        """),
    }
