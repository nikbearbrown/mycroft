"""t-1 / t-2 / t-3 lag columns plus a correlation prune of redundant lags."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.stats import pearson
from ecis.guidance_models.revision_features import FEATURE_NAMES, build_revision_rows

LAGS = (1, 2, 3)
REDUNDANT = 0.85


def engineer_lags(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = build_revision_rows(ticker)
    by_tkr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_tkr[row["ticker"]].append(row)
    long: list[dict[str, Any]] = []
    contemporaneous: dict[tuple[str, str], dict[str, float]] = {}
    lagged: dict[tuple[str, str, str, int], float] = {}
    for tkr, items in by_tkr.items():
        items = sorted(items, key=lambda r: r["quarter"])
        for i, row in enumerate(items):
            feats = row.get("features") or {}
            contemporaneous[(tkr, row["quarter"])] = {n: float(feats.get(n) or 0) for n in FEATURE_NAMES}
            for lag in LAGS:
                src = items[i - lag] if i >= lag else None
                for name in FEATURE_NAMES:
                    val = None if src is None else float((src.get("features") or {}).get(name) or 0)
                    lagged[(tkr, row["quarter"], name, lag)] = val if val is not None else 0.0
                    long.append({
                        "ticker": tkr,
                        "quarter": row["quarter"],
                        "feature": name,
                        "lag": lag,
                        "value": 0.0 if val is None else val,
                        "selected": 1,
                    })

    by_feat: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in long:
        by_feat[row["feature"]].append(row)
    drop: set[tuple[str, int]] = set()
    for name, items in by_feat.items():
        for lag in LAGS:
            xs = []
            ys = []
            for row in items:
                if row["lag"] != lag:
                    continue
                cur = contemporaneous.get((row["ticker"], row["quarter"]), {}).get(name)
                xs.append(cur)
                ys.append(row["value"])
            r = pearson(xs, ys)
            if r is not None and abs(r) >= REDUNDANT:
                drop.add((name, lag))
    for row in long:
        if (row["feature"], row["lag"]) in drop:
            row["selected"] = 0
    return long
