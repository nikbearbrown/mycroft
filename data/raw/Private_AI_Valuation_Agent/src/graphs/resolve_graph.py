"""The resolution graph: deterministic match, then a human, then persistence.

    candidates -> recall -> triage -->  accept  -> persist -> END
                                   \-> review -> persist -> END
                                        ^
                                        |
                                  interrupt() -- the run stops here, the state
                                  is in Postgres, and the process may exit

plan.md week 6: "LangGraph graph: candidates -> adjudication -> confidence
check -> interrupt() on low confidence, new company, or suspected split.
Postgres checkpointer so a paused run survives restart and resumes days later.
Reviewer view; persist to match_decisions; guarantee decisions are reused,
never re-asked."

--------------------------------------------------------------------------
The unit of work is an ambiguity, not a holding
--------------------------------------------------------------------------
One graph run resolves one distinct (issuer_name, title_of_issue) pair and
writes a match_decisions row for *every* holding that shares it. The 5,806
universe holdings are 231 such pairs, so a queue keyed by holding would ask the
same question up to 85 times -- once per Databricks spelling. plan.md asks for
both `unique (raw_id)` on match_decisions and for decisions "keyed so the same
ambiguity is never presented twice"; the two tables in schema.sql are how both
are true at once.

The thread_id is derived from the decision key, so re-running the pipeline
resumes the same paused thread rather than opening a second one.

--------------------------------------------------------------------------
What reaches a human, and what does not
--------------------------------------------------------------------------
Three triggers, from plan.md, in the order they are checked:

  split        the price for this company and fund moved by a near-integer
               ratio between consecutive period ends. Never auto-adjusted.
  unresolved   the deterministic matcher declined to name a company.
  band         it named one, below the auto-accept score.
  new_company  it named a company that is not a frozen universe v1 member.

**Model confidence is deliberately not a trigger.** Week 5 measured it: the
model returned 1.000 on 315 of 322 answers including 12 of the 15 it got wrong
(docs/entity_resolution.md section 9.4). Sorting a review queue by it would put
the wrong rows at the bottom. The LLM adjudicator is wired in below and is
**off by default** for the same reason.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Any, TypedDict

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from langgraph.checkpoint.postgres import PostgresSaver  # noqa: E402
from langgraph.graph import END, StateGraph  # noqa: E402
from langgraph.types import interrupt  # noqa: E402

from src.db.seed import company_ids  # noqa: E402
from src.ingest.universe import status_of  # noqa: E402
from src.resolve.adjudicate import AUTO_ACCEPT, REVIEW_FLOOR  # noqa: E402
from src.resolve.match import resolve  # noqa: E402

KEY_SEP = " || "

# The near-integer price-ratio rule lives in src/marks/splits.py, which is the
# real detector; this queue trigger uses the same numbers so the two can never
# disagree about what a split looks like.
#
# Corrected in Week 7. This module first used 2% *of the ratio* with no cap,
# which called an OpenAI move of 348x "near-integer" (a 2% window at 348 is
# +/- 7). The fix was an absolute 0.02 window plus a cap of 20 -- and the cap
# was the part that mattered. The absolute window then quietly failed plan.md's
# own verification case: Perplexity's 695 -> 58 is a ratio of 11.93, and an
# absolute 0.02 around 12 misses it by a factor of three. The rule is now a
# RELATIVE 1% window under the same cap, which catches 11.93, still leaves
# X.AI's 2.064 repricing alone, and still excludes 348 -- by the cap.
from src.marks.splits import (  # noqa: E402
    SPLIT_MAX_RATIO,
    SPLIT_MIN_RATIO,
    SPLIT_TOLERANCE,
    is_split_ratio,  # noqa: F401  -- re-exported for the queue's tests
)

VERDICT_COMPANY = "company"
VERDICT_NOT_IN_UNIVERSE = "not_in_universe"
VERDICT_UNRESOLVED = "unresolved"
VERDICTS = (VERDICT_COMPANY, VERDICT_NOT_IN_UNIVERSE, VERDICT_UNRESOLVED)


# --------------------------------------------------------------------------
# Keys
# --------------------------------------------------------------------------


def decision_key(issuer_name: str, title: str | None) -> str:
    """The identity of a question, not of a row.

    Case- and whitespace-normalised, so the two MWAM SpaceX vehicles that
    differ only by a trailing space in the filed name are one question rather
    than two. Kept as readable text rather than a hash: a reviewer has to be
    able to audit the key in the table (P5).
    """
    name = re.sub(r"\s+", " ", (issuer_name or "")).strip().upper()
    ttl = re.sub(r"\s+", " ", (title or "")).strip().upper()
    return f"{name}{KEY_SEP}{ttl}"


def company_key(company: str) -> str:
    """The key for a decision about a COMPANY rather than about a spelling.

    `new_company` is the one trigger whose question is not really about the
    string in front of the reviewer. X.AI appears under twenty spellings in the
    universe layer, and asking twenty times whether X.AI belongs in the universe
    is precisely the failure this week exists to remove. One answer, recorded
    against the company, is reused by every spelling of it.
    """
    return f"COMPANY{KEY_SEP}{company.strip().upper()}"


def thread_id(key: str) -> str:
    """Deterministic from the key, so a re-run resumes instead of forking."""
    return "resolve:" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------
# Reading the work out of Postgres
# --------------------------------------------------------------------------

PENDING_SQL = """
WITH holding AS (
    SELECT r.raw_id,
           r.issuer_name,
           r.title_of_issue,
           r.lei,
           r.price_per_share,
           r.company_provisional,
           r.is_spv,
           fl.period_end,
           f.family
      FROM raw_holdings r
      JOIN filings fl ON fl.filing_id = r.filing_id
      JOIN funds   f  ON f.fund_id    = fl.fund_id
)
SELECT upper(regexp_replace(coalesce(issuer_name, ''), '\\s+', ' ', 'g'))
         || %(sep)s
         || upper(regexp_replace(coalesce(title_of_issue, ''), '\\s+', ' ', 'g'))
           AS decision_key,
       min(issuer_name)                        AS issuer_name,
       min(title_of_issue)                     AS title_of_issue,
       max(lei)                                AS lei,
       array_agg(DISTINCT raw_id ORDER BY raw_id) AS raw_ids,
       count(*)                                AS holdings,
       min(price_per_share)                    AS price_min,
       max(price_per_share)                    AS price_max,
       min(period_end)::text                   AS period_first,
       max(period_end)::text                   AS period_last,
       count(DISTINCT family)                  AS families,
       string_agg(DISTINCT family, ', ' ORDER BY family) AS family_list,
       min(company_provisional)                AS company_provisional,
       bool_or(is_spv)                         AS is_spv
  FROM holding
 GROUP BY 1
 ORDER BY 1
"""

# Trailing-space and case variants collapse in the GROUP BY above, so the
# aggregate strings are picked with min() to keep the query deterministic.

SPLIT_SQL = """
WITH priced AS (
    SELECT r.issuer_name,
           r.title_of_issue,
           r.company_provisional AS company,
           fl.fund_id,
           fl.period_end,
           r.price_per_share AS px
      FROM raw_holdings r
      JOIN filings fl ON fl.filing_id = r.filing_id
     WHERE r.price_per_share IS NOT NULL
       AND r.price_per_share > 0
       AND r.company_provisional IS NOT NULL
), stepped AS (
    SELECT priced.*,
           lag(px)         OVER w AS prev_px,
           lag(period_end) OVER w AS prev_period
      FROM priced
    WINDOW w AS (PARTITION BY company, fund_id ORDER BY period_end, px)
)
SELECT issuer_name, title_of_issue, company, period_end::text, prev_period::text,
       px, prev_px,
       CASE WHEN px > prev_px THEN px / prev_px ELSE prev_px / px END AS ratio
  FROM stepped
 WHERE prev_px IS NOT NULL
   AND period_end <> prev_period
   AND CASE WHEN px > prev_px THEN px / prev_px ELSE prev_px / px END
        BETWEEN %(min_ratio)s AND %(max_ratio)s
   AND abs(
        (CASE WHEN px > prev_px THEN px / prev_px ELSE prev_px / px END)
        - round(CASE WHEN px > prev_px THEN px / prev_px ELSE prev_px / px END)
       ) <= %(tol)s * round(CASE WHEN px > prev_px THEN px / prev_px ELSE prev_px / px END)
 ORDER BY ratio DESC
"""


def pending_ambiguities(conn, only_undecided: bool = True) -> list[dict]:
    """Every distinct question in raw_holdings, newest data included.

    `only_undecided` drops the ones already recorded in match_decisions, so a
    second pipeline run does no work rather than re-deciding what is settled.
    """
    with conn.cursor() as cur:
        cur.execute(PENDING_SQL, {"sep": KEY_SEP})
        columns = [c[0] for c in cur.description]
        rows = [dict(zip(columns, r)) for r in cur.fetchall()]
        if only_undecided:
            cur.execute("SELECT DISTINCT decision_key FROM match_decisions "
                        "WHERE decision_key IS NOT NULL")
            done = {r[0] for r in cur.fetchall()}
            rows = [r for r in rows if r["decision_key"] not in done]
    for row in rows:
        row["price_min"] = float(row["price_min"]) if row["price_min"] is not None else None
        row["price_max"] = float(row["price_max"]) if row["price_max"] is not None else None
        row["raw_ids"] = list(row["raw_ids"])
    return rows


def split_signals(conn) -> dict:
    """decision_key -> the worst near-integer price step found for it.

    A queue trigger, not the Week 7 split detector. It answers one question --
    is there a price move here a human should look at before this holding is
    trusted -- and deliberately errs toward asking.
    """
    with conn.cursor() as cur:
        cur.execute(SPLIT_SQL, {"min_ratio": SPLIT_MIN_RATIO,
                                "max_ratio": SPLIT_MAX_RATIO,
                                "tol": SPLIT_TOLERANCE})
        out: dict = {}
        for name, title, company, period, prev, px, prev_px, ratio in cur.fetchall():
            key = decision_key(name, title)
            signal = {
                "company": company,
                "period_end": period,
                "prev_period": prev,
                "price": float(px),
                "prior_price": float(prev_px),
                "ratio": round(float(ratio), 4),
            }
            if key not in out or signal["ratio"] > out[key]["ratio"]:
                out[key] = signal
    return out


# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------


class ResolveState(TypedDict, total=False):
    # the question
    decision_key: str
    issuer_name: str
    title_of_issue: str
    lei: str | None
    raw_ids: list
    holdings: int
    price_min: float | None
    price_max: float | None
    period_first: str
    period_last: str
    families: int
    family_list: str
    company_provisional: str | None
    is_spv: bool
    split: dict | None
    # what the deterministic matcher concluded
    company: str | None
    score: float
    method: str
    class_normalized: str
    wrapper: str
    note: str
    # routing
    reused: bool
    route: str
    trigger: str
    # the decision
    verdict: str
    reviewer: str
    rationale: str
    # bookkeeping
    persisted: int


# --------------------------------------------------------------------------
# Nodes
# --------------------------------------------------------------------------


def build_graph(conn, checkpointer, *, backend=None, run_id: int | None = None):
    """Compile the graph against one connection and one checkpointer.

    `backend` is the LLM adjudicator and defaults to None -- see the module
    docstring. Passing one does not change what reaches a human; it only fills
    in a suggestion on the review card, clearly labelled as a model judgment
    (P8: model judgments are always labelled as judgments).
    """
    ids = company_ids(conn)

    def node_candidates(state: ResolveState) -> dict:
        match = resolve(state["issuer_name"], state.get("title_of_issue"),
                        state.get("lei"))
        return {
            "company": match.company,
            "score": round(match.score, 4),
            "method": match.method,
            "class_normalized": match.share_class.label(),
            "wrapper": match.wrapper,
            "note": match.note,
        }

    def node_recall(state: ResolveState) -> dict:
        """The 'never asked twice' guarantee, and the only place it lives.

        Two lookups, most specific first: a decision about this exact spelling,
        then a decision about the company the matcher named. The second is what
        stops X.AI being asked twenty times.
        """
        lookup = """
                SELECT rd.verdict, c.canonical_name, rd.class_normalized,
                       rd.reviewer, rd.rationale
                  FROM review_decisions rd
             LEFT JOIN companies c ON c.company_id = rd.company_id
                 WHERE rd.decision_key = %s
        """
        with conn.cursor() as cur:
            cur.execute(lookup, (state["decision_key"],))
            row = cur.fetchone()
            if not row and state.get("company"):
                cur.execute(lookup, (company_key(state["company"]),))
                row = cur.fetchone()
        if not row:
            return {"reused": False}
        verdict, company, klass, reviewer, rationale = row
        return {
            "reused": True,
            "verdict": verdict,
            "company": company,
            "class_normalized": klass or state.get("class_normalized", "UNKNOWN"),
            "reviewer": reviewer,
            "rationale": rationale,
            "method": "reused",
        }

    def node_triage(state: ResolveState) -> dict:
        if state.get("reused"):
            return {"route": "accept", "trigger": "reused"}
        if state.get("split"):
            return {"route": "review", "trigger": "split"}
        company, score = state.get("company"), state.get("score", 0.0)
        if company is None:
            return {"route": "review", "trigger": "unresolved"}
        if score < AUTO_ACCEPT:
            return {"route": "review", "trigger": "band"}
        if status_of(company) == "watchlist":
            # Resolved to a company the Week 1 gate did not admit. plan.md:
            # additions happen only at a version boundary, so this is a human
            # decision by construction, however confident the matcher is.
            return {"route": "review", "trigger": "new_company"}
        return {"route": "accept", "trigger": "auto"}

    def node_review(state: ResolveState) -> dict:
        """Stop. The state is already in Postgres; the process may now exit."""
        answer = interrupt(review_card(state, backend=backend))
        if not isinstance(answer, dict):
            raise TypeError(
                "a review decision must be a dict with verdict/reviewer/rationale; "
                f"got {type(answer).__name__}"
            )
        verdict = answer.get("verdict")
        if verdict not in VERDICTS:
            raise ValueError(f"verdict must be one of {VERDICTS}, got {verdict!r}")
        reviewer = (answer.get("reviewer") or "").strip()
        rationale = (answer.get("rationale") or "").strip()
        if not reviewer:
            raise ValueError("a decision needs a named reviewer -- 'auto' is not a name (P4)")
        if not rationale:
            raise ValueError("a decision needs a rationale; 'looks good' is not a handoff (P4)")
        company = answer.get("company")
        if verdict == VERDICT_COMPANY:
            if not company:
                raise ValueError("verdict 'company' needs a company")
            if company not in ids:
                raise ValueError(
                    f"{company!r} is not in the companies table. A new company is a "
                    "universe-version decision, not a review-queue decision."
                )
        else:
            company = None
        return {
            "verdict": verdict,
            "company": company,
            "class_normalized": answer.get("class_normalized")
                                or state.get("class_normalized", "UNKNOWN"),
            "reviewer": reviewer,
            "rationale": rationale,
            "method": "human",
        }

    def node_persist(state: ResolveState) -> dict:
        verdict = state.get("verdict") or (
            VERDICT_COMPANY if state.get("company") else VERDICT_UNRESOLVED
        )
        company = state.get("company")
        company_id = ids.get(company) if company else None
        method = state.get("method", "none")
        human = method == "human"

        with conn.cursor() as cur:
            if human:
                insert = """
                    INSERT INTO review_decisions
                        (decision_key, issuer_name, title_of_issue, verdict, company_id,
                         class_normalized, trigger, reviewer, rationale, holdings_covered,
                         thread_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (decision_key) DO NOTHING
                """
                cur.execute(insert, (state["decision_key"], state["issuer_name"],
                                     state.get("title_of_issue"), verdict, company_id,
                                     state.get("class_normalized"), state.get("trigger"),
                                     state["reviewer"], state["rationale"],
                                     state.get("holdings"),
                                     thread_id(state["decision_key"])))
                # A new_company answer is about the company, so record it against
                # the company as well. Every other spelling then reuses it
                # instead of asking again.
                if state.get("trigger") == "new_company" and state.get("company"):
                    key = company_key(state["company"])
                    cur.execute(insert, (key, state["company"], None, verdict, company_id,
                                         None, "new_company", state["reviewer"],
                                         state["rationale"], None, thread_id(key)))

            written = 0
            for raw_id in state.get("raw_ids", []):
                cur.execute("""
                    INSERT INTO match_decisions
                        (raw_id, company_id, method, confidence, model, reviewer,
                         rationale, decision_key, trigger, run_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (raw_id) DO NOTHING
                """, (raw_id, company_id, method,
                      state.get("score") if not human else None,
                      None, state.get("reviewer"), state.get("rationale"),
                      state["decision_key"], state.get("trigger"), run_id))
                written += cur.rowcount
        conn.commit()
        return {"persisted": written, "verdict": verdict}

    graph = StateGraph(ResolveState)
    graph.add_node("candidates", node_candidates)
    graph.add_node("recall", node_recall)
    graph.add_node("triage", node_triage)
    graph.add_node("review", node_review)
    graph.add_node("persist", node_persist)

    graph.set_entry_point("candidates")
    graph.add_edge("candidates", "recall")
    graph.add_edge("recall", "triage")
    graph.add_conditional_edges("triage", lambda s: s["route"],
                                {"accept": "persist", "review": "review"})
    graph.add_edge("review", "persist")
    graph.add_edge("persist", END)
    return graph.compile(checkpointer=checkpointer)


# --------------------------------------------------------------------------
# The reviewer's view (P5: a human artifact, not a log)
# --------------------------------------------------------------------------

TRIGGER_TEXT = {
    "band": "the matcher named a company but scored below the auto-accept line",
    "unresolved": "the matcher declined to name a company",
    "new_company": "resolved to a company that universe v1 does not admit",
    "split": "the price moved by a near-integer ratio between period ends",
}


def review_card(state: ResolveState, backend=None) -> dict:
    """What the reviewer is shown. Markdown, because a person reads it."""
    lines = [
        f"## Review: {state['issuer_name']}",
        "",
        f"**Why you are seeing this** — {TRIGGER_TEXT.get(state.get('trigger'), state.get('trigger'))}",
        "",
        "| | |",
        "|---|---|",
        f"| issuer name | `{state['issuer_name']}` |",
        f"| security title | `{state.get('title_of_issue') or '(none)'}` |",
        f"| holdings covered | {state.get('holdings')} |",
        f"| filer families | {state.get('family_list') or '(unknown)'} |",
        f"| periods | {state.get('period_first')} to {state.get('period_last')} |",
    ]
    lo, hi = state.get("price_min"), state.get("price_max")
    if lo is not None:
        price = f"{lo:,.4f}" if lo == hi else f"{lo:,.4f} to {hi:,.4f}"
        lines.append(f"| price per share | {price} |")
    if state.get("is_spv"):
        lines.append("| wrapper | flagged as an SPV |")
    lines += [
        "",
        "**The matcher's reading**",
        "",
        f"- company: {state.get('company') or '_nothing_'}",
        f"- score: {state.get('score'):.2f} "
        f"(auto-accept {AUTO_ACCEPT:.2f}, floor {REVIEW_FLOOR:.2f})",
        f"- method: {state.get('method')}",
        f"- share class: {state.get('class_normalized')}",
    ]
    if state.get("note"):
        lines.append(f"- note: {state['note']}")
    if state.get("company_provisional"):
        lines.append(f"- the frozen Week 2 name patterns said: "
                     f"{state['company_provisional']}")

    split = state.get("split")
    if split:
        lines += [
            "",
            "**Suspected split**",
            "",
            f"- {split['prev_period']}: {split['prior_price']:,.4f}",
            f"- {split['period_end']}: {split['price']:,.4f}",
            f"- ratio {split['ratio']:.4f} against {split['company']}",
            "",
            "A suspected split is never auto-adjusted. If this is a genuine split, "
            "say so in the rationale; the mark stays blocked from change "
            "calculations until Week 7's detector adjudicates it.",
        ]

    if backend is not None:
        from src.resolve.adjudicate import adjudicate

        verdict = adjudicate(backend, state["issuer_name"],
                             state.get("title_of_issue"), state.get("family_list"))
        lines += [
            "",
            "**Model suggestion — a judgment, not evidence**",
            "",
            f"- says: {verdict.company or 'nothing'}",
            f"- its stated reason: {verdict.reason or '(none)'}",
            "",
            "Week 5 measured this model at 5.1 points of precision *below* the "
            "matcher, and its confidence at 1.000 on 315 of 322 answers "
            "including 12 of the 15 it got wrong. Treat it as a prompt to look, "
            "never as a second opinion that counts.",
        ]

    lines += [
        "",
        "**Your options**",
        "",
        "- `company` — name one of the companies already in the universe",
        "- `not_in_universe` — deliberately none of ours",
        "- `unresolved` — you cannot tell; it stays reported, never dropped",
        "",
        "A decision needs your name and a reason. It will be reused for every "
        f"one of the {state.get('holdings')} holdings that share this key, and it "
        "will never be asked again.",
    ]
    return {
        "decision_key": state["decision_key"],
        "trigger": state.get("trigger"),
        "issuer_name": state["issuer_name"],
        "title_of_issue": state.get("title_of_issue"),
        "holdings": state.get("holdings"),
        "matcher_company": state.get("company"),
        "matcher_score": state.get("score"),
        "split": split,
        "markdown": "\n".join(lines),
    }


# --------------------------------------------------------------------------
# Driving it
# --------------------------------------------------------------------------


def checkpointer_from(url: str):
    """PostgresSaver as a context manager. Caller owns the `with`."""
    return PostgresSaver.from_conn_string(url)


def resolve_one(graph, item: dict, split: dict | None = None) -> dict:
    """Run one ambiguity to completion or to its interrupt.

    Returns the graph's own view of what happened. An interrupted run leaves
    nothing in Postgres except the checkpoint, which is the point: no
    half-decided rows in match_decisions.
    """
    state: dict[str, Any] = dict(item)
    state["split"] = split
    config = {"configurable": {"thread_id": thread_id(item["decision_key"])}}
    result = graph.invoke(state, config=config)
    return result


def pending_reviews(graph, keys: list[str] | None = None) -> list[dict]:
    """Every thread sitting at an interrupt, with its card."""
    out = []
    for key in keys or []:
        config = {"configurable": {"thread_id": thread_id(key)}}
        snapshot = graph.get_state(config)
        for task in snapshot.tasks:
            for value in getattr(task, "interrupts", ()) or ():
                card = getattr(value, "value", value)
                out.append({"decision_key": key,
                            "thread_id": config["configurable"]["thread_id"],
                            "card": card})
    return out
