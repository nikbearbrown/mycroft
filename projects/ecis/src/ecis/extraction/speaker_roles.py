"""Map normalised speaker strings to a role and a triangulator weight."""

from __future__ import annotations

import re

from ecis.config.settings import settings

SPEAKER_ROLES = ("cfo", "ceo", "coo", "ir", "analyst", "operator", "unknown")

_ROLE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("operator", re.compile(
        r"(?i)\b(operator|moderator|conference\s+operator)\b"
    )),
    ("cfo", re.compile(
        r"(?i)\b(cfo|chief\s+financial\s+officer|finance\s+(?:officer|director))\b"
    )),
    ("ceo", re.compile(
        r"(?i)\b(ceo|chief\s+executive(?:\s+officer)?|president\s+and\s+ceo)\b"
    )),
    ("coo", re.compile(
        r"(?i)\b(coo|chief\s+operating\s+officer)\b"
    )),
    ("ir", re.compile(
        r"(?i)\b(investor\s+relations|\bir\b|head\s+of\s+ir)\b"
    )),
    ("analyst", re.compile(
        r"(?i)\b(analyst|unidentified\s+analyst)\b"
    )),
]


def classify_speaker(speaker: str) -> str:
    """Return a canonical role for a speaker attribution string."""
    text = (speaker or "").strip()
    if not text:
        return "unknown"

    lowered = text.lower()
    if lowered in {"management", "executive", "company"}:
        return "unknown"

    for role, pattern in _ROLE_PATTERNS:
        if pattern.search(text):
            return role
    return "unknown"


def speaker_weight(speaker: str, role: str | None = None) -> float:
    """Weight multiplier for a speaker. CFO is 1.0; analysts and operators are downweighted."""
    resolved = role or classify_speaker(speaker)
    table = settings.speaker_role_weights
    return float(table.get(resolved, table.get("unknown", 0.8)))
