"""Shared boilerplate detection used by cleaning, normalisation, and chunk validation."""

from __future__ import annotations

import re

_BOILERPLATE_PATTERNS = [
    re.compile(r"(?i)safe\s+harbo(?:u)?r\s+statement[^.!\n]*[.!]?", re.MULTILINE),
    re.compile(r"(?i)forward[- ]looking\s+statements?[^.!\n]*[.!]?", re.MULTILINE),
    re.compile(r"(?i)this\s+(?:document|filing|release)\s+contains[^.!\n]*forward[- ]looking[^.!\n]*[.!]?", re.MULTILINE),
    re.compile(r"(?i)©\s*\d{4}.*?all\s+rights\s+reserved[^.!\n]*[.!]?", re.MULTILINE),
    re.compile(r"(?i)UNITED\s+STATES\s+SECURITIES\s+AND\s+EXCHANGE\s+COMMISSION.*?(?:FORM\s+8-K)", re.DOTALL),
    re.compile(
        r"(?i)(?:except\s+as\s+required\s+by\s+law|we\s+undertake\s+no\s+obligation)"
        r"[^.!\n]*[.!]?"
    ),
    re.compile(
        r"(?i)(?:actual\s+results\s+may\s+differ\s+materially|"
        r"no\s+assurance\s+can\s+be\s+given|"
        r"these\s+statements\s+are\s+based\s+on\s+current\s+expectations)[^.!\n]*[.!]?"
    ),
    re.compile(r"(?i)non[- ]gaap\s+financial\s+measures[^.!\n]*[.!]?", re.MULTILINE),
]

_BOILERPLATE_TOKEN_RE = re.compile(
    r"(?i)\b("
    r"forward[- ]looking|safe\s+harbo(?:u)?r|sec\s+filing|form\s+8-k|"
    r"materially\s+differ|no\s+obligation\s+to\s+update|"
    r"non[- ]gaap|reconciliation|cautionary\s+statement|"
    r"risk\s+factors|private\s+securities\s+litigation"
    r")\b"
)


def strip_boilerplate(text: str) -> str:
    cleaned = text
    for pattern in _BOILERPLATE_PATTERNS:
        cleaned = pattern.sub(" ", cleaned)
    return cleaned


def boilerplate_token_ratio(text: str) -> float:
    tokens = re.findall(r"\b\w+\b", text)
    if not tokens:
        return 1.0
    hits = _BOILERPLATE_TOKEN_RE.findall(text)
    return min(1.0, len(hits) / max(len(tokens) / 8.0, 1.0))
