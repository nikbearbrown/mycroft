"""Rule-based intent parser. Retrieval / comparison / analysis / explanation."""

from __future__ import annotations

import re
from typing import Any

_TICKER = re.compile(r"\b([A-Z]{1,5})\b")
_STOP = {
    "Q", "VS", "A", "I", "CEO", "CFO", "OOD", "SHAP", "MLP",
    "WHAT", "WAS", "THE", "AND", "FOR", "WHY", "HOW", "WHO", "LAST",
    "SHOW", "DODGE", "SCORE", "QUARTER", "FLAGGED", "COMPARE", "WHICH",
}

_COMPARE = re.compile(r"(?i)\b(?:compare|vs\.?|versus|against|difference between)\b")
_EXPLAIN = re.compile(r"(?i)\b(?:why|explain|flagged|because|shap|attribution)\b")
_ANALYZE = re.compile(r"(?i)\b(?:which|deteriorat|contagion|uncertain|abstain|ood|worst|scan)\b")


def parse_intent(query: str) -> dict[str, Any]:
    blob = query or ""
    tickers = [t for t in _TICKER.findall(blob) if t not in _STOP]
    if _EXPLAIN.search(blob):
        intent = "explanation"
    elif _COMPARE.search(blob) or len(tickers) >= 2:
        intent = "comparison"
    elif _ANALYZE.search(blob) and not tickers:
        intent = "analysis"
    elif _ANALYZE.search(blob):
        intent = "analysis"
    else:
        intent = "retrieval"
    return {"intent": intent, "tickers": tickers[:4], "query": blob}
