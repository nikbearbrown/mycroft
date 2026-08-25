"""Human-in-the-loop pending approvals for watchdog and learning-graph proposals."""

from __future__ import annotations

import json
import logging
from typing import Any

from ecis.db.init_db import get_connection, log_agent_action

logger = logging.getLogger(__name__)


def insert_pending(
    agent_name: str,
    action_type: str,
    proposal: dict[str, Any],
    evidence: dict[str, Any] | None = None,
) -> int:
    """Store a proposal that requires human approval. Returns approval_id."""
    conn = get_connection("agents")
    cursor = conn.execute(
        """INSERT INTO pending_approvals
           (agent_name, action_type, proposal_json, evidence_json, status)
           VALUES (?, ?, ?, ?, 'pending')""",
        (
            agent_name,
            action_type,
            json.dumps(proposal),
            json.dumps(evidence or {}),
        ),
    )
    conn.commit()
    approval_id = cursor.lastrowid
    conn.close()
    log_agent_action(
        agent_name,
        json.dumps(evidence or {}),
        action_type,
        f"pending_approval:{approval_id}",
    )
    return int(approval_id)


def list_pending() -> list[dict[str, Any]]:
    conn = get_connection("agents")
    rows = conn.execute(
        """SELECT * FROM pending_approvals
           WHERE status = 'pending'
           ORDER BY created_at DESC"""
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def list_all(limit: int = 50) -> list[dict[str, Any]]:
    conn = get_connection("agents")
    rows = conn.execute(
        """SELECT * FROM pending_approvals
           ORDER BY created_at DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_approval(approval_id: int) -> dict[str, Any] | None:
    conn = get_connection("agents")
    row = conn.execute(
        "SELECT * FROM pending_approvals WHERE approval_id = ?",
        (approval_id,),
    ).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def resolve_approval(
    approval_id: int,
    approved: bool,
    note: str = "",
) -> dict[str, Any]:
    """Approve or reject a pending proposal. On approve, apply it."""
    row = get_approval(approval_id)
    if row is None:
        raise ValueError(f"Approval {approval_id} not found")
    if row["status"] != "pending":
        raise ValueError(f"Approval {approval_id} is already {row['status']}")

    status = "approved" if approved else "rejected"
    if approved:
        apply_proposal(row["proposal"])

    conn = get_connection("agents")
    conn.execute(
        """UPDATE pending_approvals
           SET status = ?, resolved_at = datetime('now'), resolution_note = ?
           WHERE approval_id = ?""",
        (status, note, approval_id),
    )
    conn.commit()
    conn.close()

    log_agent_action(
        row["agent_name"],
        json.dumps(row.get("evidence") or {}),
        f"{row['action_type']}_{status}",
        note or status,
    )
    row["status"] = status
    return row


def apply_proposal(proposal: dict[str, Any]) -> None:
    """Execute a stored proposal (weight change, threshold change, recalibrate)."""
    action = proposal.get("action_type")

    if action == "reduce_weight":
        reader = proposal.get("reader_name", "llm")
        new_weight = float(proposal.get("proposed_weight", 0.05))
        conn = get_connection("agents")
        conn.execute(
            "UPDATE reader_weights SET weight = ?, updated_at = datetime('now') WHERE reader_name = ?",
            (round(new_weight, 4), reader),
        )
        conn.commit()
        conn.close()

    elif action == "adjust_thresholds":
        proposed = proposal.get("proposed_thresholds") or {}
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

    elif action == "update_weights":
        weights = proposal.get("proposed_weights") or {}
        conn = get_connection("agents")
        for name, weight in weights.items():
            conn.execute(
                """INSERT INTO reader_weights (reader_name, weight, updated_at)
                   VALUES (?, ?, datetime('now'))
                   ON CONFLICT(reader_name) DO UPDATE SET
                       weight = excluded.weight,
                       updated_at = excluded.updated_at""",
                (name, round(float(weight), 4)),
            )
        conn.commit()
        conn.close()

    elif action == "recalibrate":
        from ecis.scoring.recalibrator import recalibrate_signals

        reader = proposal.get("reader_name")
        recalibrate_signals(method="platt", source_method=reader)

    else:
        logger.warning("Unknown proposal action_type: %s", action)


def _row_to_dict(row) -> dict[str, Any]:
    d = dict(row)
    for key in ("proposal_json", "evidence_json"):
        raw = d.pop(key, None)
        dest = "proposal" if key == "proposal_json" else "evidence"
        try:
            d[dest] = json.loads(raw) if raw else {}
        except (json.JSONDecodeError, TypeError):
            d[dest] = {}
    return d
