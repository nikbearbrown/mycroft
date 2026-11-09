"""Rule-based speech-act labels. DeBERTa is optional and off by default."""

from __future__ import annotations

import os
import re
from collections import defaultdict
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.db.init_db import get_connection

ACTS = ("promise", "commitment", "hedged_intention", "prediction", "deflection", "assertion")
_LOAD = os.getenv("ADVANCED_LOAD_DEBERTA", "").lower() in {"1", "true", "yes"}

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("promise", re.compile(r"(?i)\bwe\s+will\s+(?:deliver|achieve|grow|invest|return)\b")),
    ("commitment", re.compile(r"(?i)\bwe\s+are\s+committed\b|\bcommitment\s+to\b")),
    ("hedged_intention", re.compile(r"(?i)\bwe\s+(?:hope|aim|intend|would\s+like)\s+to\b")),
    ("prediction", re.compile(r"(?i)\bwe\s+(?:expect|anticipate|forecast|project)\b")),
    ("deflection", re.compile(r"(?i)\bwe(?:'ll|\s+will)\s+see\b|\bit\s+remains\s+to\s+be\s+seen\b")),
    ("assertion", re.compile(r"(?i)\bwe\s+(?:achieved|grew|reported|delivered)\b|\brevenue\s+grew\b")),
]


def classify_sentence(text: str) -> str:
    blob = text or ""
    if _LOAD:
        try:
            from transformers import pipeline

            clf = pipeline("text-classification", model="microsoft/deberta-v3-base")
            return str(clf(blob[:400])[0]["label"]).lower()
        except Exception:
            pass
    for name, pat in _PATTERNS:
        if pat.search(blob):
            return name
    return "assertion"


def classify_text(text: str) -> dict[str, float]:
    parts = re.split(r"(?<=[.!?])\s+", text or "")
    counts = {a: 0 for a in ACTS}
    n = 0
    for part in parts:
        if len(part.split()) < 3:
            continue
        counts[classify_sentence(part)] += 1
        n += 1
    if n == 0:
        return {a: 0.0 for a in ACTS}
    return {a: counts[a] / n for a in ACTS}


def call_distributions(ticker: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection("signals")
    query = "SELECT ticker, transcript_date, supporting_quote FROM signals"
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    buckets: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in conn.execute(query, params).fetchall():
        buckets[((row["ticker"] or "").upper(), (row["transcript_date"] or "")[:10])].append(row["supporting_quote"] or "")
    conn.close()
    out = []
    prev: dict[str, dict[str, float]] = {}
    for (tkr, day), quotes in sorted(buckets.items()):
        dist = classify_text(" ".join(quotes))
        shift = None
        if tkr in prev:
            shift = sum(abs(dist[a] - prev[tkr][a]) for a in ACTS) / 2.0
        prev[tkr] = dist
        out.append({
            "ticker": tkr,
            "transcript_date": day,
            "quarter": quarter_key(day),
            **{f"p_{a}": dist[a] for a in ACTS},
            "mix_shift": shift,
        })
    return out
