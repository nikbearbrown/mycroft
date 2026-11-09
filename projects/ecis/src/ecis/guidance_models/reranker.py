"""Question-answer relevance: cross-encoder when available, lexical fallback otherwise."""

from __future__ import annotations

import math
import os
import re
from functools import lru_cache

_TOKEN_RE = re.compile(r"[A-Za-z]{3,}")
_CROSS_ENCODER_NAME = os.getenv("QA_CROSS_ENCODER", "cross-encoder/ms-marco-MiniLM-L-6-v2")
_LOAD_CROSS_ENCODER = os.getenv("GUIDANCE_LOAD_CROSS_ENCODER", "").lower() in {"1", "true", "yes"}

_encoder = None
_encoder_failed = False


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text or "")}


def lexical_relevance(question: str, answer: str) -> float:
    q = _tokens(question)
    a = _tokens(answer)
    if not q or not a:
        return 0.0
    overlap = len(q & a) / math.sqrt(len(q) * len(a))
    return max(0.0, min(1.0, overlap))


@lru_cache(maxsize=1)
def _try_cross_encoder():
    global _encoder, _encoder_failed
    if _encoder is not None or _encoder_failed or not _LOAD_CROSS_ENCODER:
        return _encoder
    try:
        from sentence_transformers import CrossEncoder

        _encoder = CrossEncoder(_CROSS_ENCODER_NAME)
    except Exception:
        _encoder_failed = True
        _encoder = None
    return _encoder


def relevance_score(question: str, answer: str) -> tuple[float, str]:
    """Return (0–1 relevance, method). Soft-fails to lexical overlap."""
    model = _try_cross_encoder()
    if model is not None:
        try:
            raw = float(model.predict([(question, answer)]))
            score = 1.0 / (1.0 + math.exp(-raw))
            return max(0.0, min(1.0, score)), "cross_encoder"
        except Exception:
            pass
    return lexical_relevance(question, answer), "lexical"
