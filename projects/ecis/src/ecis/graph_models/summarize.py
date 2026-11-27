"""Signal-aware extractive ranking plus a short abstractive template per call."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.db.init_db import get_connection
from ecis.guidance_models.qa_parser import parse_qa_corpus

_SENT = re.compile(r"(?<=[.!?])\s+")
_GUIDE = re.compile(r"(?i)\b(?:guidance|outlook|forecast|raise|lower|maintain|hedge|expect)\b")
_NUM = re.compile(r"\d")


def _sentences(text: str) -> list[str]:
    parts = _SENT.split((text or "").strip())
    return [p.strip() for p in parts if len(p.strip()) > 20]


def _score(sent: str, *, qa: bool = False) -> float:
    s = 0.15 * min(len(sent.split()), 40) / 40.0
    if _GUIDE.search(sent):
        s += 0.45
    if _NUM.search(sent):
        s += 0.25
    if qa:
        s += 0.10
    return s


def _abstract(extractive: list[str], ticker: str, flags: list[str]) -> str:
    guide = [s for s in extractive if _GUIDE.search(s)][:2]
    other = [s for s in extractive if s not in guide][:2]
    qa = [s for s in extractive if s.endswith("?")][:1]
    paras = []
    paras.append(f"{ticker} call. " + (" ".join(guide) if guide else "No explicit guidance sentence ranked."))
    if other:
        paras.append("Language: " + " ".join(other))
    if qa:
        paras.append("Q&A: " + " ".join(qa))
    if flags:
        paras.append("Flags: " + "; ".join(flags[:4]))
    while len(paras) < 3:
        paras.append("No additional ranked content.")
    return "\n\n".join(paras[:5])


def summarize_calls(ticker: str | None = None) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str], dict[str, Any]] = defaultdict(lambda: {"sents": [], "flags": []})
    try:
        conn = get_connection("signals")
        query = """SELECT ticker, transcript_date, supporting_quote, direction, hedging_index
                   FROM signals"""
        params: list[str] = []
        if ticker:
            query += " WHERE ticker = ?"
            params.append(ticker.upper())
        for row in conn.execute(query, params).fetchall():
            key = ((row["ticker"] or "").upper(), (row["transcript_date"] or "")[:10])
            buckets[key]["sents"].extend(_sentences(row["supporting_quote"] or ""))
            if row["direction"]:
                buckets[key]["flags"].append(f"direction={row['direction']}")
            if row["hedging_index"] is not None and float(row["hedging_index"]) >= 0.4:
                buckets[key]["flags"].append("elevated hedging")
        conn.close()
    except Exception:
        pass
    for pair in parse_qa_corpus(ticker):
        key = ((pair.get("ticker") or "").upper(), (pair.get("transcript_date") or "")[:10])
        buckets[key]["sents"].extend(_sentences(pair.get("question") or ""))
        buckets[key]["sents"].extend(_sentences(pair.get("answer") or ""))
    out = []
    for (tkr, day), blob in sorted(buckets.items()):
        ranked = sorted({s: _score(s) for s in blob["sents"]}.items(), key=lambda p: -p[1])
        extractive = [s for s, _ in ranked[:8]]
        out.append({
            "ticker": tkr,
            "transcript_date": day,
            "quarter": quarter_key(day),
            "extractive": " ".join(extractive),
            "abstractive": _abstract(extractive, tkr, blob["flags"]),
            "highlights": "; ".join(extractive[:3]),
            "n_sentences": len(extractive),
            "method": "extractive-template",
        })
    return out
