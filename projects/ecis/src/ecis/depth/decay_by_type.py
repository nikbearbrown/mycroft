"""Per-signal-type decay: correlation vs excess returns and half-life."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.stats import pearson
from ecis.db.init_db import get_connection

SIGNAL_TYPES = (
    "hedging_index",
    "tone_shift",
    "confidence",
    "dodge_score",
    "fls_density",
    "market_share_score",
)
HORIZON_MAP = {
    1: "ret_same_day",
    2: "ret_1_3d",
    5: "ret_1_3d",
    10: "ret_1_2w",
    20: "ret_1_2w",
    30: "excess_return",
    60: "excess_return",
}
SIGNIFICANCE = 0.20


def _joined(ticker: str | None = None) -> list[dict[str, Any]]:
    conn_s = get_connection("signals")
    query = """
        SELECT signal_id, ticker, transcript_date,
               COALESCE(hedging_index, 0) AS hedging_index,
               COALESCE(tone_shift, 0) AS tone_shift,
               COALESCE(confidence_calibrated, confidence_raw) AS confidence,
               COALESCE(fls_density, 0) AS fls_density
        FROM signals
    """
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    signals = [dict(r) for r in conn_s.execute(query, params).fetchall()]
    conn_s.close()

    conn_o = get_connection("outcomes")
    outcomes = [dict(r) for r in conn_o.execute("SELECT * FROM outcomes").fetchall()]
    conn_o.close()
    by_sid: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in outcomes:
        by_sid[int(row["signal_id"])].append(row)

    dodge: dict[tuple[str, str], float] = {}
    share: dict[tuple[str, str], float] = {}
    try:
        conn_a = get_connection("agents")
        for row in conn_a.execute(
            "SELECT ticker, transcript_date, dodge FROM dodge_scores WHERE scope = 'call'"
        ).fetchall():
            dodge[((row["ticker"] or "").upper(), (row["transcript_date"] or "")[:10])] = row["dodge"]
        for row in conn_a.execute(
            "SELECT ticker, transcript_date, score FROM market_share_language"
        ).fetchall():
            share[((row["ticker"] or "").upper(), (row["transcript_date"] or "")[:10])] = row["score"]
        conn_a.close()
    except Exception:
        pass

    out = []
    for sig in signals:
        recs = by_sid.get(int(sig["signal_id"])) or []
        pick = {}
        for rec in recs:
            if int(rec.get("horizon_days") or 0) == 30 or not pick:
                pick = rec
        key = ((sig.get("ticker") or "").upper(), (sig.get("transcript_date") or "")[:10])
        out.append({
            **sig,
            "dodge_score": dodge.get(key),
            "market_share_score": share.get(key),
            "ret_same_day": pick.get("ret_same_day"),
            "ret_1_3d": pick.get("ret_1_3d"),
            "ret_1_2w": pick.get("ret_1_2w"),
            "excess_return": pick.get("excess_return"),
        })
    return out


def half_life(corrs: list[tuple[int, float | None]]) -> int | None:
    """First horizon where |r| drops below SIGNIFICANCE after a stronger start."""
    started = False
    for days, r in sorted(corrs, key=lambda p: p[0]):
        if r is None:
            continue
        if abs(r) >= SIGNIFICANCE:
            started = True
            continue
        if started:
            return days
    strong = [d for d, r in corrs if r is not None and abs(r) >= SIGNIFICANCE]
    return None if not strong else (max(strong) if started else None)


def analyse_decay(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = _joined(ticker)
    out: list[dict[str, Any]] = []
    for name in SIGNAL_TYPES:
        xs = [r.get(name) for r in rows]
        corrs: list[tuple[int, float | None]] = []
        for days, col in HORIZON_MAP.items():
            ys = [r.get(col) for r in rows]
            r = pearson(xs, ys)
            corrs.append((days, r))
            out.append({
                "signal_type": name,
                "horizon_days": days,
                "n": sum(1 for a, b in zip(xs, ys) if a is not None and b is not None),
                "pearson": r,
                "significant": 1 if r is not None and abs(r) >= SIGNIFICANCE else 0,
                "half_life_days": None,
                "weight_hint": "recent" if days <= 10 else "persistent",
            })
        life = half_life(corrs)
        for row in out:
            if row["signal_type"] == name:
                row["half_life_days"] = life
                row["weight_hint"] = "recent" if (life or 99) <= 10 else "persistent"
    return out
