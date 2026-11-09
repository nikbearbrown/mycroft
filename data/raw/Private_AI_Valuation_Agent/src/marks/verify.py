"""Verify the marks panel against `plan.md`'s named end-to-end checks.

plan.md lists the checks this project must be able to pass. Six of them land on
the marks panel; they are implemented here as functions that return what they
found rather than a boolean, so a failure says what the data actually said.

Each check traces back to an accession number, because "verified by hand
against source filings" means a person can open the filing.

One check on plan.md's list is **structurally unreachable** and says so rather
than passing quietly: the Anthropic repricing to ~$589 has period ends of
2026-05-29 and 2026-05-31, which sit in the 2026Q3 bulk set. The SEC has not
published it. Bulk data ends at 2026-04-30 (docs/feasibility.md), so no marks
panel built from bulk can contain that pair.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

TOLERANCE = 0.005  # half a cent, for comparing a recomputed price to a filed one


def _rows(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, r)) for r in cur.fetchall()]


# --------------------------------------------------------------------------
# 1. One position, by hand
# --------------------------------------------------------------------------


def anthropic_fidelity_position(conn) -> dict:
    """plan.md: "Verify the Anthropic 2026-03-31 Fidelity position by hand:
    46,814 shares, $12,131,380, **$259.14** per share."
    """
    found = _rows(conn, """
        SELECT f.family, fl.accession, fl.period_end,
               r.issuer_name, r.title_of_issue,
               r.balance::numeric(18,0)   AS shares,
               r.value_usd::numeric(18,0) AS value_usd,
               (r.value_usd / r.balance)::numeric(18,4) AS recomputed
          FROM raw_holdings r
          JOIN filings fl ON fl.filing_id = r.filing_id
          JOIN funds   f  ON f.fund_id    = fl.fund_id
         WHERE f.family = 'Fidelity'
           AND fl.period_end = DATE '2026-03-31'
           AND r.balance = 46814
         ORDER BY r.value_usd DESC
    """)
    expected = {"shares": 46814, "value_usd": 12131380, "price": 259.14}
    ok = any(
        int(r["shares"]) == expected["shares"]
        and abs(float(r["value_usd"]) - expected["value_usd"]) <= 1
        and abs(float(r["recomputed"]) - expected["price"]) <= TOLERANCE
        for r in found
    )
    return {"check": "Anthropic / Fidelity / 2026-03-31 position",
            "expected": expected, "found": found, "passed": ok}


# --------------------------------------------------------------------------
# 2. Four managers, one price
# --------------------------------------------------------------------------


def anthropic_manager_agreement(conn) -> dict:
    """plan.md: "Confirm four managers resolve to the same $259.14 for
    Anthropic in the 3/31-4/30 window"."""
    found = _rows(conn, """
        SELECT m.price_per_share::numeric(18,4) AS price,
               count(DISTINCT f.family)         AS families,
               string_agg(DISTINCT f.family, ', ' ORDER BY f.family) AS managers,
               count(*)                         AS marks
          FROM marks m
          JOIN companies c ON c.company_id = m.company_id
          JOIN funds     f ON f.fund_id    = m.fund_id
         WHERE c.canonical_name = 'Anthropic PBC'
           AND m.period_end BETWEEN DATE '2026-03-31' AND DATE '2026-04-30'
           AND m.price_per_share IS NOT NULL
         GROUP BY 1
         ORDER BY 2 DESC, 1
    """)
    # Two clusters sit inside half a cent of 259.14 -- 259.1364 (8 families)
    # and 259.1400 (ARK and Fidelity) -- because filers round value and share
    # count differently. Taking only the largest cluster would report 8 where
    # the honest answer is 10, so every cluster within tolerance is counted.
    at_259 = [r for r in found if abs(float(r["price"]) - 259.14) <= TOLERANCE]
    families = sum(int(r["families"]) for r in at_259)
    return {"check": "four managers agree at 259.14 in the 3/31-4/30 window",
            "expected": ">= 4 distinct manager families at 259.14",
            "found": found[:6],
            "clusters_within_half_a_cent": [
                {"price": str(r["price"]), "families": int(r["families"]),
                 "managers": r["managers"]} for r in at_259],
            "families_at_259_14": families,
            "passed": families >= 4}


def anthropic_589_pair(conn) -> dict:
    """plan.md also asks for the 5/29-5/31 pair at ~$589. It is not in bulk."""
    found = _rows(conn, """
        SELECT count(*) AS marks, max(period_end)::text AS newest_anthropic_period
          FROM marks m JOIN companies c ON c.company_id = m.company_id
         WHERE c.canonical_name = 'Anthropic PBC'
           AND m.period_end IN (DATE '2026-05-29', DATE '2026-05-31')
    """)
    newest = _rows(conn, "SELECT max(period_end)::text AS newest FROM marks")[0]["newest"]
    return {"check": "Anthropic 5/29-5/31 pair at ~589",
            "expected": "unreachable from bulk: those period ends are in 2026Q3, unpublished",
            "found": {"marks_in_panel": found[0]["marks"], "newest_period_in_panel": newest},
            "passed": None,
            "note": "Not a failure. The Week 1 hand-verification of 589.0095 stands on the "
                    "live filings; the bulk archive ends at 2026-04-30 and cannot contain it."}


# --------------------------------------------------------------------------
# 3. The split is caught and quarantined
# --------------------------------------------------------------------------


def perplexity_split_blocked(conn) -> dict:
    """plan.md: "Confirm Perplexity's 695 -> 58 transition is flagged as a
    suspected split and blocked from the change series until adjudicated."
    """
    found = _rows(conn, """
        SELECT s.class_normalized                       AS class,
               m.prior_price_per_share::numeric(18,4)   AS price_before,
               m.price_per_share::numeric(18,4)         AS price_after,
               m.split_ratio::numeric(12,4)             AS ratio,
               m.split_suspected, m.split_adjudicated, m.change_blocked,
               m.prior_period_end::text                 AS from_period,
               m.period_end::text                       AS to_period
          FROM marks m
          JOIN securities s ON s.security_id = m.security_id
          JOIN companies  c ON c.company_id  = m.company_id
         WHERE c.canonical_name = 'Perplexity AI, Inc.'
           AND m.split_suspected
         ORDER BY m.split_ratio DESC
    """)
    the_695_58 = [
        r for r in found
        if r["price_before"] and abs(float(r["price_before"]) - 695) < 1
        and r["price_after"] and abs(float(r["price_after"]) - 58) < 1
    ]
    # The requirement is "flagged as a suspected split and blocked from the
    # change series until adjudicated". An earlier version also required
    # `not split_adjudicated`, which meant a human answering the question made
    # the check fail -- it tested the pre-review state rather than the rule.
    # Adjudication state is reported, not required.
    ok = bool(the_695_58) and all(
        r["split_suspected"] and r["change_blocked"] for r in the_695_58
    )
    adjudicated = [r for r in the_695_58 if r["split_adjudicated"]]
    return {"check": "Perplexity 695 -> 58 flagged and blocked",
            "expected": "split_suspected and change_blocked; a confirmed split stays "
                        "blocked pending the Week 8 adjustment",
            "found": found, "the_695_58": the_695_58,
            "adjudicated": f"{len(adjudicated)} of {len(the_695_58)}",
            "passed": ok}


# --------------------------------------------------------------------------
# 4. SpaceX 10x is a unit artifact, not a class differential
# --------------------------------------------------------------------------


def spacex_unit_artifact(conn) -> dict:
    """plan.md: "Confirm SpaceX common versus preferred is flagged as a 10x
    unit artifact, not a class differential."

    Two ways the artifact shows up, and the panel has to survive both:
    same filing / same title / ten times apart, which becomes a **blended**
    mark with no price; and common against preferred across the panel on one
    day, which must be visible as a 10x relationship rather than published as
    a preference premium.
    """
    blended = _rows(conn, """
        SELECT c.canonical_name AS company, s.share_class_raw AS title,
               m.period_end::text, m.lines,
               m.price_min::numeric(18,4), m.price_max::numeric(18,4),
               (m.price_max / m.price_min)::numeric(12,4) AS ratio,
               m.price_per_share, m.block_reason
          FROM marks m
          JOIN securities s ON s.security_id = m.security_id
          JOIN companies  c ON c.company_id  = m.company_id
         WHERE m.is_blended
         ORDER BY ratio DESC
    """)
    same_day = _rows(conn, """
        SELECT m.period_end::text,
               min(m.price_per_share) FILTER (WHERE s.class_normalized LIKE 'COM%')::numeric(18,2) AS common,
               max(m.price_per_share) FILTER (WHERE s.class_normalized LIKE 'PFD%')::numeric(18,2) AS preferred
          FROM marks m
          JOIN securities s ON s.security_id = m.security_id
          JOIN companies  c ON c.company_id  = m.company_id
         WHERE c.canonical_name = 'Space Exploration Technologies Corp.'
           AND m.price_per_share IS NOT NULL
         GROUP BY 1
        HAVING min(m.price_per_share) FILTER (WHERE s.class_normalized LIKE 'COM%') IS NOT NULL
           AND max(m.price_per_share) FILTER (WHERE s.class_normalized LIKE 'PFD%') IS NOT NULL
         ORDER BY 1
    """)
    tenfold = [
        r for r in same_day
        if r["common"] and r["preferred"]
        and abs(float(r["preferred"]) / float(r["common"]) - 10) < 0.1
    ]
    spacex_blended = [r for r in blended if "Space Exploration" in (r["company"] or "")]
    return {"check": "SpaceX 10x is a unit artifact, not a class differential",
            "expected": "blended marks carry no price; the 10x is visible, not published "
                        "as a preference premium",
            "blended_marks": blended, "spacex_blended": len(spacex_blended),
            "same_day_pairs": same_day[:8], "tenfold_days": len(tenfold),
            "passed": len(spacex_blended) > 0 and all(
                r["price_per_share"] is None for r in blended)}


# --------------------------------------------------------------------------
# 5. World Labs C versus C Prime, a genuine differential
# --------------------------------------------------------------------------

WORLD_LABS_SQL = """
SELECT upper(ISSUER_TITLE) AS title,
       count(*)            AS holdings,
       min(PRICE_PER_SHARE) AS price_min,
       max(PRICE_PER_SHARE) AS price_max,
       count(DISTINCT CIK)  AS filers
  FROM p
 WHERE upper(ISSUER_NAME) LIKE '%WORLD LABS%'
   AND PRICE_PER_SHARE IS NOT NULL
 GROUP BY 1
 ORDER BY 1
"""


def world_labs_differential(quarters=None) -> dict:
    """plan.md: "Confirm World Labs Series C versus C Prime survives as a
    genuine differential."

    World Labs is **not** in universe v1, so it is not in the marks panel at
    all. The claim is about the share-class parser, not about the panel, and it
    is checked where the rows actually live: the Parquet private layer.
    """
    import duckdb

    from src.ingest.build_parquet import ALL_QUARTERS, PARQUET

    quarters = quarters or ALL_QUARTERS
    files = [(PARQUET / q / "private_holdings.parquet").as_posix() for q in quarters]
    con = duckdb.connect()
    con.execute(f"CREATE VIEW p AS SELECT * FROM read_parquet([{','.join(map(repr, files))}])")
    rows = [dict(zip([c[0] for c in con.description], r))
            for r in con.execute(WORLD_LABS_SQL).fetchall()] if False else None
    cur = con.execute(WORLD_LABS_SQL)
    columns = [c[0] for c in cur.description]
    rows = [dict(zip(columns, r)) for r in cur.fetchall()]
    con.close()

    from src.resolve.normalize import parse_class

    plain = [r for r in rows if "PRIME" not in r["title"]]
    prime = [r for r in rows if "PRIME" in r["title"]]
    labels = {r["title"]: parse_class(r["title"]).label() for r in rows}
    distinct_labels = len({v for v in labels.values()})
    prices_differ = bool(plain and prime) and (
        max(float(r["price_max"]) for r in plain)
        != max(float(r["price_max"]) for r in prime)
    )
    return {"check": "World Labs Series C vs C Prime is a real differential",
            "expected": "two distinct class labels and two distinct price levels",
            "found": rows, "class_labels": labels,
            "in_universe": False,
            "passed": distinct_labels >= 2 and prices_differ}


# --------------------------------------------------------------------------
# 6. Nothing vanishes
# --------------------------------------------------------------------------


def run_summary(conn) -> dict:
    """plan.md: "Confirm unresolved rows and opaque SPV counts appear in the
    run summary rather than vanishing."
    """
    rows = _rows(conn, """
        SELECT (SELECT count(*) FROM raw_holdings)                               AS holdings,
               (SELECT count(*) FROM match_decisions WHERE company_id IS NULL)   AS not_in_universe,

               (SELECT coalesce(sum(lines), 0) FROM marks)                       AS lines_in_marks,
               (SELECT count(*) FROM marks)                                      AS marks,
               (SELECT count(*) FROM marks WHERE price_per_share IS NULL)        AS unpriced_marks,
               (SELECT count(*) FROM marks WHERE spv_opaque)                     AS opaque_spv_marks,
               (SELECT count(*) FROM marks WHERE change_blocked)                 AS blocked_marks
    """)[0]
    from src.marks.build import coverage

    cov = coverage(conn)
    rows["superseded_by_amendment"] = cov["superseded_by_amendment"]
    return {"check": "every holding is accounted for",
            "expected": "holdings == not_in_universe + superseded_by_amendment "
                        "+ lines_in_marks, and the SPV count is reported not dropped",
            "found": rows, "reconciliation": cov,
            "passed": cov["reconciles"]}


def run_all(conn) -> list[dict]:
    return [
        anthropic_fidelity_position(conn),
        anthropic_manager_agreement(conn),
        anthropic_589_pair(conn),
        perplexity_split_blocked(conn),
        spacex_unit_artifact(conn),
        world_labs_differential(),
        run_summary(conn),
    ]
