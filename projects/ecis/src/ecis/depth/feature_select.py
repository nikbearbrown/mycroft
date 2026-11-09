"""RFE-style drop, permutation importance, and LASSO-like shrink on revision features."""

from __future__ import annotations

from typing import Any

from ecis.guidance_models.revision_features import FEATURE_NAMES, build_revision_rows
from ecis.analytics.stats import pearson

REDUNDANT = 0.85


def _matrix(ticker: str | None = None) -> tuple[list[str], list[list[float]], list[float]]:
    rows = [r for r in build_revision_rows(ticker) if r.get("target") is not None]
    names = list(FEATURE_NAMES)
    X = [list(r["vector"]) for r in rows]
    y = [float(r["target"]) for r in rows]
    return names, X, y


def _col(X: list[list[float]], j: int) -> list[float]:
    return [row[j] for row in X]


def _lasso_weights(X: list[list[float]], y: list[float], l1: float = 0.08) -> list[float]:
    if not X:
        return []
    dims = len(X[0])
    w = [0.0] * dims
    for _ in range(40):
        for j in range(dims):
            resid = []
            xs = []
            for i, row in enumerate(X):
                pred = sum(row[k] * w[k] for k in range(dims) if k != j)
                resid.append(y[i] - pred)
                xs.append(row[j])
            r = pearson(xs, resid)
            step = 0.0 if r is None else r
            val = w[j] + 0.2 * step
            if val > l1:
                w[j] = val - l1
            elif val < -l1:
                w[j] = val + l1
            else:
                w[j] = 0.0
    return w


def audit_features(ticker: str | None = None) -> list[dict[str, Any]]:
    names, X, y = _matrix(ticker)
    if len(y) < 3:
        return [{"feature": n, "recommendation": "monitor", "marginal": None, "redundant_with": None} for n in names]

    base = [pearson(_col(X, j), y) for j in range(len(names))]
    abs_base = [abs(v) if v is not None else 0.0 for v in base]

    rfe_rank = sorted(range(len(names)), key=lambda j: abs_base[j])
    perm_drop = []
    for j in range(len(names)):
        shuffled = list(_col(X, j))
        shuffled = shuffled[1:] + shuffled[:1]
        r = pearson(shuffled, y)
        drop = abs_base[j] - (abs(r) if r is not None else 0.0)
        perm_drop.append(drop)
    lasso = _lasso_weights(X, y)
    abs_lasso = [abs(v) for v in lasso]

    def bottom10(scores: list[float]) -> set[int]:
        order = sorted(range(len(scores)), key=lambda i: scores[i])
        k = max(1, len(scores) // 10)
        return set(order[:k])

    drop_idx = bottom10(abs_base) & bottom10(perm_drop) & bottom10(abs_lasso)

    redundant: dict[int, str] = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            r = pearson(_col(X, i), _col(X, j))
            if r is not None and abs(r) >= REDUNDANT:
                loser = i if abs_base[i] < abs_base[j] else j
                redundant[loser] = names[j if loser == i else i]

    out = []
    for j, name in enumerate(names):
        rec = "drop" if j in drop_idx else "monitor" if j in redundant or abs_base[j] < 0.05 else "keep"
        out.append({
            "feature": name,
            "marginal": base[j],
            "permutation_drop": perm_drop[j],
            "lasso_weight": lasso[j],
            "rfe_rank": rfe_rank.index(j) + 1,
            "redundant_with": redundant.get(j),
            "recommendation": rec,
        })
    return sorted(out, key=lambda r: (-(abs(r["marginal"]) if r["marginal"] is not None else 0), r["feature"]))
