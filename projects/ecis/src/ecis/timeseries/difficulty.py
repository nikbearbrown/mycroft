"""Per-question difficulty and difficulty-normalized dodge."""

from __future__ import annotations

from typing import Any

from ecis.analytics.features import quarter_key
from ecis.guidance_models.dodge import score_pairs
from ecis.guidance_models.qa_parser import parse_qa_corpus
from ecis.guidance_models.question_types import TYPE_WEIGHTS, classify_question
from ecis.timeseries.analysts import parse_analyst

_SPECIFIC = (
    "percent", "%", "bps", "basis point", "million", "billion",
    "guidance", "committed", "you said", "last quarter you", "previously",
)
_CONFRONT = ("why should", "how do you justify", "shortfall", "miss", "disagree", "concern")
_COMMIT = ("you said", "you told", "last quarter you", "previously guided", "promised")


def score_difficulty(question: str, question_type: str | None = None) -> dict[str, float | str]:
    blob = (question or "").lower()
    qtype = question_type or classify_question(question or "")
    type_w = TYPE_WEIGHTS.get(qtype, 0.5)
    spec = min(1.0, sum(p in blob for p in _SPECIFIC) / 4.0)
    confront = min(1.0, sum(p in blob for p in _CONFRONT) / 3.0)
    commit = min(1.0, sum(p in blob for p in _COMMIT) / 2.0)
    difficulty = 0.35 * type_w + 0.25 * spec + 0.25 * confront + 0.15 * commit
    difficulty = max(0.05, min(1.0, difficulty))
    return {
        "question_type": qtype,
        "type_weight": type_w,
        "specificity": spec,
        "confrontational": confront,
        "commitment": commit,
        "difficulty": difficulty,
    }


def normalize_dodge(dodge: float | None, difficulty: float) -> float:
    raw = float(dodge or 0)
    return max(0.0, min(1.0, raw / max(0.35, difficulty)))


def score_questions(ticker: str | None = None, pairs: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    rows = score_pairs(pairs if pairs is not None else parse_qa_corpus(ticker))
    out: list[dict[str, Any]] = []
    for row in rows:
        ident = parse_analyst(row.get("question_speaker") or "")
        scored = score_difficulty(row.get("question") or "", row.get("question_type"))
        dodge = float(row.get("dodge") or 0)
        out.append({
            "ticker": (row.get("ticker") or "").upper(),
            "transcript_date": (row.get("transcript_date") or "")[:10],
            "quarter": quarter_key(row.get("transcript_date")),
            "pair_index": row.get("pair_index"),
            "analyst_key": ident["analyst_key"],
            "question_type": scored["question_type"],
            "difficulty": scored["difficulty"],
            "specificity": scored["specificity"],
            "dodge": dodge,
            "dodge_normalized": normalize_dodge(dodge, float(scored["difficulty"])),
        })
    return out
