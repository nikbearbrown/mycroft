"""Week 8's four measurements, over the marks panel.

    re-mark frequency   how often a mark actually moves
    dispersion          how far apart managers are on one company at one time
    propagation         how long a repricing takes to reach every manager
    the Cerebras study  the Level 3 run-up to an IPO

Every one of them reads `marks` and nothing else, so each number traces to a
filed holding through `match_decisions` and `raw_holdings` (P3).

--------------------------------------------------------------------------
What is excluded, and why it is excluded here rather than upstream
--------------------------------------------------------------------------
Three guards, all from plan.md, applied in one place so that no measurement can
forget one:

  change_blocked      a mark with an unadjudicated suspected split, a confirmed
                      split awaiting adjustment, or no price at all. plan.md:
                      "A mark with split_suspected = true and
                      split_adjudicated = false never enters a change
                      calculation."
  incomplete run      "A run with complete = false is never the prior-period
                      baseline for re-mark detection." There are no incomplete
                      runs today, so this guard is currently inert -- which is
                      worth saying rather than implying it did work.
  no prior            a first observation is not a carry-forward and not a
                      re-mark. It is recorded as neither.

A zero delta and a carry-forward are the same arithmetic and different facts,
and the difference is not observable from a filing: a fund that re-valued and
arrived at the same number is indistinguishable from one that carried the old
number forward. So this module reports "unchanged" and never claims staleness.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# A repricing is "the same price" across managers when they agree this closely.
# Filers round value and share count differently: ten manager families report
# Anthropic at 259.14 and split into 259.1364 and 259.1400 at four decimals.
SAME_PRICE_REL = 0.001          # 0.1%, so 259.1364 and 259.1400 are one level

# Dispersion needs enough managers to be a spread rather than a disagreement
# between two funds. plan.md calls for "a minimum-holders threshold" without
# fixing it; 3 is the smallest number for which a spread has a middle.
MIN_HOLDERS = 3
# The window is a forward SPAN, not a radius. The first version used +/- 45
# days, which is a 90-day span, and over 90 days a fast-appreciating company
# genuinely reprices -- Databricks moved 28.32 to 60.00 inside one such
# window, and calling that "manager disagreement" would be nonsense. 31 days
# matches plan.md's own near-simultaneous example: ARK on 4/30, BlackRock on
# 5/29, Capital Group on 5/31.
WINDOW_DAYS = 31

# A manager this far from the window median is not disagreeing about value; it
# is quoting a different instrument or a different unit. Five, because the
# artifacts in this corpus are an order of magnitude (SpaceX's 10x preferred
# convention) or worse (a 150-million-unit LLC interest), while real spreads
# run to tens of percent.
OUTLIER_FACTOR = 5.0

# Two manager prices belong to the same price level when they are this close.
# 2%: filers round differently (141.5965 against 140.9676 is 0.45%, and
# Fidelity's 261.5705 against the 259.1364 consensus is 0.94%), while a genuine
# round change is tens of percent (203.36 to 259.14 is 27%).
LEVEL_REL = 0.02

# Only marks that survive every guard may enter a measurement.
USABLE = """
SELECT m.mark_id, m.company_id, m.security_id, m.fund_id, m.period_end,
       m.price_per_share, m.prior_price_per_share, m.prior_period_end,
       m.is_remark, c.canonical_name AS company, f.family AS manager,
       s.class_normalized AS class
  FROM marks m
  JOIN companies  c ON c.company_id  = m.company_id
  JOIN funds      f ON f.fund_id     = m.fund_id
  JOIN securities s ON s.security_id = m.security_id
  LEFT JOIN runs  r ON r.run_id      = m.run_id
 WHERE m.price_per_share IS NOT NULL
   AND NOT m.change_blocked
   AND (r.run_id IS NULL OR r.complete)
"""


def _rows(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, r)) for r in cur.fetchall()]


def guards(conn) -> dict:
    """What each guard removed. Reported so a reader can see the cost."""
    return _rows(conn, """
        SELECT (SELECT count(*) FROM marks)                                AS marks,
               (SELECT count(*) FROM marks WHERE price_per_share IS NULL)  AS unpriced,
               (SELECT count(*) FROM marks WHERE change_blocked)           AS change_blocked,
               (SELECT count(*) FROM marks WHERE split_suspected
                                             AND NOT split_adjudicated)    AS unadjudicated_splits,
               (SELECT count(*) FROM marks WHERE split_adjudicated
                                             AND split_factor IS NOT NULL) AS confirmed_splits,
               (SELECT count(*) FROM runs WHERE NOT complete)              AS incomplete_runs,
               (SELECT count(*) FROM marks m LEFT JOIN runs r
                                               ON r.run_id = m.run_id
                 WHERE r.run_id IS NOT NULL AND NOT r.complete)            AS on_incomplete_runs
    """)[0]


# --------------------------------------------------------------------------
# 1. Re-mark versus carry-forward
# --------------------------------------------------------------------------


def remark_frequency(conn) -> dict:
    """How often a mark moves, once every guard is applied.

    plan.md's stated expectation: "Roughly 30-40% of consecutive observations
    are unchanged. Staleness is real but is *not* the majority case."
    """
    overall = _rows(conn, f"""
        WITH usable AS ({USABLE})
        SELECT count(*) FILTER (WHERE prior_price_per_share IS NOT NULL) AS steps,
               count(*) FILTER (WHERE is_remark)                          AS moved,
               count(*) FILTER (WHERE is_remark IS FALSE)                 AS unchanged,
               count(*) FILTER (WHERE is_remark IS NULL)                  AS first_observation,
               count(*)                                                   AS marks
          FROM usable
    """)[0]
    steps = int(overall["steps"])
    overall["share_unchanged"] = round(int(overall["unchanged"]) / steps, 4) if steps else None
    overall["share_moved"] = round(int(overall["moved"]) / steps, 4) if steps else None

    by_company = _rows(conn, f"""
        WITH usable AS ({USABLE})
        SELECT company,
               count(*) FILTER (WHERE prior_price_per_share IS NOT NULL) AS steps,
               count(*) FILTER (WHERE is_remark)                          AS moved,
               count(*) FILTER (WHERE is_remark IS FALSE)                 AS unchanged,
               count(DISTINCT manager)                                    AS managers
          FROM usable
         GROUP BY 1
        HAVING count(*) FILTER (WHERE prior_price_per_share IS NOT NULL) > 0
         ORDER BY 2 DESC
    """)
    for row in by_company:
        row["share_unchanged"] = round(int(row["unchanged"]) / int(row["steps"]), 4)

    by_manager = _rows(conn, f"""
        WITH usable AS ({USABLE})
        SELECT manager,
               count(*) FILTER (WHERE prior_price_per_share IS NOT NULL) AS steps,
               count(*) FILTER (WHERE is_remark)                          AS moved,
               count(*) FILTER (WHERE is_remark IS FALSE)                 AS unchanged,
               count(DISTINCT company)                                    AS companies
          FROM usable
         GROUP BY 1
        HAVING count(*) FILTER (WHERE prior_price_per_share IS NOT NULL) >= 20
         ORDER BY 2 DESC
    """)
    for row in by_manager:
        row["share_unchanged"] = round(int(row["unchanged"]) / int(row["steps"]), 4)

    # A move of a hundredth of a cent is rounding, not a re-mark. The headline
    # uses the exact rule; this says how much the answer would move under
    # looser ones, so "75% of marks move" is not resting on noise.
    sensitivity = _rows(conn, f"""
        WITH usable AS ({USABLE})
        SELECT count(*) FILTER (WHERE is_remark)                             AS moved,
               count(*) FILTER (WHERE is_remark IS FALSE)                    AS unchanged,
               count(*) FILTER (WHERE is_remark AND abs(price_per_share - prior_price_per_share)
                                      <= 0.001 * prior_price_per_share)      AS moved_under_0_1pct,
               count(*) FILTER (WHERE is_remark AND abs(price_per_share - prior_price_per_share)
                                      <= 0.01 * prior_price_per_share)       AS moved_under_1pct
          FROM usable
         WHERE prior_price_per_share IS NOT NULL
    """)[0]
    # A panel with no priors is a legitimate state -- a first run, or a fixture
    # -- and must not divide by zero.
    steps_s = int(sensitivity["moved"]) + int(sensitivity["unchanged"])

    def share(extra=0):
        if not steps_s:
            return None
        return round((int(sensitivity["unchanged"]) + extra) / steps_s, 4)

    sensitivity["unchanged_exact"] = share()
    sensitivity["unchanged_if_0_1pct_is_flat"] = share(
        int(sensitivity["moved_under_0_1pct"]))
    sensitivity["unchanged_if_1pct_is_flat"] = share(
        int(sensitivity["moved_under_1pct"]))

    return {"overall": overall, "by_company": by_company, "by_manager": by_manager,
            "sensitivity": sensitivity,
            "plan_expectation": "30-40% of consecutive observations unchanged"}


def _levels(prices: list[float], rel: float) -> list[list[float]]:
    """Cluster sorted prices into price levels.

    A price joins the current level if it is within `rel` of that level's
    highest member so far. Filers round differently (Fidelity 141.5965 against
    JPMorgan 140.9676 is 0.45%) and 2% groups those as one level while keeping
    203.36 and 259.14 apart, which is a 27% gap and a different round.
    """
    clusters: list[list[float]] = []
    for price in sorted(prices):
        if clusters and price <= clusters[-1][-1] * (1 + rel):
            clusters[-1].append(price)
        else:
            clusters.append([price])
    return clusters


# --------------------------------------------------------------------------
# 2. Cross-manager dispersion
# --------------------------------------------------------------------------


def dispersion(conn, min_holders: int = MIN_HOLDERS,
               window_days: int = WINDOW_DAYS,
               outlier_factor: float = OUTLIER_FACTOR) -> dict:
    """Spread across managers marking one company in a near-simultaneous window.

    The window is rolling and anchored on each period end: every mark from a
    different manager within `window_days` counts as near-simultaneous. It has
    to be a window rather than an exact date, because fund fiscal quarter ends
    are staggered -- the same stagger that makes propagation observable makes
    an exact-date comparison see almost nothing.

    --------------------------------------------------------------------------
    Comparing like with like, which took two attempts
    --------------------------------------------------------------------------
    The first version compared every priced mark of a company and reported
    spreads of 31,983% and 1,098%. Those are not disagreements about value:

      * **SpaceX files preferred at ten times common by convention** -- 81.00
        against 970.00 on the same day. Comparing them is exactly the trap
        plan.md describes.
      * **One Coatue mark** of `OPENAI GLOBAL, LLC` carries 150,000,000 units
        at $1.5072. A hundred and fifty million "shares" of a company whose
        other marks sit near $500 is an LLC interest priced per dollar of
        commitment, not a share price. The class parser called it UNKNOWN and
        it passed the per-share basis check.

    So dispersion is computed **within (company, class kind)** -- common with
    common, preferred with preferred -- and any manager further than
    `outlier_factor` from the window median is set aside as a **scale
    artifact** and reported by name rather than dropped silently.
    """
    per_manager = f"""
        WITH usable AS ({USABLE}),
        kinded AS (
            SELECT company_id, company, manager, period_end, price_per_share,
                   CASE WHEN class LIKE 'COM%%' THEN 'common'
                        WHEN class LIKE 'PFD%%' THEN 'preferred'
                        ELSE 'unclassified' END AS kind
              FROM usable
        )
        SELECT company_id, company, kind, manager, period_end,
               avg(price_per_share) AS price
          FROM kinded
         GROUP BY 1, 2, 3, 4, 5
    """

    raw = _rows(conn, f"""
        WITH pm AS ({per_manager}),
        anchored AS (
            SELECT a.company, a.kind, a.period_end AS anchor,
                   b.manager, b.period_end AS reported, b.price
              FROM pm a
              JOIN pm b ON b.company_id = a.company_id
                       AND b.kind = a.kind
                       AND b.period_end BETWEEN a.period_end
                                            AND a.period_end + %(window)s * INTERVAL '1 day'
        )
        -- The median is computed in Python below: Postgres does not allow
        -- percentile_cont as a window function, and a self-join to fake one
        -- would be slower and harder to read than sorting a list.
        SELECT company, kind, anchor::text AS anchor, manager,
               reported::text AS reported,
               price::numeric(18,4) AS price
          FROM anchored
         ORDER BY company, kind, anchor, price
    """, {"window": window_days})

    groups: dict = {}
    for row in raw:
        groups.setdefault((row["company"], row["kind"], row["anchor"]), []).append(row)

    windows, outliers = [], []
    for (company, kind, anchor), members in sorted(groups.items()):
        prices_all = sorted(float(m["price"]) for m in members)
        median_all = prices_all[len(prices_all) // 2]
        keep, dropped = [], []
        for member in members:
            ratio = float(member["price"]) / median_all if median_all else 1.0
            if ratio > outlier_factor or ratio < 1 / outlier_factor:
                dropped.append(dict(member, vs_median=round(ratio, 4)))
            else:
                keep.append(member)
        outliers.extend(dropped)

        # One price per manager: a manager holding four classes of one company
        # at one price must not count four times.
        by_manager: dict = {}
        for member in keep:
            by_manager.setdefault(member["manager"], []).append(float(member["price"]))
        if len(by_manager) < min_holders:
            continue
        manager_price = {m: sum(v) / len(v) for m, v in by_manager.items()}

        prices = sorted(manager_price.values())
        low, high = prices[0], prices[-1]
        clusters = _levels(prices, LEVEL_REL)
        state = "steady" if len(clusters) == 1 else "transition"
        windows.append({
            "company": company, "kind": kind, "anchor": anchor,
            "state": state,
            "levels": len(clusters),
            "managers": len(manager_price),
            "price_min": round(low, 4), "price_max": round(high, 4),
            "price_median": round(prices[len(prices) // 2], 4),
            "spread": round((high - low) / low, 4) if low else None,
            "level_prices": [round(sum(c) / len(c), 4) for c in clusters],
            "who": ", ".join(sorted(manager_price)),
            "laggards": ", ".join(sorted(m for m, p in manager_price.items()
                                         if p <= clusters[0][-1] * (1 + LEVEL_REL)))
                        if len(clusters) > 1 else "",
            "movers": ", ".join(sorted(m for m, p in manager_price.items()
                                       if p >= clusters[-1][0] * (1 - LEVEL_REL)))
                      if len(clusters) > 1 else "",
            "set_aside": len(dropped),
        })

    windows.sort(key=lambda w: -(w["spread"] or 0))
    steady = [w for w in windows if w["state"] == "steady"]
    transition = [w for w in windows if w["state"] == "transition"]

    by_company: dict = {}
    for window in steady:
        by_company.setdefault((window["company"], window["kind"]), []).append(window["spread"])
    summary = [
        {"company": company, "kind": kind, "windows": len(spreads),
         "median_spread": round(sorted(spreads)[len(spreads) // 2], 4),
         "max_spread": round(max(spreads), 4)}
        for (company, kind), spreads in sorted(by_company.items(),
                                               key=lambda kv: -max(kv[1]))
    ]
    steady_spreads = sorted(w["spread"] for w in steady if w["spread"] is not None)
    artifacts: dict = {}
    for row in outliers:
        key = (row["company"], row["kind"], row["manager"])
        artifacts[key] = artifacts.get(key, 0) + 1
    return {"min_holders": min_holders, "window_days": window_days,
            "outlier_factor": outlier_factor, "level_rel": LEVEL_REL,
            "windows": windows,
            "steady": steady, "transition": transition,
            "median_steady_spread": (steady_spreads[len(steady_spreads) // 2]
                                     if steady_spreads else None),
            "share_in_transition": (round(len(transition) / len(windows), 4)
                                    if windows else None),
            "by_company": summary,
            "scale_artifacts_set_aside": [
                {"company": c, "kind": k, "manager": m, "window_appearances": n}
                for (c, k, m), n in sorted(artifacts.items(), key=lambda kv: -kv[1])],
            "plan_expectation": "Databricks ~9% spread, Perplexity ~19%"}


# --------------------------------------------------------------------------
# 3. Propagation lag
# --------------------------------------------------------------------------


def propagation(conn, min_holders: int = MIN_HOLDERS) -> dict:
    """Days between the first manager reporting a new price level and the last.

    A "price level" is a price that at least `min_holders` managers eventually
    report, matched within 0.1% because filers round differently. The lag is
    the gap between the first and last manager's first sighting of it.

    The lag is bounded below by the fiscal-quarter stagger, not by how fast
    funds work: a manager reporting on 30 April cannot reflect a 31 March
    repricing any sooner than 30 April. So this measures observability, not
    diligence, and the report says so.
    """
    events = _rows(conn, f"""
        WITH usable AS ({USABLE}),
        per_manager AS (
            SELECT company_id, company, manager, period_end,
                   avg(price_per_share) AS price
              FROM usable GROUP BY 1, 2, 3, 4
        ),
        -- Cluster prices into levels: a level is represented by its lowest
        -- member, and any price within the relative tolerance joins. No bare
        -- percent sign here: psycopg2 scans SQL comments for placeholders too.
        levels AS (
            SELECT DISTINCT a.company_id, a.company,
                   first_value(a.price) OVER (
                       PARTITION BY a.company_id
                       ORDER BY a.price
                       ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS ignored,
                   a.price AS level_price
              FROM per_manager a
        ),
        first_sighting AS (
            SELECT p.company_id, p.company, l.level_price, p.manager,
                   min(p.period_end) AS first_seen
              FROM per_manager p
              JOIN levels l ON l.company_id = p.company_id
                           AND abs(p.price - l.level_price)
                               <= %(rel)s * greatest(l.level_price, 1)
             GROUP BY 1, 2, 3, 4
        )
        SELECT company, level_price::numeric(18,4) AS price,
               count(DISTINCT manager)             AS managers,
               min(first_seen)::text               AS first_manager_date,
               max(first_seen)::text               AS last_manager_date,
               array_agg(first_seen ORDER BY first_seen) AS adoption_dates,
               string_agg(DISTINCT manager, ', ' ORDER BY manager) AS who
          FROM first_sighting
         GROUP BY 1, 2
        HAVING count(DISTINCT manager) >= %(min_holders)s
         ORDER BY company, price
    """, {"rel": SAME_PRICE_REL, "min_holders": min_holders})

    # Deduplicate: clustering by "within the tolerance of some observed price"
    # produces one row per member of a cluster. Keep the row with the most
    # managers for each (company, rounded price) -- the cluster's own
    # representative.
    best: dict = {}
    for event in events:
        key = (event["company"], round(float(event["price"]), 2))
        if key not in best or event["managers"] > best[key]["managers"]:
            best[key] = event
    deduped = sorted(best.values(), key=lambda e: (e["company"], float(e["price"])))

    # Half-adoption, because the last manager is not a propagation measure.
    #
    # The first version reported only first-to-last, and produced lags of 427
    # and 396 days on Databricks levels. Those are not slow propagation: they
    # are managers still carrying a 2023 level in late 2024, long after the
    # company had repriced. A straggler like that says something about
    # staleness, not about how fast a round travels.
    #
    # So the headline is the gap from the first manager to the point where half
    # the eventual adopters have reported the level. First-to-last is kept
    # beside it, labelled for what it includes.
    for event in deduped:
        dates = sorted(event.pop("adoption_dates"))
        first = dates[0]
        half_index = (len(dates) - 1) // 2
        event["managers_at_half"] = half_index + 1
        event["lag_to_half_days"] = (dates[half_index] - first).days
        event["lag_to_all_days"] = (dates[-1] - first).days

    lags = [int(e["lag_to_half_days"]) for e in deduped
            if e["lag_to_half_days"] is not None]
    lags_all = [int(e["lag_to_all_days"]) for e in deduped
                if e["lag_to_all_days"] is not None]
    stagger = _rows(conn, """
        SELECT count(DISTINCT period_end) AS distinct_period_ends,
               count(DISTINCT extract(day FROM period_end)) AS distinct_days_of_month,
               min(period_end)::text AS first, max(period_end)::text AS last
          FROM marks
    """)[0]
    return {"min_holders": min_holders, "same_price_rel": SAME_PRICE_REL,
            "events": deduped,
            "median_lag_to_half_days": (sorted(lags)[len(lags) // 2]
                                        if lags else None),
            "max_lag_to_half_days": max(lags) if lags else None,
            "median_lag_to_all_days": (sorted(lags_all)[len(lags_all) // 2]
                                       if lags_all else None),
            "max_lag_to_all_days": max(lags_all) if lags_all else None,
            "events_counted": len(deduped),
            "stagger": stagger,
            "caveat": "Two bounds, both real. The lag cannot be shorter than the "
                      "fiscal-quarter stagger -- a manager reporting on 30 April "
                      "cannot reflect a 31 March repricing any sooner -- so this "
                      "measures observability, not diligence. And first-to-last "
                      "includes managers still carrying an old level long after the "
                      "company repriced, which is staleness rather than slow "
                      "propagation; that is why the headline is first-to-half."}


# --------------------------------------------------------------------------
# 4. The Cerebras study
# --------------------------------------------------------------------------


def cerebras(conn) -> dict:
    """The Level 3 run-up, and an honest account of the missing Level 1 leg.

    plan.md: "Fidelity marked Cerebras Level 3 at $89.02 on 2026-03-31.
    BlackRock reports it Level 1 at $236.99 on 2026-05-29 -- it went public in
    between. That is a free, clean, private-mark-to-public-price event study
    with no additional data collection."

    It is not free, because the Level 1 observation is not in the data:

    1. `src/ingest/universe.py` filters the private layer to
       `FAIR_VALUE_LEVEL = '3'`, so Level 1 rows never reached Postgres. Every
       one of the 5,806 rows in `raw_holdings` is Level 3.
    2. The bulk archive's newest period end is 2026-04-30. A 2026-05-29 period
       end is in 2026Q3, which the SEC has not published.

    (1) alone would be a filter to widen. (1) and (2) together mean the
    comparison needs the live-EDGAR path, which is Week 3's still-open item.
    Probing the raw 2026Q2 archive directly -- every fair value level, no
    filter -- returns 22 Cerebras row groups and **all of them are Level 3**.

    So what is reported is the run-up that *is* measurable, and the missing leg
    is named rather than quietly dropped.
    """
    series = _rows(conn, """
        SELECT m.period_end::text AS period_end,
               f.family           AS manager,
               s.class_normalized AS class,
               m.price_per_share::numeric(18,4) AS price,
               m.balance::numeric(18,0)         AS shares,
               m.value_usd::numeric(20,2)       AS value_usd,
               m.is_remark
          FROM marks m
          JOIN companies  c ON c.company_id  = m.company_id
          JOIN funds      f ON f.fund_id     = m.fund_id
          JOIN securities s ON s.security_id = m.security_id
         WHERE c.canonical_name = 'Cerebras Systems Inc.'
           AND m.price_per_share IS NOT NULL
         ORDER BY m.period_end, f.family, s.class_normalized
    """)
    levels = _rows(conn, """
        SELECT m.period_end::text AS period_end,
               count(DISTINCT f.family) AS managers,
               min(m.price_per_share)::numeric(18,4) AS price_min,
               max(m.price_per_share)::numeric(18,4) AS price_max
          FROM marks m
          JOIN companies c ON c.company_id = m.company_id
          JOIN funds     f ON f.fund_id    = m.fund_id
         WHERE c.canonical_name = 'Cerebras Systems Inc.'
           AND m.price_per_share IS NOT NULL
         GROUP BY 1 ORDER BY 1
    """)
    first, last = (levels[0], levels[-1]) if levels else (None, None)
    return {
        "series": series,
        "by_period": levels,
        "first": first,
        "last": last,
        "total_return": (round(float(last["price_max"]) / float(first["price_min"]) - 1, 4)
                         if first and last else None),
        "level_1_reachable": False,
        "level_1_blockers": [
            "the private layer is filtered to FAIR_VALUE_LEVEL = 3, so Level 1 rows "
            "never entered Postgres: all 5,806 raw_holdings rows are Level 3",
            "the bulk archive's newest period end is 2026-04-30; plan.md's Level 1 "
            "observation has a 2026-05-29 period end, which is in unpublished 2026Q3",
        ],
        "raw_probe": "Probing the raw 2026Q2 archive with no fair-value filter returns "
                     "22 Cerebras row groups, all Level 3. The earliest possible Level 1 "
                     "period end is therefore after the archive ends.",
        "plan_expectation": "Level 3 at 89.02 on 2026-03-31 against Level 1 at 236.99 "
                            "on 2026-05-29",
    }


def run_all(conn) -> dict:
    """Every measurement, plus the two dispersion readings that answer different
    questions.

    `same_date` is the honest test of whether managers disagree: no window, so
    no repricing can drift into the comparison. `windowed` allows 31 days and is
    what shows a round in flight.

    Within-level spread is **not** reported as a finding anywhere, because it is
    bounded by LEVEL_REL by construction -- saying "managers inside a level
    agree to 2%" would be restating the clustering threshold, not measuring
    anything.
    """
    return {
        "guards": guards(conn),
        "remark": remark_frequency(conn),
        "dispersion_same_date": dispersion(conn, window_days=0),
        "dispersion_windowed": dispersion(conn, window_days=WINDOW_DAYS),
        "propagation": propagation(conn),
        "cerebras": cerebras(conn),
    }
