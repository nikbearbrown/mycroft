"""Rule-based analyst question types. Weights raise dodge cost on harder questions."""

from __future__ import annotations

import re

QUESTION_TYPES = ("forward-looking", "backward-looking", "clarification", "confrontational")

TYPE_WEIGHTS = {
    "confrontational": 1.00,
    "forward-looking": 0.90,
    "backward-looking": 0.55,
    "clarification": 0.35,
}

_FORWARD = re.compile(
    r"(?i)\b(?:outlook|guidance|next\s+quarter|coming\s+year|going\s+forward|"
    r"expect(?:s|ed)?|will\s+you|pipeline|target|forecast|ahead)\b"
)
_BACKWARD = re.compile(
    r"(?i)\b(?:last\s+quarter|this\s+quarter|reported|what\s+drove|why\s+did|"
    r"versus\s+(?:last|prior)|year[- ]over[- ]year|what\s+happened)\b"
)
_CLARIFY = re.compile(
    r"(?i)\b(?:can\s+you\s+clarify|just\s+to\s+confirm|follow[- ]up|"
    r"could\s+you\s+expand|more\s+color|walk\s+us\s+through)\b"
)
_CONFRONT = re.compile(
    r"(?i)\b(?:but\s+(?:you|that)|push\s+back|disagree|shortfall|miss(?:ed)?|"
    r"why\s+should|how\s+do\s+you\s+justify|isn'?t\s+that|concern(?:ed|s)?)\b"
)


def classify_question(text: str) -> str:
    blob = text or ""
    scores = {
        "confrontational": len(_CONFRONT.findall(blob)),
        "forward-looking": len(_FORWARD.findall(blob)),
        "backward-looking": len(_BACKWARD.findall(blob)),
        "clarification": len(_CLARIFY.findall(blob)),
    }
    if "?" in blob and scores["clarification"] == 0 and max(scores.values()) == 0:
        return "clarification"
    winner = max(QUESTION_TYPES, key=lambda k: scores[k])
    if scores[winner] == 0:
        if _FORWARD.search(blob):
            return "forward-looking"
        return "clarification"
    return winner


def question_weight(question_type: str) -> float:
    return TYPE_WEIGHTS.get(question_type, 0.5)
