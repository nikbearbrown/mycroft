"""Multi-quarter streaks: hedging, confidence, dodge, specificity."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.analytics.management import guidance_language, management_confidence
from ecis.db.init_db import get_connection


def _series(ticker: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection("signals")
    query = """
        SELECT ticker, transcript_date,
               COALESCE(hedging_index, 0) AS hedging_index,
               COALESCE(confidence_calibrated, confidence_raw) AS confidence
        FROM signals
    """
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[((row["ticker"] or "").upper(), quarter_key(row.get("transcript_date")))].append(row)

    dodge: dict[tuple[str, str], float] = {}
    try:
        conn_a = get_connection("agents")
        for row in conn_a.execute(
            "SELECT ticker, quarter, dodge FROM dodge_scores WHERE scope = 'call'"
        ).fetchall():
            dodge[((row["ticker"] or "").upper(), row["quarter"])] = row["dodge"]
        conn_a.close()
    except Exception:
        pass
    conf = {(r["ticker"], r["quarter"]): r for r in management_confidence(ticker)}
    guide = {(r["ticker"], r["quarter"]): r for r in guidance_language(ticker)}

    out = []
    for (tkr, q), items in buckets.items():
        n = max(len(items), 1)
        out.append({
            "ticker": tkr,
            "quarter": q,
            "hedging": sum(float(i["hedging_index"]) for i in items) / n,
            "confidence": (conf.get((tkr, q)) or {}).get("confidence")
            or (sum(float(i["confidence"] or 0) for i in items) / n * 100),
            "dodge": dodge.get((tkr, q)),
            "specificity": (guide.get((tkr, q)) or {}).get("specificity"),
        })
    return sorted(out, key=lambda r: (r["ticker"], r["quarter"]))


def _streak(values: list[float | None], rising: bool) -> int:
    n = 0
    for i in range(len(values) - 1, 0, -1):
        a, b = values[i - 1], values[i]
        if a is None or b is None:
            break
        if rising and b > a + 1e-6:
            n += 1
        elif (not rising) and b < a - 1e-6:
            n += 1
        else:
            break
    return n


def chain_signals(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = _series(ticker)
    by_tkr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_tkr[row["ticker"]].append(row)

    out: list[dict[str, Any]] = []
    for tkr, items in by_tkr.items():
        hedges = [i["hedging"] for i in items]
        confs = [i["confidence"] for i in items]
        dodges = [i["dodge"] for i in items]
        specs = [i["specificity"] for i in items]
        last = items[-1]
        hedge_up = _streak(hedges, True)
        conf_down = _streak(confs, False)
        dodge_up = _streak(dodges, True)
        spec_down = _streak(specs, False)
        deterioration = hedge_up >= 2 and conf_down >= 2
        out.append({
            "ticker": tkr,
            "quarter": last["quarter"],
            "hedging_streak": hedge_up,
            "hedging_direction": "rising" if hedge_up else "stable",
            "confidence_streak": conf_down,
            "confidence_trajectory": "declining" if conf_down else "stable",
            "dodge_momentum": dodge_up,
            "specificity_drift": spec_down,
            "chain_length": max(hedge_up, conf_down, dodge_up, spec_down),
            "flag": "sustained_deterioration" if deterioration else "normal",
            "weight": 1.5 if deterioration else 1.0,
        })
    return out
