"""Purpose: Merge correctness, relevance, and groundedness grades.
Input: JSON object with grade records from logs/.
Output: Combined grading summary for logs/ and reports/generated/.
Side effects: Optional file write only; no external calls.
Idempotent: Yes; merging is deterministic.
Recipe: recipes/rag-grader.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.tools.rag_grader_shared import emit_json, load_json_input, merge_grades


def merge_rag_grades(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Merge correctness, relevance, and groundedness grades.
    Input: JSON object with grade records.
    Output: Combined grading summary.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/rag-grader.md
    """
    grades = payload.get("grades") or [payload.get("correctness", {}), payload.get("relevance", {}), payload.get("groundedness", {})]
    return merge_grades(*[grade for grade in grades if isinstance(grade, dict)])


if __name__ == "__main__":
    sample = {"grades": [{"correct": True}, {"relevant": True}, {"grounded": True}]}
    payload = load_json_input(sample)
    emit_json(merge_rag_grades(payload["data"]), payload["output"])
