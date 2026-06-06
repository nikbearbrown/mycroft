"""Shared utilities for the News Monitoring Agent conversion.

Purpose: Provide local, auditable helpers used by the converted n8n node scripts.
Input: JSON-compatible records from command arguments, stdin, data/raw/, or data/verified/.
Output: JSON-compatible records for logs/, data/verified/, or reports/generated/.
Side effects: Optional file writes when an output path is supplied; no network calls.
Idempotent: Yes; deterministic helpers overwrite only explicitly supplied output paths.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json_input(sample: Any | None = None) -> Any:
    """Load JSON input from --input, stdin, or a supplied sample object."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON string or path to a JSON file.")
    parser.add_argument("--output", help="Optional path to write JSON output.")
    parser.add_argument("--url", help="Optional URL for ingest nodes.")
    args = parser.parse_args()
    data: Any
    if args.input:
        candidate = Path(args.input)
        data = json.loads(candidate.read_text()) if candidate.exists() else json.loads(args.input)
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        data = json.loads(text) if text else sample
    else:
        data = sample
    return {"data": data, "output": args.output, "url": args.url}


def emit_json(data: Any, output_path: str | None = None) -> None:
    """Print JSON and optionally write the same JSON to an explicit output path."""
    text = json.dumps(data, indent=2, sort_keys=True, default=str)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n")
    print(text)


def stable_id(*parts: Any) -> str:
    """Return a stable SHA-256 identifier for JSON-compatible values."""
    payload = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_article(article: dict[str, Any]) -> dict[str, Any]:
    """Normalize one raw news article into the verified article schema."""
    title = str(article.get("title") or "").strip()
    content = str(article.get("content") or article.get("summary") or article.get("description") or "").strip()
    url = str(article.get("url") or article.get("link") or "").strip()
    published_date = article.get("published_date") or article.get("published") or article.get("updated") or ""
    source_name = article.get("source_name") or article.get("source") or article.get("site_name") or ""
    return {
        "id": article.get("id") or stable_id(url, title, published_date),
        "title": title,
        "content": content,
        "url": url,
        "published_date": str(published_date),
        "source_name": str(source_name),
        "site_name": str(article.get("site_name") or source_name),
        "fetch_lib": str(article.get("fetch_lib") or "local"),
    }


def filter_complete_articles(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep records that have non-empty content."""
    return [item for item in items if item and str(item.get("content") or "").strip()]


def dedupe_articles(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicate articles by URL and title while preserving first-seen order."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in items:
        key = stable_id(item.get("url"), item.get("title"))
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def split_articles(payload: dict[str, Any] | list[Any]) -> list[dict[str, Any]]:
    """Split a payload containing an articles array into normalized article records."""
    articles = payload.get("articles", []) if isinstance(payload, dict) else payload
    return [normalize_article(item) for item in articles if isinstance(item, dict)]


def chunk_text(text: str, size: int = 1000, overlap: int = 120) -> list[str]:
    """Split text into overlapping chunks for local vector-store preparation."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks: list[str] = []
    step = max(size - overlap, 1)
    for start in range(0, len(text), step):
        chunks.append(text[start : start + size])
        if start + size >= len(text):
            break
    return chunks


def build_documents(items: list[dict[str, Any]], collection: str) -> list[dict[str, Any]]:
    """Build chunked document records with metadata for a named collection."""
    docs: list[dict[str, Any]] = []
    for item in items:
        body = f"{item.get('title', '')}\n{item.get('content', '')}".strip()
        for index, chunk in enumerate(chunk_text(body)):
            docs.append(
                {
                    "id": stable_id(collection, item.get("id"), index, chunk),
                    "collection": collection,
                    "text": chunk,
                    "metadata": {
                        "article_id": item.get("id"),
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "published_date": item.get("published_date"),
                        "source_name": item.get("source_name"),
                        "site_name": item.get("site_name"),
                        "sentiment": item.get("sentiment") or {
                            "label": item.get("label"),
                            "score": item.get("score"),
                        },
                        "fetch_lib": item.get("fetch_lib"),
                    },
                }
            )
    return docs


def lexical_sentiment(article: dict[str, Any]) -> dict[str, Any]:
    """Score financial sentiment with a small deterministic local lexicon."""
    text = f"{article.get('title', '')} {article.get('content', '')}".lower()
    positive = ["beat", "growth", "profit", "upgrade", "surge", "record", "strong", "buy", "raise"]
    negative = ["miss", "loss", "downgrade", "lawsuit", "decline", "weak", "sell", "cut", "probe"]
    pos = sum(text.count(word) for word in positive)
    neg = sum(text.count(word) for word in negative)
    if pos > neg:
        label = "positive"
    elif neg > pos:
        label = "negative"
    else:
        label = "neutral"
    score = abs(pos - neg) / max(pos + neg, 1)
    output = dict(article)
    output["label"] = label
    output["score"] = round(float(score), 4)
    output["sentiment"] = {"label": label, "score": output["score"], "method": "local_lexicon"}
    return output


def embedding_stub(record: dict[str, Any], model: str) -> dict[str, Any]:
    """Create a deterministic 16-dimensional placeholder embedding from text."""
    text = str(record.get("text") or record.get("content") or record)
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    vector = [round((byte / 255.0) * 2 - 1, 6) for byte in digest[:16]]
    return {"model": model, "embedding_dimensions": len(vector), "embedding": vector}


def refine_query(question: str) -> dict[str, list[str]]:
    """Create one to three concise retrieval queries from a natural-language question."""
    cleaned = re.sub(r"\b(today|latest|please|can you|tell me about)\b", " ", question, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ?.")
    parts = [cleaned] if cleaned else [question.strip()]
    tokens = [token for token in re.findall(r"[A-Za-z0-9$.-]+", cleaned) if len(token) > 2]
    if len(tokens) > 4:
        parts.append(" ".join(tokens[:6]))
    return {"refined_queries": list(dict.fromkeys(parts))[:3]}


def metadata_filter(question: str, now: datetime | None = None) -> dict[str, Any]:
    """Translate common time and sentiment words into a simple Qdrant-style filter."""
    now = now or datetime.now(timezone.utc)
    lowered = question.lower()
    must: list[dict[str, Any]] = []
    for sentiment in ("positive", "neutral", "negative"):
        if sentiment in lowered:
            must.append({"key": "metadata.sentiment.label", "match": {"value": sentiment}})
    if "today" in lowered or "latest" in lowered:
        must.append({"key": "metadata.published_date", "range": {"gte": now.date().isoformat()}})
    return {"filter": {"must": must}}


def answer_from_documents(question: str, documents: list[dict[str, Any]], agent_name: str) -> dict[str, Any]:
    """Produce a source-grounded extractive answer from local document records."""
    terms = {term.lower() for term in re.findall(r"[A-Za-z0-9$.-]+", question) if len(term) > 2}
    scored: list[tuple[int, dict[str, Any]]] = []
    for doc in documents:
        haystack = json.dumps(doc, default=str).lower()
        scored.append((sum(1 for term in terms if term in haystack), doc))
    matches = [doc for score, doc in sorted(scored, key=lambda item: item[0], reverse=True) if score > 0][:5]
    return {
        "agent": agent_name,
        "question": question,
        "answer": "Local retrieval found relevant articles; human review required before investment interpretation."
        if matches
        else "No relevant local articles were found for the question.",
        "sources": [match.get("metadata", match) for match in matches],
    }


def read_csv_questions(path: str) -> list[dict[str, str]]:
    """Read a CSV of questions from disk for RAG evaluation."""
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
