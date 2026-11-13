from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from ecis.analytics.sector_sentiment import sector_mood_index
from ecis.db.ticker_registry import get_ticker

STATES = ("bearish", "transitional", "bullish")


def _observations(ticker: str | None = None) -> dict[str, list[dict[str, Any]]]:
    rows = sector_mood_index(ticker)
    if ticker:
        sector = "AI"
        try:
            rec = get_ticker(ticker.upper())
            if rec:
                sector = rec.get("sector") or "AI"
        except Exception:
            pass
        rows = [r for r in rows if r.get("sector") == sector]
    by_sector: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_sector[row["sector"]].append(row)
    for sector in by_sector:
        by_sector[sector] = sorted(by_sector[sector], key=lambda r: r["quarter"])
    return by_sector


def _forward_backward(xs: np.ndarray, means: np.ndarray, vars_: np.ndarray, A: np.ndarray, pi: np.ndarray):
    n, k = len(xs), len(STATES)
    emit = np.zeros((n, k))
    for j in range(k):
        emit[:, j] = np.exp(-0.5 * (xs - means[j]) ** 2 / max(vars_[j], 1e-6)) / np.sqrt(2 * np.pi * max(vars_[j], 1e-6))
        emit[:, j] = np.clip(emit[:, j], 1e-12, None)
    alpha = np.zeros((n, k))
    alpha[0] = pi * emit[0]
    alpha[0] /= alpha[0].sum() or 1.0
    for t in range(1, n):
        alpha[t] = emit[t] * (alpha[t - 1] @ A)
        alpha[t] /= alpha[t].sum() or 1.0
    beta = np.ones((n, k))
    for t in range(n - 2, -1, -1):
        beta[t] = (A * emit[t + 1] * beta[t + 1]).sum(axis=1)
        beta[t] /= beta[t].sum() or 1.0
    gamma = alpha * beta
    gamma /= np.clip(gamma.sum(axis=1, keepdims=True), 1e-12, None)
    return gamma, emit, A


def _viterbi(xs: np.ndarray, means: np.ndarray, vars_: np.ndarray, A: np.ndarray, pi: np.ndarray) -> list[int]:
    n, k = len(xs), len(STATES)
    emit = np.zeros((n, k))
    for j in range(k):
        emit[:, j] = np.exp(-0.5 * (xs - means[j]) ** 2 / max(vars_[j], 1e-6))
    logA = np.log(np.clip(A, 1e-12, None))
    logE = np.log(np.clip(emit, 1e-12, None))
    delta = np.log(np.clip(pi, 1e-12, None)) + logE[0]
    psi = np.zeros((n, k), dtype=int)
    for t in range(1, n):
        scores = delta[:, None] + logA
        psi[t] = scores.argmax(axis=0)
        delta = scores.max(axis=0) + logE[t]
    path = [int(delta.argmax())]
    for t in range(n - 1, 0, -1):
        path.append(int(psi[t][path[-1]]))
    path.reverse()
    return path


def fit_regimes(ticker: str | None = None, series: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Baum-Welch on sector mood; maps states to bearish / transitional / bullish by mean."""
    groups = series if series is not None else _observations(ticker)
    out: list[dict[str, Any]] = []
    for sector, items in groups.items():
        xs = np.array([float(r.get("mood_score") or 0) for r in items], dtype=float)
        if len(xs) < 3:
            continue
        order = np.argsort(xs)
        means = np.array([
            xs[order[max(0, len(xs) // 6)]],
            np.median(xs),
            xs[order[min(len(xs) - 1, 5 * len(xs) // 6)]],
        ], dtype=float)
        vars_ = np.array([max(float(np.var(xs)), 1e-3)] * 3)
        A = np.array([
            [0.70, 0.25, 0.05],
            [0.20, 0.60, 0.20],
            [0.05, 0.25, 0.70],
        ])
        pi = np.array([0.3, 0.4, 0.3])
        for _ in range(8):
            gamma, _, _ = _forward_backward(xs, means, vars_, A, pi)
            means = (gamma * xs[:, None]).sum(axis=0) / np.clip(gamma.sum(axis=0), 1e-6, None)
            vars_ = np.clip(((gamma * (xs[:, None] - means) ** 2).sum(axis=0) / np.clip(gamma.sum(axis=0), 1e-6, None)), 1e-4, None)
            xi = np.zeros((3, 3))
            for t in range(len(xs) - 1):
                outer = np.outer(gamma[t], gamma[t + 1])
                xi += outer / (outer.sum() or 1.0)
            A = xi / np.clip(xi.sum(axis=1, keepdims=True), 1e-6, None)
            pi = gamma[0]
        # relabel by emission mean so 0=bearish, 2=bullish
        rank = np.argsort(means)
        remap = {int(old): new for new, old in enumerate(rank)}
        path = _viterbi(xs, means, vars_, A, pi)
        gamma, _, _ = _forward_backward(xs, means, vars_, A, pi)
        for i, row in enumerate(items):
            probs = np.zeros(3)
            for j in range(3):
                probs[remap[j]] = gamma[i, j]
            state = remap[path[i]]
            out.append({
                "sector": sector,
                "quarter": row["quarter"],
                "regime": STATES[state],
                "p_bearish": float(probs[0]),
                "p_transitional": float(probs[1]),
                "p_bullish": float(probs[2]),
                "emission": float(means[path[i]]),
                "method": "baum-welch",
            })
    return out
