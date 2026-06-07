"""Purpose: Grade whether a RAG answer is relevant to the question.
Input: JSON object with question and output/answer from logs/.
Output: JSON object with explanation and relevant boolean.
Side effects: Optional file write only; no external LLM calls.
Idempotent: Yes; local lexical grading is deterministic.
Recipe: recipes/rag-grader.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.tools.rag_grader_shared import emit_json, grade_relevance, load_json_input


def rag_relevance_grader(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Grade whether a RAG answer is relevant to the question.
    Input: JSON object with question and output/answer.
    Output: JSON object with explanation and relevant boolean.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/rag-grader.md
    """
    return grade_relevance(payload)


if __name__ == "__main__":
    payload = load_json_input({"question": "What moved AI stocks?", "output": "AI stocks moved on earnings news."})
    emit_json(rag_relevance_grader(payload["data"]), payload["output"])
