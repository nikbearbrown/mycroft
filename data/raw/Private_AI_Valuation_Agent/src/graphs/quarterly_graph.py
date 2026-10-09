"""The quarterly analysis graph: fan out per company, then synthesise.

`plan.md` week 10: "Quarterly analysis graph: per-company fan-out -> dispersion
and propagation -> synthesis via Groq."

    python -m src.graphs.quarterly_graph              # run, write both artifacts
    python -m src.graphs.quarterly_graph --dry-run    # no model call

--------------------------------------------------------------------------
Why this one IS a graph
--------------------------------------------------------------------------
`plan.md` is strict that most of this project should not be a state machine:
"Most of this project is batch ETL, and batch ETL should not be a graph." This
is one of the two places it says a graph earns its place, and the reason is
visible in the topology rather than claimed in a comment:

    collect ─► fan_out ─► per-company measurement (N branches) ─┐
                                                                 ▼
                       commentary ◄── assemble ◄── gather ◄──────┘

The fan-out is real: each company's dispersion and propagation are computed
independently and one company's thin coverage must not suppress another's
figures. The synthesis step then needs *all* of them at once, because the note
is about the quarter and not about a company. That is a join, and a join over
a variable number of branches is what a graph is for.

--------------------------------------------------------------------------
Suppression is a decision, not an absence
--------------------------------------------------------------------------
A company with `status = 'thin'` publishes marks but not dispersion or
propagation -- Week 1's coverage decision. In the signal that shows up as
`dispersion: {"groups": 0, "median_spread": null, "suppressed_reason": "..."}`
rather than as a missing key, so a consumer can tell "we did not publish this"
from "there was nothing to publish".
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Annotated, TypedDict

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.signal import commentary as C  # noqa: E402
from src.signal import contract  # noqa: E402

SIGNAL_PATH = ROOT / "docs" / "_signal.json"
NOTE_PATH = ROOT / "docs" / "quarterly_note.md"

# Companies whose coverage is too thin to characterise. Week 1 froze the
# status; this is the threshold at which the *graph* also refuses, so a
# 'full' company that happens to have two managers this quarter is suppressed
# too. plan.md's dispersion rule uses a minimum-holders threshold; the same
# idea, applied to publication rather than to a single measurement.
MIN_MANAGERS_FOR_DISPERSION = 3


def _merge(left: list, right: list) -> list:
    """Reducer for the fan-out. Branches append; order is not meaningful."""
    return (left or []) + (right or [])


class QuarterState(TypedDict, total=False):
    companies: list[str]
    statuses: dict
    measured: Annotated[list[dict], _merge]
    period: dict
    coverage: dict
    guards: dict
    signal: dict
    note: str
    dry_run: bool
    backend: str | None


# --------------------------------------------------------------------------
# Nodes
# --------------------------------------------------------------------------


def collect(state: QuarterState) -> dict:
    """What exists: the universe, the period range and the guard counts."""
    from src.db.connect import connect
    from src.signal.findings import guards

    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.canonical_name, c.status,
                       count(m.mark_id) AS marks
                  FROM companies c
                  LEFT JOIN marks m ON m.company_id = c.company_id
                 GROUP BY 1, 2 ORDER BY 3 DESC
            """)
            rows = cur.fetchall()
            cur.execute("""
                SELECT min(period_end), max(period_end),
                       count(DISTINCT period_end) FROM marks
            """)
            first, last, periods = cur.fetchone()
            cur.execute("""
                SELECT count(*) AS marks,
                       count(*) FILTER (WHERE NOT change_blocked
                                    AND price_per_share IS NOT NULL)
                                                      AS published,
                       count(DISTINCT company_id)     AS companies,
                       count(*) FILTER (WHERE spv_opaque) AS opaque_spv
                  FROM marks
            """)
            marks, published, companies_with_marks, opaque = cur.fetchone()
            cur.execute("SELECT count(DISTINCT family) FROM funds")
            managers = cur.fetchone()[0]
            cur.execute("""
                SELECT count(*) FROM review_decisions WHERE verdict = 'unresolved'
            """)
            unresolved = cur.fetchone()[0]
        measured_guards = guards(conn)
    finally:
        conn.close()

    return {
        "companies": [r[0] for r in rows if r[2]],
        "statuses": {r[0]: r[1] for r in rows},
        "period": {
            "latest_period_end": str(last) if last else None,
            "first_period_end": str(first) if first else None,
            "periods": int(periods or 0),
        },
        "coverage": {
            "companies": int(companies_with_marks or 0),
            "managers": int(managers or 0),
            "marks": int(marks or 0),
            "marks_published": int(published or 0),
            "opaque_spv_positions": int(opaque or 0),
        },
        "guards": {
            "change_blocked": int(measured_guards["change_blocked"]),
            "unadjudicated_splits": int(measured_guards["unadjudicated_splits"]),
            "confirmed_splits": int(measured_guards["confirmed_splits"]),
            "incomplete_runs": int(measured_guards["incomplete_runs"]),
            "unresolved_reviews": int(unresolved or 0),
            "unpriced_marks": int(measured_guards["unpriced"]),
        },
    }


def measure_company(state: QuarterState, company: str) -> dict:
    """One branch of the fan-out: everything the signal says about one company.

    Opens its own connection. Branches may run concurrently and a psycopg2
    connection is not safe to share across them; one connection per branch is
    the cost of the fan-out being real.
    """
    from src.db.connect import connect
    from src.signal.findings import dispersion, propagation

    status = (state.get("statuses") or {}).get(company) or "watchlist"
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT count(*)                      AS marks,
                       count(DISTINCT f.family)      AS managers,
                       max(m.period_end)             AS latest
                  FROM marks m
                  JOIN companies c ON c.company_id = m.company_id
                  JOIN funds f     ON f.fund_id    = m.fund_id
                 WHERE c.canonical_name = %s
                   AND NOT m.change_blocked AND m.price_per_share IS NOT NULL
            """, (company,))
            marks, managers, latest = cur.fetchone()

            latest_min = latest_max = None
            if latest:
                cur.execute("""
                    SELECT min(m.price_per_share), max(m.price_per_share)
                      FROM marks m JOIN companies c ON c.company_id = m.company_id
                     WHERE c.canonical_name = %s AND m.period_end = %s
                       AND NOT m.change_blocked AND m.price_per_share IS NOT NULL
                """, (company, latest))
                low, high = cur.fetchone()
                latest_min = round(float(low), 4) if low is not None else None
                latest_max = round(float(high), 4) if high is not None else None

            cur.execute("""
                SELECT count(*) FILTER (WHERE m.is_remark) AS moved,
                       count(*)                            AS steps
                  FROM marks m JOIN companies c ON c.company_id = m.company_id
                 WHERE c.canonical_name = %s
                   AND m.prior_price_per_share IS NOT NULL
                   AND NOT m.change_blocked
            """, (company,))
            moved, steps = cur.fetchone()
            remark_rate = round(float(moved) / float(steps), 4) if steps else None

        thin = status != "full" or (managers or 0) < MIN_MANAGERS_FOR_DISPERSION
        if thin:
            reason = (f"coverage status is {status!r}" if status != "full" else
                      f"only {managers} managers priced this company, below the "
                      f"{MIN_MANAGERS_FOR_DISPERSION} needed to characterise a "
                      "spread")
            disp = {"groups": 0, "median_spread": None, "max_spread": None,
                    "suppressed_reason": reason}
            prop = {"events": 0, "median_days_to_half": None,
                    "max_days_to_half": None, "suppressed_reason": reason}
        else:
            windows = [w for w in dispersion(conn, window_days=0)["windows"]
                       if w["company"] == company and w["spread"] is not None]
            spreads = sorted(float(w["spread"]) for w in windows)
            disp = {
                "groups": len(spreads),
                "median_spread": (round(spreads[len(spreads) // 2], 4)
                                  if spreads else None),
                "max_spread": round(spreads[-1], 4) if spreads else None,
                "suppressed_reason": None,
            }
            events = [e for e in propagation(conn)["events"]
                      if e["company"] == company
                      and e.get("lag_to_half_days") is not None]
            lags = sorted(int(e["lag_to_half_days"]) for e in events)
            prop = {
                "events": len(lags),
                "median_days_to_half": (lags[len(lags) // 2] if lags else None),
                "max_days_to_half": lags[-1] if lags else None,
                "suppressed_reason": None,
            }
    finally:
        conn.close()

    return {"measured": [{
        "company": company,
        "status": status,
        "marks": int(marks or 0),
        "managers": int(managers or 0),
        "latest_period_end": str(latest) if latest else None,
        "latest_price_min": latest_min,
        "latest_price_max": latest_max,
        "remark_rate": remark_rate,
        "dispersion": disp,
        "propagation": prop,
    }]}


def assemble(state: QuarterState) -> dict:
    """Join the branches into one validated signal (without commentary yet)."""
    measured = sorted(state.get("measured") or [],
                      key=lambda r: -int(r["marks"]))
    signal = contract.envelope(
        period=state["period"],
        coverage=state["coverage"],
        companies=measured,
        guards=state["guards"],
        commentary=None,
    )
    return {"signal": signal}


def commentary_node(state: QuarterState) -> dict:
    """The only LLM call. Grounded strictly in the assembled signal.

    The model is handed the signal's own figures and nothing else -- no
    database, no tools, no retrieval -- so a number in its prose that is not
    in those figures is a fabrication, and `check_grounding` rejects the whole
    note when it finds one.
    """
    signal = dict(state["signal"])
    if state.get("dry_run"):
        signal["commentary"] = {
            "text": "", "is_model_output": True, "model": None,
            "generated_at": signal["generated_at"], "grounded_in": [],
            "refused": True,
            "refusal_reason": "--dry-run: no model was called.",
        }
        return {"signal": contract.validate(signal)}

    facts = {k: signal[k] for k in
             ("period", "coverage", "companies", "guards", "not_supported")}
    signal["commentary"] = C.write_commentary(facts,
                                              backend=state.get("backend"))
    return {"signal": contract.validate(signal)}


def render_note(state: QuarterState) -> dict:
    """The human artifact. Deliberately a separate thing from the signal."""
    signal = state["signal"]
    period, coverage = signal["period"], signal["coverage"]
    comment = signal.get("commentary") or {}

    lines = [
        "# Quarterly note — private AI valuations",
        "",
        f"As of **{period['latest_period_end']}** · "
        f"{coverage['companies']} companies · {coverage['managers']} managers · "
        f"{coverage['marks_published']:,} published marks of "
        f"{coverage['marks']:,}",
        "",
        "> Every figure below is as of a filed period end, not as of today. "
        "Filings lag their period end by roughly 55–60 days and the bulk data "
        "sets lag those again.",
        "",
        "## Commentary",
        "",
    ]
    if comment.get("refused"):
        lines += [
            f"_No commentary was generated. {comment.get('refusal_reason')}_",
            "",
            "The figures below are unaffected — they are deterministic and "
            "were computed before any model was consulted.",
            "",
        ]
    else:
        lines += [
            comment.get("text", "").strip(),
            "",
            f"— *Model output, not a verified claim. Written by "
            f"`{comment.get('model')}` from the figures in this note and "
            "nothing else; every number in it was checked against them.*",
            "",
        ]

    lines += [
        "## By company",
        "",
        "| Company | Status | Marks | Managers | Latest | Latest price range | "
        "Re-mark rate | Median spread | Median days to half |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in signal["companies"]:
        disp, prop = row.get("dispersion") or {}, row.get("propagation") or {}
        price = ("—" if row["latest_price_min"] is None else
                 f"{row['latest_price_min']:,.2f} – {row['latest_price_max']:,.2f}")
        rate = ("—" if row["remark_rate"] is None
                else f"{row['remark_rate']:.1%}")
        spread = ("suppressed" if disp.get("suppressed_reason")
                  else "—" if disp.get("median_spread") is None
                  else f"{disp['median_spread']:.1%}")
        days = ("suppressed" if prop.get("suppressed_reason")
                else "—" if prop.get("median_days_to_half") is None
                else f"{prop['median_days_to_half']}d")
        lines.append(
            f"| {row['company']} | `{row['status']}` | {row['marks']:,} | "
            f"{row['managers']} | {row['latest_period_end'] or '—'} | {price} | "
            f"{rate} | {spread} | {days} |")

    suppressed = [r for r in signal["companies"]
                  if (r.get("dispersion") or {}).get("suppressed_reason")]
    if suppressed:
        lines += ["", "### Why some figures are suppressed", ""]
        for row in suppressed:
            lines.append(f"- **{row['company']}** — "
                         f"{row['dispersion']['suppressed_reason']}.")
        lines += ["", "A suppressed figure is a decision, not an absence. The "
                      "signal carries it as an explicit `suppressed_reason` so "
                      "a consumer can tell the two apart.", ""]

    guards = signal["guards"]
    lines += [
        "",
        "## Guards",
        "",
        "| Guard | Count |",
        "|---|---|",
        f"| Marks blocked from change series | {guards['change_blocked']:,} |",
        f"| Suspected splits awaiting adjudication | "
        f"{guards['unadjudicated_splits']} |",
        f"| Confirmed splits | {guards.get('confirmed_splits', 0)} |",
        f"| Unresolved review decisions | {guards['unresolved_reviews']} |",
        f"| Incomplete ingest runs | {guards['incomplete_runs']} |",
        f"| Unpriced marks | {guards.get('unpriced_marks', 0):,} |",
        "",
        "## What this note does not say",
        "",
    ]
    lines += [f"{i}. {line}" for i, line in
              enumerate(signal["not_supported"], 1)]
    lines += [
        "",
        f"---",
        "",
        f"Signal `schema_version` {signal['schema_version']} · generated "
        f"{signal['generated_at']} · machine-readable twin in "
        "`docs/_signal.json`.",
        "",
    ]
    return {"note": "\n".join(lines)}


# --------------------------------------------------------------------------
# Wiring
# --------------------------------------------------------------------------


def fan_out(state: QuarterState):
    """One branch per company. The reason this is a graph at all."""
    from langgraph.types import Send

    return [Send("measure_company", {**state, "_company": c})
            for c in state["companies"]]


def _measure_entry(state) -> dict:
    return measure_company(state, state["_company"])


def build_graph():
    graph = StateGraph(QuarterState)
    graph.add_node("collect", collect)
    graph.add_node("measure_company", _measure_entry)
    graph.add_node("assemble", assemble)
    graph.add_node("commentary", commentary_node)
    graph.add_node("render_note", render_note)

    graph.add_edge(START, "collect")
    graph.add_conditional_edges("collect", fan_out, ["measure_company"])
    graph.add_edge("measure_company", "assemble")
    graph.add_edge("assemble", "commentary")
    graph.add_edge("commentary", "render_note")
    graph.add_edge("render_note", END)
    return graph.compile()


def run(*, dry_run: bool = False, backend: str | None = None) -> dict:
    final = build_graph().invoke({"dry_run": dry_run, "backend": backend})
    contract.write(final["signal"], SIGNAL_PATH)
    NOTE_PATH.write_text(final["note"], encoding="utf-8", newline="\n")
    return final


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="skip the model call; emit the signal and the note "
                         "with commentary refused")
    ap.add_argument("--backend", choices=("groq", "ollama"),
                    help="force a commentary backend")
    args = ap.parse_args()

    final = run(dry_run=args.dry_run, backend=args.backend)
    signal = final["signal"]
    comment = signal.get("commentary") or {}
    print(f"wrote {SIGNAL_PATH}")
    print(f"wrote {NOTE_PATH}")
    print(json.dumps({
        "schema_version": signal["schema_version"],
        "companies": len(signal["companies"]),
        "marks_published": signal["coverage"]["marks_published"],
        "commentary": ("refused: " + str(comment.get("refusal_reason"))
                       if comment.get("refused") else
                       f"{len(comment.get('text', '').split())} words from "
                       f"{comment.get('model')}"),
    }, indent=2))


if __name__ == "__main__":
    main()
