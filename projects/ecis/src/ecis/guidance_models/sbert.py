"""Financial Q&A embeddings. Uses MiniLM; optional local adapter if one was trained."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ecis.guidance_models.qa_parser import parse_qa_corpus
from ecis.config.settings import settings

FINETUNE_SKIPPED = True
ADAPTER_DIR = Path(os.getenv("QA_SBERT_ADAPTER", str(settings.data_dir / "models" / "qa-sbert")))


def collect_training_pairs(ticker: str | None = None) -> list[dict[str, str]]:
    """Positive Q&A pairs from the normalised corpus. Ready for a later fine-tune."""
    rows = []
    for pair in parse_qa_corpus(ticker):
        if pair.get("question") and pair.get("answer"):
            rows.append({"question": pair["question"], "answer": pair["answer"]})
    return rows


def retrieval_accuracy(pairs: list[dict[str, str]], embeds_q: list[list[float]], embeds_a: list[list[float]]) -> float:
    """Leave-one-in retrieval: question should rank its own answer first."""
    if not pairs or len(embeds_q) != len(embeds_a):
        return 0.0
    hits = 0
    for i, qv in enumerate(embeds_q):
        best_j = 0
        best = -1e9
        for j, av in enumerate(embeds_a):
            score = sum(a * b for a, b in zip(qv, av))
            if score > best:
                best = score
                best_j = j
        if best_j == i:
            hits += 1
    return hits / len(pairs)


def embed_qa(texts: list[str]) -> list[list[float]]:
    """Embed with a local financial adapter when present, else stock MiniLM."""
    if ADAPTER_DIR.exists() and any(ADAPTER_DIR.iterdir()):
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(str(ADAPTER_DIR))
            return model.encode(texts, show_progress_bar=False, convert_to_numpy=True).tolist()
        except Exception:
            pass
    from ecis.embedding.embedder import embed_texts

    return embed_texts(texts)


def finetune_status() -> dict[str, Any]:
    return {
        "skipped": FINETUNE_SKIPPED,
        "adapter_dir": str(ADAPTER_DIR),
        "adapter_present": ADAPTER_DIR.exists() and any(ADAPTER_DIR.iterdir()) if ADAPTER_DIR.exists() else False,
        "base_model": settings.embedding_model_name,
        "note": "Fine-tuning is not run in this repo. Drop a trained adapter at QA_SBERT_ADAPTER to use it.",
    }
