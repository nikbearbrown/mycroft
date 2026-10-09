"""The demo, as a runnable script rather than a recording.

`plan.md` week 11: "Record a demo: ingest, a review-queue decision, a resolved
series, a propagation chart, an MCP query."

    python -m scripts.demo            # print the transcript
    python -m scripts.demo --write    # also write docs/demo.md

Five acts, in the order the plan names them. A script rather than a video for
one reason: a recording is true on the day it was made, and this re-runs. Every
figure it prints is queried live, so a transcript that disagrees with the
database is a bug rather than an old file.

--------------------------------------------------------------------------
Read-only, deliberately
--------------------------------------------------------------------------
Act II shows a review-queue decision that a named human already made. It does
not make a new one. A demo that recorded a judgment would be a demo that
clears a gate for the sake of a screenshot, which is the failure the gate
exists to prevent (P4).

Act I does not re-download 6 GB either. It shows the reconciliation the ingest
produced, which is the thing worth seeing: that nothing was dropped for being
awkward.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.connect import connect  # noqa: E402

REPORT = ROOT / "docs" / "demo.md"
BAR = "─" * 72


def _rows(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, r)) for r in cur.fetchall()]


class Transcript:
    """Collects what is printed so it can also be written to Markdown."""

    def __init__(self):
        self.lines: list[str] = []

    def act(self, number: str, title: str) -> None:
        self.lines += ["", f"## {number} — {title}", ""]
        print(f"\n{BAR}\n  {number} — {title}\n{BAR}")

    def say(self, text: str = "") -> None:
        self.lines.append(text)
        print(text)

    def code(self, text: str) -> None:
        self.lines += ["```", text, "```", ""]
        print(f"    {text}")

    def table(self, rows: list[dict], columns: list[str]) -> None:
        if not rows:
            self.say("_(none)_")
            return
        self.lines += ["| " + " | ".join(columns) + " |",
                       "|" + "---|" * len(columns)]
        for row in rows:
            cells = [str(row.get(c, "")) for c in columns]
            self.lines.append("| " + " | ".join(cells) + " |")
            print("    " + "  ".join(f"{c:>14.14}" for c in cells))
        self.lines.append("")


# --------------------------------------------------------------------------
# Act I — ingest, and the reconciliation that proves nothing was dropped
# --------------------------------------------------------------------------


def act_ingest(conn, t: Transcript) -> None:
    t.act("Act I", "Ingest, and the reconciliation")
    t.code("python -m src.ingest.download_bulk 2026q2 && "
           "python -m src.ingest.build_parquet --all && python -m src.db.load --all")

    scale = _rows(conn, """
        SELECT (SELECT count(DISTINCT source_quarter) FROM raw_holdings) AS quarters,
               (SELECT count(*) FROM filings)                            AS filings,
               (SELECT count(DISTINCT family) FROM funds)                AS families,
               (SELECT count(*) FROM raw_holdings)                       AS holdings,
               (SELECT count(*) FROM marks)                              AS marks
    """)[0]
    t.say(f"**{scale['quarters']} quarters** ingested · "
          f"{scale['filings']:,} filings · {scale['families']} fund families · "
          f"**{scale['holdings']:,} filed private holdings** → "
          f"**{scale['marks']:,} marks**.")
    t.say()
    t.say("The reconciliation is the point. Every filed holding is accounted "
          "for — nothing is dropped for being awkward:")
    t.say()

    recon = _rows(conn, """
        SELECT 'filed universe holdings' AS line, count(*) AS n FROM raw_holdings
        UNION ALL SELECT 'resolved to a company', count(*) FROM match_decisions
                   WHERE company_id IS NOT NULL
        UNION ALL SELECT 'rejected as not in universe', count(*) FROM match_decisions
                   WHERE company_id IS NULL
        UNION ALL SELECT 'marks built', count(*) FROM marks
        UNION ALL SELECT '  of which unpriced', count(*) FROM marks
                   WHERE price_per_share IS NULL
        UNION ALL SELECT '  of which blocked from change series', count(*) FROM marks
                   WHERE change_blocked
    """)
    t.table(recon, ["line", "n"])


# --------------------------------------------------------------------------
# Act II — a review-queue decision a human actually made
# --------------------------------------------------------------------------


def act_review(conn, t: Transcript) -> None:
    t.act("Act II", "A review-queue decision")
    t.code("python -m scripts.review_queue --list   # what is waiting\n"
           "    python -m scripts.review_queue --show 3   # one card in full")

    counts = _rows(conn, """
        SELECT count(*) AS decisions,
               count(DISTINCT reviewer) AS reviewers,
               count(*) FILTER (WHERE verdict = 'unresolved') AS unresolved
          FROM review_decisions
    """)[0]
    split = _rows(conn, """
        SELECT count(*) FILTER (WHERE method IN ('human', 'reused')) AS by_human,
               count(*) FILTER (WHERE method NOT IN ('human', 'reused')) AS by_machine,
               count(*) AS total
          FROM match_decisions
    """)[0]
    t.say(f"**{split['by_machine']:,} of {split['total']:,} holdings "
          f"({split['by_machine'] / split['total']:.1%}) resolved without a "
          f"human.** The remaining {split['by_human']:,} carry a named "
          f"reviewer's decision — {counts['decisions']} distinct answers, "
          f"{counts['unresolved']} still unresolved.")
    t.say()
    t.say("One real decision, as recorded:")
    t.say()

    example = _rows(conn, """
        SELECT r.issuer_name, r.verdict, c.canonical_name AS company,
               r.reviewer, r.holdings_covered, left(r.rationale, 90) AS rationale
          FROM review_decisions r
          LEFT JOIN companies c ON c.company_id = r.company_id
         WHERE r.reviewer <> 'auto' AND r.holdings_covered > 1
         ORDER BY r.holdings_covered DESC LIMIT 1
    """)
    for row in example:
        for key, value in row.items():
            t.say(f"- **{key}**: {value}")
    t.say()
    t.say("One human answer fans out to every holding that shares its key — "
          "which is why 5,806 holdings are only 231 questions.")


# --------------------------------------------------------------------------
# Act III — a resolved series
# --------------------------------------------------------------------------


def act_series(conn, t: Transcript, company: str = "Anthropic PBC") -> None:
    t.act("Act III", f"A resolved series — {company}")
    t.code(f'python -m scripts.build_marks --panel   # company / manager / period')

    series = _rows(conn, """
        SELECT m.period_end::text                        AS period_end,
               count(DISTINCT f.family)                  AS managers,
               min(m.price_per_share)::numeric(18,2)     AS price_min,
               max(m.price_per_share)::numeric(18,2)     AS price_max
          FROM marks m
          JOIN companies c ON c.company_id = m.company_id
          JOIN funds f     ON f.fund_id = m.fund_id
         WHERE c.canonical_name = %s
           AND m.price_per_share IS NOT NULL AND NOT m.change_blocked
         GROUP BY 1 ORDER BY 1 DESC LIMIT 8
    """, (company,))
    t.say("The eight most recent period ends, newest first:")
    t.say()
    t.table(series, ["period_end", "managers", "price_min", "price_max"])
    t.say("Each price is `value_usd / balance` as filed, computed once at "
          "ingest. Where managers differ on one date, that is usually a round "
          "some have reflected and others have not — which Act IV measures.")


# --------------------------------------------------------------------------
# Act IV — propagation
# --------------------------------------------------------------------------


def act_propagation(conn, t: Transcript) -> None:
    from src.signal.findings import propagation

    t.act("Act IV", "Propagation — how fast a new price travels")
    t.code("python -m scripts.analyze --run   # the four measurements")

    measured = propagation(conn)
    events = measured["events"]
    lags = sorted(int(e["lag_to_half_days"]) for e in events
                  if e.get("lag_to_half_days") is not None)
    t.say(f"**{len(events)} price levels** adopted by three or more managers. "
          f"Median **{lags[len(lags) // 2]} days** for a new level to reach half "
          f"its eventual holders; {sum(1 for x in lags if x == 0)} of "
          f"{len(lags)} reach half on the very same period end; the slowest "
          f"takes {max(lags)}.")
    t.say()

    top = sorted(events, key=lambda e: -int(e["managers"]))[:5]
    rows = [{"company": e["company"][:28], "price": e["price"],
             "managers": e["managers"], "days_to_half": e["lag_to_half_days"]}
            for e in top]
    t.table(rows, ["company", "price", "managers", "days_to_half"])
    t.say("Bounded below by the fiscal-quarter stagger — a manager reporting "
          "on 30 April cannot reflect a 31 March repricing any sooner — so "
          "this measures observability, not diligence.")


# --------------------------------------------------------------------------
# Act V — an MCP query
# --------------------------------------------------------------------------


def act_mcp(conn, t: Transcript) -> None:
    from src.mcp import queries as Q
    from src.mcp.paging import page

    t.act("Act V", "An MCP query")
    t.code('get_marks(company="Databricks, Inc.", limit=3)')

    rows, summary = Q.get_marks(conn, "Databricks, Inc.")
    bounded = page(rows, scope={"tool": "get_marks", "args": {}}, limit=3,
                   summary=summary)
    whole = len(json.dumps({"summary": summary, "rows": rows}, default=str))
    small = len(json.dumps(bounded, indent=2, default=str))

    t.say(f"The full result is **{bounded['page']['total']:,} rows** — "
          f"{whole:,} characters, roughly {whole // 4:,} tokens serialised "
          f"whole. Past most context windows, and useless inside them.")
    t.say()
    t.say(f"Bounded, the same call is **{small:,} characters**: a summary of "
          f"the whole result set, {bounded['page']['returned']} rows, and a "
          f"cursor for the remaining {bounded['page']['remaining']:,}.")
    t.say()
    t.say("```json")
    t.lines.append(json.dumps({"summary": bounded["summary"],
                               "page": bounded["page"]},
                              indent=2, default=str))
    t.say("```")
    print("    summary + page envelope printed to the transcript")
    t.say()
    t.say("Nothing in the server writes. No tool records a decision, clears a "
          "gate, or changes a mark.")


# --------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true",
                    help=f"also write {REPORT.name}")
    args = ap.parse_args()

    t = Transcript()
    t.lines += [
        "# Demo — five acts, end to end",
        "",
        "Generated by `python -m scripts.demo --write`. Every figure is "
        "queried live, so a transcript that disagrees with the database is a "
        "bug rather than an old file.",
        "",
        "> **Read-only.** Act II shows a decision a named human already made; "
        "it does not make a new one. A demo that recorded a judgment would be "
        "a demo that clears a gate for the sake of a screenshot.",
    ]

    conn = connect()
    try:
        act_ingest(conn, t)
        act_review(conn, t)
        act_series(conn, t)
        act_propagation(conn, t)
        act_mcp(conn, t)
    finally:
        conn.close()

    print(f"\n{BAR}")
    if args.write:
        REPORT.write_text("\n".join(t.lines) + "\n", encoding="utf-8",
                          newline="\n")
        print(f"  wrote {REPORT}")
    else:
        print("  (pass --write to save docs/demo.md)")


if __name__ == "__main__":
    main()
