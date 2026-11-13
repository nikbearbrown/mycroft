"""Analyst question vs management answer alignment. MiniLM stays off unless TIMESERIES_LOAD_EMBED=1."""

from __future__ import annotations

import math
import os
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.guidance_models.qa_parser import parse_qa_corpus
from ecis.guidance_models.question_types import classify_question
from ecis.timeseries.analysts import parse_analyst

_LOAD = os.getenv("TIMESERIES_LOAD_EMBED", "").lower() in {"1", "true", "yes"}

EXPECTED = {
    "clarification": 0.55,
    "backward-looking": 0.45,
    "forward-looking": 0.35,
    "confrontational": 0.25,
}


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in (text or "").split() if len(t) > 2}


def lexical_similarity(question: str, answer: str) -> float:
    a, b = _tokens(question), _tokens(answer)
    if not a or not b:
        return 0.0
    return len(a & b) / max(len(a | b), 1)


def _embed_similarity(question: str, answer: str) -> float | None:
    if not _LOAD:
        return None
    try:
        from ecis.embedding.embedder import embed_texts

        q, a = embed_texts([question or "", answer or ""])
        num = sum(x * y for x, y in zip(q, a))
        dq = math.sqrt(sum(x * x for x in q)) or 1.0
        da = math.sqrt(sum(y * y for y in a)) or 1.0
        return max(-1.0, min(1.0, num / (dq * da)))
    except Exception:
        return None


def pair_alignment(question: str, answer: str, question_type: str | None = None) -> dict[str, Any]:
    qtype = question_type or classify_question(question or "")
    embed = _embed_similarity(question, answer)
    sim = embed if embed is not None else lexical_similarity(question, answer)
    expected = EXPECTED.get(qtype, 0.4)
    gap = sim - expected
    return {
        "question_type": qtype,
        "similarity": sim,
        "expected": expected,
        "alignment": gap,
        "flag": "disconnect" if gap < -0.10 else "ok",
        "method": "minilm" if embed is not None else "lexical",
    }


def score_alignment(ticker: str | None = None, pairs: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    rows = pairs if pairs is not None else parse_qa_corpus(ticker)
    out: list[dict[str, Any]] = []
    for row in rows:
        ident = parse_analyst(row.get("question_speaker") or "")
        scored = pair_alignment(row.get("question") or "", row.get("answer") or "", row.get("question_type"))
        out.append({
            "ticker": (row.get("ticker") or "").upper(),
            "quarter": quarter_key(row.get("transcript_date")),
            "transcript_date": (row.get("transcript_date") or "")[:10],
            "analyst_key": ident["analyst_key"],
            **scored,
        })
    return out
