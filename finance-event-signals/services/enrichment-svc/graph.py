"""The enrichment agent as a LangGraph state machine.

    classify -> extract (xN) -> check_consistency --agree--> verify --ok--> emit
                                              |                    |
                                              +--disagree--> withhold <--not ok--+

`emit` produces a signal with status "pending_review" (the human gate is downstream).
`withhold` produces a signal with status "withheld" and a reason — the agent looked and
declined. Nothing here decides or acts.
"""

from __future__ import annotations

import os
from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

# 8-K item code -> event_type, most-material first (priority order for multi-item filings)
ITEM_MAP: list[tuple[str, str]] = [
    ("1.03", "bankruptcy"),
    ("4.02", "restatement"),
    ("2.06", "impairment"),
    ("3.01", "delisting"),
    ("2.04", "debt_acceleration"),
    ("2.05", "restructuring_costs"),
    ("2.01", "acquisition_disposition"),
    ("2.02", "earnings"),
    ("5.01", "change_of_control"),
    ("5.02", "exec_change"),
    ("4.01", "auditor_change"),
    ("1.02", "material_agreement_termination"),
    ("1.01", "material_agreement"),
    ("2.03", "debt_obligation"),
    ("7.01", "reg_fd"),
    ("8.01", "other_event"),
    ("5.03", "charter_amendment"),
]

CONF_THRESHOLD = float(os.getenv("ENRICH_CONF_THRESHOLD", "0.5"))
N_PASSES = int(os.getenv("ENRICH_SELF_CONSISTENCY_PASSES", "2"))
TEMPS = [0.2, 0.6, 0.9]


class State(TypedDict, total=False):
    event: dict
    event_type: str
    items: list[str]
    extractions: list[dict]
    signal: Optional[dict]
    withheld_reason: Optional[str]


def _classify(state: State) -> State:
    ev = state["event"]
    items = ev.get("items") or []
    et = "other_event"
    for code, name in ITEM_MAP:
        if any(str(i).strip().startswith(code) for i in items):
            et = name
            break
    else:
        # no usable item codes — fall back to a coarse title keyword
        t = (ev.get("title") or "").lower()
        if "earnings" in t or "results of operations" in t:
            et = "earnings"
        elif "bankrupt" in t:
            et = "bankruptcy"
    return {"event_type": et, "items": items, "extractions": []}


def _extract(llm):
    def node(state: State) -> State:
        ev = state["event"]
        passes = []
        for i in range(max(1, N_PASSES)):
            temp = TEMPS[i % len(TEMPS)]
            passes.append(
                llm.extract(state["event_type"], ev.get("title", ""), state["items"], temperature=temp)
            )
        return {"extractions": passes}

    return node


def _check_consistency(state: State) -> State:
    dirs = {e["direction"] for e in state["extractions"]}
    if len(dirs) > 1:
        return {"withheld_reason": f"self-consistency: passes disagreed ({sorted(dirs)})"}
    return {"withheld_reason": None}  # LangGraph nodes must return a non-empty delta


def _route_after_consistency(state: State) -> str:
    return "withhold" if state.get("withheld_reason") else "verify"


def _verify(llm):
    def node(state: State) -> State:
        agreed = state["extractions"][0]
        ev = state["event"]
        if agreed["direction"] == "unclear":
            return {"withheld_reason": "extraction: direction unclear from filing metadata"}
        if agreed["confidence"] < CONF_THRESHOLD:
            return {"withheld_reason": f"extraction: confidence {agreed['confidence']:.2f} < {CONF_THRESHOLD}"}
        crit = llm.critique(state["event_type"], ev.get("title", ""), agreed)
        if not crit["ok"]:
            return {"withheld_reason": f"verify: {crit['reason']}"}
        return {"withheld_reason": None}

    return node


def _route_after_verify(state: State) -> str:
    return "withhold" if state.get("withheld_reason") else "emit"


def _emit(state: State, llm) -> State:
    agreed = state["extractions"][0]
    conf = sum(e["confidence"] for e in state["extractions"]) / len(state["extractions"])
    # confidence_basis: 'heuristic' = a rule-table constant (deterministic provider),
    # 'model_estimate' = an LLM's own guess. NEITHER is calibrated against outcomes
    # until the Week-4 grader. Do not read it as a probability.
    basis = "heuristic" if getattr(llm, "provider", "") == "deterministic" else "model_estimate"
    return {
        "signal": {
            "status": "pending_review",
            "event_type": state["event_type"],
            "direction": agreed["direction"],
            "magnitude": agreed["magnitude"],
            "confidence": round(conf, 3),
            "confidence_basis": basis,
            "rationale": agreed["rationale"],
            "passes": len(state["extractions"]),
        }
    }


def _withhold(state: State) -> State:
    return {
        "signal": {
            "status": "withheld",
            "event_type": state["event_type"],
            "withheld_reason": state.get("withheld_reason") or "withheld",
        }
    }


def build_graph(llm):
    g = StateGraph(State)
    g.add_node("classify", _classify)
    g.add_node("extract", _extract(llm))
    g.add_node("check_consistency", _check_consistency)
    g.add_node("verify", _verify(llm))
    g.add_node("emit", lambda s: _emit(s, llm))
    g.add_node("withhold", _withhold)

    g.add_edge(START, "classify")
    g.add_edge("classify", "extract")
    g.add_edge("extract", "check_consistency")
    g.add_conditional_edges("check_consistency", _route_after_consistency,
                            {"verify": "verify", "withhold": "withhold"})
    g.add_conditional_edges("verify", _route_after_verify,
                            {"emit": "emit", "withhold": "withhold"})
    g.add_edge("emit", END)
    g.add_edge("withhold", END)
    return g.compile()
