"""FinBERT sentiment reader for financial text chunks."""

from __future__ import annotations

import logging
from typing import Any

import torch

from ecis.config.settings import settings
from ecis.schemas.signal import GuidanceDirection

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None
_LABEL_MAP = {0: "positive", 1: "negative", 2: "neutral"}
_DIRECTION_MAP = {
    "positive": GuidanceDirection.RAISED,
    "negative": GuidanceDirection.LOWERED,
    "neutral": GuidanceDirection.MAINTAINED,
}


def _load_model():
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer

    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    logger.info("Loading FinBERT model: %s", settings.finbert_model_name)
    _tokenizer = AutoTokenizer.from_pretrained(settings.finbert_model_name)
    _model = AutoModelForSequenceClassification.from_pretrained(settings.finbert_model_name)
    _model.eval()

    if torch.cuda.is_available():
        _model = _model.cuda()
        logger.info("FinBERT loaded on CUDA")
    elif torch.backends.mps.is_available():
        _model = _model.to("mps")
        logger.info("FinBERT loaded on MPS")
    else:
        logger.info("FinBERT loaded on CPU")

    return _model, _tokenizer


def read_chunk(chunk_text: str) -> dict[str, Any]:
    if len(chunk_text.split()) < 5:
        return {
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 1.0,
            "dominant": "neutral",
            "confidence": 0.0,
            "direction": None,
        }

    model, tokenizer = _load_model()
    device = next(model.parameters()).device

    inputs = tokenizer(
        chunk_text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1).squeeze().cpu().tolist()

    scores = {
        "positive": probs[0],
        "negative": probs[1],
        "neutral": probs[2],
    }
    dominant = max(scores, key=scores.get)
    confidence = scores[dominant]

    direction = _DIRECTION_MAP.get(dominant) if confidence > 0.5 else None

    return {
        **scores,
        "dominant": dominant,
        "confidence": confidence,
        "direction": direction,
    }


def read_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not chunks:
        return []

    model, tokenizer = _load_model()
    device = next(model.parameters()).device
    batch_size = settings.finbert_batch_size

    results: list[dict[str, Any]] = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c["text"] for c in batch]

        valid_indices = [j for j, t in enumerate(texts) if len(t.split()) >= 5]
        if not valid_indices:
            for j, c in enumerate(batch):
                results.append({
                    "chunk_index": c.get("chunk_index", i + j),
                    "positive": 0.0,
                    "negative": 0.0,
                    "neutral": 1.0,
                    "dominant": "neutral",
                    "confidence": 0.0,
                    "direction": None,
                })
            continue

        valid_texts = [texts[j] for j in valid_indices]
        inputs = tokenizer(
            valid_texts,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        ).to(device)

        with torch.no_grad():
            outputs = model(**inputs)
            all_probs = torch.softmax(outputs.logits, dim=-1).cpu().tolist()

        prob_map = {vi: p for vi, p in zip(valid_indices, all_probs)}
        for j, c in enumerate(batch):
            if j in prob_map:
                probs = prob_map[j]
                scores = {"positive": probs[0], "negative": probs[1], "neutral": probs[2]}
                dominant = max(scores, key=scores.get)
                confidence = scores[dominant]
                direction = _DIRECTION_MAP.get(dominant) if confidence > 0.5 else None
                results.append({
                    "chunk_index": c.get("chunk_index", i + j),
                    **scores,
                    "dominant": dominant,
                    "confidence": confidence,
                    "direction": direction,
                })
            else:
                results.append({
                    "chunk_index": c.get("chunk_index", i + j),
                    "positive": 0.0,
                    "negative": 0.0,
                    "neutral": 1.0,
                    "dominant": "neutral",
                    "confidence": 0.0,
                    "direction": None,
                })

    return _flag_adjacent_anomalies(results)


def _flag_adjacent_anomalies(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(results, key=lambda r: r.get("chunk_index", 0))
    for i, row in enumerate(ordered):
        row["consistency_anomaly"] = False
        if i == 0 or i == len(ordered) - 1:
            continue
        prev, nxt = ordered[i - 1], ordered[i + 1]
        if (
            row.get("dominant") not in (None, "neutral")
            and prev.get("dominant") == nxt.get("dominant")
            and row.get("dominant") != prev.get("dominant")
            and (row.get("confidence") or 0) > 0.6
            and (prev.get("confidence") or 0) > 0.5
            and (nxt.get("confidence") or 0) > 0.5
        ):
            row["consistency_anomaly"] = True
            row["confidence"] = min(row.get("confidence") or 0, 0.4)
            logger.info(
                "FinBERT adjacent anomaly at chunk %s (%s amid %s)",
                row.get("chunk_index"),
                row.get("dominant"),
                prev.get("dominant"),
            )
    return ordered
