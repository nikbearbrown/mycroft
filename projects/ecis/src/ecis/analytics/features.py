"""Shared feature helpers: polarity, hedging, FLS, and language specificity."""

from __future__ import annotations

import math
import re
from typing import Any

_DIRECTION_POLARITY = {"raised": 1.0, "maintained": 0.0, "lowered": -1.0}

_NUMBER_RE = re.compile(
    r"(?<![A-Za-z])(?:\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)(?:\s*(?:%|percent|bps|bp))?",
    re.I,
)
_DATE_RE = re.compile(
    r"\b(?:q[1-4]\s*fy?\d{2,4}|\d{4}-\d{2}-\d{2}|"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})\b",
    re.I,
)
_VAGUE_RE = re.compile(
    r"\b(?:approximately|about|around|somewhat|various|several|a\s+range|"
    r"mid-?single|high-?single|low-?single|double-?digit)\b",
    re.I,
)
_DEFINITIVE_RE = re.compile(
    r"\b(?:will|expect(?:s|ed)?|guide(?:s|d|ance)?|target(?:s|ed)?|"
    r"committed|on\s+track|confirm(?:s|ed)?)\b",
    re.I,
)
_HEDGE_RE = re.compile(
    r"\b(?:may|might|could|possibly|potentially|uncertain|subject\s+to|"
    r"depending|approximately|around)\b",
    re.I,
)


def direction_polarity(direction: str | None) -> float:
    return _DIRECTION_POLARITY.get((direction or "").lower(), 0.0)


def tone_from_signal(row: dict[str, Any]) -> float:
    """FinBERT-style polarity: stated tone shift if present, else direction × confidence."""
    shift = row.get("tone_shift")
    if shift is not None:
        try:
            val = float(shift)
            if math.isfinite(val):
                return max(-1.0, min(1.0, val))
        except (TypeError, ValueError):
            pass
    conf = float(row.get("confidence") or 0.0)
    return direction_polarity(row.get("direction")) * max(0.0, min(1.0, conf))


def hedging(row: dict[str, Any], text: str = "") -> float:
    val = row.get("hedging_index")
    if val is not None:
        try:
            return max(0.0, min(1.0, float(val)))
        except (TypeError, ValueError):
            pass
    if not text:
        return 0.0
    tokens = max(len(text.split()), 1)
    return min(1.0, len(_HEDGE_RE.findall(text)) / tokens * 20.0)


def fls(row: dict[str, Any], text: str = "") -> float:
    val = row.get("fls_density")
    if val is not None:
        try:
            return max(0.0, min(1.0, float(val)))
        except (TypeError, ValueError):
            pass
    if not text:
        return 0.0
    tokens = max(len(text.split()), 1)
    return min(1.0, len(_DEFINITIVE_RE.findall(text)) / tokens * 15.0)


def numerical_specificity(text: str) -> float:
    """Share of numeric / dated claims versus vague phrasing, 0–1."""
    if not text or not text.strip():
        return 0.0
    numbers = len(_NUMBER_RE.findall(text))
    dates = len(_DATE_RE.findall(text))
    vague = len(_VAGUE_RE.findall(text))
    denom = numbers + dates + vague
    if denom == 0:
        return 0.0
    return max(0.0, min(1.0, (numbers + dates) / denom))


def definitive_ratio(text: str) -> float:
    if not text or not text.strip():
        return 0.0
    definitive = len(_DEFINITIVE_RE.findall(text))
    hedges = len(_HEDGE_RE.findall(text))
    denom = definitive + hedges
    if denom == 0:
        return 0.0
    return definitive / denom


def quarter_key(transcript_date: str | None) -> str:
    raw = (transcript_date or "")[:10]
    if len(raw) >= 7:
        year, month = raw[:4], raw[5:7]
        try:
            m = int(month)
            q = (m - 1) // 3 + 1
            return f"{year}-Q{q}"
        except ValueError:
            return raw[:7]
    return raw or "unknown"
