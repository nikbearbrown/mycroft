"""Claim–evidence argument mining from management language."""

from __future__ import annotations

import re
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.db.init_db import get_connection
from ecis.guidance_models.qa_parser import parse_qa_corpus

_CLAIM = re.compile(
    r"(?i)\b(?:we expect|we will|we believe|on track|guidance|outlook|committed to|accelerate)\b"
)
_EVIDENCE = re.compile(
    r"(?i)\b(?:driven by|due to|because|pipeline|percent|%|bps|million|billion|increase of|decrease of)\b"
)
_VAGUE = re.compile(r"(?i)\b(?:approximately|around|various|several|a range|some)\b")
_NUM = re.compile(r"\d")
_SENT = re.compile(r"(?<=[.!?])\s+")


def mine_sentence(text: str, speaker: str = "") -> dict[str, Any] | None:
    blob = (text or "").strip()
    if not blob or not _CLAIM.search(blob):
        return None
    sents = _SENT.split(blob) or [blob]
    claim = next((s for s in sents if _CLAIM.search(s)), sents[0])
    evidence = next((s for s in sents if _EVIDENCE.search(s) and s != claim), "")
    if not evidence and _EVIDENCE.search(claim):
        evidence = claim
    spec = 0.7 if _NUM.search(evidence or claim) else 0.3
    if _VAGUE.search(claim) and not _NUM.search(claim):
        spec = min(spec, 0.25)
    strength = spec * (1.0 if evidence else 0.45)
    return {
        "speaker": speaker,
        "claim": claim.strip(),
        "evidence": (evidence or "").strip(),
        "warrant": "numerical support" if _NUM.search(evidence or claim) else "qualitative support",
        "strength": round(max(0.0, min(1.0, strength)), 4),
        "specificity": spec,
    }


def mine_arguments(ticker: str | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        conn = get_connection("signals")
        query = "SELECT ticker, transcript_date, supporting_quote FROM signals"
        params: list[str] = []
        if ticker:
            query += " WHERE ticker = ?"
            params.append(ticker.upper())
        for row in conn.execute(query, params).fetchall():
            mined = mine_sentence(row["supporting_quote"] or "")
            if not mined:
                continue
            out.append({
                "ticker": (row["ticker"] or "").upper(),
                "transcript_date": (row["transcript_date"] or "")[:10],
                "quarter": quarter_key(row["transcript_date"]),
                **mined,
                "method": "rule",
            })
        conn.close()
    except Exception:
        pass
    for pair in parse_qa_corpus(ticker):
        mined = mine_sentence(pair.get("answer") or "", speaker=pair.get("answer_speaker") or "")
        if not mined:
            continue
        out.append({
            "ticker": (pair.get("ticker") or "").upper(),
            "transcript_date": (pair.get("transcript_date") or "")[:10],
            "quarter": quarter_key(pair.get("transcript_date")),
            **mined,
            "method": "rule",
        })
    return out
