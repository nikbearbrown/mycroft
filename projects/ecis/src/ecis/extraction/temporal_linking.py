"""Retrospective trend labels written onto logged signals (enrichment only)."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from ecis.db.init_db import get_connection, log_agent_action

logger = logging.getLogger(__name__)

TREND_LABELS = (
    "consecutive_raise",
    "consecutive_lower",
    "stable_maintained",
    "reversal",
    "single",
)


def label_trend(current: str, prior: str | None) -> str:
    if not prior:
        return "single"
    if current == prior == "raised":
        return "consecutive_raise"
    if current == prior == "lowered":
        return "consecutive_lower"
    if current == prior == "maintained":
        return "stable_maintained"
    return "reversal"


def assign_trends(rows: list[dict[str, Any]]) -> dict[int, str]:
    """Map signal_id → trend using the prior-quarter representative for that ticker.

    Per ticker and transcript date, the highest-confidence signal is the
    quarter representative. Every signal on that date is labelled against
    the previous date's representative. Gaps (missing quarters) are skipped.
    """
    by_ticker: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_ticker[str(row["ticker"])].append(row)

    labels: dict[int, str] = {}
    for ticker_rows in by_ticker.values():
        by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in ticker_rows:
            by_date[str(row["transcript_date"])].append(row)
        dates = sorted(by_date)
        prior_dir: str | None = None
        for day in dates:
            group = by_date[day]
            representative = max(group, key=lambda r: float(r.get("confidence_raw") or 0.0))
            trend = label_trend(str(representative["direction"]), prior_dir)
            for row in group:
                labels[int(row["signal_id"])] = trend
            prior_dir = str(representative["direction"])
    return labels


def link_trends(ticker: str | None = None) -> dict[str, Any]:
    """Write trend labels into signals.db without changing extraction fields."""
    conn = get_connection("signals")
    query = "SELECT signal_id, ticker, direction, confidence_raw, transcript_date FROM signals"
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    labels = assign_trends(rows)
    for signal_id, trend in labels.items():
        conn.execute("UPDATE signals SET trend = ? WHERE signal_id = ?", (trend, signal_id))
    conn.commit()
    conn.close()

    counts: dict[str, int] = defaultdict(int)
    for trend in labels.values():
        counts[trend] += 1
    log_agent_action(
        "temporal_linking",
        f"labelled {len(labels)} signals",
        "write_trend",
        ",".join(f"{k}={v}" for k, v in sorted(counts.items())),
    )
    logger.info("Wrote trend labels for %d signals", len(labels))
    return {"labelled": len(labels), "by_trend": dict(counts)}
