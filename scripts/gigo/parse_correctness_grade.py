"""Purpose: Validate correctness grader output.
Input: JSON object with explanation and correct from logs/.
Output: Normalized JSON object with explanation and correct boolean.
Side effects: Optional file write only.
Idempotent: Yes; parsing is deterministic.
Recipe: recipes/rag-grader.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.tools.rag_grader_shared import emit_json, load_json_input, normalize_boolean_grade


def parse_correctness_grade(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Validate correctness grader output.
    Input: JSON object with explanation and correct.
    Output: Normalized JSON object with explanation and correct boolean.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/rag-grader.md
    """
    return normalize_boolean_grade(payload, "correct")


if __name__ == "__main__":
    payload = load_json_input({"explanation": "No conflict markers.", "correct": True})
    emit_json(parse_correctness_grade(payload["data"]), payload["output"])
