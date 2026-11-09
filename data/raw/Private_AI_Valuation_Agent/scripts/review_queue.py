"""The review queue: run the resolution graph, then answer what it stops on.

    python -m scripts.review_queue --run              # resolve everything resolvable
    python -m scripts.review_queue --status            # what happened, in counts
    python -m scripts.review_queue --list              # what is waiting for a human
    python -m scripts.review_queue --show 3            # the full review card
    python -m scripts.review_queue --decide 3 --verdict company \\
        --company "Databricks, Inc." --reviewer "Om Mali" \\
        --rationale "filer's own SPV name; price matches the Databricks series"
    python -m scripts.review_queue --export-fixture    # decisions -> regression tests

`--run` is safe to repeat. Ambiguities already recorded in match_decisions are
skipped, and an ambiguity waiting on a human stays exactly where it is: the
LangGraph Postgres checkpointer holds the paused state, so the queue survives
this process exiting and is still there days later.

Nothing here writes a decision on a human's behalf. `--decide` requires a
reviewer name and a rationale, and the graph rejects a blank of either (P4:
"looks good" is not a handoff condition).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from langgraph.types import Command  # noqa: E402

from src.db.connect import apply_schema, connect, database_url  # noqa: E402
from src.db.seed import seed_companies  # noqa: E402
from src.graphs.resolve_graph import (  # noqa: E402
    VERDICTS,
    build_graph,
    checkpointer_from,
    pending_ambiguities,
    resolve_one,
    split_signals,
    thread_id,
)

FIXTURE = ROOT / "tests" / "fixtures" / "review_decisions_v1.json"
REPORT = ROOT / "docs" / "review_queue.md"
CONT = "\\"  # a shell line-continuation, for the copyable commands


def _load_backend(name: str | None):
    """Only if explicitly asked for. Week 5 is why the default is off."""
    if not name:
        return None
    from src.resolve.adjudicate import RESPONSE_SCHEMA
    from src.resolve.llm import load_backend

    return load_backend(model=name, schema=RESPONSE_SCHEMA)


def _paused(graph, keys) -> list[dict]:
    """Threads sitting at an interrupt, in a stable order."""
    out = []
    for key in keys:
        config = {"configurable": {"thread_id": thread_id(key)}}
        snapshot = graph.get_state(config)
        cards = [
            getattr(value, "value", value)
            for task in snapshot.tasks
            for value in (getattr(task, "interrupts", ()) or ())
        ]
        if cards:
            out.append({"decision_key": key, "thread_id": config["configurable"]["thread_id"],
                        "card": cards[0]})
    return sorted(out, key=lambda r: r["decision_key"])


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------


def cmd_run(conn, url, args) -> None:
    items = pending_ambiguities(conn, only_undecided=not args.all)
    splits = split_signals(conn)
    if args.limit:
        items = items[: args.limit]

    backend = _load_backend(args.model)
    accepted = paused = reused = 0
    triggers: dict = {}

    with checkpointer_from(url) as cp:
        cp.setup()
        graph = build_graph(conn, cp, backend=backend, run_id=args.run_id)
        for item in items:
            key = item["decision_key"]
            result = resolve_one(graph, item, splits.get(key))
            trigger = result.get("trigger", "?")
            triggers[trigger] = triggers.get(trigger, 0) + item["holdings"]
            if result.get("__interrupt__") or result.get("route") == "review":
                paused += 1
            elif trigger == "reused":
                reused += 1
            else:
                accepted += 1

    print(f"ambiguities processed : {len(items)}")
    print(f"  auto-accepted       : {accepted}")
    print(f"  reused a decision   : {reused}")
    print(f"  waiting on a human  : {paused}")
    if triggers:
        print("\nholdings by route:")
        for name, count in sorted(triggers.items(), key=lambda kv: -kv[1]):
            print(f"  {name:<12} {count:>6,}")
    if paused:
        print(f"\n{paused} ambiguities are paused in Postgres. "
              f"Run --list to see them; this process can exit safely.")


def cmd_status(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM raw_holdings")
        holdings = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM match_decisions")
        decided = cur.fetchone()[0]
        cur.execute("""
            SELECT method, count(*), count(DISTINCT decision_key)
              FROM match_decisions GROUP BY 1 ORDER BY 2 DESC
        """)
        by_method = cur.fetchall()
        cur.execute("""
            SELECT coalesce(trigger, '(none)'), count(*)
              FROM match_decisions GROUP BY 1 ORDER BY 2 DESC
        """)
        by_trigger = cur.fetchall()
        cur.execute("""
            SELECT verdict, count(*), sum(holdings_covered)
              FROM review_decisions GROUP BY 1 ORDER BY 1
        """)
        reviews = cur.fetchall()
        cur.execute("""
            SELECT c.canonical_name, count(*)
              FROM match_decisions m JOIN companies c USING (company_id)
             GROUP BY 1 ORDER BY 2 DESC
        """)
        by_company = cur.fetchall()

    print(f"holdings in raw_holdings : {holdings:,}")
    print(f"holdings with a decision : {decided:,}  ({decided / max(holdings, 1):.1%})")
    print(f"holdings still undecided : {holdings - decided:,}\n")

    print(f"{'method':<12}{'holdings':>10}{'ambiguities':>14}")
    print("-" * 36)
    for method, n, keys in by_method:
        print(f"{method:<12}{n:>10,}{keys:>14,}")

    print(f"\n{'trigger':<14}{'holdings':>10}")
    print("-" * 24)
    for trigger, n in by_trigger:
        print(f"{trigger:<14}{n:>10,}")

    if reviews:
        print(f"\n{'human verdict':<18}{'decisions':>10}{'holdings':>10}")
        print("-" * 38)
        for verdict, n, covered in reviews:
            print(f"{verdict:<18}{n:>10,}{(covered or 0):>10,}")

    if by_company:
        print(f"\n{'company':<40}{'holdings':>10}")
        print("-" * 50)
        for name, n in by_company:
            print(f"{name:<40}{n:>10,}")


def cmd_list(conn, url) -> None:
    items = pending_ambiguities(conn)
    keys = [i["decision_key"] for i in items]
    with checkpointer_from(url) as cp:
        graph = build_graph(conn, cp)
        rows = _paused(graph, keys)
    if not rows:
        print("nothing is waiting on a human.")
        return
    print(f"{len(rows)} ambiguities are waiting on a human.\n")
    print(f"{'#':>3}  {'trigger':<12}{'holdings':>9}  {'matcher said':<26}issuer")
    print("-" * 108)
    for i, row in enumerate(rows, 1):
        card = row["card"]
        said = str(card.get("matcher_company") or "nothing")
        score = card.get("matcher_score")
        said = f"{said[:18]} {score:.2f}" if score else said[:24]
        print(f"{i:>3}  {str(card.get('trigger')):<12}{card.get('holdings', 0):>9}  "
              f"{said:<26}{card.get('issuer_name', '')[:44]}")
    groups: dict = {}
    for row in rows:
        card = row["card"]
        bucket = (card.get("trigger"), card.get("matcher_company") or "nothing")
        entry = groups.setdefault(bucket, {"cards": 0, "holdings": 0})
        entry["cards"] += 1
        entry["holdings"] += card.get("holdings", 0) or 0
    print(f"\n{'trigger':<14}{'matcher said':<40}{'cards':>6}{'holdings':>10}")
    print("-" * 70)
    for (trigger, company), entry in sorted(groups.items(),
                                            key=lambda kv: -kv[1]["holdings"]):
        print(f"{str(trigger):<14}{company[:38]:<40}"
              f"{entry['cards']:>6}{entry['holdings']:>10,}")
    print("\n--show <#> for the full card, --decide <#> to answer one.")
    print("--decide-company <name> answers every paused spelling of one company at once.")


def _pick(conn, url, which: str):
    items = pending_ambiguities(conn)
    keys = [i["decision_key"] for i in items]
    with checkpointer_from(url) as cp:
        graph = build_graph(conn, cp)
        rows = _paused(graph, keys)
    if which.isdigit():
        index = int(which) - 1
        if not 0 <= index < len(rows):
            sys.exit(f"there is no #{which}; --list shows {len(rows)}")
        return rows[index]
    matches = [r for r in rows if which.upper() in r["decision_key"]]
    if not matches:
        sys.exit(f"no paused ambiguity matches {which!r}")
    if len(matches) > 1:
        sys.exit(f"{which!r} matches {len(matches)} paused ambiguities; be more specific")
    return matches[0]


def cmd_show(conn, url, which: str) -> None:
    row = _pick(conn, url, which)
    print(row["card"]["markdown"])
    print(f"\n<!-- thread {row['thread_id']} · key {row['decision_key']} -->")


def cmd_decide(conn, url, args) -> None:
    row = _pick(conn, url, args.decide)
    config = {"configurable": {"thread_id": row["thread_id"]}}
    answer = {
        "verdict": args.verdict,
        "company": args.company,
        "class_normalized": args.share_class,
        "reviewer": args.reviewer,
        "rationale": args.rationale,
    }
    with checkpointer_from(url) as cp:
        graph = build_graph(conn, cp, run_id=args.run_id)
        result = graph.invoke(Command(resume=answer), config=config)
    print(f"decided: {row['decision_key']}")
    print(f"  verdict   : {result.get('verdict')}")
    print(f"  company   : {result.get('company') or '(none)'}")
    print(f"  reviewer  : {result.get('reviewer')}")
    print(f"  holdings  : {result.get('persisted')} match_decisions rows written")
    print("  this ambiguity will never be presented again.")


def cmd_decide_company(conn, url, args) -> None:
    """One answer, applied to every spelling of one company.

    The `new_company` trigger asks whether a company belongs in the universe.
    X.AI reaches the queue under twenty spellings, and twenty cards asking the
    same question is the failure this week exists to remove. The human answers
    once here; the graph resumes every paused thread for that company with that
    same answer, and each spelling still gets its own audit row citing the one
    reviewer and the one rationale.
    """
    items = pending_ambiguities(conn)
    keys = [i["decision_key"] for i in items]
    answer = {
        "verdict": args.verdict,
        "company": args.company,
        "class_normalized": args.share_class,
        "reviewer": args.reviewer,
        "rationale": args.rationale,
    }
    target = args.decide_company.strip().lower()
    with checkpointer_from(url) as cp:
        graph = build_graph(conn, cp, run_id=args.run_id)
        rows = [
            r for r in _paused(graph, keys)
            if str(r["card"].get("matcher_company") or "").strip().lower() == target
        ]
        if not rows:
            sys.exit(f"no paused ambiguity has the matcher reading {args.decide_company!r}")
        holdings = 0
        for row in rows:
            config = {"configurable": {"thread_id": row["thread_id"]}}
            result = graph.invoke(Command(resume=answer), config=config)
            holdings += result.get("persisted", 0) or 0
    print(f"one decision applied to {len(rows)} spellings of {args.decide_company}")
    print(f"  verdict  : {args.verdict}")
    print(f"  reviewer : {args.reviewer}")
    print(f"  holdings : {holdings} match_decisions rows written")
    print("  future spellings of this company will reuse it without asking.")


def cmd_report(conn, url, args) -> None:
    """Write the queue as a Markdown report -- the human half of P5.

    --list is for whoever is working the queue. This is for whoever has to
    decide whether the queue is worth working: one section per question, the
    evidence beside it, and an explicit statement of what is blocked until it
    is answered.
    """
    items = pending_ambiguities(conn)
    keys = [i["decision_key"] for i in items]
    with checkpointer_from(url) as cp:
        graph = build_graph(conn, cp)
        rows = _paused(graph, keys)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM raw_holdings")
        holdings = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM match_decisions")
        decided = cur.fetchone()[0]

    groups: dict = {}
    for row in rows:
        card = row["card"]
        bucket = (card.get("trigger"), card.get("matcher_company") or "nothing")
        entry = groups.setdefault(bucket, {"cards": [], "holdings": 0})
        entry["cards"].append(row)
        entry["holdings"] += card.get("holdings", 0) or 0

    waiting = sum(e["holdings"] for e in groups.values())
    out = [
        "# Review queue",
        "",
        f"*Generated by `scripts/review_queue.py --report`. {len(rows)} ambiguities are "
        f"paused in Postgres, covering {waiting:,} holdings.*",
        "",
        "| | |",
        "|---|---|",
        f"| holdings in the universe layer | {holdings:,} |",
        f"| decided without a human | {decided:,} |",
        f"| waiting on a human | {waiting:,} |",
        f"| distinct questions | {len(groups)} |",
        f"| cards behind those questions | {len(rows)} |",
        "",
        "Nothing here has been decided. A paused review holds its state in the "
        "LangGraph Postgres checkpointer, so this list is the same list after a "
        "restart, and it is still the same list next week.",
        "",
        "## The questions",
        "",
        "| # | trigger | the matcher's reading | cards | holdings |",
        "|---|---|---|---|---|",
    ]
    ordered = sorted(groups.items(), key=lambda kv: -kv[1]["holdings"])
    for i, ((trigger, company), entry) in enumerate(ordered, 1):
        out.append(f"| {i} | `{trigger}` | {company} | {len(entry['cards'])} "
                   f"| {entry['holdings']:,} |")

    for i, ((trigger, company), entry) in enumerate(ordered, 1):
        first = entry["cards"][0]["card"]
        out += [
            "",
            f"### {i}. {trigger} — {company}",
            "",
            f"{len(entry['cards'])} cards, {entry['holdings']:,} holdings.",
            "",
            ("One answer settles all of them: `new_company` asks whether a company "
             "belongs in the universe, and the answer is recorded against the "
             "company, so every other spelling reuses it without asking."
             if trigger == "new_company" else
             "Each card is formally its own question -- a `split` is a specific "
             "price step and a `band` case is a specific string. `--decide-company` "
             "will apply one answer to all of them, which is right only if it is "
             "genuinely the same call."),
            "",
            "<details><summary>The first card, verbatim</summary>",
            "",
            first.get("markdown", ""),
            "",
            "</details>",
            "",
            "```",
            f"python -m scripts.review_queue --decide-company {company!r} " + CONT,
            f"    --verdict company --company {company!r} " + CONT,
            '    --reviewer "<your name>" --rationale "<why>"',
            "```",
        ]

    out += [
        "",
        "## What answering does",
        "",
        "- writes one `review_decisions` row per question and one `match_decisions` "
        "row per holding, each naming the reviewer and the reason;",
        "- resumes the paused graph rather than re-running it, so the deterministic "
        "work is not repeated;",
        "- is reused for every future spelling of the same question, which is the "
        "guarantee the week was built for;",
        "- becomes a regression case via `--export-fixture`, so a later matcher "
        "change that would overturn the decision fails a test instead of "
        "silently winning.",
        "",
    ]
    target = Path(args.report) if isinstance(args.report, str) else REPORT
    target.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {target} -- {len(groups)} questions, {len(rows)} cards, "
          f"{waiting:,} holdings waiting")


def cmd_export_fixture(conn) -> None:
    """Every human decision becomes a regression case (plan.md week 6)."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT rd.decision_key, rd.issuer_name, rd.title_of_issue, rd.verdict,
                   c.canonical_name, rd.class_normalized, rd.trigger, rd.reviewer,
                   rd.rationale, rd.holdings_covered, rd.decided_at
              FROM review_decisions rd
         LEFT JOIN companies c ON c.company_id = rd.company_id
             ORDER BY rd.decision_key
        """)
        columns = [c[0] for c in cur.description]
        rows = [dict(zip(columns, r)) for r in cur.fetchall()]
    for row in rows:
        row["decided_at"] = row["decided_at"].isoformat()
    payload = {
        "fixture_version": "1.0.0",
        "note": (
            "Every human decision from the Week 6 review queue, exported as regression "
            "cases. tests/test_review_queue.py asserts the deterministic matcher never "
            "silently contradicts one of these: if a matcher change would overturn a "
            "human decision, the test fails and a human decides again."
        ),
        "decisions": rows,
    }
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"wrote {FIXTURE.relative_to(ROOT)} -- {len(rows)} decisions")


def main() -> None:
    # The review card is Markdown and carries em dashes and middot separators.
    # Windows hands Python a cp1252 stdout, which encodes those as single bytes
    # that are not valid UTF-8 -- piping the card to a file then produced
    # something grep called a binary file and refused to print. The card is a
    # human artifact (P5); it has to survive a redirect.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", action="store_true", help="run the graph over pending work")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--show", metavar="N_OR_KEY")
    ap.add_argument("--decide", metavar="N_OR_KEY")
    ap.add_argument("--decide-company", metavar="COMPANY", dest="decide_company",
                    help="answer once for every paused spelling of one company")
    ap.add_argument("--export-fixture", action="store_true")
    ap.add_argument("--report", nargs="?", const=True,
                    help="write the queue as Markdown (default docs/review_queue.md)")
    ap.add_argument("--verdict", choices=VERDICTS)
    ap.add_argument("--company")
    ap.add_argument("--share-class")
    ap.add_argument("--reviewer")
    ap.add_argument("--rationale")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--all", action="store_true",
                    help="with --run, re-process ambiguities that already have decisions")
    ap.add_argument("--run-id", type=int, dest="run_id")
    ap.add_argument("--model", help="also show a model suggestion on the card (off by default)")
    args = ap.parse_args()

    url = os.getenv("DATABASE_URL") or database_url()
    conn = connect()
    apply_schema(conn)
    seed_companies(conn)

    try:
        if args.run:
            cmd_run(conn, url, args)
        elif args.status:
            cmd_status(conn)
        elif args.list:
            cmd_list(conn, url)
        elif args.show:
            cmd_show(conn, url, args.show)
        elif args.decide:
            if not (args.verdict and args.reviewer and args.rationale):
                ap.error("--decide needs --verdict, --reviewer and --rationale")
            cmd_decide(conn, url, args)
        elif args.decide_company:
            if not (args.verdict and args.reviewer and args.rationale):
                ap.error("--decide-company needs --verdict, --reviewer and --rationale")
            cmd_decide_company(conn, url, args)
        elif args.report:
            cmd_report(conn, url, args)
        elif args.export_fixture:
            cmd_export_fixture(conn)
        else:
            ap.error("give --run, --status, --list, --show, --decide, "
                     "--decide-company or --export-fixture")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
