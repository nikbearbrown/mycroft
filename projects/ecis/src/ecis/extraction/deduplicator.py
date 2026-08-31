"""Semantic deduplication of signals within a single transcript."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from ecis.embedding.embedder import embed_texts

logger = logging.getLogger(__name__)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a), np.array(b)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def deduplicate_signals(
    signals: list[dict[str, Any]],
    *,
    similarity_threshold: float = 0.90,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:

    if len(signals) <= 1:
        return signals, []

    quotes = [s.get("supporting_quote", s.get("text", "")) for s in signals]
    embeddings = embed_texts(quotes)

    for sig, emb in zip(signals, embeddings):
        sig["quote_embedding"] = emb

    merged_indices: set[int] = set()
    flagged: list[dict[str, Any]] = []

    for i in range(len(signals)):
        if i in merged_indices:
            continue
        for j in range(i + 1, len(signals)):
            if j in merged_indices:
                continue

            sim = cosine_similarity(embeddings[i], embeddings[j])
            if sim < similarity_threshold:
                continue

            dir_i = signals[i].get("direction")
            dir_j = signals[j].get("direction")

            if dir_i == dir_j:
                conf_i = signals[i].get("confidence_raw", signals[i].get("confidence", 0.0))
                conf_j = signals[j].get("confidence_raw", signals[j].get("confidence", 0.0))
                loser = j if conf_i >= conf_j else i
                merged_indices.add(loser)
                winner = i if loser == j else j
                signals[winner].setdefault("merged_from", []).append(
                    signals[loser].get("chunk_index")
                )
                logger.info(
                    "Merged duplicate signals (chunks %s and %s, sim=%.3f)",
                    signals[i].get("chunk_index"),
                    signals[j].get("chunk_index"),
                    sim,
                )
            else:
                flagged.append({
                    "signal_a": signals[i],
                    "signal_b": signals[j],
                    "similarity": sim,
                    "reason": f"Direction disagreement ({dir_i} vs {dir_j}) at similarity {sim:.3f}",
                })
                logger.warning(
                    "Flagged conflicting duplicate (chunks %s and %s, sim=%.3f, %s vs %s)",
                    signals[i].get("chunk_index"),
                    signals[j].get("chunk_index"),
                    sim,
                    dir_i,
                    dir_j,
                )

    deduplicated = [s for i, s in enumerate(signals) if i not in merged_indices]
    return deduplicated, flagged
