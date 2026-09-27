"""Calibration watchdog LangGraph: monitors reader performance and triggers corrective actions."""

from __future__ import annotations

import json
import logging
from typing import Any

from langgraph.graph import END, StateGraph

from ecis.db.init_db import get_connection
from ecis.scoring.metrics import brier_score, expected_calibration_error
from ecis.schemas.state import WatchdogState

logger = logging.getLogger(__name__)

DEFAULT_ECE_THRESHOLD = 0.10
DEFAULT_NEGATIVE_SKILL_THRESHOLD = 3
DEFAULT_UNDERPERFORMANCE_THRESHOLD = 5


def compute_rolling_metrics(state: WatchdogState) -> dict:
    """Compute rolling Brier and ECE for the reader."""
    reader = state.get("reader_name", "triangulated")
    window = state.get("rolling_window_size", 100)

    conn_s = get_connection("signals")
    rows = conn_s.execute(
        """SELECT signal_id, confidence_raw FROM signals
           WHERE source_method = ?
           ORDER BY created_at DESC LIMIT ?""",
        (reader, window),
    ).fetchall()
    conn_s.close()

    if len(rows) < 10:
        return {
            "rolling_brier": 0.0,
            "rolling_ece": 0.0,
            "rolling_skill_score": 0.0,
        }

    conn_o = get_connection("outcomes")
    confidences = []
    outcomes = []
    for row in rows:
        out = conn_o.execute(
            "SELECT correct FROM outcomes WHERE signal_id = ? AND correct IS NOT NULL",
            (row["signal_id"],),
        ).fetchone()
        if out:
            confidences.append(row["confidence_raw"])
            outcomes.append(out["correct"])
    conn_o.close()

    if len(confidences) < 10:
        return {"rolling_brier": 0.0, "rolling_ece": 0.0, "rolling_skill_score": 0.0}

    bs = brier_score(confidences, outcomes)
    ece, _ = expected_calibration_error(confidences, outcomes)
    base_rate = sum(outcomes) / len(outcomes)
    ref = base_rate * (1 - base_rate)
    ss = 1.0 - (bs / ref) if ref > 0 else 0.0

    return {
        "rolling_brier": round(bs, 6),
        "rolling_ece": round(ece, 6),
        "rolling_skill_score": round(ss, 6),
    }


def check_thresholds(state: WatchdogState) -> dict:
    """Check if metrics breach any thresholds and determine action."""
    ece = state.get("rolling_ece", 0.0)
    ss = state.get("rolling_skill_score", 0.0)
    ece_threshold = state.get("ece_threshold", DEFAULT_ECE_THRESHOLD)
    neg_threshold = state.get("negative_skill_threshold", DEFAULT_NEGATIVE_SKILL_THRESHOLD)

    consecutive_neg = state.get("consecutive_negative_skill", 0)
    if ss < 0:
        consecutive_neg += 1
    else:
        consecutive_neg = 0

    action_type = None
    action_details: dict[str, Any] = {}
    requires_approval = False

    if ece > ece_threshold:
        action_type = "recalibrate"
        action_details = {"reason": f"ECE {ece:.4f} exceeds threshold {ece_threshold:.4f}"}

    if consecutive_neg >= neg_threshold:
        action_type = "reduce_weight"
        action_details = {
            "reason": f"Negative skill score for {consecutive_neg} consecutive windows",
            "current_consecutive": consecutive_neg,
        }
        requires_approval = True

    return {
        "consecutive_negative_skill": consecutive_neg,
        "action_type": action_type,
        "action_details": action_details,
        "requires_human_approval": requires_approval,
    }


def execute_action(state: WatchdogState) -> dict:
    """Execute the corrective action if approved."""
    action = state.get("action_type")
    reader = state.get("reader_name", "triangulated")
    details = state.get("action_details", {})

    if not action:
        return {}

    if state.get("requires_human_approval") and not state.get("human_approved"):
        from ecis.db.approvals import insert_pending

        current_weight = None
        try:
            conn = get_connection("agents")
            row = conn.execute(
                "SELECT weight FROM reader_weights WHERE reader_name = ?",
                (reader,),
            ).fetchone()
            conn.close()
            if row:
                current_weight = row["weight"]
        except Exception:
            pass

        proposal = {
            "action_type": action,
            "reader_name": reader,
            "current_weight": current_weight,
            "proposed_weight": round(max(0.05, (current_weight or 0.5) * 0.8), 4)
            if action == "reduce_weight"
            else current_weight,
        }
        insert_pending(
            f"watchdog_{reader}",
            action,
            proposal,
            {"rolling_ece": state.get("rolling_ece"), "rolling_skill_score": state.get("rolling_skill_score"), **details},
        )
        _log_action(reader, action, "pending_approval", details)
        return {}

    if action == "recalibrate":
        from ecis.scoring.recalibrator import recalibrate_signals
        n = recalibrate_signals(method="platt", source_method=reader)
        _log_action(reader, action, f"recalibrated {n} signals", details)

    elif action == "reduce_weight":
        conn = get_connection("agents")
        row = conn.execute(
            "SELECT weight FROM reader_weights WHERE reader_name = ?", (reader,)
        ).fetchone()
        if row:
            new_weight = max(0.05, row["weight"] * 0.8)
            conn.execute(
                "UPDATE reader_weights SET weight = ?, updated_at = datetime('now') WHERE reader_name = ?",
                (round(new_weight, 4), reader),
            )
            conn.commit()
            _log_action(reader, action, f"weight {row['weight']:.4f} → {new_weight:.4f}", details)
        conn.close()

    return {}


def _log_action(reader: str, action: str, result: str, details: dict) -> None:
    """Log watchdog action to agent audit trail."""
    conn = get_connection("agents")
    conn.execute(
        """INSERT INTO agent_actions (agent_name, observation, action_taken, result)
           VALUES (?, ?, ?, ?)""",
        (f"watchdog_{reader}", json.dumps(details), action, result),
    )
    conn.commit()
    conn.close()


def build_watchdog_graph() -> StateGraph:
    """Build the calibration watchdog LangGraph."""
    graph = StateGraph(WatchdogState)

    graph.add_node("compute_metrics", compute_rolling_metrics)
    graph.add_node("check_thresholds", check_thresholds)
    graph.add_node("execute_action", execute_action)

    graph.set_entry_point("compute_metrics")
    graph.add_edge("compute_metrics", "check_thresholds")
    graph.add_edge("check_thresholds", "execute_action")
    graph.add_edge("execute_action", END)

    return graph


def run_watchdog(reader_name: str, window_size: int = 100) -> dict:
    """Run the watchdog for a specific reader."""
    graph = build_watchdog_graph()
    app = graph.compile()

    initial_state: WatchdogState = {
        "reader_name": reader_name,
        "rolling_window_size": window_size,
        "ece_threshold": DEFAULT_ECE_THRESHOLD,
        "negative_skill_threshold": DEFAULT_NEGATIVE_SKILL_THRESHOLD,
    }

    config = {"configurable": {"thread_id": f"watchdog_{reader_name}"}}
    final = app.invoke(initial_state, config=config)
    return dict(final)
