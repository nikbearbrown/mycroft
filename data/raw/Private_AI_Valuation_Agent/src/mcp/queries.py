"""The six MCP tools' data layer: SQL in, dicts out, no protocol.

Kept apart from `server.py` so that every tool can be tested without an MCP
client, and so the server file stays a thin binding of names to functions. The
split also keeps one rule enforceable in one place: **nothing here reads a
table the rest of the project does not already read**, and nothing computes a
number the project does not already publish. The MCP server is a view over the
verified layer, not a second implementation of it (P2).

Two rules every function here follows:

* **Blocked marks never leave.** Week 7 quarantined 301 marks whose change
  crosses an unadjudicated split. They are excluded from every price series
  exactly as `src/signal/findings.py` excludes them, so the MCP answer and the
  findings report cannot disagree.
* **A judgment is labelled.** Nothing here returns a model's opinion, but
  `list_unresolved` returns the matcher's proposals, and they are marked as
  proposals.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _rows(conn, sql, args=None) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(sql, args)
        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, r)) for r in cur.fetchall()]


def _one(conn, sql, args=None) -> dict:
    rows = _rows(conn, sql, args)
    return rows[0] if rows else {}


# -------------------------------------------------------------------------
# list_companies
# -------------------------------------------------------------------------

def list_companies(conn) -> tuple[list[dict], dict]:
    """Every company in the universe, with the size of its evidence.

    This is the entry point: a model that calls anything else first is
    guessing at a company name. `status` carries the Week 1 coverage decision
    -- `full`, `thin` or `watchlist` -- because a caller asking for dispersion
    on a thin company should be told it is thin before it reads a number.
    """
    rows = _rows(conn, """
        SELECT c.canonical_name                       AS company,
               c.status,
               count(m.mark_id)                       AS marks,
               count(DISTINCT f.family)               AS managers,
               count(DISTINCT m.period_end)           AS periods,
               min(m.period_end)                      AS first_period,
               max(m.period_end)                      AS last_period,
               count(*) FILTER (WHERE m.change_blocked) AS blocked_marks
          FROM companies c
          LEFT JOIN marks m ON m.company_id = c.company_id
          LEFT JOIN funds f ON f.fund_id = m.fund_id
         GROUP BY 1, 2
         ORDER BY count(m.mark_id) DESC
    """)
    summary = {
        "companies": len(rows),
        "with_marks": sum(1 for r in rows if r["marks"]),
        "coverage_status": {
            s: sum(1 for r in rows if r["status"] == s)
            for s in sorted({r["status"] for r in rows if r["status"]})},
        "note": "status 'thin' means marks are published but dispersion and "
                "propagation are suppressed; 'watchlist' means the company is "
                "outside universe v1 and its rows are carried for a later "
                "revisit, not published as findings.",
    }
    return rows, summary


# -------------------------------------------------------------------------
# get_marks
# -------------------------------------------------------------------------

def get_marks(conn, company: str, share_class: str | None = None,
              since: str | None = None) -> tuple[list[dict], dict]:
    """The price series for one company, optionally one share class.

    Returns one row per (period end, manager, class) rather than per filed
    holding, because a manager reporting one security across several lots is
    normal and the lots are already summed into a mark.
    """
    rows = _rows(conn, """
        SELECT m.period_end,
               f.family                                AS manager,
               s.class_normalized                      AS share_class,
               m.asset_category,
               m.price_per_share::numeric(18,4)        AS price_per_share,
               m.balance,
               m.value_usd,
               m.is_remark,
               m.is_blended,
               m.is_spv,
               m.split_suspected
          FROM marks m
          JOIN companies c  ON c.company_id  = m.company_id
          JOIN funds f      ON f.fund_id     = m.fund_id
          JOIN securities s ON s.security_id = m.security_id
         WHERE c.canonical_name = %(company)s
           AND NOT m.change_blocked
           AND m.price_per_share IS NOT NULL
           AND (%(share_class)s IS NULL OR s.class_normalized = %(share_class)s)
           AND (%(since)s IS NULL OR m.period_end >= %(since)s::date)
         ORDER BY m.period_end DESC, f.family
    """, {"company": company, "share_class": share_class, "since": since})

    if not rows:
        return rows, {"company": company, "marks": 0,
                      "note": "no published marks. Either the company is not "
                              "in the universe (call list_companies), or every "
                              "mark for it is blocked or unpriced."}

    prices = [float(r["price_per_share"]) for r in rows]
    periods = sorted({str(r["period_end"]) for r in rows})
    latest = [r for r in rows if str(r["period_end"]) == periods[-1]]
    blocked = _one(conn, """
        SELECT count(*) AS blocked
          FROM marks m JOIN companies c ON c.company_id = m.company_id
         WHERE c.canonical_name = %s AND m.change_blocked
    """, (company,))

    summary = {
        "company": company,
        "share_class": share_class,
        "marks": len(rows),
        "periods": len(periods),
        "first_period": periods[0],
        "last_period": periods[-1],
        "latest_period_managers": len({r["manager"] for r in latest}),
        "latest_price_min": round(min(float(r["price_per_share"]) for r in latest), 4),
        "latest_price_max": round(max(float(r["price_per_share"]) for r in latest), 4),
        "price_min": round(min(prices), 4),
        "price_max": round(max(prices), 4),
        "blocked_marks_excluded": int(blocked.get("blocked") or 0),
        "note": "price_per_share is value_usd / balance as filed. Blocked "
                "marks -- those whose change crosses an unadjudicated split -- "
                "are excluded and counted above, never silently dropped.",
    }
    return rows, summary


# -------------------------------------------------------------------------
# compare_managers
# -------------------------------------------------------------------------

def compare_managers(conn, company: str, window: str | None = None,
                     min_holders: int = 2) -> tuple[list[dict], dict]:
    """What different managers said about one company on the same date.

    `window` is a period end. Omitted, it means the latest period on which at
    least `min_holders` managers both priced the company -- which is not the
    same as the latest period overall, and asking for the latter would often
    return a single manager and no comparison at all.
    """
    if window is None:
        latest = _one(conn, """
            SELECT m.period_end
              FROM marks m JOIN companies c ON c.company_id = m.company_id
              JOIN funds f ON f.fund_id = m.fund_id
             WHERE c.canonical_name = %(company)s
               AND NOT m.change_blocked AND m.price_per_share IS NOT NULL
             GROUP BY m.period_end
            HAVING count(DISTINCT f.family) >= %(min_holders)s
             ORDER BY m.period_end DESC LIMIT 1
        """, {"company": company, "min_holders": min_holders})
        window = str(latest["period_end"]) if latest else None

    if window is None:
        return [], {"company": company, "managers": 0,
                    "note": f"no period end has {min_holders} or more managers "
                            "pricing this company, so there is nothing to "
                            "compare. get_marks returns the single-manager "
                            "series."}

    rows = _rows(conn, """
        SELECT f.family                         AS manager,
               s.class_normalized               AS share_class,
               m.price_per_share::numeric(18,4) AS price_per_share,
               m.balance,
               m.value_usd,
               m.is_remark,
               m.prior_price_per_share::numeric(18,4) AS prior_price_per_share
          FROM marks m
          JOIN companies c  ON c.company_id  = m.company_id
          JOIN funds f      ON f.fund_id     = m.fund_id
          JOIN securities s ON s.security_id = m.security_id
         WHERE c.canonical_name = %(company)s
           AND m.period_end = %(window)s::date
           AND NOT m.change_blocked
           AND m.price_per_share IS NOT NULL
         ORDER BY m.price_per_share
    """, {"company": company, "window": window})

    if not rows:
        return rows, {"company": company, "period_end": window, "managers": 0,
                      "note": "no published marks on that period end."}

    prices = [float(r["price_per_share"]) for r in rows]
    low, high = min(prices), max(prices)
    from src.signal.findings import LEVEL_REL, _levels

    levels = _levels(prices, LEVEL_REL)
    summary = {
        "company": company,
        "period_end": window,
        "managers": len({r["manager"] for r in rows}),
        "marks": len(rows),
        "price_min": round(low, 4),
        "price_max": round(high, 4),
        "spread": round(high / low - 1, 4) if low else None,
        "distinct_price_levels": len(levels),
        "note": "A spread is not automatically disagreement. Where "
                "distinct_price_levels is 2 or more, some managers may have "
                "reflected a new round and others not -- the levels are "
                "clustered within "
                f"{LEVEL_REL:.0%} of each other. Period ends are staggered "
                "across fund families, so same-date here means same filed "
                "period end, not same observation moment.",
    }
    return rows, summary


# -------------------------------------------------------------------------
# get_propagation
# -------------------------------------------------------------------------

def get_propagation(conn, company: str | None = None,
                    event: str | None = None,
                    min_holders: int = 3) -> tuple[list[dict], dict]:
    """How long a new price level took to reach the managers who adopted it.

    Delegates the measurement to `src.signal.findings.propagation` rather than
    re-deriving it, so that an MCP caller and the findings report cannot get
    different numbers from the same database (P6).
    """
    from src.signal.findings import propagation

    measured = propagation(conn, min_holders=min_holders)
    rows = measured["events"]
    if company:
        rows = [r for r in rows if r["company"] == company]
    if event:
        rows = [r for r in rows if str(r.get("price")) == str(event)
                or str(r.get("first_manager_date")) == str(event)]

    lags = [int(r["lag_to_half_days"]) for r in rows
            if r.get("lag_to_half_days") is not None]
    summary = {
        "company": company,
        "events": len(rows),
        "min_holders": min_holders,
        "median_days_to_half": (sorted(lags)[len(lags) // 2] if lags else None),
        "max_days_to_half": max(lags) if lags else None,
        "same_period_end": sum(1 for lag in lags if lag == 0),
        "caveat": measured["caveat"],
    }
    return rows, summary


# -------------------------------------------------------------------------
# get_fund_exposure
# -------------------------------------------------------------------------

def get_fund_exposure(conn, fund: str | None = None) -> tuple[list[dict], dict]:
    """What a manager holds, and how much of its funds it is.

    `fund` matches the family name case-insensitively and by prefix, because a
    caller will say "Baron" and the stored value is "Baron Capital".
    """
    from src.signal.exposure import exposure_map

    rows = exposure_map(conn)
    if fund:
        needle = fund.strip().lower()
        rows = [r for r in rows if needle in (r["manager"] or "").lower()]

    pcts = [float(r["max_pct_net_assets"]) for r in rows
            if r["max_pct_net_assets"] is not None]
    summary = {
        "fund": fund,
        "pairs": len(rows),
        "managers": len({r["manager"] for r in rows}),
        "companies": len({r["company"] for r in rows}),
        "max_pct_net_assets": round(max(pcts), 4) if pcts else None,
        "note": "pct of net assets is the filer's own figure from N-PORT, not "
                "value divided by a net-asset number computed here. Each row "
                "is that manager's latest reported period end, which differs "
                "between managers.",
    }
    if fund and not rows:
        summary["note"] = (f"no manager matching {fund!r}. Call "
                           "get_fund_exposure with no argument to list them.")
    return rows, summary


# -------------------------------------------------------------------------
# list_unresolved
# -------------------------------------------------------------------------

def list_unresolved(conn) -> tuple[list[dict], dict]:
    """What the resolution pipeline could not settle, and what is still open.

    Three distinct kinds of open question, returned together because a caller
    asking "what is unresolved" means all of them:

      review_unresolved  a human looked and could not tell
      split_pending      a suspected split nobody has adjudicated
      identity_pending   a Form D CIK with no affirmed identity

    An empty list is a real answer and says so, rather than looking like a
    failed query.
    """
    rows = _rows(conn, """
        SELECT 'review_unresolved'           AS kind,
               r.decision_key                AS subject,
               r.issuer_name                 AS detail,
               r.trigger                     AS reason,
               r.reviewer,
               r.decided_at::date            AS as_of
          FROM review_decisions r
         WHERE r.verdict = 'unresolved'
        UNION ALL
        SELECT 'split_pending',
               c.canonical_name,
               'ratio ' || round(m.split_ratio, 4) || ' at ' || m.period_end,
               m.split_reason,
               NULL,
               m.period_end
          FROM marks m JOIN companies c ON c.company_id = m.company_id
         WHERE m.split_suspected AND NOT m.split_adjudicated
        UNION ALL
        SELECT 'identity_pending',
               f.cik,
               f.entity_name,
               'Form D issuer with no affirmed identity',
               NULL,
               max(f.filing_date)
          FROM form_d_filings f
          LEFT JOIN company_identity i ON i.cik = f.cik
         WHERE i.cik IS NULL AND f.vehicle_class = 'candidate_operating'
         GROUP BY 1, 2, 3, 4, 5
         ORDER BY 1, 2
    """)
    kinds: dict[str, int] = {}
    for row in rows:
        kinds[row["kind"]] = kinds.get(row["kind"], 0) + 1
    summary = {
        "open_items": len(rows),
        "by_kind": kinds,
        "note": ("nothing is unresolved: every ambiguity has a recorded human "
                 "decision, every suspected split is adjudicated, and every "
                 "Form D candidate identity is affirmed."
                 if not rows else
                 "each row is a question a named human has not yet answered. "
                 "Nothing downstream treats these as resolved."),
    }
    return rows, summary
