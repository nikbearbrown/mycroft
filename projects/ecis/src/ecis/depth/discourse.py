"""Narrative ordering from sentiment trajectory in prepared remarks."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.guidance_models.finbert_ensemble import lexicon_polarity
from ecis.analytics.features import quarter_key
from ecis.db.init_db import get_connection

PATTERNS = ("front_load", "bury", "progressive", "deflect", "flat")


def classify_trajectory(scores: list[float]) -> str:
    if len(scores) < 3:
        return "flat"
    first, mid, last = scores[0], scores[len(scores) // 2], scores[-1]
    if first < -0.1 and last > 0.1:
        return "front_load"
    if mid < min(first, last) - 0.1:
        return "bury"
    if last > mid > first:
        return "progressive"
    if first < 0 and abs(last) < 0.08:
        return "deflect"
    return "flat"


def analyse_discourse(ticker: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection("signals")
    query = """
        SELECT ticker, transcript_date, section_label, supporting_quote, chunk_index
        FROM signals
    """
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if (row.get("section_label") or "") not in {"prepared_remarks", "prepared", ""}:
            continue
        buckets[((row["ticker"] or "").upper(), (row["transcript_date"] or "")[:10])].append(row)

    hist: dict[str, list[str]] = defaultdict(list)
    out = []
    for (tkr, day), items in sorted(buckets.items()):
        items = sorted(items, key=lambda r: int(r.get("chunk_index") or 0))
        scores = [lexicon_polarity(r.get("supporting_quote") or "") for r in items]
        pattern = classify_trajectory(scores)
        unusual = pattern in {"front_load", "bury", "deflect"} and hist[tkr].count(pattern) == 0 and hist[tkr]
        hist[tkr].append(pattern)
        out.append({
            "ticker": tkr,
            "transcript_date": day,
            "quarter": quarter_key(day),
            "pattern": pattern,
            "n_chunks": len(items),
            "start_polarity": scores[0] if scores else None,
            "end_polarity": scores[-1] if scores else None,
            "flag": "unusual" if unusual else "normal",
        })
    return out
