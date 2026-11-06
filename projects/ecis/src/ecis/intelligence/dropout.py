"""Monte Carlo dropout stand-in: noisy re-evaluations of stored revision probabilities."""

from __future__ import annotations

import math
import os
import random
from typing import Any

from ecis.db.init_db import get_connection

N_DRAWS = int(os.getenv("MC_DROPOUT_DRAWS", "50"))
NOISE = float(os.getenv("MC_DROPOUT_NOISE", "0.08"))


def _entropy(p: float) -> float:
    p = min(1 - 1e-9, max(1e-9, p))
    return -(p * math.log(p) + (1 - p) * math.log(1 - p))


def mc_dropout(ticker: str | None = None, rng: random.Random | None = None) -> list[dict[str, Any]]:
    rng = rng or random.Random(7)
    try:
        conn = get_connection("agents")
        query = "SELECT ticker, quarter, model_name, probability FROM revision_predictions WHERE model_name = 'mlp'"
        params: list[str] = []
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker.upper())
        rows = [dict(r) for r in conn.execute(query, params).fetchall()]
        if not rows:
            query = "SELECT ticker, quarter, model_name, probability FROM revision_predictions"
            params = []
            if ticker:
                query += " WHERE ticker = ?"
                params.append(ticker.upper())
            rows = [dict(r) for r in conn.execute(query, params).fetchall()]
        conn.close()
    except Exception:
        return []
    out = []
    for row in rows:
        p0 = float(row.get("probability") or 0)
        draws = []
        for _ in range(max(N_DRAWS, 5)):
            draws.append(min(1.0, max(0.0, p0 + rng.gauss(0, NOISE))))
        mean = sum(draws) / len(draws)
        var = sum((d - mean) ** 2 for d in draws) / max(len(draws) - 1, 1)
        out.append({
            "ticker": (row.get("ticker") or "").upper(),
            "quarter": row.get("quarter"),
            "model_name": row.get("model_name") or "mlp",
            "mean": mean,
            "variance": var,
            "stdev": var ** 0.5,
            "entropy": _entropy(mean),
            "mutual_info": max(0.0, _entropy(p0) - _entropy(mean)),
            "n_draws": len(draws),
        })
    return out
