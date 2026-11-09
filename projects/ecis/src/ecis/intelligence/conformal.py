"""Split conformal intervals around revision probabilities. Target coverage 90%."""

from __future__ import annotations

from typing import Any

from ecis.db.init_db import get_connection

TARGET_COVERAGE = 0.90


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    xs = sorted(values)
    idx = min(len(xs) - 1, max(0, int(q * (len(xs) + 1)) - 1))
    return xs[idx]


def conformal_intervals(ticker: str | None = None) -> list[dict[str, Any]]:
    """Interval [p − q, p + q] from |actual − p| residuals on a later-quarter holdout."""
    try:
        conn = get_connection("agents")
        preds = [dict(r) for r in conn.execute(
            "SELECT ticker, quarter, model_name, probability, actual FROM revision_predictions"
        ).fetchall()]
        conn.close()
    except Exception:
        return []
    if ticker:
        preds = [p for p in preds if (p.get("ticker") or "").upper() == ticker.upper()]
    labelled = [p for p in preds if p.get("actual") is not None and p.get("probability") is not None]
    if len(labelled) < 4:
        return []
    quarters = sorted({p.get("quarter") or "" for p in labelled})
    hold = quarters[-1]
    cal = [p for p in labelled if p.get("quarter") == hold]
    rest = [p for p in labelled if p.get("quarter") != hold] or cal
    if not cal:
        cal = rest[-max(1, len(rest) // 4):]
    residuals = [abs(float(p["actual"]) - float(p["probability"])) for p in cal]
    q = _quantile(residuals, TARGET_COVERAGE)
    out = []
    for p in labelled + [r for r in preds if r.get("actual") is None]:
        prob = float(p.get("probability") or 0)
        lo = max(0.0, prob - q)
        hi = min(1.0, prob + q)
        out.append({
            "ticker": (p.get("ticker") or "").upper(),
            "quarter": p.get("quarter"),
            "model_name": p.get("model_name"),
            "probability": prob,
            "lower": lo,
            "upper": hi,
            "width": hi - lo,
            "coverage_target": TARGET_COVERAGE,
            "nonconformity": q,
        })
    return out
