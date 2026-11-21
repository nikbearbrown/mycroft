"""The episode supervisor (DESIGN.md §7.2–7.4): one company-quarter, end to end, as a LangGraph graph.

    START → opening → timeline → triage ─┬─ Send ─► read(filing 1) ─┐
                                         ├─ Send ─► read(filing 2) ─┼─► ledger → checks ─┬─ clear ──────► END
                                         └─ (nothing relevant) ─────┘      ▲             └─ questions ─┐
                                                                           └── investigate ×N ◄────────┘ (≤ 2 rounds)

* **timeline** (code): the filings in the window, through `edgar_pit` at the episode's cut-off, one copy per
  document (P45).
* **triage** (rules, `qwen3:4b` for the doubtful): which filings are about debt.
* **read** ×N (`qwen3:4b` points, code parses): one LangGraph `Send` per relevant filing. The branches run in
  the same super-step, so they run at the same time; model calls go through one GPU semaphore sized to
  Ollama's parallel slots (§7.5). Each branch appends its events to the shared state (`Annotated[list, add]`).
* **ledger** (code, `ledger/engine.py`): merge the events on the match key, sweep matured bonds, apply the
  rest in filing order to the opening ledger.
* **checks** (code, `ledger/checks.py`): self-checks; their flags and open questions.
* **investigate** ×N (week 6; code, `qwen3:4b` points): one `Send` per open question the engine raised
  (`graph/nodes/investigator.py`). Each returns an amendment with its citation, or leaves the question open; the
  ledger and checks run again on the amended events. At most two rounds (§7.1 rule 5); a question is investigated
  once.

The **opening ledger** has two modes (ablation A4). *Oracle start*: the harness gives the graph the opening ledger
baseline B0 carries forward, so the difference from B0 is what reading the filings added. *Agent start* (week 6):
the `opening` node reads it from the opening report's debt table (`graph/nodes/opening.py`). On one GPU slot the
opening reader and triage would queue anyway, so the node runs before the timeline rather than beside it.

Every tool the nodes use is passed in as `Tools`, so the graph can run on fakes in a test, and nothing in it can
reach the answer key (`eval/` is never imported). A SQLite checkpointer saves every step under the episode's
id: a crash or a sleeping laptop resumes where it stopped.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from operator import add
from typing import Annotated, Any, Callable, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from ..ledger import checks as ck
from ..ledger import engine
from .nodes.timeline import drop_duplicate_documents


class EpisodeState(TypedDict, total=False):
    episode: str
    cik: int
    quarter_end: str                       # the quarter being predicted (sweep year), YYYY-MM-DD
    window_open: str
    cutoff_date: str
    opening: list[dict]                    # the opening ledger, grader format
    opening_totals: dict
    candidates: list[dict]
    relevant: list[dict]
    events: Annotated[list[dict], add]     # appended by parallel readers
    readings: Annotated[list[dict], add]
    ledger: dict
    checks: dict
    timings: Annotated[list[dict], add]
    findings: Annotated[list[dict], add]   # investigators' results, every round
    rounds: int
    opening_reading: dict                  # agent start: what the opening-ledger reader returned


@dataclass
class Tools:
    """What the nodes may call. `timeline(cik, start, end)` → candidate dicts; `texts(row)` → {doc type: text};
    `triage(row, texts)` → triage record; `read(row)` → {"events": [...], ...}. Model-calling tools must hold
    `gpu` around each call."""
    timeline: Callable[[int, str, str], list[dict]]
    texts: Callable[[dict], dict]
    triage: Callable[[dict, dict], dict]
    read: Callable[[dict], dict]
    gpu: threading.Semaphore = field(default_factory=lambda: threading.Semaphore(2))
    opening: Callable[[dict], dict] | None = None             # agent start: state -> {"instruments", "totals", ...}
    investigate: Callable[[dict, list], dict] | None = None   # (question, ledger instruments) -> finding
    max_rounds: int = 2


INVESTIGABLE = {"new_without_amount", "new_without_maturity", "exit_of_unknown", "launch_not_priced"}


def build(tools: Tools, checkpointer: Any = None):
    def opening(state: EpisodeState) -> dict:
        if tools.opening is None or state.get("opening") is not None:
            return {}                                   # oracle start: the opening ledger came with the input
        t0 = time.time()
        r = tools.opening(state)
        return {"opening": r["instruments"], "opening_totals": r.get("totals", {}),
                "opening_reading": {k: v for k, v in r.items() if k not in ("instruments", "raw")},
                "timings": [{"node": "opening", "seconds": round(time.time() - t0, 2)}]}

    def timeline(state: EpisodeState) -> dict:
        t0 = time.time()
        rows = tools.timeline(state["cik"], state["window_open"], state["cutoff_date"])
        rows = drop_duplicate_documents(rows, lambda r: " ".join(tools.texts(r).values()))   # P45
        return {"candidates": rows, "timings": [{"node": "timeline", "seconds": round(time.time() - t0, 2),
                                                 "filings": len(rows)}]}

    def triage(state: EpisodeState) -> dict:
        t0 = time.time()
        kept = []
        for row in state["candidates"]:
            r = tools.triage(row, tools.texts(row))
            if r["relevant"]:
                kept.append(row | {"triage": r})
        return {"relevant": kept, "timings": [{"node": "triage", "seconds": round(time.time() - t0, 2),
                                               "kept": len(kept)}]}

    def fan_out(state: EpisodeState):
        if not state.get("relevant"):
            return "ledger"
        return [Send("read", {"filing": row}) for row in state["relevant"]]

    def read(payload: dict) -> dict:
        row = payload["filing"]
        t0 = time.time()
        r = tools.read(row)
        evs = [e | {"accession": row["accession"], "accepted": row["accepted"], "form": row["form"],
                    "filer_cik": row["cik"]} for e in r.get("events", [])]
        summary = {"accession": row["accession"], "form": row["form"], "accepted": row["accepted"],
                   "events": len(evs), "error": r.get("error"), "set_aside": len(r.get("set_aside", [])),
                   "seconds": r.get("seconds"), "cached": r.get("cached", False)}
        return {"events": evs, "readings": [summary],
                "timings": [{"node": "read", "accession": row["accession"], "seconds": round(time.time() - t0, 2)}]}

    def ledger(state: EpisodeState) -> dict:
        t0 = time.time()
        amendments = [f["amendment"] for f in state.get("findings", []) if f.get("amendment")]
        led = engine.closing_ledger(state["opening"], state.get("opening_totals", {}), state.get("events", []),
                                    state["quarter_end"], amendments)
        return {"ledger": led, "timings": [{"node": "ledger", "seconds": round(time.time() - t0, 3)}]}

    def checks(state: EpisodeState) -> dict:
        res = ck.run_checks(state["ledger"], state["quarter_end"], (state.get("opening_totals") or {}).get("total_debt"))
        return {"checks": res}

    def after_checks(state: EpisodeState):
        if tools.investigate is None or state.get("rounds", 0) >= tools.max_rounds:
            return END
        seen = {f["fingerprint"] for f in state.get("findings", [])}
        qs = [q for q in state["checks"]["questions"]
              if q["type"] in INVESTIGABLE and engine.fingerprint(q["event"]) not in seen]
        if not qs:
            return END
        return [Send("investigate", {"question": q, "instruments": state["ledger"]["instruments"]}) for q in qs]

    def investigate(payload: dict) -> dict:
        t0 = time.time()
        f = tools.investigate(payload["question"], payload["instruments"])
        return {"findings": [f], "timings": [{"node": "investigate", "seconds": round(time.time() - t0, 2)}]}

    def next_round(state: EpisodeState) -> dict:
        return {"rounds": state.get("rounds", 0) + 1}

    g = StateGraph(EpisodeState)
    g.add_node("opening", opening)
    g.add_node("timeline", timeline)
    g.add_node("triage", triage)
    g.add_node("read", read)
    g.add_node("ledger", ledger)
    g.add_node("checks", checks)
    g.add_node("investigate", investigate)
    g.add_node("next_round", next_round)
    g.add_edge(START, "opening")
    g.add_edge("opening", "timeline")
    g.add_edge("timeline", "triage")
    g.add_conditional_edges("triage", fan_out, ["read", "ledger"])
    g.add_edge("read", "ledger")
    g.add_edge("ledger", "checks")
    g.add_conditional_edges("checks", after_checks, ["investigate", END])
    g.add_edge("investigate", "next_round")
    g.add_edge("next_round", "ledger")
    return g.compile(checkpointer=checkpointer)
