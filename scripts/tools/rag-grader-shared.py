"""Shared utilities for the RAG Grader conversion.

Purpose: Provide deterministic local grading helpers for RAG answer evaluation.
Input: JSON-compatible question, answer, and retrieved fact records from logs/ or data/verified/.
Output: JSON-compatible grading records for logs/ and reports/generated/.
Side effects: Optional file writes through caller scripts; no network calls.
Idempotent: Yes; lexical grading helpers are deterministic for the same input.
Recipe: recipes/rag-grader.md
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input


def words(text: str) -> set[str]:
    """Return normalized content words for overlap checks."""
    stop = {"the", "and", "for", "with", "that", "this", "from", "are", "was", "were", "what", "which", "have"}
    return {word.lower() for word in re.findall(r"[A-Za-z0-9$.-]+", text) if len(word) > 2 and word.lower() not in stop}


def facts_text(payload: dict[str, Any]) -> str:
    """Collect retrieved fact text from common RAG intermediate-step shapes."""
    facts = payload.get("facts") or payload.get("intermediateSteps") or payload.get("sources") or []
    if isinstance(facts, str):
        return facts
    collected: list[str] = []
    for item in facts:
        if isinstance(item, dict):
            collected.append(str(item.get("observation") or item.get("text") or item.get("content") or item))
        else:
            collected.append(str(item))
    return "\n".join(collected)


def grade_relevance(payload: dict[str, Any]) -> dict[str, Any]:
    """Grade whether the answer addresses the question."""
    question = str(payload.get("question") or "")
    answer = str(payload.get("output") or payload.get("answer") or "")
    overlap = words(question) & words(answer)
    relevant = bool(answer.strip()) and (len(overlap) > 0 or len(words(question)) <= 2)
    return {
        "explanation": f"Answer/question content-word overlap count: {len(overlap)}.",
        "relevant": relevant,
    }


def grade_groundedness(payload: dict[str, Any]) -> dict[str, Any]:
    """Grade whether the answer is supported by retrieved facts."""
    answer = str(payload.get("output") or payload.get("answer") or "")
    facts = facts_text(payload)
    answer_words = words(answer)
    fact_words = words(facts)
    if not answer_words:
        grounded = False
        ratio = 0.0
    else:
        ratio = len(answer_words & fact_words) / max(len(answer_words), 1)
        grounded = ratio >= 0.25 and bool(facts.strip())
    return {
        "explanation": f"Answer/fact lexical support ratio: {ratio:.2f}. Human review required for semantic support.",
        "grounded": grounded,
    }


def grade_correctness(payload: dict[str, Any]) -> dict[str, Any]:
    """Grade answer correctness with contradiction and abstention checks."""
    answer = str(payload.get("output") or payload.get("answer") or "")
    lowered = answer.lower()
    contradiction_markers = ["not ", "however", "contradict", "cannot verify", "unknown"]
    has_conflict_marker = any(marker in lowered for marker in contradiction_markers)
    correct = bool(answer.strip()) and not has_conflict_marker
    return {
        "explanation": "Local correctness check flags empty answers and obvious uncertainty/conflict markers; human review remains required.",
        "correct": correct,
    }


def normalize_boolean_grade(payload: dict[str, Any], key: str) -> dict[str, Any]:
    """Normalize a grader response to explanation plus a required boolean key."""
    value = payload.get(key)
    if isinstance(value, str):
        value = value.strip().lower() == "true"
    return {"explanation": str(payload.get("explanation") or ""), key: bool(value)}


def merge_grades(*grades: dict[str, Any]) -> dict[str, Any]:
    """Merge grader outputs into a single reportable record."""
    merged: dict[str, Any] = {"passed": True, "grades": {}}
    for grade in grades:
        for key in ("correct", "relevant", "grounded"):
            if key in grade:
                merged["grades"][key] = grade
                merged["passed"] = merged["passed"] and bool(grade[key])
    return merged


__all__ = [
    "emit_json",
    "load_json_input",
    "grade_relevance",
    "grade_groundedness",
    "grade_correctness",
    "normalize_boolean_grade",
    "merge_grades",
]
