"""Earnings-call quality gate before downstream analytics."""

from __future__ import annotations

import os
import re
from typing import Any

from ecis.guidance_models.qa_parser import iter_normalised_transcripts
from ecis.analytics.features import quarter_key

QUALITY_FLOOR = float(os.getenv("CALL_QUALITY_FLOOR", "0.45"))
_SENT_RE = re.compile(r"[^.!?]+[.!?]")
_GARBLED = re.compile(r"[^\w\s.,;:'\"!?%$()\-/]")


def score_text(text: str) -> dict[str, Any]:
    blob = text or ""
    has_prepared = "[SECTION: prepared_remarks]" in blob or "prepared" in blob.lower()
    has_qa = "[SECTION: qa]" in blob or "question" in blob.lower()
    completeness = (0.5 if has_prepared else 0.0) + (0.5 if has_qa else 0.0)

    qa = blob.split("[SECTION: qa]")[-1] if "[SECTION: qa]" in blob else ""
    qa_tokens = len(qa.split())
    qa_score = 0.0 if qa_tokens < 20 else min(1.0, qa_tokens / 200.0)

    speakers = len(re.findall(r"\[SPEAKER:", blob))
    lines = max(len([ln for ln in blob.splitlines() if ln.strip()]), 1)
    speaker_coverage = min(1.0, speakers / max(lines / 8.0, 1.0))

    sentences = _SENT_RE.findall(blob) or ([blob] if blob.strip() else [])
    if not sentences:
        coherence = 0.0
    else:
        garbled = sum(len(_GARBLED.findall(s)) for s in sentences)
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        coherence = max(0.0, min(1.0, 1.0 - garbled / max(len(blob), 1) - (0.2 if avg_len < 3 else 0.0)))

    formatting = 1.0 if has_prepared and speakers else 0.4 if has_prepared or has_qa else 0.2
    score = (
        0.25 * completeness
        + 0.20 * qa_score
        + 0.20 * speaker_coverage
        + 0.20 * coherence
        + 0.15 * formatting
    )
    return {
        "completeness": completeness,
        "qa_score": qa_score,
        "speaker_coverage": speaker_coverage,
        "coherence": coherence,
        "formatting": formatting,
        "quality": max(0.0, min(1.0, score)),
        "flag": "low_quality" if score < QUALITY_FLOOR else "ok",
        "weight": 0.4 if score < QUALITY_FLOOR else 1.0,
    }


def score_calls(ticker: str | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    files = iter_normalised_transcripts(ticker)
    if not files:
        return out
    for tkr, day, path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rec = score_text(text)
        rec.update({
            "ticker": tkr,
            "transcript_date": day,
            "quarter": quarter_key(day),
        })
        out.append(rec)
    return out
