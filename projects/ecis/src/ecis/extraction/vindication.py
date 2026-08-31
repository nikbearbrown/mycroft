"""Aggregate conflict-resolution vindications and update triangulator weights."""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from typing import Any

from ecis.db.init_db import get_connection, log_agent_action

logger = logging.getLogger(__name__)

MIN_CONFLICTS = 5
ADJUSTMENT_RATE = 0.05
STRUCTURAL_CHANGE_FRACTION = 0.50  # HITL if a weight would move by more than this


def aggregate_vindications(
    *,
    min_conflicts: int = MIN_CONFLICTS,
    adjustment_rate: float = ADJUSTMENT_RATE,
    apply: bool = True,
) -> dict[str, Any]:
    """Compute per-reader win rates and optionally write updated weights.

    Routine weight tweaks apply automatically. A proposed change that would
    move any reader weight by more than 50% is returned without applying so
    a human can approve it.
    """
    conn = get_connection("agents")
    rows = conn.execute(
        "SELECT vindicated_reader, defeated_reader FROM vindication_records"
    ).fetchall()
    weight_rows = conn.execute("SELECT reader_name, weight FROM reader_weights").fetchall()
    conn.close()

    current_weights = {r["reader_name"]: r["weight"] for r in weight_rows}
    wins: dict[str, int] = defaultdict(int)
    losses: dict[str, int] = defaultdict(int)

    for row in rows:
        vindicated = (row["vindicated_reader"] or "unknown").lower()
        defeated = (row["defeated_reader"] or "unknown").lower()
        if vindicated not in ("unknown", ""):
            wins[vindicated] += 1
        if defeated not in ("unknown", ""):
            losses[defeated] += 1

    total = len(rows)
    rates: dict[str, dict[str, Any]] = {}
    for reader in sorted(set(list(wins) + list(losses) + ["keyword", "finbert", "llm"])):
        w = wins[reader]
        l = losses[reader]
        n = w + l
        rates[reader] = {
            "wins": w,
            "losses": l,
            "conflicts": n,
            "win_rate": round(w / n, 4) if n else None,
        }

    result: dict[str, Any] = {
        "total_conflicts": total,
        "rates": rates,
        "current_weights": current_weights,
        "proposed_weights": dict(current_weights),
        "applied": False,
        "requires_human_approval": False,
        "reason": "",
    }

    if total < min_conflicts:
        result["reason"] = f"Need at least {min_conflicts} conflicts (have {total})"
        log_agent_action(
            "vindication_aggregation",
            json.dumps({"total_conflicts": total}),
            "skip",
            result["reason"],
        )
        return result

    proposed = dict(current_weights)
    for reader, stats in rates.items():
        if reader not in proposed or reader == "agreement":
            continue
        if stats["conflicts"] < min_conflicts:
            continue
        win_rate = stats["win_rate"]
        if win_rate is None:
            continue
        delta = 0.0
        if win_rate >= 0.60:
            delta = adjustment_rate
        elif win_rate <= 0.40:
            delta = -adjustment_rate
        if delta:
            proposed[reader] = max(0.05, min(0.80, proposed[reader] + delta))

    core = ["keyword", "finbert", "llm"]
    core_sum = sum(proposed.get(k, 0.0) for k in core)
    target = 0.85
    if core_sum > 0:
        for k in core:
            proposed[k] = round(proposed.get(k, 0.0) / core_sum * target, 4)

    result["proposed_weights"] = proposed

    max_frac = 0.0
    for k in core:
        old = current_weights.get(k, 0.0)
        new = proposed.get(k, 0.0)
        if old > 0:
            max_frac = max(max_frac, abs(new - old) / old)

    if max_frac > STRUCTURAL_CHANGE_FRACTION:
        result["requires_human_approval"] = True
        result["reason"] = f"Weight move {max_frac:.0%} exceeds 50% structural threshold"
        if apply:
            from ecis.db.approvals import insert_pending

            insert_pending(
                "vindication_aggregation",
                "update_weights",
                {
                    "action_type": "update_weights",
                    "proposed_weights": proposed,
                    "current_weights": current_weights,
                },
                {"rates": rates, "max_fractional_change": max_frac},
            )
        log_agent_action(
            "vindication_aggregation",
            json.dumps({"rates": rates}),
            "propose_weight_update",
            result["reason"],
        )
        return result

    if apply:
        _write_weights(proposed)
        result["applied"] = True
        result["reason"] = "Weights updated from vindication rates"
        log_agent_action(
            "vindication_aggregation",
            json.dumps({"rates": rates}),
            "update_weights",
            json.dumps(proposed),
        )

    return result


def _write_weights(weights: dict[str, float]) -> None:
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
