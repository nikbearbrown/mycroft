"""Orchestration learning graph: tune escalation thresholds from Category D misses."""

from __future__ import annotations

import json
import logging
from typing import Any

from langgraph.graph import END, StateGraph

from ecis.db.approvals import insert_pending
from ecis.db.init_db import get_connection, log_agent_action
from ecis.schemas.state import LearningState

logger = logging.getLogger(__name__)

FN_LOOSEN_RATE = 0.05
FN_TIGHTEN_RATE = 0.02
STEP_FRACTION = 0.10  # 10% threshold move per cycle
HITL_FRACTION = 0.25
NEAR_MISS_MARGIN = 0.15
MIN_D_CHUNKS = 10


def _load_thresholds() -> dict[str, float]:
    conn = get_connection("agents")
    rows = conn.execute("SELECT param_name, value FROM escalation_thresholds").fetchall()
    conn.close()
    if rows:
        return {r["param_name"]: r["value"] for r in rows}
    return {
        "finbert_confidence_min": 0.6,
        "keyword_confidence_min": 0.5,
        "escalation_agreement_threshold": 0.7,
    }


def identify_false_negatives(state: LearningState) -> dict:
    """Category D near-misses: FinBERT just below the skip threshold."""
    thresholds = _load_thresholds()
    finbert_min = thresholds.get("finbert_confidence_min", 0.6)

    conn = get_connection("agents")
    d_rows = conn.execute(
        """SELECT ticker, transcript_date, chunk_index, finbert_confidence,
                  keyword_matched, keyword_confidence
           FROM chunk_classifications WHERE category = 'D'"""
    ).fetchall()
    n_d = len(d_rows)
    n_all = conn.execute("SELECT COUNT(*) AS n FROM chunk_classifications").fetchone()["n"]
    conn.close()

    conn_s = get_connection("signals")
    n_signals = conn_s.execute("SELECT COUNT(*) AS n FROM signals").fetchone()["n"]
    conn_s.close()

    missed: list[dict] = []
    floor = max(0.0, finbert_min - NEAR_MISS_MARGIN)
    for row in d_rows:
        fb = row["finbert_confidence"] or 0.0
        kw_conf = row["keyword_confidence"] or 0.0
        if floor <= fb < finbert_min and fb > 0:
            missed.append(dict(row))
        elif kw_conf > 0 and not row["keyword_matched"]:
            missed.append(dict(row))

    n_missed = len(missed)
    expected = n_signals + n_missed
    fn_rate = (n_missed / expected) if expected else 0.0

    return {
        "current_thresholds": thresholds,
        "total_signals_expected": expected,
        "missed_signals": missed[:50],
        "missed_from_category_d": n_missed,
        "false_negative_rate": round(fn_rate, 6),
        "d_chunk_count": n_d,
        "classified_chunks": n_all,
    }


def propose_thresholds(state: LearningState) -> dict:
    """Loosen if FN > 5%, tighten if FN < 2%, HITL if move > 25%."""
    fn_rate = state.get("false_negative_rate", 0.0)
    current = dict(state.get("current_thresholds") or _load_thresholds())
    proposed = dict(current)
    d_count = state.get("d_chunk_count", 0) or 0

    if d_count < MIN_D_CHUNKS:
        return {
            "proposed_thresholds": proposed,
            "adjustment_magnitude": 0.0,
            "requires_human_approval": False,
            "skip_reason": f"Need at least {MIN_D_CHUNKS} Category D chunks (have {d_count})",
        }

    direction = 0.0
    if fn_rate > FN_LOOSEN_RATE:
        direction = -1.0  # lower bars → more LLM
    elif fn_rate < FN_TIGHTEN_RATE:
        direction = 1.0  # raise bars → skip more

    if direction == 0.0:
        return {
            "proposed_thresholds": proposed,
            "adjustment_magnitude": 0.0,
            "requires_human_approval": False,
        }

    for key in ("finbert_confidence_min", "keyword_confidence_min"):
        old = proposed.get(key, 0.5)
        new = old * (1.0 + direction * STEP_FRACTION)
        proposed[key] = round(min(0.85, max(0.30, new)), 4)

    magnitudes = []
    for key in ("finbert_confidence_min", "keyword_confidence_min"):
        old = current.get(key, 0.5)
        if old:
            magnitudes.append(abs(proposed[key] - old) / old)
    mag = max(magnitudes) if magnitudes else 0.0

    return {
        "proposed_thresholds": proposed,
        "adjustment_magnitude": round(mag, 4),
        "requires_human_approval": mag > HITL_FRACTION,
    }


def apply_or_queue(state: LearningState) -> dict:
    """Write thresholds, or queue a HITL proposal."""
    current = state.get("current_thresholds") or {}
    proposed = state.get("proposed_thresholds") or current
    mag = state.get("adjustment_magnitude", 0.0)
    fn_rate = state.get("false_negative_rate", 0.0)
    skip = state.get("skip_reason")

    if skip:
        log_agent_action("learning_graph", skip, "skip", skip)
        return {"adjustment_applied": False}

    if mag == 0.0:
        log_agent_action(
            "learning_graph",
            json.dumps({"fn_rate": fn_rate}),
            "no_change",
            "FN rate within 2–5% band",
        )
        return {"adjustment_applied": False}

    evidence = {
        "false_negative_rate": fn_rate,
        "missed_from_category_d": state.get("missed_from_category_d", 0),
        "total_signals_expected": state.get("total_signals_expected", 0),
        "adjustment_magnitude": mag,
        "current_thresholds": current,
        "proposed_thresholds": proposed,
    }

    if state.get("requires_human_approval") and not state.get("human_approved"):
        insert_pending(
            "learning_graph",
            "adjust_thresholds",
            {
                "action_type": "adjust_thresholds",
                "proposed_thresholds": proposed,
                "current_thresholds": current,
            },
            evidence,
        )
        return {"adjustment_applied": False}

    conn = get_connection("agents")
    for name, value in proposed.items():
        conn.execute(
            """INSERT INTO escalation_thresholds (param_name, value, updated_at)
               VALUES (?, ?, datetime('now'))
               ON CONFLICT(param_name) DO UPDATE SET
                   value = excluded.value,
                   updated_at = excluded.updated_at""",
            (name, float(value)),
        )
    conn.commit()
    conn.close()
    log_agent_action(
        "learning_graph",
        json.dumps(evidence),
        "adjust_thresholds",
        json.dumps(proposed),
    )
    return {"adjustment_applied": True}


def build_learning_graph() -> StateGraph:
    graph = StateGraph(LearningState)
    graph.add_node("identify_fn", identify_false_negatives)
    graph.add_node("propose", propose_thresholds)
    graph.add_node("apply", apply_or_queue)
    graph.set_entry_point("identify_fn")
    graph.add_edge("identify_fn", "propose")
    graph.add_edge("propose", "apply")
    graph.add_edge("apply", END)
    return graph


def run_learning() -> dict:
    """Run one learning-graph cycle."""
    app = build_learning_graph().compile()
    initial: LearningState = {
        "missed_signals": [],
        "requires_human_approval": False,
        "adjustment_applied": False,
    }
    final = app.invoke(initial, config={"configurable": {"thread_id": "learning"}})
    return dict(final)
