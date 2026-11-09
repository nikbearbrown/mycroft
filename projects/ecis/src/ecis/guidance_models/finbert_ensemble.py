"""Average several FinBERT-style polarity scores. Soft-fails to a lexicon."""

from __future__ import annotations

import os
import re
from typing import Any

from ecis.config.settings import settings

_POS = re.compile(r"(?i)\b(?:strong|grow|growth|improve|upside|beat|exceed|positive|raise|gain)\b")
_NEG = re.compile(r"(?i)\b(?:weak|decline|pressure|miss|downside|challenging|lower|loss|headwind)\b")

_LOAD = os.getenv("GUIDANCE_LOAD_FINBERT", "").lower() in {"1", "true", "yes"}
_EXTRA = [m.strip() for m in os.getenv("FINBERT_ENSEMBLE", "").split(",") if m.strip()]


def lexicon_polarity(text: str) -> float:
    blob = text or ""
    pos = len(_POS.findall(blob))
    neg = len(_NEG.findall(blob))
    denom = pos + neg
    if denom == 0:
        return 0.0
    return (pos - neg) / denom


def _one_finbert(text: str, model_name: str) -> float | None:
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        import torch

        tok = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        model.eval()
        inputs = tok(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            probs = torch.softmax(model(**inputs).logits, dim=-1).squeeze().tolist()

        if isinstance(probs, float):
            return None
        pos, neg = float(probs[0]), float(probs[1])
        return pos - neg
    except Exception:
        return None


def ensemble_polarity(text: str) -> dict[str, Any]:
    scores = [lexicon_polarity(text)]
    method = "lexicon"
    if _LOAD:
        names = [settings.finbert_model_name, * _EXTRA]
        seen = []
        for name in names:
            if name in seen:
                continue
            seen.append(name)
            val = _one_finbert(text, name)
            if val is not None:
                scores.append(val)
                method = "ensemble" if len(scores) > 2 else "finbert"
    mean = sum(scores) / len(scores)
    if len(scores) == 1:
        var = 0.0
    else:
        var = sum((s - mean) ** 2 for s in scores) / (len(scores) - 1)
    return {
        "polarity": max(-1.0, min(1.0, mean)),
        "variance": var,
        "n_members": len(scores),
        "method": method,
    }
