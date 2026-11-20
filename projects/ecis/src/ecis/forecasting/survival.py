"""Kaplan-Meier survival and Cox PH time-to-revision."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from ecis.analytics.store import fetch_table
from ecis.guidance_models.revision_features import build_revision_rows

COX_FEATURES = (
    "hedging_index",
    "management_confidence",
    "dodge_score",
    "ceo_cfo_divergence",
    "sector_mood_z",
)
HORIZONS = (1, 2, 3, 4, 6, 8)


def _events(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = build_revision_rows(ticker)
    by_tkr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_tkr[row["ticker"]].append(row)
    out: list[dict[str, Any]] = []
    for tkr, items in by_tkr.items():
        items = sorted(items, key=lambda r: r["quarter"])
        for i, row in enumerate(items):
            time = None
            event = 0
            for j in range(i, len(items)):
                if items[j].get("target") == 1:
                    time = j - i + 1
                    event = 1
                    break
            if time is None:
                time = max(len(items) - i, 1)
                event = 0
            feats = row.get("features") or {}
            x = [float(feats.get(n) or 0) for n in COX_FEATURES]
            extra = _extra_features(tkr, row.get("quarter"))
            out.append({
                "ticker": tkr,
                "quarter": row["quarter"],
                "time": time,
                "event": event,
                "x": x + extra,
            })
    return out


def _extra_features(ticker: str, quarter: str | None) -> list[float]:
    sev = 0.0
    align = 0.0
    try:
        for row in fetch_table("contradictions", limit=200):
            if (row.get("ticker") or "").upper() == ticker and (not quarter or row.get("quarter") == quarter):
                sev = max(sev, float(row.get("severity") or 0))
    except Exception:
        pass
    try:
        for row in fetch_table("analyst_alignment", limit=200):
            if (row.get("ticker") or "").upper() == ticker and (not quarter or row.get("quarter") == quarter):
                align = float(row.get("alignment") or 0)
    except Exception:
        pass
    try:
        for row in fetch_table("momentum_features", limit=200):
            if (row.get("ticker") or "").upper() == ticker and row.get("signal_type") == "dodge_score" and (not quarter or row.get("quarter") == quarter):
                extra_m = float(row.get("momentum") or 0)
                return [sev, extra_m, align]
    except Exception:
        pass
    return [sev, 0.0, align]


def kaplan_meier(times: list[int], events: list[int]) -> dict[int, float]:
    pairs = sorted(zip(times, events))
    n = len(pairs)
    surv = 1.0
    curve = {0: 1.0}
    i = 0
    while i < len(pairs):
        t = pairs[i][0]
        d = 0
        while i < len(pairs) and pairs[i][0] == t:
            d += pairs[i][1]
            i += 1
        at_risk = sum(1 for tt, _ in pairs if tt >= t)
        if at_risk:
            surv *= 1.0 - d / at_risk
        curve[int(t)] = max(0.0, min(1.0, surv))
    return curve


def _cox_beta(X: np.ndarray, times: np.ndarray, events: np.ndarray) -> np.ndarray:
    if len(X) < 3 or int(events.sum()) == 0:
        return np.zeros(X.shape[1])
    beta = np.zeros(X.shape[1])
    lr = 0.05
    for _ in range(40):
        grad = np.zeros(X.shape[1])
        for i, ev in enumerate(events):
            if ev < 1:
                continue
            risk = times >= times[i]
            xb = X[risk] @ beta
            xb = xb - np.max(xb)
            w = np.exp(np.clip(xb, -20, 20))
            w = w / (w.sum() or 1.0)
            grad += X[i] - w @ X[risk]
        beta += lr * grad / max(float(events.sum()), 1.0)
    return beta


def fit_survival(ticker: str | None = None, events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    recs = events if events is not None else _events(ticker)
    if ticker:
        recs = [r for r in recs if r["ticker"] == ticker.upper()]
    if not recs:
        return {"curves": [], "hazards": []}
    names = list(COX_FEATURES) + ["contradiction_severity", "dodge_momentum", "analyst_alignment"]
    X = np.array([r["x"] for r in recs], dtype=float)
    times = np.array([r["time"] for r in recs], dtype=float)
    ev = np.array([r["event"] for r in recs], dtype=float)
    km = kaplan_meier([int(t) for t in times], [int(e) for e in ev])
    beta = _cox_beta(X, times, ev)
    hazards = []
    for name, b in zip(names, beta):
        hazards.append({
            "ticker": ticker.upper() if ticker else "ALL",
            "feature": name,
            "hazard_ratio": float(np.exp(np.clip(b, -5, 5))),
            "coef": float(b),
        })
    curves = []
    by_tkr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in recs:
        by_tkr[row["ticker"]].append(row)
    for tkr, items in by_tkr.items():
        t_km = kaplan_meier([int(r["time"]) for r in items], [int(r["event"]) for r in items]) or km
        x = np.mean([r["x"] for r in items], axis=0)
        log_h = float(x @ beta) if beta.size else 0.0
        for h in HORIZONS:
            s = 1.0
            for t, val in sorted(t_km.items()):
                if t <= h:
                    s = val
            # Cox shift: S(t)^exp(xβ)
            s = float(s ** max(0.2, min(5.0, math_exp(log_h))))
            curves.append({
                "ticker": tkr,
                "horizon": h,
                "survival": s,
                "hazard": 1.0 - s,
                "danger": int(s < 0.50 and h <= 2),
                "method": "cox-km",
            })
    return {"curves": curves, "hazards": hazards}


def math_exp(z: float) -> float:
    return float(np.exp(np.clip(z, -5, 5)))
