"""Additive trend + quarterly seasonality + residual."""

from __future__ import annotations

import math
import os
from collections import defaultdict
from typing import Any

import numpy as np

from ecis.guidance_models.revision_features import FEATURE_NAMES, build_revision_rows

_LOAD = os.getenv("FORECASTING_LOAD_PROPHET", "").lower() in {"1", "true", "yes"}
PERIOD = 4.0


def _ols(t: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    sin = np.sin(2 * math.pi * t / PERIOD)
    cos = np.cos(2 * math.pi * t / PERIOD)
    X = np.column_stack([np.ones(len(t)), t, sin, cos])
    try:
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    except Exception:
        beta = np.zeros(4)
    fitted = X @ beta
    return beta, fitted


def _decompose_series(values: list[float]) -> list[dict[str, float]]:
    y = np.asarray(values, dtype=float)
    t = np.arange(len(y), dtype=float)
    _, fitted = _ols(t, y)
    sin = np.sin(2 * math.pi * t / PERIOD)
    cos = np.cos(2 * math.pi * t / PERIOD)
    X = np.column_stack([np.ones(len(t)), t, sin, cos])
    beta, fitted = _ols(t, y)
    trend = beta[0] + beta[1] * t
    season = beta[2] * sin + beta[3] * cos
    resid = y - fitted
    sd = float(np.std(resid)) if len(resid) > 1 else 0.0
    out = []
    for i in range(len(y)):
        out.append({
            "observed": float(y[i]),
            "trend": float(trend[i]),
            "seasonality": float(season[i]),
            "residual": float(resid[i]),
            "flag": "anomaly" if sd and abs(resid[i]) > 1.5 * sd else "ok",
        })
    return out


def decompose(ticker: str | None = None) -> list[dict[str, Any]]:
    if _LOAD:
        try:
            from prophet import Prophet  # type: ignore
        except Exception:
            Prophet = None
        else:
            _ = Prophet  # optional path documented; numpy used below for local runs

    rows = build_revision_rows(ticker)
    by_tkr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_tkr[row["ticker"]].append(row)
    out: list[dict[str, Any]] = []
    for tkr, items in by_tkr.items():
        items = sorted(items, key=lambda r: r["quarter"])
        if len(items) < 4:
            continue
        for name in FEATURE_NAMES:
            series = [float((r.get("features") or {}).get(name) or 0) for r in items]
            parts = _decompose_series(series)
            for row, part in zip(items, parts):
                out.append({
                    "ticker": tkr,
                    "signal_type": name,
                    "quarter": row["quarter"],
                    **part,
                    "method": "additive",
                })
    return out
