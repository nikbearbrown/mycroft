"""High-confidence misses: cluster by root cause and apply a confidence modifier."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from ecis.db.init_db import get_connection

HIGH_CONF = 0.70
MODIFIER = 0.75

_AMBIGUOUS = re.compile(r"(?i)\b(?:may|might|could|approximately|around|somewhat|subject to)\b")
_SARCASM = re.compile(r"(?i)\b(?:sure(?:ly)?|obviously|right|great(?:\s+job)?|wonderful)\b")
_CONTEXT = re.compile(r"(?i)\b(?:as\s+I\s+said|depending|it\s+depends|we'll\s+see)\b")


def _cause(quote: str, section: str, excess: float | None) -> str:
    text = quote or ""
    if section == "qa" and _SARCASM.search(text):
        return "sarcasm_misread"
    if section == "qa" and "analyst" in text.lower():
        return "section_misattribution"
    if _AMBIGUOUS.search(text):
        return "ambiguous_language"
    if _CONTEXT.search(text):
        return "context_dependent"
    if excess is not None and abs(excess) > 0.08:
        return "anomalous_market"
    return "ambiguous_language"


def analyse_false_positives(ticker: str | None = None) -> list[dict[str, Any]]:
    conn_s = get_connection("signals")
    query = """
        SELECT signal_id, ticker, transcript_date, direction, section_label,
               supporting_quote,
               COALESCE(confidence_calibrated, confidence_raw) AS confidence
        FROM signals
    """
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    signals = [dict(r) for r in conn_s.execute(query, params).fetchall()]
    conn_s.close()

    conn_o = get_connection("outcomes")
    outcomes = conn_o.execute(
        "SELECT signal_id, correct, excess_return, horizon_days FROM outcomes"
    ).fetchall()
    conn_o.close()
    grade: dict[int, tuple[int | None, float | None]] = {}
    for row in outcomes:
        sid = int(row["signal_id"])
        if int(row["horizon_days"] or 0) == 30 or sid not in grade:
            grade[sid] = (row["correct"], row["excess_return"])

    sectors: dict[str, str] = {}
    try:
        conn_a = get_connection("agents")
        for row in conn_a.execute("SELECT ticker, sector FROM tickers").fetchall():
            sectors[(row["ticker"] or "").upper()] = row["sector"] or "AI"
        conn_a.close()
    except Exception:
        pass

    rows: list[dict[str, Any]] = []
    for sig in signals:
        conf = float(sig.get("confidence") or 0)
        if conf < HIGH_CONF:
            continue
        correct, excess = grade.get(int(sig["signal_id"]), (None, None))
        if correct != 0:
            continue
        quote = sig.get("supporting_quote") or ""
        section = (sig.get("section_label") or "").lower()
        cause = _cause(quote, section, excess)
        rows.append({
            "signal_id": sig["signal_id"],
            "ticker": (sig.get("ticker") or "").upper(),
            "transcript_date": sig.get("transcript_date"),
            "direction": sig.get("direction"),
            "confidence": conf,
            "section_label": section,
            "root_cause": cause,
            "sector": sectors.get((sig.get("ticker") or "").upper(), "AI"),
            "excess_return": excess,
            "confidence_modifier": MODIFIER,
            "quote": quote[:240],
        })
    return rows


def cause_summary(rows: list[dict[str, Any]] | None = None, ticker: str | None = None) -> list[dict[str, Any]]:
    rows = rows if rows is not None else analyse_false_positives(ticker)
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[row["root_cause"]].append(row)
    return [
        {"root_cause": cause, "n": len(items), "mean_confidence": sum(i["confidence"] for i in items) / len(items)}
        for cause, items in sorted(buckets.items())
    ]


def matches_fp_pattern(quote: str, section: str = "") -> bool:
    return _cause(quote, section, None) in {
        "ambiguous_language", "sarcasm_misread", "context_dependent", "section_misattribution",
    }
