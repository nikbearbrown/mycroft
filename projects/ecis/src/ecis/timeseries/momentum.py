"""Quarter-over-quarter momentum, acceleration, and regime-relative z-scores."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.stats import mean, stdev
from ecis.guidance_models.revision_features import FEATURE_NAMES, build_revision_rows
from ecis.timeseries.hmm import fit_regimes
from ecis.db.ticker_registry import get_ticker

SIGNAL_TYPES = FEATURE_NAMES


def engineer_momentum(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = build_revision_rows(ticker)
    regimes = {}
    for rec in fit_regimes(ticker):
        regimes[(rec["sector"], rec["quarter"])] = rec["regime"]
    by_tkr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_tkr[row["ticker"]].append(row)
    out: list[dict[str, Any]] = []
    for tkr, items in by_tkr.items():
        items = sorted(items, key=lambda r: r["quarter"])
        sector = "AI"
        try:
            rec = get_ticker(tkr)
            if rec:
                sector = rec.get("sector") or "AI"
        except Exception:
            pass
        history: dict[str, list[float]] = defaultdict(list)
        prev_level: dict[str, float] = {}
        prev_mom: dict[str, float] = {}
        for row in items:
            feats = row.get("features") or {}
            regime = regimes.get((sector, row["quarter"])) or "transitional"
            for name in SIGNAL_TYPES:
                level = float(feats.get(name) or 0)
                mom = None if name not in prev_level else level - prev_level[name]
                acc = None if mom is None or name not in prev_mom else mom - prev_mom[name]
                history[name].append(level)
                mu = mean(history[name])
                sd = stdev(history[name])
                z = None if mu is None or sd in (None, 0) else (level - mu) / sd
                out.append({
                    "ticker": tkr,
                    "quarter": row["quarter"],
                    "signal_type": name,
                    "level": level,
                    "momentum": mom,
                    "acceleration": acc,
                    "zscore": z,
                    "regime": regime,
                })
                prev_level[name] = level
                if mom is not None:
                    prev_mom[name] = mom
    return out
