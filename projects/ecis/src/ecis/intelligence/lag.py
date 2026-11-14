"""Per-signal-type lag vs excess returns, using stored outcome windows as daily-lag proxies."""

from __future__ import annotations

from typing import Any

from ecis.analytics.stats import pearson
from ecis.depth.decay_by_type import HORIZON_MAP, SIGNAL_TYPES, _joined


def temporal_lags(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = _joined(ticker)
    out: list[dict[str, Any]] = []
    for name in SIGNAL_TYPES:
        xs = [r.get(name) for r in rows]
        best_r, best_lag = None, None
        for days, col in HORIZON_MAP.items():
            ys = [r.get(col) for r in rows]
            r = pearson(xs, ys)
            out.append({
                "signal_type": name,
                "lag_days": days,
                "pearson": r,
                "n": sum(1 for a, b in zip(xs, ys) if a is not None and b is not None),
                "best": 0,
            })
            if r is not None and (best_r is None or abs(r) > abs(best_r)):
                best_r, best_lag = r, days
        for row in out:
            if row["signal_type"] == name:
                row["best"] = int(row["lag_days"] == best_lag)
                row["optimal_lag_days"] = best_lag
                row["weight_hint"] = "fast" if (best_lag or 99) <= 10 else "slow"
    return out
