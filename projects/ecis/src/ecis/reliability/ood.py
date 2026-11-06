"""Mahalanobis distance and a numpy isolation-forest stand-in."""

from __future__ import annotations

import math
import os
import random
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.guidance_models.revision_features import build_revision_rows, normalize_vectors

OOD_THRESHOLD = float(os.getenv("OOD_MAHALANOBIS_THRESHOLD", "3.0"))
PENALTY_MAX = float(os.getenv("OOD_CONFIDENCE_PENALTY", "0.35"))


def _mean(cols: list[list[float]]) -> list[float]:
    n = max(len(cols), 1)
    dims = len(cols[0]) if cols else 0
    return [sum(row[j] for row in cols) / n for j in range(dims)]


def _cov_inv(cols: list[list[float]], mean: list[float]) -> list[list[float]] | None:
    n = len(cols)
    d = len(mean)
    if n < d + 1 or d == 0:
        return None
    cov = [[0.0] * d for _ in range(d)]
    for row in cols:
        delta = [row[j] - mean[j] for j in range(d)]
        for i in range(d):
            for j in range(d):
                cov[i][j] += delta[i] * delta[j]
    scale = 1.0 / max(n - 1, 1)
    for i in range(d):
        for j in range(d):
            cov[i][j] *= scale
        cov[i][i] += 1e-4
    return _invert(cov)


def _invert(matrix: list[list[float]]) -> list[list[float]] | None:
    n = len(matrix)
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(matrix)]
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(aug[r][i]))
        if abs(aug[pivot][i]) < 1e-12:
            return None
        aug[i], aug[pivot] = aug[pivot], aug[i]
        div = aug[i][i]
        aug[i] = [v / div for v in aug[i]]
        for r in range(n):
            if r == i:
                continue
            factor = aug[r][i]
            aug[r] = [a - factor * b for a, b in zip(aug[r], aug[i])]
    return [row[n:] for row in aug]


def mahalanobis(vector: list[float], mean: list[float], precision: list[list[float]] | None) -> float:
    if not precision:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vector, mean)))
    delta = [a - b for a, b in zip(vector, mean)]
    mid = [sum(precision[i][j] * delta[j] for j in range(len(delta))) for i in range(len(delta))]
    return math.sqrt(max(sum(d * m for d, m in zip(delta, mid)), 0.0))


def isolation_score(vector: list[float], cloud: list[list[float]], trees: int = 16, rng: random.Random | None = None) -> float:
    rng = rng or random.Random(17)
    if len(cloud) < 4:
        return 0.0
    depths = []
    dims = len(vector)
    for _ in range(trees):
        sample = [cloud[rng.randrange(len(cloud))] for _ in range(min(len(cloud), 16))]
        depth = 0
        points = sample
        while len(points) > 1 and depth < 8:
            axis = rng.randrange(dims)
            lo = min(p[axis] for p in points)
            hi = max(p[axis] for p in points)
            if hi <= lo:
                break
            cut = lo + (hi - lo) * rng.random()
            side = vector[axis] <= cut
            points = [p for p in points if (p[axis] <= cut) == side]
            depth += 1
        depths.append(depth)
    avg = sum(depths) / len(depths)
    return max(0.0, 1.0 - avg / 8.0)


def penalty_for(score: float) -> float:
    if score < OOD_THRESHOLD * 0.6:
        return 0.0
    if score < OOD_THRESHOLD:
        return PENALTY_MAX * 0.35
    excess = min((score - OOD_THRESHOLD) / max(OOD_THRESHOLD, 1e-6), 2.0)
    return min(PENALTY_MAX, PENALTY_MAX * (0.5 + 0.25 * excess))


def detect_ood(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = [r for r in normalize_vectors(build_revision_rows(ticker)) if r.get("vector")]
    labelled = [r for r in rows if r.get("target") is not None]
    cloud = [list(r["vector"]) for r in (labelled or rows)]
    if len(cloud) < 2:
        return []
    mu = _mean(cloud)
    precision = _cov_inv(cloud, mu)
    out = []
    for row in rows:
        vec = list(row["vector"])
        maha = mahalanobis(vec, mu, precision)
        iso = isolation_score(vec, cloud)
        score = max(maha, iso * 4.0)
        flag = "ood" if score >= OOD_THRESHOLD or iso >= 0.7 else "in_distribution"
        penalty = penalty_for(score) if flag == "ood" else 0.0
        out.append({
            "ticker": row.get("ticker"),
            "transcript_date": row.get("transcript_date"),
            "quarter": row.get("quarter") or quarter_key(row.get("transcript_date")),
            "mahalanobis": maha,
            "isolation": iso,
            "score": score,
            "flag": flag,
            "penalty": penalty,
            "tier": "extreme" if penalty >= PENALTY_MAX * 0.8 else "marginal" if penalty > 0 else "ok",
        })
    return out
