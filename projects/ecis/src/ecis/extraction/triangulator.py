"""Multi-reader signal triangulation with dynamic weighting."""

from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import date, datetime
from typing import Any

from ecis.config.settings import settings
from ecis.db.init_db import get_connection
from ecis.extraction.chunk_quality import score_chunk
from ecis.extraction.speaker_roles import classify_speaker, speaker_weight
from ecis.schemas.signal import (
    GuidanceDirection,
    SectionLabel,
    SignalRecord,
    SourceMethod,
)

logger = logging.getLogger(__name__)


def _load_weights() -> dict[str, float]:
    """Load current reader weights from SQLite (or use defaults)."""
    try:
        conn = get_connection("agents")
        rows = conn.execute("SELECT reader_name, weight FROM reader_weights").fetchall()
        conn.close()
        if rows:
            return {r["reader_name"]: r["weight"] for r in rows}
    except Exception:
        pass

    return {
        "keyword": settings.weight_keyword,
        "finbert": settings.weight_finbert,
        "llm": settings.weight_llm,
        "agreement": settings.weight_agreement,
    }


def triangulate_chunk(
    chunk: dict[str, Any],
    keyword_result: dict[str, Any] | None,
    finbert_result: dict[str, Any] | None,
    llm_result: dict[str, Any] | None,
    ner_result: dict[str, Any] | None = None,
) -> SignalRecord | None:
    """Combine reader outputs for a single chunk into a unified signal.

    Returns None if no reader detected a signal.
    """
    weights = _load_weights()
    votes: list[tuple[str, float]] = []  # (direction, weighted_confidence)

    if keyword_result and keyword_result.get("matched"):
        direction = keyword_result["direction"]
        conf = keyword_result.get("confidence", 1.0) * weights.get("keyword", 0.15)
        votes.append((direction, conf))

    if finbert_result and finbert_result.get("direction"):
        direction = finbert_result["direction"]
        if isinstance(direction, GuidanceDirection):
            direction = direction.value
        conf = finbert_result.get("confidence", 0.0) * weights.get("finbert", 0.20)
        votes.append((direction, conf))

    if llm_result and llm_result.get("direction") not in (None, "none"):
        direction = llm_result["direction"]
        llm_w = settings.llm_weight_for(llm_result.get("llm_model"), weights)
        conf = llm_result.get("confidence", 0.0) * llm_w
        votes.append((direction, conf))

    if not votes:
        return None

    direction_scores: dict[str, float] = {}
    for direction, conf in votes:
        direction_scores[direction] = direction_scores.get(direction, 0.0) + conf

    directions = [v[0] for v in votes]
    direction_counter = Counter(directions)
    best_direction = max(direction_scores, key=direction_scores.get)

    if direction_counter[best_direction] == len(votes) and len(votes) > 1:
        direction_scores[best_direction] += weights.get("agreement", 0.15)

    total_weight = sum(weights.get(k, 0.0) for k in ["keyword", "finbert", "llm", "agreement"])
    raw_confidence = min(direction_scores[best_direction] / total_weight, 1.0)

    role = classify_speaker(chunk.get("speaker", ""))
    spk_w = speaker_weight(chunk.get("speaker", ""), role)
    quality = score_chunk(chunk)
    quality_score = quality["chunk_quality"]
    raw_confidence = min(raw_confidence * spk_w * quality_score, 1.0)

    supporting_quote = ""
    reasoning_trace = ""
    if llm_result and llm_result.get("direction") == best_direction:
        supporting_quote = llm_result.get("supporting_quote", "")
        reasoning_trace = llm_result.get("reasoning", "")
    elif keyword_result and keyword_result.get("matched"):
        supporting_quote = "; ".join(keyword_result.get("phrases", []))

    if not supporting_quote:
        supporting_quote = chunk.get("text", "")[:200]

    llm_model = (llm_result.get("llm_model") if llm_result else None) or settings.llm_model
    raw_confidence = round(raw_confidence, 4)
    low_confidence = raw_confidence < settings.min_scorecard_confidence

    try:
        signal = SignalRecord(
            ticker=chunk.get("ticker", "UNKNOWN"),
            direction=GuidanceDirection(best_direction),
            confidence_raw=raw_confidence,
            source_method=SourceMethod.TRIANGULATED,
            supporting_quote=supporting_quote,
            section_label=SectionLabel(chunk.get("section_label", "prepared_remarks")),
            speaker=chunk.get("speaker", ""),
            speaker_role=role,
            speaker_weight=spk_w,
            chunk_quality=quality_score,
            transcript_date=date.fromisoformat(chunk.get("transcript_date", str(date.today()))),
            chunk_index=chunk.get("chunk_index", 0),
            character_offsets=(chunk.get("char_start", 0), max(chunk.get("char_end", 1), 1)),
            reasoning_trace=reasoning_trace or None,
            ner_entities=ner_result.get("entities") if ner_result else None,
            self_consistency_votes=llm_result.get("self_consistency_votes") if llm_result else None,
            verification_status=llm_result.get("verification_status") if llm_result else None,
            llm_model=llm_model,
            content_hash=chunk.get("content_hash"),
            retry_count=int((llm_result or {}).get("retry_count") or 0),
            provenance=(llm_result or {}).get("provenance"),
            raw_llm_output=(llm_result or {}).get("raw_llm_output"),
            low_confidence=low_confidence,
        )
    except Exception as exc:
        logger.error("Failed to create SignalRecord for chunk %s: %s", chunk.get("chunk_index"), exc)
        return None

    return signal


def log_signal(signal: SignalRecord) -> int:
    """Write a validated signal to the append-only decision log. Returns the signal_id."""
    conn = get_connection("signals")
    cursor = conn.execute(
        """INSERT INTO signals
           (ticker, direction, confidence_raw, confidence_calibrated,
            source_method, supporting_quote, section_label, speaker,
            speaker_role, speaker_weight, chunk_quality, trend,
            transcript_date, chunk_index, char_start, char_end,
            reasoning_trace, ner_entities, self_consistency_votes,
            verification_status, llm_model, content_hash, retry_count,
            provenance, raw_llm_output, low_confidence)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            signal.ticker,
            signal.direction.value,
            signal.confidence_raw,
            signal.confidence_calibrated,
            signal.source_method.value,
            signal.supporting_quote,
            signal.section_label.value,
            signal.speaker,
            signal.speaker_role,
            signal.speaker_weight,
            signal.chunk_quality,
            signal.trend,
            str(signal.transcript_date),
            signal.chunk_index,
            signal.character_offsets[0],
            signal.character_offsets[1],
            signal.reasoning_trace,
            json.dumps(signal.ner_entities) if signal.ner_entities else None,
            json.dumps(signal.self_consistency_votes) if signal.self_consistency_votes else None,
            signal.verification_status.value if signal.verification_status else None,
            signal.llm_model,
            signal.content_hash,
            signal.retry_count,
            signal.provenance,
            signal.raw_llm_output,
            1 if signal.low_confidence else 0,
        ),
    )
    conn.commit()
    signal_id = cursor.lastrowid
    conn.close()
    logger.info("Logged signal %d: %s %s (conf=%.2f)", signal_id, signal.ticker, signal.direction.value, signal.confidence_raw)
    return signal_id
