"""Conflict resolution logic for Category C chunks (reader disagreement)."""

from __future__ import annotations

import json
import logging
from typing import Any

import ollama

from ecis.config.settings import settings
from ecis.db.init_db import get_connection
from ecis.embedding.embedder import query_similar

logger = logging.getLogger(__name__)

_RESOLUTION_PROMPT = """You are resolving a disagreement between two extraction methods analysing an earnings call transcript.

**Keyword reader** found: {keyword_info}
**Sentiment model (FinBERT)** found: {finbert_info}

Here is the surrounding context:

Preceding chunk:
{preceding_chunk}

Conflicting chunk:
{chunk_text}

Following chunk:
{following_chunk}

Determine:
1. What actually happened in this passage?
2. Which reader was correct?
3. What is the actual guidance direction?

Respond with JSON only:
{{
  "resolved_direction": "raised" | "lowered" | "maintained" | "none",
  "confidence": <float 0.0 to 1.0>,
  "vindicated_reader": "keyword" | "finbert",
  "reasoning": "<explanation of why one reader was misled>"
}}"""


def retrieve_surrounding_chunks(
    ticker: str,
    chunk_index: int,
) -> tuple[str, str]:
    """Retrieve the chunks immediately before and after the given chunk from ChromaDB."""
    preceding = ""
    following = ""

    try:
        results = query_similar(
            "",
            n_results=20,
            ticker=ticker,
        )
        for r in results:
            idx = r["metadata"].get("chunk_index", -1)
            if idx == chunk_index - 1:
                preceding = r["text"]
            elif idx == chunk_index + 1:
                following = r["text"]
    except Exception as exc:
        logger.debug("Context retrieval failed: %s", exc)

    return preceding, following


def resolve_conflict(
    chunk_text: str,
    ticker: str,
    chunk_index: int,
    keyword_result: dict[str, Any],
    finbert_result: dict[str, Any],
) -> dict[str, Any]:
    """Resolve a keyword vs FinBERT disagreement using the LLM."""
    preceding, following = retrieve_surrounding_chunks(ticker, chunk_index)

    keyword_info = (
        f"Direction: {keyword_result.get('direction', 'N/A')}, "
        f"Phrases: {keyword_result.get('phrases', [])}"
    )
    finbert_info = (
        f"Direction: {finbert_result.get('direction', 'N/A')}, "
        f"Positive: {finbert_result.get('positive', 0):.3f}, "
        f"Negative: {finbert_result.get('negative', 0):.3f}, "
        f"Neutral: {finbert_result.get('neutral', 0):.3f}"
    )

    prompt = _RESOLUTION_PROMPT.format(
        keyword_info=keyword_info,
        finbert_info=finbert_info,
        preceding_chunk=preceding or "(not available)",
        chunk_text=chunk_text,
        following_chunk=following or "(not available)",
    )

    try:
        response = ollama.chat(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "You are a financial analyst resolving extraction conflicts. Respond with JSON only."},
                {"role": "user", "content": prompt},
            ],
            options={"temperature": 0.0},
        )
        raw = response["message"]["content"]
    except Exception as exc:
        logger.error("Conflict resolution LLM call failed: %s", exc)
        return {
            "resolved_direction": "none",
            "confidence": 0.0,
            "vindicated_reader": "unknown",
            "reasoning": f"LLM call failed: {exc}",
        }

    from ecis.readers.llm_reader import _parse_llm_json
    result = _parse_llm_json(raw)

    _record_vindication(
        ticker=ticker,
        chunk_index=chunk_index,
        vindicated=result.get("vindicated_reader", "unknown"),
        defeated="finbert" if result.get("vindicated_reader") == "keyword" else "keyword",
        reasoning=result.get("reasoning", ""),
        keyword_direction=keyword_result.get("direction"),
        finbert_direction=str(finbert_result.get("direction")),
    )

    return result


def _record_vindication(
    ticker: str,
    chunk_index: int,
    vindicated: str,
    defeated: str,
    reasoning: str,
    keyword_direction: str | None = None,
    finbert_direction: str | None = None,
) -> None:
    """Write a vindication record to the agents database."""
    conflict_type = f"{keyword_direction or 'N/A'}_vs_{finbert_direction or 'N/A'}"
    try:
        conn = get_connection("agents")
        conn.execute(
            """INSERT INTO vindication_records
               (ticker, chunk_index, conflict_type, vindicated_reader, defeated_reader, reasoning)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (ticker, chunk_index, conflict_type, vindicated, defeated, reasoning),
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.error("Failed to record vindication: %s", exc)
