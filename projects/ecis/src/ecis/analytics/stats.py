"""Lightweight stats used by sector and impact analytics (stdlib only)."""

from __future__ import annotations

import math
from typing import Sequence


def _clean(xs: Sequence[float | None]) -> list[float]:
    return [float(x) for x in xs if x is not None and math.isfinite(float(x))]


def mean(xs: Sequence[float | None]) -> float | None:
    vals = _clean(xs)
    if not vals:
        return None
    return sum(vals) / len(vals)


def median(xs: Sequence[float | None]) -> float | None:
    vals = sorted(_clean(xs))
    if not vals:
        return None
    n = len(vals)
    mid = n // 2
    if n % 2:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2.0


def stdev(xs: Sequence[float | None], *, sample: bool = True) -> float | None:
    vals = _clean(xs)
    n = len(vals)
    if n < 2:
        return None
    mu = sum(vals) / n
    denom = n - 1 if sample else n
    var = sum((v - mu) ** 2 for v in vals) / denom
    return math.sqrt(var)


def zscore(value: float | None, xs: Sequence[float | None]) -> float | None:
    if value is None:
        return None
    mu = mean(xs)
    sd = stdev(xs)
    if mu is None or sd is None or sd == 0:
        return None
    return (float(value) - mu) / sd


def pearson(xs: Sequence[float | None], ys: Sequence[float | None]) -> float | None:
    pairs = [
        (float(x), float(y))
        for x, y in zip(xs, ys)
        if x is not None and y is not None and math.isfinite(float(x)) and math.isfinite(float(y))
    ]
    n = len(pairs)
    if n < 3:
        return None
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    num = sum((p[0] - mx) * (p[1] - my) for p in pairs)
    dx = math.sqrt(sum((p[0] - mx) ** 2 for p in pairs))
    dy = math.sqrt(sum((p[1] - my) ** 2 for p in pairs))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def spearman(xs: Sequence[float | None], ys: Sequence[float | None]) -> float | None:
    pairs = [
        (float(x), float(y))
        for x, y in zip(xs, ys)
        if x is not None and y is not None and math.isfinite(float(x)) and math.isfinite(float(y))
    ]
    if len(pairs) < 3:
        return None

    def _ranks(vals: list[float]) -> list[float]:
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[order[k]] = avg
            i = j + 1
        return ranks

    rx = _ranks([p[0] for p in pairs])
    ry = _ranks([p[1] for p in pairs])
    return pearson(rx, ry)


def weighted_mean(xs: Sequence[float | None], weights: Sequence[float | None]) -> float | None:
    total_w = 0.0
    acc = 0.0
    for x, w in zip(xs, weights):
        if x is None or w is None or not math.isfinite(float(x)) or not math.isfinite(float(w)):
            continue
        if float(w) <= 0:
            continue
        acc += float(x) * float(w)
        total_w += float(w)
    if total_w == 0:
        return None
    return acc / total_w
