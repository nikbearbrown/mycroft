"""Signal-to-price correlations and multi-horizon reaction windows."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.features import direction_polarity, quarter_key, tone_from_signal
from ecis.analytics.stats import mean, pearson, spearman
from ecis.db.init_db import get_connection

WINDOWS = ("1d", "5d", "30d")
FEATURES = ("direction", "confidence", "hedging", "tone_shift")


def _joined(ticker: str | None = None) -> list[dict[str, Any]]:
    s_conn = get_connection("signals")
    query = """
        SELECT signal_id, ticker, transcript_date, direction,
               COALESCE(confidence_calibrated, confidence_raw) AS confidence,
               surprise_score, hedging_index, fls_density, tone_shift
        FROM signals
    """
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    signals = [dict(r) for r in s_conn.execute(query, params).fetchall()]
    s_conn.close()

    o_conn = get_connection("outcomes")
    outcomes = [dict(r) for r in o_conn.execute("SELECT * FROM outcomes").fetchall()]
    o_conn.close()
    by_sid: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in outcomes:
        by_sid[int(row["signal_id"])].append(row)

    joined: list[dict[str, Any]] = []
    for sig in signals:
        recs = by_sid.get(int(sig["signal_id"])) or []
        pick: dict[str, Any] = {}
        for rec in recs:
            hz = int(rec.get("horizon_days") or 0)
            if hz == 30 or not pick:
                pick = rec
        joined.append({**sig, **{k: pick.get(k) for k in (
            "ret_same_day", "ret_1_3d", "ret_1_2w", "excess_return",
            "reaction_magnitude", "horizon_days",
        )}})
    return joined


def _window_return(row: dict[str, Any], window: str) -> float | None:
    mapping = {
        "same_day": "ret_same_day",
        "1d": "ret_same_day",
        "2d": "ret_1_3d",
        "5d": "ret_1_3d",
        "10d": "ret_1_2w",
        "30d": "excess_return",
    }
    return row.get(mapping[window])


def _feature_value(row: dict[str, Any], feature: str) -> float | None:
    if feature == "direction":
        return direction_polarity(row.get("direction")) * float(row.get("confidence") or 0)
    if feature == "confidence":
        try:
            return float(row.get("confidence") or 0)
        except (TypeError, ValueError):
            return None
    if feature == "hedging":
        try:
            return float(row["hedging_index"]) if row.get("hedging_index") is not None else None
        except (TypeError, ValueError):
            return None
    if feature == "tone_shift":
        return tone_from_signal(row)
    return None


def _confidence_tier(conf: float | None) -> str:
    if conf is None:
        return "unknown"
    if conf >= 0.8:
        return "high"
    if conf >= 0.5:
        return "medium"
    return "low"


def _reaction_pattern(car_1d: float | None, car_30d: float | None) -> str:
    if car_1d is None or car_30d is None:
        return "unknown"
    if car_1d == 0:
        return "unknown"
    if (car_1d > 0 and car_30d > car_1d) or (car_1d < 0 and car_30d < car_1d):
        return "underreaction"
    if (car_1d > 0 > car_30d) or (car_1d < 0 < car_30d):
        return "overreaction"
    return "persistent"


def signal_price_correlation(ticker: str | None = None) -> list[dict[str, Any]]:
    """Pearson / Spearman of each signal feature vs 1d / 5d / 30d excess returns."""
    rows = _joined(ticker)
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        tkr = (row.get("ticker") or "").upper()
        q = quarter_key(row.get("transcript_date"))
        groups[(tkr, q)].append(row)

    universe: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        universe[quarter_key(row.get("transcript_date"))].append(row)

    def _emit(scope: str, quarter: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for feature in FEATURES:
            xs = [_feature_value(r, feature) for r in items]
            for window in WINDOWS:
                rets = [_window_return(r, window) for r in items]
                n = sum(1 for a, b in zip(xs, rets) if a is not None and b is not None)
                p = pearson(xs, rets)
                s = spearman(xs, rets)
                informativeness = None
                if p is not None and s is not None:
                    informativeness = (abs(p) + abs(s)) / 2.0
                elif p is not None:
                    informativeness = abs(p)
                elif s is not None:
                    informativeness = abs(s)
                out.append({
                    "ticker": scope,
                    "quarter": quarter,
                    "feature": feature,
                    "window": window,
                    "n": n,
                    "pearson": p,
                    "spearman": s,
                    "informativeness": informativeness,
                })
        return out

    out: list[dict[str, Any]] = []
    for (tkr, quarter), items in sorted(groups.items()):
        out.extend(_emit(tkr, quarter, items))
    for quarter, items in sorted(universe.items()):
        out.extend(_emit("ALL", quarter, items))
    out.sort(key=lambda r: (-(r["informativeness"] or 0.0), r["ticker"], r["feature"], r["window"]))
    return out


def reaction_windows(ticker: str | None = None) -> list[dict[str, Any]]:
    """Mean CAR-style returns from same-day through 30d, by direction and confidence tier."""
    rows = _joined(ticker)
    buckets: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        direction = (row.get("direction") or "unknown").lower()
        q = quarter_key(row.get("transcript_date"))
        try:
            conf = float(row.get("confidence") or 0)
        except (TypeError, ValueError):
            conf = 0.0
        buckets[(direction, q, _confidence_tier(conf))].append(row)

    out: list[dict[str, Any]] = []
    for (direction, quarter, tier), items in sorted(buckets.items()):
        car_1d = mean([_window_return(r, "1d") for r in items])
        car_30d = mean([_window_return(r, "30d") for r in items])
        out.append({
            "direction": direction,
            "quarter": quarter,
            "confidence_tier": tier,
            "n": len(items),
            "car_same_day": mean([_window_return(r, "same_day") for r in items]),
            "car_1d": car_1d,
            "car_2d": mean([_window_return(r, "2d") for r in items]),
            "car_5d": mean([_window_return(r, "5d") for r in items]),
            "car_10d": mean([_window_return(r, "10d") for r in items]),
            "car_30d": car_30d,
            "mean_reaction_magnitude": mean([r.get("reaction_magnitude") for r in items]),
            "pattern": _reaction_pattern(car_1d, car_30d),
        })
    return out
