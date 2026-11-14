"""Same-sector Granger-style lead/lag on hedging and confidence series."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.analytics.stats import pearson
from ecis.db.init_db import get_connection
from ecis.db.ticker_registry import list_tickers


def _series(field: str, ticker: str | None = None) -> dict[str, dict[str, float]]:
    conn = get_connection("signals")
    col = "COALESCE(hedging_index, 0)" if field == "hedging_index" else (
        "COALESCE(confidence_calibrated, confidence_raw)" if field == "confidence" else f"COALESCE({field}, 0)"
    )
    query = f"SELECT ticker, transcript_date, {col} AS val FROM signals"
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    rows = conn.execute(query, params).fetchall()
    conn.close()
    out: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rows:
        q = quarter_key(row["transcript_date"])
        out[(row["ticker"] or "").upper()][q] = float(row["val"] or 0)
    return out


def _granger(leader: list[float], follower: list[float]) -> tuple[float | None, int]:
    """Lag-1 correlation of leader[t-1] vs follower[t] as a Granger proxy."""
    if len(leader) < 4 or len(follower) < 4:
        return None, 1
    xs = leader[:-1]
    ys = follower[1:len(leader)]
    if len(xs) != len(ys) or len(xs) < 3:
        return None, 1
    r = pearson(xs, ys)
    return r, 1


def contagion_links(ticker: str | None = None) -> list[dict[str, Any]]:
    sectors: dict[str, str] = {}
    try:
        for rec in list_tickers():
            sectors[(rec.get("ticker") or "").upper()] = rec.get("sector") or "AI"
    except Exception:
        pass
    hedge = _series("hedging_index", ticker)
    tickers = sorted(hedge)
    by_sector: dict[str, list[str]] = defaultdict(list)
    for tkr in tickers:
        by_sector[sectors.get(tkr, "AI")].append(tkr)
    out = []
    for sector, names in by_sector.items():
        for a in names:
            for b in names:
                if a == b:
                    continue
                qa = sorted(hedge[a])
                qb = sorted(hedge[b])
                shared = [q for q in qa if q in hedge[b]]
                if len(shared) < 4:
                    continue
                la = [hedge[a][q] for q in shared]
                lb = [hedge[b][q] for q in shared]
                r, lag = _granger(la, lb)
                if r is None or r < 0.25:
                    continue
                out.append({
                    "leader": a,
                    "follower": b,
                    "sector": sector,
                    "signal_type": "hedging_index",
                    "granger_r": r,
                    "lag_quarters": lag,
                    "n": len(shared),
                    "strength": "strong" if r >= 0.5 else "moderate",
                })
    return sorted(out, key=lambda r: -(r["granger_r"] or 0))
