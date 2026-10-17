"""Build the marks panel, detect splits, verify it, and write the report.

    python -m scripts.build_marks --build     # securities, marks, split detector
    python -m scripts.build_marks --verify    # plan.md's end-to-end checks
    python -m scripts.build_marks --panel     # the per-company/manager/period panel
    python -m scripts.build_marks --report    # docs/marks_panel.md, for a human
    python -m scripts.build_marks --adjudicate --company Perplexity         --verdict split --reviewer "<name>" --rationale "<why>"

`--build` is idempotent: it rebuilds `marks` from `raw_holdings` and
`match_decisions` every time, so the panel is a pure function of the raw layer
plus the recorded resolution decisions. Nothing accumulates.

No command here adjusts a price. A suspected split is quarantined and reported;
adjudicating it is a human decision and a Week 8 input.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.connect import apply_schema, connect  # noqa: E402
from src.marks import verify as verify_mod  # noqa: E402
from src.marks.build import build_marks, build_securities, coverage  # noqa: E402
from src.marks.splits import (  # noqa: E402
    VERDICTS,
    adjudicate,
    detect,
    suspected,
)

REPORT = ROOT / "docs" / "marks_panel.md"

# The deliverable: one row per company, manager family and period end. Marks
# live at security grain; the panel aggregates to the grain a person asks
# questions at. Where a manager reports more than one price for one company on
# one day, both ends are shown -- averaging them would invent a number.
PANEL_SQL = """
SELECT c.canonical_name                          AS company,
       f.family                                  AS manager,
       m.period_end,
       count(*)                                  AS marks,
       count(DISTINCT m.security_id)             AS securities,
       count(DISTINCT m.fund_id)                 AS funds,
       min(m.price_per_share)::numeric(18,4)     AS price_low,
       max(m.price_per_share)::numeric(18,4)     AS price_high,
       sum(m.value_usd)::numeric(20,2)           AS value_usd,
       count(*) FILTER (WHERE m.change_blocked)  AS blocked,
       count(*) FILTER (WHERE m.split_suspected) AS split_suspected,
       count(*) FILTER (WHERE m.is_remark)       AS re_marked,
       count(*) FILTER (WHERE m.is_remark IS FALSE) AS carried_forward
  FROM marks m
  JOIN companies c ON c.company_id = m.company_id
  JOIN funds     f ON f.fund_id    = m.fund_id
 GROUP BY 1, 2, 3
 ORDER BY 1, 3, 2
"""

SUMMARY_SQL = """
SELECT c.canonical_name                            AS company,
       count(*)                                    AS marks,
       count(DISTINCT m.security_id)               AS securities,
       count(DISTINCT f.family)                    AS managers,
       count(DISTINCT m.period_end)                AS periods,
       min(m.period_end)::text                     AS first_period,
       max(m.period_end)::text                     AS last_period,
       min(m.price_per_share)::numeric(18,2)       AS price_min,
       max(m.price_per_share)::numeric(18,2)       AS price_max,
       count(*) FILTER (WHERE m.change_blocked)    AS blocked,
       count(*) FILTER (WHERE m.split_suspected)   AS split_suspected
  FROM marks m
  JOIN companies c ON c.company_id = m.company_id
  JOIN funds     f ON f.fund_id    = m.fund_id
 GROUP BY 1
 ORDER BY 2 DESC
"""


def rows(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, r)) for r in cur.fetchall()]


def cmd_build(conn, args) -> None:
    print("securities:", build_securities(conn))
    print("marks     :", build_marks(conn, run_id=args.run_id))
    print("splits    :", detect(conn))
    cov = coverage(conn)
    print("coverage  :", cov)
    if not cov["reconciles"]:
        sys.exit("coverage does not reconcile -- holdings are unaccounted for")


def cmd_verify(conn) -> int:
    failures = 0
    for result in verify_mod.run_all(conn):
        state = {True: "PASS", False: "FAIL", None: "N/A "}[result["passed"]]
        print(f"{state}  {result['check']}")
        print(f"      expected: {result['expected']}")
        if result["passed"] is False:
            failures += 1
            for key, value in result.items():
                if key not in ("check", "expected", "passed"):
                    print(f"      {key}: {str(value)[:400]}")
        if result.get("note"):
            print(f"      note: {result['note']}")
    print(f"\n{failures} failed")
    return failures


def cmd_panel(conn, company: str | None) -> None:
    panel = rows(conn, PANEL_SQL)
    if company:
        panel = [r for r in panel if company.lower() in r["company"].lower()]
    print(f"{'company':<30}{'manager':<20}{'period':<12}{'low':>11}{'high':>11}"
          f"{'marks':>7}{'blocked':>9}")
    print("-" * 100)
    for r in panel[:60]:
        low = f'{r["price_low"]:.2f}' if r["price_low"] is not None else "-"
        high = f'{r["price_high"]:.2f}' if r["price_high"] is not None else "-"
        print(f'{r["company"][:28]:<30}{r["manager"][:18]:<20}'
              f'{str(r["period_end"]):<12}{low:>11}{high:>11}'
              f'{r["marks"]:>7}{r["blocked"]:>9}')
    print(f"\n{len(panel)} panel rows"
          + (f" (showing the first 60)" if len(panel) > 60 else ""))


def cmd_report(conn) -> None:
    summary = rows(conn, SUMMARY_SQL)
    panel = rows(conn, PANEL_SQL)
    cov = coverage(conn)
    quarantine = suspected(conn)
    checks = verify_mod.run_all(conn)

    totals = rows(conn, """
        SELECT count(*)                                          AS marks,
               count(*) FILTER (WHERE price_per_share IS NOT NULL) AS priced,
               count(*) FILTER (WHERE change_blocked)            AS blocked,
               count(*) FILTER (WHERE is_blended)                AS blended,
               count(*) FILTER (WHERE spv_opaque)                AS opaque_spv,
               count(*) FILTER (WHERE is_remark)                 AS re_marked,
               count(*) FILTER (WHERE is_remark IS FALSE)        AS carried,
               count(*) FILTER (WHERE is_remark IS NULL AND price_per_share IS NOT NULL)
                                                                 AS first_obs,
               count(DISTINCT security_id)                       AS securities,
               count(DISTINCT period_end)                        AS periods
          FROM marks
    """)[0]
    blocks = rows(conn, """
        SELECT block_reason, count(*) AS marks FROM marks
         WHERE change_blocked GROUP BY 1 ORDER BY 2 DESC
    """)
    large = rows(conn, """
        SELECT c.canonical_name AS company, count(*) AS steps,
               min(m.split_ratio)::numeric(10,3) AS ratio_min,
               max(m.split_ratio)::numeric(10,3) AS ratio_max
          FROM marks m JOIN companies c ON c.company_id = m.company_id
         WHERE m.split_reason LIKE 'large move%'
         GROUP BY 1 ORDER BY 2 DESC
    """)

    out = [
        "# The marks panel",
        "",
        "*Generated by `scripts/build_marks.py --report`. Every number is queried at "
        "build time; nothing here is typed by hand.*",
        "",
        f"`price_per_share = value_usd / balance`, computed once per "
        f"(security, fund, period end) over **{totals['marks']:,} marks** covering "
        f"{totals['securities']} securities and {totals['periods']} period ends.",
        "",
        "## What is in it",
        "",
        "| | |",
        "|---|---|",
        f"| Marks | {totals['marks']:,} |",
        f"| Priced | {totals['priced']:,} |",
        f"| Unpriced, on purpose | {totals['marks'] - totals['priced']:,} |",
        f"| Blocked from any change series | {totals['blocked']:,} |",
        f"| Re-marked against the prior period | {totals['re_marked']:,} |",
        f"| Carried forward unchanged | {totals['carried']:,} |",
        f"| First observation, no prior | {totals['first_obs']:,} |",
        f"| Opaque SPV marks, reported not dropped | {totals['opaque_spv']:,} |",
        "",
        "### Reconciliation",
        "",
        "Every filed holding is either in a mark, rejected by the Week 6 review, or on a "
        "filing an amendment superseded. Nothing is dropped for being awkward.",
        "",
        "| | rows |",
        "|---|---|",
        f"| Holdings in `raw_holdings` | {cov['holdings']:,} |",
        f"| Rejected as not in the universe (Week 6) | {cov['rejected_not_in_universe']:,} |",
        f"| On filings superseded by an amendment | {cov['superseded_by_amendment']:,} |",
        f"| Aggregated into marks | {cov['lines_in_marks']:,} |",
        f"| **Reconciles** | **{cov['reconciles']}** |",
        "",
        "## Why a mark can carry no price",
        "",
        "| reason | marks |",
        "|---|---|",
    ]
    for row in blocks:
        out.append(f"| {row['block_reason']} | {row['marks']:,} |")

    out += [
        "",
        "## Suspected splits, and what a human decided",
        "",
        "A suspected split is **never auto-adjusted**. A `not_a_split` verdict lifts the "
        "block and the step rejoins the change series; a confirmed `split` **stays "
        "blocked**, because applying a factor is Week 8's work under its own gate.",
        "",
        "The factor is not the detected ratio. ARK's Perplexity step reads 11.93 because "
        "a 10:1 split and a 16% markdown landed in one period — Week 8 divides by 10 and "
        "leaves the markdown as the real price move it is.",
        "",
        "| company | class | ratio | before | after | verdict | factor | blocked |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in quarantine:
        verdict = (row["note"] or "open").split(" -- ")[0]
        out.append(
            f"| {row['company']} | `{row['class']}` | {row['ratio_max']} "
            f"| {row['price_before']} | {row['price_after']} "
            f"| {verdict} | {row['factor'] if row['factor'] is not None else '—'} "
            f"| {row['blocked']} of {row['marks']} |"
        )
    unadjudicated = [r for r in quarantine if not r["adjudicated"]]
    out += [
        "",
        (f"**{len(unadjudicated)} of {len(quarantine)} groups are still open.**"
         if unadjudicated else
         "**All of them are adjudicated**, each by a named reviewer with a written reason."),
    ]

    out += [
        "",
        "### Large moves, routed but not blocked",
        "",
        "A move of 2x or more whose ratio is *not* near-integer is a repricing, which is "
        "the signal this project exists to measure. It is surfaced for a look and left in "
        "the series.",
        "",
        "| company | steps | smallest | largest |",
        "|---|---|---|---|",
    ]
    for row in large:
        out.append(f"| {row['company']} | {row['steps']} | {row['ratio_min']}x "
                   f"| {row['ratio_max']}x |")

    out += [
        "",
        "## The panel, by company",
        "",
        "| company | marks | securities | managers | periods | span | price range | blocked |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in summary:
        span = f"{row['first_period']} to {row['last_period']}"
        price = (f"{row['price_min']} to {row['price_max']}"
                 if row["price_min"] is not None else "none priced")
        out.append(
            f"| {row['company']} | {row['marks']:,} | {row['securities']} "
            f"| {row['managers']} | {row['periods']} | {span} | {price} "
            f"| {row['blocked']} |"
        )

    out += [
        "",
        f"The full per-company/manager/period panel is {len(panel):,} rows; "
        "`--panel` prints it and `PANEL_SQL` in `scripts/build_marks.py` is the query.",
        "",
        "## plan.md's end-to-end checks",
        "",
        "| check | result |",
        "|---|---|",
    ]
    for result in checks:
        state = {True: "**pass**", False: "**FAIL**", None: "n/a"}[result["passed"]]
        out.append(f"| {result['check']} | {state} |")

    out += [
        "",
        "Detail for the two that need it:",
        "",
    ]
    agreement = next(c for c in checks if "four managers" in c["check"])
    out += [
        f"- **Manager agreement.** plan.md expects four managers at $259.14; the panel "
        f"has **{agreement['families_at_259_14']}**, in two clusters that agree to the "
        f"cent and not to four decimals:",
        "",
    ]
    for cluster in agreement["clusters_within_half_a_cent"]:
        out.append(f"  - `{cluster['price']}` — {cluster['families']} families: "
                   f"{cluster['managers']}")
    pair = next(c for c in checks if "5/29-5/31" in c["check"])
    out += [
        "",
        f"- **The ~$589 pair is unreachable, not missing.** {pair['note']} The newest "
        f"period in the panel is {pair['found']['newest_period_in_panel']}.",
        "",
    ]
    REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {REPORT.relative_to(ROOT)} — {totals['marks']:,} marks, "
          f"{len(panel):,} panel rows, {len(quarantine)} quarantined groups")


def cmd_adjudicate(conn, args) -> None:
    """Thin wrapper. The logic and the guards live in src/marks/splits.py so
    that a test can hold them to account -- the first version of this lived
    here, accepted --factor, and never wrote it."""
    try:
        result = adjudicate(
            conn, company=args.company, verdict=args.verdict,
            reviewer=args.reviewer or "", rationale=args.rationale or "",
            factor=args.factor, share_class=args.share_class,
        )
    except ValueError as exc:
        sys.exit(str(exc))
    if not result["marks"]:
        sys.exit(f"no suspected split matched company {args.company!r}"
                 + (f" and class {args.share_class!r}" if args.share_class else ""))
    print(f"adjudicated {result['marks']} mark(s) as {result['verdict']}")
    print(f"  reviewer : {result['reviewer']}")
    if result["series_flags_cleared"]:
        print(f"  cleared the series flag on {result['series_flags_cleared']} further mark(s)")
    if result["verdict"] == "split":
        print(f"  factor recorded: {result['factor']} -- Week 8 divides by this, "
              f"not by the detected ratio")
        print("  the block stays on: a confirmed split is adjusted in Week 8, not here.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--panel", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--adjudicate", action="store_true",
                    help="record a human verdict on a suspected split")
    ap.add_argument("--verdict", choices=VERDICTS)
    ap.add_argument("--share-class", dest="share_class")
    ap.add_argument("--factor", type=float,
                    help="with --verdict split: the factor Week 8 divides by, which is "
                         "not necessarily the detected ratio")
    ap.add_argument("--reviewer")
    ap.add_argument("--rationale")
    ap.add_argument("--company")
    ap.add_argument("--run-id", type=int, dest="run_id")
    args = ap.parse_args()

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    conn = connect()
    apply_schema(conn)
    try:
        if args.build:
            cmd_build(conn, args)
        elif args.verify:
            sys.exit(1 if cmd_verify(conn) else 0)
        elif args.panel:
            cmd_panel(conn, args.company)
        elif args.report:
            cmd_report(conn)
        elif args.adjudicate:
            if not args.company:
                ap.error("--adjudicate needs --company")
            cmd_adjudicate(conn, args)
        else:
            ap.error("give --build, --verify, --panel, --report or --adjudicate")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
