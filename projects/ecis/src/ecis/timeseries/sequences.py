"""4–8 quarter feature sequences for LSTM / GRU training."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.guidance_models.revision_features import build_revision_rows, normalize_vectors

SEQ_MIN = 4
SEQ_MAX = 8


def build_sequences(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = normalize_vectors(build_revision_rows(ticker))
    by_tkr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_tkr[row["ticker"]].append(row)
    out: list[dict[str, Any]] = []
    for tkr, items in by_tkr.items():
        items = sorted(items, key=lambda r: r["quarter"])
        for i, row in enumerate(items):
            start = max(0, i - SEQ_MAX + 1)
            window = items[start : i + 1]
            if len(window) < SEQ_MIN:
                continue
            out.append({
                "ticker": tkr,
                "quarter": row["quarter"],
                "X": [list(r["vector"]) for r in window],
                "target": row.get("target"),
                "current_direction": row.get("current_direction"),
                "next_direction": row.get("next_direction"),
                "n_steps": len(window),
            })
    return out
