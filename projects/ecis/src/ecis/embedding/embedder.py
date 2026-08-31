"""MiniLM embedding generation and ChromaDB transcript chunk storage."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import chromadb

from ecis.config.settings import settings

logger = logging.getLogger(__name__)

_embed_model = None
_chroma_client = None


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer(settings.embedding_model_name)
    return _embed_model


def _get_chroma_client() -> chromadb.ClientAPI:
    global _chroma_client
    if _chroma_client is None:
        if settings.chroma_persist_dir:
            _chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        else:
            _chroma_client = chromadb.Client()
    return _chroma_client


def get_transcript_collection() -> chromadb.Collection:
    """Return (or create) the ecis_transcripts ChromaDB collection."""
    client = _get_chroma_client()
    return client.get_or_create_collection(
        name="ecis_transcripts",
        metadata={"hnsw:space": "cosine"},
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate MiniLM embeddings for a batch of texts."""
    model = _get_embed_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


def embed_single(text: str) -> list[float]:
    """Generate a MiniLM embedding for a single text."""
    return embed_texts([text])[0]


def store_chunks(chunks: list[dict[str, Any]]) -> int:
    """Embed and store transcript chunks in ChromaDB.

    Each chunk dict must have: chunk_index, text, ticker, transcript_date,
    section_label, speaker, char_start, char_end, source_file.

    Returns the number of chunks stored.
    """
    if not chunks:
        return 0

    collection = get_transcript_collection()
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    ids = [
        f"{c['ticker']}_{c['transcript_date']}_{Path(c['source_file']).stem}_{c['chunk_index']}"
        for c in chunks
    ]

    metadatas = [
        {
            "ticker": c["ticker"],
            "transcript_date": c["transcript_date"],
            "section_label": c["section_label"],
            "speaker": c["speaker"],
            "chunk_index": c["chunk_index"],
            "char_start": c["char_start"],
            "char_end": c["char_end"],
            "source_file": c["source_file"],
        }
        for c in chunks
    ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    logger.info("Stored %d chunks in ecis_transcripts", len(chunks))
    return len(chunks)


def query_similar(
    query_text: str,
    *,
    n_results: int = 5,
    ticker: str | None = None,
    section_label: str | None = None,
    date_range: tuple[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Query the transcript collection by semantic similarity with optional metadata filters.

    Returns list of dicts with keys: text, metadata, distance.
    """
    collection = get_transcript_collection()
    query_embedding = embed_single(query_text)

    where_filters: dict | None = None
    conditions = []
    if ticker:
        conditions.append({"ticker": {"$eq": ticker}})
    if section_label:
        conditions.append({"section_label": {"$eq": section_label}})
    if date_range:
        conditions.append({"transcript_date": {"$gte": date_range[0]}})
        conditions.append({"transcript_date": {"$lte": date_range[1]}})

    if len(conditions) == 1:
        where_filters = conditions[0]
    elif len(conditions) > 1:
        where_filters = {"$and": conditions}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filters,
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


def embed_and_store_from_file(chunks_json_path: Path) -> int:
    """Load chunks from a JSON file and store them in ChromaDB."""
    with open(chunks_json_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return store_chunks(chunks)
