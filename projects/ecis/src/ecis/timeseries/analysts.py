"""Normalize analyst identities and build per-analyst question-pattern profiles."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from ecis.guidance_models.dodge import score_pairs
from ecis.guidance_models.qa_parser import parse_qa_corpus
from ecis.guidance_models.question_types import classify_question

_FIRM_SPLIT = re.compile(r"\s*[-–—,]\s*")
_ROLE_TAIL = re.compile(r",?\s*(?:analyst|unidentified\s+analyst)\s*$", re.I)
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def parse_analyst(speaker: str) -> dict[str, str]:
    text = _ROLE_TAIL.sub("", (speaker or "").strip()).strip(" ,-")
    parts = _FIRM_SPLIT.split(text, maxsplit=1)
    name = (parts[0] or "").strip() or "unknown"
    firm = parts[1].strip() if len(parts) > 1 else ""
    key = _NON_ALNUM.sub("_", name.lower()).strip("_") or "unknown"
    return {"analyst_key": key, "display_name": name, "firm": firm}


def _complexity(question: str) -> float:
    tokens = (question or "").split()
    n = max(len(tokens), 1)
    marks = (question or "").count("?")
    return min(1.0, (n / 40.0) + 0.1 * marks)


def _tone(question: str) -> float:
    blob = (question or "").lower()
    pos = sum(w in blob for w in ("opportunity", "strong", "growth", "beat", "upside"))
    neg = sum(w in blob for w in ("risk", "miss", "shortfall", "concern", "weak", "decline"))
    return (pos - neg) / max(pos + neg, 1)


def build_profiles(ticker: str | None = None, pairs: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    rows = score_pairs(pairs if pairs is not None else parse_qa_corpus(ticker))
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    meta: dict[str, dict[str, str]] = {}
    for row in rows:
        ident = parse_analyst(row.get("question_speaker") or "")
        key = ident["analyst_key"]
        meta[key] = ident
        qtype = row.get("question_type") or classify_question(row.get("question") or "")
        item = dict(row)
        item["question_type"] = qtype
        item.update(ident)
        buckets[key].append(item)
    out: list[dict[str, Any]] = []
    for key, items in sorted(buckets.items()):
        n = max(len(items), 1)
        types: dict[str, int] = defaultdict(int)
        for r in items:
            types[r["question_type"]] += 1
        follow = sum(1 for r in items if r.get("follow_up")) / n
        complex_ = sum(_complexity(r.get("question") or "") for r in items) / n
        tone = sum(_tone(r.get("question") or "") for r in items) / n
        confront = types.get("confrontational", 0) / n
        forward = types.get("forward-looking", 0) / n
        bullish = max(-1.0, min(1.0, tone))
        out.append({
            "analyst_key": key,
            "display_name": meta[key]["display_name"],
            "firm": meta[key]["firm"],
            "n_questions": len(items),
            "follow_up_rate": follow,
            "complexity": complex_,
            "tone": tone,
            "bullish_score": bullish,
            "tough_score": confront,
            "forward_looking": forward,
            "backward_looking": types.get("backward-looking", 0) / n,
            "clarification": types.get("clarification", 0) / n,
            "confrontational": confront,
            "stance": "bullish" if bullish > 0.15 else ("bearish" if bullish < -0.15 else "neutral"),
        })
    return out
