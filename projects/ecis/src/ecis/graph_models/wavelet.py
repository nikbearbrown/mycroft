"""Haar wavelet split of signal series into low / mid / high frequency."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from ecis.guidance_models.revision_features import FEATURE_NAMES, build_revision_rows


def haar_levels(values: list[float]) -> dict[str, list[float]]:
    y = np.asarray(values, dtype=float)
    if len(y) < 2:
        z = y.tolist() or [0.0]
        return {"low": z, "mid": [0.0] * len(z), "high": [0.0] * len(z)}
    even = y[0::2]
    odd = y[1::2]
    n = min(len(even), len(odd))
    even, odd = even[:n], odd[:n]
    approx = (even + odd) / 2.0
    detail = (even - odd) / 2.0
    if len(approx) >= 2:
        e2, o2 = approx[0::2], approx[1::2]
        m = min(len(e2), len(o2))
        low_c = (e2[:m] + o2[:m]) / 2.0
        mid_c = (e2[:m] - o2[:m]) / 2.0
    else:
        low_c, mid_c = approx, np.zeros_like(approx)
    low = np.repeat(low_c, 4)[: len(y)]
    mid = np.repeat(mid_c, 4)[: len(y)]
    high = np.repeat(detail, 2)[: len(y)]
    if len(low) < len(y):
        low = np.pad(low, (0, len(y) - len(low)), mode="edge")
        mid = np.pad(mid, (0, len(y) - len(mid)), mode="edge")
        high = np.pad(high, (0, len(y) - len(high)), mode="edge")
    return {"low": low.tolist(), "mid": mid.tolist(), "high": high.tolist()}


def decompose_wavelets(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = build_revision_rows(ticker)
    by_tkr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_tkr[row["ticker"]].append(row)
    out: list[dict[str, Any]] = []
    for tkr, items in by_tkr.items():
        items = sorted(items, key=lambda r: r["quarter"])
        if len(items) < 2:
            continue
        for name in FEATURE_NAMES:
            series = [float((r.get("features") or {}).get(name) or 0) for r in items]
            parts = haar_levels(series)
            for i, row in enumerate(items):
                out.append({
                    "ticker": tkr,
                    "signal_type": name,
                    "quarter": row["quarter"],
                    "low": parts["low"][i],
                    "mid": parts["mid"][i],
                    "high": parts["high"][i],
                    "observed": series[i],
                    "method": "haar",
                })
    return out
