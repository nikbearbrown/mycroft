"""Few-shot exemplar ChromaDB collection for retrieval-augmented prompting."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import chromadb

from ecis.config.settings import settings
from ecis.embedding.embedder import _get_chroma_client, embed_texts

logger = logging.getLogger(__name__)


def get_exemplar_collection() -> chromadb.Collection:
    """Return (or create) the ecis_exemplars ChromaDB collection."""
    client = _get_chroma_client()
    return client.get_or_create_collection(
        name="ecis_exemplars",
        metadata={"hnsw:space": "cosine"},
    )


def add_exemplar(
    exemplar_id: str,
    chunk_text: str,
    direction: str,
    confidence: float,
    supporting_quote: str,
    reasoning_trace: str,
    signal_category: str = "general",
    is_negative: bool = False,
) -> None:
    """Add a single curated exemplar to the collection."""
    collection = get_exemplar_collection()
    embedding = embed_texts([chunk_text])[0]

    collection.upsert(
        ids=[exemplar_id],
        embeddings=[embedding],
        documents=[chunk_text],
        metadatas=[{
            "direction": direction,
            "confidence": confidence,
            "supporting_quote": supporting_quote,
            "reasoning_trace": reasoning_trace,
            "signal_category": signal_category,
            "is_negative": is_negative,
        }],
    )
    logger.info("Added exemplar %s (direction=%s, category=%s)", exemplar_id, direction, signal_category)


def load_exemplars_from_file(path: Path) -> int:
    """Load exemplars from a JSON file.

    Expected format: list of dicts with keys:
        id, chunk_text, direction, confidence, supporting_quote,
        reasoning_trace, signal_category, is_negative
    """
    with open(path, "r", encoding="utf-8") as f:
        exemplars = json.load(f)

    for ex in exemplars:
        add_exemplar(
            exemplar_id=ex["id"],
            chunk_text=ex["chunk_text"],
            direction=ex["direction"],
            confidence=ex["confidence"],
            supporting_quote=ex["supporting_quote"],
            reasoning_trace=ex["reasoning_trace"],
            signal_category=ex.get("signal_category", "general"),
            is_negative=ex.get("is_negative", False),
        )

    logger.info("Loaded %d exemplars from %s", len(exemplars), path)
    return len(exemplars)


def retrieve_exemplars(
    query_text: str,
    *,
    n_results: int = 5,
    signal_category: str | None = None,
    include_negative: bool = True,
) -> list[dict[str, Any]]:
    """Retrieve the most similar exemplars for a given chunk text.

    Returns list of dicts with keys: text, metadata, distance.
    """
    collection = get_exemplar_collection()
    query_embedding = embed_texts([query_text])[0]

    where_filter = None
    conditions = []
    if signal_category:
        conditions.append({"signal_category": {"$eq": signal_category}})
    if not include_negative:
        conditions.append({"is_negative": {"$eq": False}})

    if len(conditions) == 1:
        where_filter = conditions[0]
    elif len(conditions) > 1:
        where_filter = {"$and": conditions}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    if results["documents"]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append({"text": doc, "metadata": meta, "distance": dist})

    return output
