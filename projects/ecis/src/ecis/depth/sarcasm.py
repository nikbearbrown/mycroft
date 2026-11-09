"""Q&A sarcasm: surface-positive vs challenging context. RoBERTa optional."""

from __future__ import annotations

import os
import re
from collections import defaultdict
from typing import Any

from ecis.guidance_models.finbert_ensemble import lexicon_polarity
from ecis.guidance_models.qa_parser import parse_qa_corpus
from ecis.analytics.features import quarter_key

_LOAD = os.getenv("ADVANCED_LOAD_ROBERTA", "").lower() in {"1", "true", "yes"}
_CHALLENGE = re.compile(
    r"(?i)\b(?:how\s+do\s+you\s+justify|why\s+should|shortfall|miss|but\s+you|"
    r"really\?|seriously|come\s+on)\b"
)
_POSITIVE = re.compile(r"(?i)\b(?:great|sure|wonderful|pleased|excited|strong)\b")


def score_exchange(question: str, answer: str) -> dict[str, Any]:
    if _LOAD:
        try:
            from transformers import pipeline

            clf = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-irony")
            pred = clf((answer or "")[:400])[0]
            sarcastic = "irony" in str(pred.get("label", "")).lower() or float(pred.get("score", 0)) > 0.7
            return {"sarcastic": int(sarcastic), "method": "roberta", "score": float(pred.get("score", 0))}
        except Exception:
            pass
    q, a = question or "", answer or ""
    surface = lexicon_polarity(a)
    sarcastic = bool(_CHALLENGE.search(q) and (_POSITIVE.search(a) or surface > 0.15))
    return {
        "sarcastic": int(sarcastic),
        "method": "rule",
        "score": 0.8 if sarcastic else 0.1,
        "question": q[:200],
        "answer": a[:200],
    }


def detect_sarcasm(ticker: str | None = None) -> list[dict[str, Any]]:
    pairs = parse_qa_corpus(ticker)
    out = []
    by_call: dict[tuple[str, str], int] = defaultdict(int)
    n_call: dict[tuple[str, str], int] = defaultdict(int)
    scored = []
    for pair in pairs:
        rec = score_exchange(pair.get("question") or "", pair.get("answer") or "")
        rec.update({
            "ticker": pair.get("ticker"),
            "transcript_date": pair.get("transcript_date"),
            "quarter": quarter_key(pair.get("transcript_date")),
        })
        scored.append(rec)
        key = ((pair.get("ticker") or "").upper(), (pair.get("transcript_date") or "")[:10])
        n_call[key] += 1
        by_call[key] += rec["sarcastic"]

    for rec in scored:
        key = ((rec.get("ticker") or "").upper(), (rec.get("transcript_date") or "")[:10])
        rec["call_sarcasm_rate"] = by_call[key] / max(n_call[key], 1)
        rec["contentious"] = int(rec["call_sarcasm_rate"] >= 0.25)
    return scored
