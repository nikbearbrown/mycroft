"""Per-chunk quality score used as a triangulator multiplier."""

from __future__ import annotations

import re
from typing import Any

from ecis.config.settings import settings
from ecis.preprocessing.boilerplate import boilerplate_token_ratio

_SPEAKER_MARK = re.compile(r"\[SPEAKER:\s*.+?\]")
_SENTENCE_END = re.compile(r"""[.!?]["']?\s*$""")


def _token_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def boilerplate_score(text: str) -> float:
    return max(0.0, 1.0 - boilerplate_token_ratio(text or ""))


def token_count_score(text: str) -> float:
    target = max(settings.chunk_size_tokens, 1)
    count = _token_count(text)
    if count <= 0:
        return 0.0
    return min(1.0, count / target)


def completeness_score(text: str) -> float:
    stripped = (text or "").strip()
    if not stripped:
        return 0.0
    body = _SPEAKER_MARK.sub("", stripped).strip()
    if not body:
        body = stripped
    first_alpha = next((ch for ch in body if ch.isalpha()), "")
    starts_clean = bool(first_alpha and first_alpha.isupper()) or stripped.startswith("[")
    ends_clean = bool(_SENTENCE_END.search(body))
    if starts_clean and ends_clean:
        return 1.0
    if starts_clean or ends_clean:
        return 0.5
    return 0.2


def speaker_transition_score(text: str) -> float:
    marks = _SPEAKER_MARK.findall(text or "")
    n = len(marks)
    if n <= 1:
        return 1.0
    if n == 2:
        return 0.6
    return 0.3


def score_chunk(chunk: dict[str, Any] | str) -> dict[str, float]:
    """Return sub-scores and a weighted 0–1 quality score."""
    text = chunk if isinstance(chunk, str) else (chunk.get("text") or "")
    subs = {
        "boilerplate": boilerplate_score(text),
        "token_count": token_count_score(text),
        "completeness": completeness_score(text),
        "speaker_transitions": speaker_transition_score(text),
    }
    weights = settings.chunk_quality_weights
    total_w = sum(weights.get(k, 0.0) for k in subs) or 1.0
    combined = sum(subs[k] * weights.get(k, 0.0) for k in subs) / total_w
    return {**subs, "chunk_quality": round(min(max(combined, 0.0), 1.0), 4)}
