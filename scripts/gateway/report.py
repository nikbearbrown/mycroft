"""Aggregate logbook attempts into request-level cost and latency."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Iterator

SUCCESS_OUTCOMES = frozenset({"ok"})


def read_records(path: str | Path) -> list[dict[str, Any]]:
    # A malformed line raises rather than being dropped: a log you cannot
    # fully parse is not a smaller log, it is an unreliable one.
    records: list[dict[str, Any]] = []
    text = Path(path).read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno} is not valid JSON: {exc}") from exc
    return records


def by_request(records: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["request_id"]].append(record)
    for attempts in grouped.values():
        attempts.sort(key=lambda r: r["attempt_no"])
    return dict(grouped)


def request_totals(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    # Cost and latency SUM across attempts -- an escalated request really
    # did cost both calls, and really did make the caller wait for both.
    totals: list[dict[str, Any]] = []
    for request_id, attempts in by_request(records).items():
        final = attempts[-1]
        totals.append({
            "request_id": request_id,
            "task_type": final["task_type"],
            "caller": final["caller"],
            "attempts": len(attempts),
            "escalated": len(attempts) > 1,
            "first_tier": attempts[0]["tier"],
            "final_tier": final["tier"],
            "first_model": attempts[0]["model"],
            "final_model": final["model"],
            "total_cost_usd": sum(a["cost_usd"] for a in attempts),
            "total_latency_ms": sum(a["latency_ms"] for a in attempts),
            "final_outcome": final["outcome"],
            "succeeded": final["outcome"] in SUCCESS_OUTCOMES,
            "price_table_versions": sorted({a["price_table_version"] for a in attempts}),
        })
    totals.sort(key=lambda r: r["request_id"])
    return totals


def percentile(values: list[float], pct: float) -> float:
    # Nearest-rank, so a reported p95 is a latency some request actually
    # experienced rather than a synthesised value.
    if not values:
        raise ValueError("percentile of an empty list is undefined")
    if not 0 < pct <= 100:
        raise ValueError(f"pct must be in (0, 100], got {pct}")
    ordered = sorted(values)
    rank = max(1, -(-len(ordered) * int(pct) // 100))
    return float(ordered[rank - 1])


def summary(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """The Sprint 7 baseline numbers, computed per request."""
    totals = request_totals(records)
    if not totals:
        return {"requests": 0, "attempts": 0, "total_cost_usd": 0.0,
                "mean_cost_per_request_usd": 0.0, "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0, "escalation_rate": 0.0,
                "failure_rate": 0.0}

    latencies = [float(t["total_latency_ms"]) for t in totals]
    escalated = sum(1 for t in totals if t["escalated"])
    failed = sum(1 for t in totals if not t["succeeded"])
    total_cost = sum(t["total_cost_usd"] for t in totals)

    return {
        "requests": len(totals),
        "attempts": sum(t["attempts"] for t in totals),
        "total_cost_usd": total_cost,
        "mean_cost_per_request_usd": total_cost / len(totals),
        "p50_latency_ms": percentile(latencies, 50),
        "p95_latency_ms": percentile(latencies, 95),
        "escalation_rate": escalated / len(totals),
        "failure_rate": failed / len(totals),
    }


def naive_mean_cost_per_attempt(records: Iterable[dict[str, Any]]) -> float:
    """DO NOT USE FOR REPORTING. Averages cost across attempt rows.

    Kept only as the counter-example the test suite pins down. On any log
    containing an escalation this returns less than the true cost per
    request, and the gap widens as escalation gets more common -- so a
    router that escalates more looks cheaper. Use summary() instead.
    """
    rows = list(records)
    if not rows:
        return 0.0
    return sum(r["cost_usd"] for r in rows) / len(rows)


def iter_provenance(records: Iterable[dict[str, Any]]) -> Iterator[tuple[str, str, str]]:
    """Answer 'which model produced this claim?' for each request."""
    for total in request_totals(records):
        yield total["request_id"], total["caller"], total["final_model"]