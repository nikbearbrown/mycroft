"""The split detector. It suspects; it never adjusts.

plan.md, trap 1: "flag near-integer ratio moves (2x, 5x, 10x, 12x), flag any
single-period move beyond a threshold, and route to human review rather than
publishing. **A suspected split is never auto-adjusted.**"

Two tiers, because they mean different things and must not be conflated:

  split_suspected   the ratio between consecutive marks is within 1% of a whole
                    number between 2 and 20. This is the split signature, and a
                    mark carrying it is **blocked from every change series**
                    until a human adjudicates it (plan.md's third invariant).

  large_move        the price moved by 2x or more and the ratio is *not*
                    near-integer. Routed to a human for a look, and deliberately
                    **not blocked** -- a repricing is the signal this project
                    exists to measure, and quarantining every round would empty
                    the panel of exactly the events it is built to see.

--------------------------------------------------------------------------
Why the tolerance is relative, and why that is a correction
--------------------------------------------------------------------------
Week 6 used an *absolute* window of 0.02 with the ratio capped at 20, after an
earlier version used 2% of the ratio with no cap at all and flagged an OpenAI
move of 348x as "near-integer" (at 348 a 2% window is +/- 7).

The cap was the real fix. The absolute window then quietly failed a different
case -- `plan.md`'s own verification list requires that **Perplexity's 695 -> 58
transition is flagged**, and that ratio is 11.93. An absolute 0.02 window around
12 misses it by a factor of three.

So the rule is a **relative** window of 1% under a hard cap of 20. At 12 that is
+/- 0.12 and 11.93 is caught; at 2 it is +/- 0.02 and X.AI's 2.064 repricing is
correctly left alone; and 348 is excluded by the cap rather than by arithmetic
that stops working at scale.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SPLIT_TOLERANCE = 0.01      # relative, of the nearest whole number
SPLIT_MIN_RATIO = 2
SPLIT_MAX_RATIO = 20
LARGE_MOVE_RATIO = 2.0      # routed for a look, never blocked

# Two prices closer than this are the same price. Below it a "change" is
# rounding in the fourth decimal, not a re-mark.
SAME_PRICE = 1e-4


def is_split_ratio(ratio: float | None) -> bool:
    """Is this ratio the signature of a split?

    Symmetric: a 10x rise and a 10x fall are the same event seen from two
    sides, so the caller passes the ratio already oriented to be >= 1.
    """
    if ratio is None or ratio < SPLIT_MIN_RATIO or ratio > SPLIT_MAX_RATIO:
        return False
    nearest = round(ratio)
    return abs(ratio - nearest) <= SPLIT_TOLERANCE * nearest


# The detector runs entirely in SQL: it is a window function over marks already
# in the table, and doing it in Python would mean pulling 5,185 rows across the
# network to compute a lag.
DETECT = """
WITH seq AS (
    SELECT mark_id,
           price_per_share AS px,
           lag(price_per_share) OVER w AS prev_px,
           lag(period_end)      OVER w AS prev_pe
      FROM marks
     WHERE price_per_share IS NOT NULL AND price_per_share > 0
    WINDOW w AS (PARTITION BY security_id, fund_id ORDER BY period_end)
), judged AS (
    SELECT mark_id, px, prev_px, prev_pe,
           CASE WHEN prev_px IS NULL OR prev_px = 0 THEN NULL
                WHEN px > prev_px THEN px / prev_px
                ELSE prev_px / px END AS ratio
      FROM seq
), flagged AS (
    SELECT j.*,
           (j.ratio IS NOT NULL
            AND j.ratio BETWEEN %(min_ratio)s AND %(max_ratio)s
            AND abs(j.ratio - round(j.ratio)) <= %(tol)s * round(j.ratio)) AS near_integer,
           (j.ratio IS NOT NULL AND j.ratio >= %(large)s)                  AS large
      FROM judged j
)
UPDATE marks m
   SET prior_price_per_share = f.prev_px,
       prior_period_end      = f.prev_pe,
       is_remark             = CASE WHEN f.prev_px IS NULL THEN NULL
                                    ELSE abs(f.px - f.prev_px) > %(same)s END,
       split_ratio           = f.ratio,
       split_suspected       = f.near_integer,
       split_reason          = CASE
                                 WHEN f.near_integer THEN
                                   'ratio ' || round(f.ratio, 4)
                                   || ' is within 1%% of ' || round(f.ratio)
                                   || ' between ' || f.prev_pe || ' and ' || m.period_end
                                 WHEN f.large THEN
                                   'large move: ' || round(f.ratio, 4)
                                   || 'x between ' || f.prev_pe || ' and ' || m.period_end
                                   || ' -- routed for review, not blocked'
                                 ELSE NULL END,
       change_blocked        = m.change_blocked OR f.near_integer,
       block_reason          = CASE
                                 WHEN f.near_integer THEN
                                   'suspected split, unadjudicated: never enters a change series'
                                 ELSE m.block_reason END
  FROM flagged f
 WHERE m.mark_id = f.mark_id
"""

# A security whose series breaks somewhere is worth knowing about, but only the
# step that breaks is blocked.
#
# The first version blocked every mark of such a security. That is stronger
# than plan.md, whose invariant is per mark -- "A mark with split_suspected =
# true and split_adjudicated = false never enters a change calculation" -- and
# it cost 90 further marks, including the whole of ARK's Anthropic series, for
# a break that a change between two other periods never crosses. So the series
# is flagged and the step is blocked, which are different claims.
WIDEN = """
UPDATE marks m
   SET series_flagged = TRUE
 WHERE m.security_id IN (SELECT security_id FROM marks
                          WHERE split_suspected AND NOT split_adjudicated)
   AND NOT m.series_flagged
"""

# What a human already said about these strings, from the Week 6 review queue.
# Carried onto the mark as evidence, never as an adjudication: the reviewer was
# answering "which company is this", and whether a step is a split is a
# different question that nobody has been asked yet.
ATTACH_CONTEXT = """
UPDATE marks m
   SET split_adjudication = 'prior human note (Week 6, identity review): '
                            || left(rd.rationale, 220)
  FROM securities s
  JOIN companies c ON c.company_id = s.company_id
  JOIN review_decisions rd ON rd.company_id = c.company_id
                          AND rd.trigger = 'split'
 WHERE m.security_id = s.security_id
   AND m.split_suspected
   AND m.split_adjudication IS NULL
"""


def detect(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE marks SET split_suspected = FALSE, split_ratio = NULL,
                             split_reason = NULL, is_remark = NULL,
                             prior_price_per_share = NULL, prior_period_end = NULL,
                             split_adjudication = NULL,
                             series_flagged = FALSE,
                             change_blocked = (price_per_share IS NULL),
                             block_reason = CASE WHEN price_per_share IS NULL
                                                 THEN block_reason ELSE NULL END
        """)
        cur.execute(DETECT, {"min_ratio": SPLIT_MIN_RATIO, "max_ratio": SPLIT_MAX_RATIO,
                             "tol": SPLIT_TOLERANCE, "large": LARGE_MOVE_RATIO,
                             "same": SAME_PRICE})
        stepped = cur.rowcount
        cur.execute(ATTACH_CONTEXT)
        cur.execute(WIDEN)
        widened = cur.rowcount
        cur.execute("""
            SELECT count(*) FILTER (WHERE split_suspected)                   AS suspected,
                   count(*) FILTER (WHERE split_reason LIKE 'large move%')   AS large_moves,
                   count(*) FILTER (WHERE change_blocked)                    AS blocked,
                   count(*) FILTER (WHERE is_remark)                         AS remarked,
                   count(*) FILTER (WHERE is_remark IS FALSE)                AS carried,
                   count(*) FILTER (WHERE is_remark IS NULL
                                      AND price_per_share IS NOT NULL)       AS first_seen,
                   count(*) FILTER (WHERE split_adjudicated)                 AS adjudicated,
                   count(*) FILTER (WHERE series_flagged)                    AS series_flagged
              FROM marks
        """)
        row = cur.fetchone()
    conn.commit()
    return {"steps_scored": stepped, "series_flagged": row[7], "flagged_now": widened,
            "split_suspected": row[0], "large_moves": row[1], "change_blocked": row[2],
            "re_marked": row[3], "carried_forward": row[4], "first_observation": row[5],
            "adjudicated": row[6]}


def suspected(conn) -> list[dict]:
    """The quarantine, for a human to read."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.canonical_name                        AS company,
                   s.class_normalized                      AS class,
                   s.share_class_raw                       AS title,
                   count(*)                                AS marks,
                   min(m.split_ratio)::numeric(12,4)       AS ratio_min,
                   max(m.split_ratio)::numeric(12,4)       AS ratio_max,
                   min(m.prior_period_end)::text           AS from_period,
                   max(m.period_end)::text                 AS to_period,
                   min(m.prior_price_per_share)::numeric(14,4) AS price_before,
                   min(m.price_per_share)::numeric(14,4)   AS price_after,
                   bool_and(m.split_adjudicated)           AS adjudicated,
                   max(m.split_factor)::numeric(12,4)      AS factor,
                   count(*) FILTER (WHERE m.change_blocked) AS blocked,
                   min(m.split_adjudication)               AS note
              FROM marks m
              JOIN securities s ON s.security_id = m.security_id
              JOIN companies  c ON c.company_id  = m.company_id
             WHERE m.split_suspected
             GROUP BY 1, 2, 3
             ORDER BY 4 DESC, 1
        """)
        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, r)) for r in cur.fetchall()]

VERDICTS = ("split", "not_a_split", "unresolved")


def adjudicate(conn, *, company: str, verdict: str, reviewer: str, rationale: str,
               factor: float | None = None, share_class: str | None = None) -> dict:
    """Record a human verdict on a suspected split. Never adjusts a price.

      not_a_split  the step is a real repricing; the block lifts and the mark
                   enters the change series.
      split        the step is a split; the block **stays on**, because
                   applying a factor is Week 8's work under its own gate. What
                   changes is that the question is now answered.
      unresolved   the reviewer cannot tell. The block stays.

    `factor` is required for a split and is **not** the ratio the detector
    measured. ARK's Perplexity step has a ratio of 11.93 because a 10:1 split
    and a 16% markdown landed in one period; the factor is 10 and the markdown
    is a real price move.

    This lives here rather than in the CLI because it was wrong in the CLI: an
    earlier version accepted `--factor` and never wrote it, so a recorded
    adjudication silently carried a null factor. A function can be tested.
    """
    if verdict not in VERDICTS:
        raise ValueError(f"verdict must be one of {VERDICTS}, got {verdict!r}")
    if not (reviewer or "").strip():
        raise ValueError("a split adjudication needs a named reviewer -- "
                         "'auto' is not a name (P4)")
    if not (rationale or "").strip():
        raise ValueError("a split adjudication needs a written reason (P4)")
    if verdict == "split" and not factor:
        raise ValueError(
            "a split verdict needs a factor, and it is not the detected ratio: "
            "ARK's Perplexity step reads 11.93 because a 10:1 split and a 16% "
            "markdown fell in one period. Adjusting by 11.93 would erase a real "
            "price move."
        )

    stamp = f"{verdict} -- {reviewer.strip()}: {rationale.strip()}"
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE marks m
               SET split_adjudicated  = TRUE,
                   split_adjudication = %(stamp)s,
                   split_factor       = %(factor)s,
                   change_blocked     = CASE WHEN %(verdict)s = 'not_a_split'
                                             THEN (m.price_per_share IS NULL)
                                             ELSE TRUE END,
                   block_reason       = CASE
                       WHEN %(verdict)s = 'not_a_split' AND m.price_per_share IS NOT NULL
                            THEN NULL
                       WHEN %(verdict)s = 'split'
                            THEN 'confirmed split, awaiting adjustment (Week 8)'
                       ELSE m.block_reason END
              FROM securities s, companies c
             WHERE m.security_id = s.security_id
               AND c.company_id  = m.company_id
               AND m.split_suspected
               AND c.canonical_name ILIKE %(company)s
               AND (%(klass)s IS NULL OR s.class_normalized = %(klass)s)
        """, {"stamp": stamp, "verdict": verdict, "factor": factor,
              "company": f"%{company}%", "klass": share_class})
        touched = cur.rowcount
        cur.execute("""
            UPDATE marks SET series_flagged = FALSE
             WHERE security_id NOT IN (SELECT security_id FROM marks
                                        WHERE split_suspected AND NOT split_adjudicated)
               AND series_flagged
        """)
        cleared = cur.rowcount
    conn.commit()
    return {"marks": touched, "series_flags_cleared": cleared,
            "verdict": verdict, "factor": factor, "reviewer": reviewer.strip()}
