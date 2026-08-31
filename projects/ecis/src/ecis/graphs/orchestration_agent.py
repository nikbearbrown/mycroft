"""Escalation classifier: categorises chunks into A/B/C/D based on fast-pass results."""

from __future__ import annotations

import logging
from typing import Any

from ecis.db.init_db import get_connection
from ecis.schemas.signal import FastPassResult, GuidanceDirection
from ecis.schemas.state import EscalationCategory

logger = logging.getLogger(__name__)


def _load_thresholds() -> dict[str, float]:
    """Load adaptive escalation thresholds from SQLite."""
    try:
        conn = get_connection("agents")
        rows = conn.execute("SELECT param_name, value FROM escalation_thresholds").fetchall()
        conn.close()
        if rows:
            return {r["param_name"]: r["value"] for r in rows}
    except Exception:
        pass

    return {
        "finbert_confidence_min": 0.6,
        "keyword_confidence_min": 0.5,
        "escalation_agreement_threshold": 0.7,
    }


def classify_chunk(fast_pass: FastPassResult) -> str:
    """Classify a chunk into escalation category A, B, C, or D.

    Category A: Both readers agree on direction.
    Category B: One reader flagged, or confidence is low.
    Category C: Readers disagree on direction.
    Category D: Neither reader detected anything.
    """
    thresholds = _load_thresholds()
    finbert_min = thresholds.get("finbert_confidence_min", 0.6)

    kw_detected = fast_pass.keyword_matched
    kw_direction = fast_pass.keyword_direction

    fb_detected = fast_pass.finbert_direction is not None
    fb_direction = fast_pass.finbert_direction
    fb_confident = fast_pass.finbert_confidence >= finbert_min

    if not kw_detected and not fb_detected:
        return EscalationCategory.D

    if kw_detected and fb_detected and fb_confident:
        if kw_direction != fb_direction:
            return EscalationCategory.C

    if kw_detected and fb_detected and fb_confident:
        if kw_direction == fb_direction:
            return EscalationCategory.A

    return EscalationCategory.B


def classify_chunks(
    fast_pass_results: list[FastPassResult],
    *,
    ticker: str | None = None,
    transcript_date: str | None = None,
) -> dict[str, list[int]]:
    """Classify all chunks and return index lists per category."""
    categories: dict[str, list[int]] = {
        EscalationCategory.A: [],
        EscalationCategory.B: [],
        EscalationCategory.C: [],
        EscalationCategory.D: [],
    }

    for fp in fast_pass_results:
        cat = classify_chunk(fp)
        categories[cat].append(fp.chunk_index)
        logger.debug("Chunk %d → Category %s", fp.chunk_index, cat)

    _log_classification(categories)
    if ticker:
        persist_classifications(ticker, transcript_date, fast_pass_results, categories)
    return categories


def persist_classifications(
    ticker: str,
    transcript_date: str | None,
    fast_pass_results: list[FastPassResult],
    categories: dict[str, list[int]],
) -> None:
    """Write per-chunk escalation decisions for the learning graph."""
    index_to_cat: dict[int, str] = {}
    for cat, indices in categories.items():
        for idx in indices:
            index_to_cat[idx] = cat

    try:
        conn = get_connection("agents")
        for fp in fast_pass_results:
            cat = index_to_cat.get(fp.chunk_index, EscalationCategory.D)
            fb_dir = fp.finbert_direction.value if fp.finbert_direction else None
            conn.execute(
                """INSERT INTO chunk_classifications
                   (ticker, transcript_date, chunk_index, category,
                    keyword_matched, keyword_confidence, finbert_confidence,
                    finbert_direction)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    ticker,
                    transcript_date,
                    fp.chunk_index,
                    cat,
                    1 if fp.keyword_matched else 0,
                    fp.keyword_confidence,
                    fp.finbert_confidence,
                    fb_dir,
                ),
            )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.error("Failed to persist chunk classifications: %s", exc)


def _log_classification(categories: dict[str, list[int]]) -> None:
    """Log the classification summary to the agent audit database."""
    summary = {k: len(v) for k, v in categories.items()}
    total = sum(summary.values())
    logger.info(
        "Escalation classification: A=%d B=%d C=%d D=%d (total=%d, LLM-bound=%d, skipped=%d)",
        summary.get("A", 0),
        summary.get("B", 0),
        summary.get("C", 0),
        summary.get("D", 0),
        total,
        summary.get("A", 0) + summary.get("B", 0),
        summary.get("D", 0),
    )

    try:
        import json
        conn = get_connection("agents")
        conn.execute(
            """INSERT INTO agent_actions (agent_name, observation, action_taken, result)
               VALUES (?, ?, ?, ?)""",
            (
                "orchestration_agent",
                f"Classified {total} chunks",
                "escalation_classification",
                json.dumps(summary),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.error("Failed to log classification: %s", exc)
