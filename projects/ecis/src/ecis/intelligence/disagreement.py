"""Six-model disagreement on the same ticker-quarter revision call."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.db.init_db import get_connection


def ensemble_disagreement(ticker: str | None = None) -> list[dict[str, Any]]:
    try:
        conn = get_connection("agents")
        query = "SELECT ticker, quarter, model_name, probability, predicted FROM revision_predictions"
        params: list[str] = []
        if ticker:
            query += " WHERE ticker = ?"
            params.append(ticker.upper())
        rows = [dict(r) for r in conn.execute(query, params).fetchall()]
        conn.close()
    except Exception:
        return []
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[((row.get("ticker") or "").upper(), row.get("quarter") or "")].append(row)
    out = []
    for (tkr, q), items in sorted(buckets.items()):
        probs = [float(i.get("probability") or 0) for i in items]
        if len(probs) < 2:
            continue
        mean = sum(probs) / len(probs)
        var = sum((p - mean) ** 2 for p in probs) / max(len(probs) - 1, 1)
        pair_max = 0.0
        for i, a in enumerate(probs):
            for b in probs[i + 1 :]:
                pair_max = max(pair_max, abs(a - b))
        votes = [int(i.get("predicted") or (1 if float(i.get("probability") or 0) >= 0.5 else 0)) for i in items]
        majority = max(set(votes), key=votes.count)
        n_majority = votes.count(majority)
        out.append({
            "ticker": tkr,
            "quarter": q,
            "n_models": len(probs),
            "stdev": var ** 0.5,
            "max_pairwise": pair_max,
            "n_majority": n_majority,
            "majority": majority,
            "disagreement": var ** 0.5,
        })
    return out
