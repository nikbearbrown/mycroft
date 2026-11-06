"""Per-call contradiction rules, severity, and resolution labels."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.db.init_db import get_connection

RULE_WEIGHT = {
    "bullish_tone_rising_hedge": 1.2,
    "high_confidence_high_dodge": 1.4,
    "offensive_declining_specificity": 1.1,
    "positive_bury": 1.3,
}


def _calls(ticker: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection("signals")
    query = """
        SELECT ticker, transcript_date,
               COALESCE(tone_shift, 0) AS tone_shift,
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
        buckets[((row["ticker"] or "").upper(), (row["transcript_date"] or "")[:10])].append(row)

    dodge: dict[tuple[str, str], float] = {}
    share: dict[tuple[str, str], float] = {}
    spec: dict[tuple[str, str], float] = {}
    discourse: dict[tuple[str, str], str] = {}
    try:
        conn_a = get_connection("agents")
        for row in conn_a.execute(
            "SELECT ticker, transcript_date, dodge FROM dodge_scores WHERE scope = 'call'"
        ).fetchall():
            dodge[((row["ticker"] or "").upper(), (row["transcript_date"] or "")[:10])] = float(row["dodge"] or 0)
        for row in conn_a.execute(
            "SELECT ticker, transcript_date, score FROM market_share_language"
        ).fetchall():
            share[((row["ticker"] or "").upper(), (row["transcript_date"] or "")[:10])] = float(row["score"] or 0)
        try:
            for row in conn_a.execute(
                "SELECT ticker, quarter, specificity FROM guidance_language"
            ).fetchall():
                spec[((row["ticker"] or "").upper(), row["quarter"] or "")] = float(row["specificity"] or 0)
        except Exception:
            pass
        try:
            for row in conn_a.execute(
                "SELECT ticker, transcript_date, pattern FROM discourse_structure"
            ).fetchall():
                discourse[((row["ticker"] or "").upper(), (row["transcript_date"] or "")[:10])] = row["pattern"] or ""
        except Exception:
            pass
        conn_a.close()
    except Exception:
        pass

    out = []
    prev_spec: dict[str, float] = {}
    for (tkr, day), items in sorted(buckets.items()):
        n = max(len(items), 1)
        q = quarter_key(day)
        rec = {
            "ticker": tkr,
            "transcript_date": day,
            "quarter": q,
            "tone": sum(float(i["tone_shift"]) for i in items) / n,
            "hedging": sum(float(i["hedging_index"]) for i in items) / n,
            "confidence": sum(float(i["confidence"] or 0) for i in items) / n,
            "dodge": dodge.get((tkr, day), 0.0),
            "share": share.get((tkr, day), 0.0),
            "specificity": spec.get((tkr, q)),
            "discourse": discourse.get((tkr, day), ""),
        }
        prior = prev_spec.get(tkr)
        rec["spec_delta"] = None if rec["specificity"] is None or prior is None else rec["specificity"] - prior
        if rec["specificity"] is not None:
            prev_spec[tkr] = rec["specificity"]
        out.append(rec)
    return out


def _severity(a: float, b: float, weight: float) -> float:
    return max(0.0, min(1.0, ((abs(a) + abs(b)) / 2.0) * weight))


def detect_contradictions(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = []
    for call in _calls(ticker):
        hits: list[dict[str, Any]] = []
        if call["tone"] > 0.05 and call["hedging"] > 0.25:
            hits.append({
                "rule": "bullish_tone_rising_hedge",
                "severity": _severity(call["tone"], call["hedging"], RULE_WEIGHT["bullish_tone_rising_hedge"]),
                "resolution": "uncertainty",
            })
        if call["confidence"] >= 0.7 and call["dodge"] >= 0.45:
            hits.append({
                "rule": "high_confidence_high_dodge",
                "severity": _severity(call["confidence"], call["dodge"], RULE_WEIGHT["high_confidence_high_dodge"]),
                "resolution": "obfuscation",
            })
        if call["share"] > 0.1 and (call["spec_delta"] is not None and call["spec_delta"] < -0.05):
            hits.append({
                "rule": "offensive_declining_specificity",
                "severity": _severity(call["share"], abs(call["spec_delta"]), RULE_WEIGHT["offensive_declining_specificity"]),
                "resolution": "mixed_outlook",
            })
        if call["tone"] > 0.05 and call["discourse"] == "bury":
            hits.append({
                "rule": "positive_bury",
                "severity": _severity(call["tone"], 0.7, RULE_WEIGHT["positive_bury"]),
                "resolution": "obfuscation",
            })
        for hit in hits:
            rows.append({
                "ticker": call["ticker"],
                "transcript_date": call["transcript_date"],
                "quarter": call["quarter"],
                "rule": hit["rule"],
                "severity": hit["severity"],
                "resolution": hit["resolution"],
                "tone": call["tone"],
                "hedging": call["hedging"],
                "confidence": call["confidence"],
                "dodge": call["dodge"],
                "tier": "high" if hit["severity"] >= 0.6 else "medium" if hit["severity"] >= 0.35 else "low",
            })
    return rows
