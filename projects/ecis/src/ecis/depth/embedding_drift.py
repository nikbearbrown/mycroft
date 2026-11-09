"""Sentence embedding centroid drift and intra-cluster variance."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.db.init_db import get_connection
from ecis.scoring.drift import psi

BULLISH = ("raise", "raising", "strong", "growth", "beat")
BEARISH = ("lower", "lowering", "weak", "decline", "miss")
HEDGING = ("may", "might", "approximately", "could")


def _bow(text: str) -> list[float]:
    tokens = (text or "").lower().split()
    vocab = list(BULLISH + BEARISH + HEDGING)
    return [float(sum(1 for t in tokens if t.startswith(w[:4]))) for w in vocab]


def _centroid(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        return []
    dims = len(vectors[0])
    n = len(vectors)
    return [sum(v[j] for v in vectors) / n for j in range(dims)]


def _cosine(a: list[float], b: list[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    da = sum(x * x for x in a) ** 0.5
    db = sum(y * y for y in b) ** 0.5
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


def _category(text: str) -> str:
    blob = (text or "").lower()
    if any(w in blob for w in BULLISH):
        return "bullish"
    if any(w in blob for w in BEARISH):
        return "bearish"
    if any(w in blob for w in HEDGING):
        return "hedging"
    return "other"


def monitor_embedding_drift(ticker: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection("signals")
    query = "SELECT ticker, transcript_date, supporting_quote FROM signals"
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()

    by_q: dict[str, list[list[float]]] = defaultdict(list)
    by_q_cat: dict[tuple[str, str], list[list[float]]] = defaultdict(list)
    flats: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        q = quarter_key(row.get("transcript_date"))
        vec = _bow(row.get("supporting_quote") or "")
        try:
            from ecis.guidance_models.sbert import embed_qa

            vec = embed_qa([row.get("supporting_quote") or ""])[0]
        except Exception:
            pass
        by_q[q].append(vec)
        by_q_cat[(q, _category(row.get("supporting_quote") or ""))].append(vec)
        flats[q].extend(vec)

    quarters = sorted(by_q)
    hist: list[list[float]] = []
    out = []
    for q in quarters:
        cent = _centroid(by_q[q])
        hist_cent = _centroid(hist) if hist else cent
        drift = 1.0 - _cosine(cent, hist_cent) if hist else 0.0
        hist.extend(by_q[q])
        prior = quarters[quarters.index(q) - 1] if quarters.index(q) else None
        psi_val = psi(flats[prior], flats[q]) if prior else 0.0
        vars_ = {}
        for cat in ("bullish", "bearish", "hedging"):
            cluster = by_q_cat.get((q, cat)) or []
            if len(cluster) < 2:
                vars_[cat] = None
                continue
            c = _centroid(cluster)
            vars_[cat] = sum((1 - _cosine(v, c)) for v in cluster) / len(cluster)
        out.append({
            "quarter": q,
            "n": len(by_q[q]),
            "centroid_drift": drift,
            "psi": psi_val,
            "bullish_var": vars_["bullish"],
            "bearish_var": vars_["bearish"],
            "hedging_var": vars_["hedging"],
            "flag": "drift" if psi_val > 0.1 or drift > 0.15 else "stable",
        })
    return out
