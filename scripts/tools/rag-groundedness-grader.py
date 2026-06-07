"""Purpose: Grade whether a RAG answer is grounded in retrieved facts.
Input: JSON object with output/answer and facts/intermediateSteps/sources from logs/.
Output: JSON object with explanation and grounded boolean.
Side effects: Optional file write only; no external LLM calls.
Idempotent: Yes; local lexical grading is deterministic.
Recipe: recipes/rag-grader.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.tools.rag_grader_shared import emit_json, grade_groundedness, load_json_input


def rag_groundedness_grader(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Grade whether a RAG answer is grounded in retrieved facts.
    Input: JSON object with output/answer and facts/intermediateSteps/sources.
    Output: JSON object with explanation and grounded boolean.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/rag-grader.md
    """
    return grade_groundedness(payload)


if __name__ == "__main__":
    sample = {"output": "AI stocks moved on earnings news.", "facts": ["AI stocks moved on earnings news."]}
    payload = load_json_input(sample)
    emit_json(rag_groundedness_grader(payload["data"]), payload["output"])
