"""Three-way surprise: NLP vs consensus, consensus vs actual, NLP vs actual."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.features import direction_polarity, quarter_key
from ecis.analytics.stats import mean
from ecis.db.init_db import get_connection
from ecis.prediction.consensus import consensus_delta, consensus_direction
from ecis.prediction.surprise import surprise_value

_DIR_ORDER = {"lowered": 0, "maintained": 1, "raised": 2}


def _actual_direction(excess: float | None) -> str | None:
    if excess is None:
        return None
    if excess > 0.01:
        return "raised"
    if excess < -0.01:
        return "lowered"
    return "maintained"


def _gap(a: str | None, b: str | None) -> float | None:
    if not a or not b:
        return None
    return abs(_DIR_ORDER.get(a, 1) - _DIR_ORDER.get(b, 1)) / 2.0


def surprise_analytics(ticker: str | None = None) -> list[dict[str, Any]]:
    """NLP-vs-consensus, consensus-vs-actual, NLP-vs-actual per ticker-quarter."""
    s_conn = get_connection("signals")
    query = """
        SELECT signal_id, ticker, transcript_date, direction, surprise_score
        FROM signals
    """
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    signals = [dict(r) for r in s_conn.execute(query, params).fetchall()]
    s_conn.close()

    o_conn = get_connection("outcomes")
    outcomes = o_conn.execute(
        "SELECT signal_id, excess_return, horizon_days FROM outcomes"
    ).fetchall()
    o_conn.close()
    excess_by_sid: dict[int, float | None] = {}
    for row in outcomes:
        sid = int(row["signal_id"])
        if int(row["horizon_days"] or 0) == 30 or sid not in excess_by_sid:
            excess_by_sid[sid] = row["excess_return"]

    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for sig in signals:
        tkr = (sig.get("ticker") or "").upper()
        q = quarter_key(sig.get("transcript_date"))
        nlp = (sig.get("direction") or "maintained").lower()
        consensus = consensus_direction(consensus_delta(tkr))
        nlp_vs_cons = sig.get("surprise_score")
        if nlp_vs_cons is None:
            nlp_vs_cons = surprise_value(nlp, consensus)
        actual = _actual_direction(excess_by_sid.get(int(sig["signal_id"])))
        buckets[(tkr, q)].append({
            "nlp": nlp,
            "consensus": consensus,
            "actual": actual,
            "nlp_vs_consensus": nlp_vs_cons,
            "consensus_vs_actual": _gap(consensus, actual),
            "nlp_vs_actual": _gap(nlp, actual),
            "nlp_polarity": direction_polarity(nlp),
            "actual_polarity": direction_polarity(actual) if actual else None,
        })

    out: list[dict[str, Any]] = []
    for (tkr, quarter), items in sorted(buckets.items()):
        nlp_hits = [
            1.0 if it["nlp"] == it["actual"] else 0.0
            for it in items if it["actual"]
        ]
        cons_hits = [
            1.0 if it["consensus"] == it["actual"] else 0.0
            for it in items if it["actual"]
        ]
        out.append({
            "ticker": tkr,
            "quarter": quarter,
            "n": len(items),
            "nlp_vs_consensus": mean([it["nlp_vs_consensus"] for it in items]),
            "consensus_vs_actual": mean([it["consensus_vs_actual"] for it in items]),
            "nlp_vs_actual": mean([it["nlp_vs_actual"] for it in items]),
            "nlp_hit_rate": mean(nlp_hits),
            "consensus_hit_rate": mean(cons_hits),
        })
    return out
