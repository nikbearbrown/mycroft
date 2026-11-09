"""Additive feature attributions. SHAP TreeExplainer stays off unless RELIABILITY_LOAD_SHAP=1."""

from __future__ import annotations

import os
from typing import Any

from ecis.guidance_models.revision_features import FEATURE_NAMES, build_revision_rows, normalize_vectors
from ecis.reliability.calibrate import _sigmoid

_LOAD = os.getenv("RELIABILITY_LOAD_SHAP", "").lower() in {"1", "true", "yes"}


def linear_shap(vector: list[float], weights: list[float], means: list[float], intercept: float = 0.0) -> list[float]:
    """phi_i = w_i * (x_i - mean_i); sums to the centered logit."""
    return [w * (x - m) for w, x, m in zip(weights, vector, means)]


def _numpy_weights(X: list[list[float]], y: list[float]) -> tuple[list[float], float]:
    if not X:
        return [0.0] * len(FEATURE_NAMES), 0.0
    dims = len(X[0])
    w = [0.0] * dims
    b = 0.0
    n = max(len(X), 1)
    for _ in range(80):
        gw = [0.0] * dims
        gb = 0.0
        for row, target in zip(X, y):
            z = b + sum(wj * xj for wj, xj in zip(w, row))
            err = _sigmoid(z) - target
            gb += err
            for j in range(dims):
                gw[j] += err * row[j]
        b -= 0.2 * gb / n
        w = [wj - 0.2 * gj / n for wj, gj in zip(w, gw)]
    return w, b


def _tree_shap(vector: list[float], model: Any) -> list[float] | None:
    if not _LOAD:
        return None
    try:
        import shap  # type: ignore
        explainer = shap.TreeExplainer(model)
        values = explainer.shap_values(vector)
        if isinstance(values, list):
            values = values[-1]
        return [float(v) for v in values]
    except Exception:
        return None


def explain_revisions(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = [r for r in normalize_vectors(build_revision_rows(ticker)) if r.get("vector")]
    labelled = [r for r in rows if r.get("target") is not None]
    if len(labelled) < 2:
        return []
    X = [list(r["vector"]) for r in labelled]
    y = [float(r["target"]) for r in labelled]
    weights, intercept = _numpy_weights(X, y)
    dims = len(FEATURE_NAMES)
    means = [sum(row[j] for row in X) / len(X) for j in range(dims)]
    out = []
    for row in rows:
        vec = list(row["vector"])
        phis = _tree_shap(vec, None) or linear_shap(vec, weights, means, intercept)
        ranked = sorted(zip(FEATURE_NAMES, phis), key=lambda p: abs(p[1]), reverse=True)
        out.append({
            "ticker": row.get("ticker"),
            "quarter": row.get("quarter"),
            "model_name": "ensemble",
            "probability": _sigmoid(intercept + sum(w * x for w, x in zip(weights, vec))),
            "contributions": [{"feature": n, "shap": v} for n, v in ranked],
            "top_features": [n for n, _ in ranked[:3]],
            "shap_sum": sum(phis),
            "method": "linear" if not _LOAD else "shap",
        })
    return out
