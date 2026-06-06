"""Purpose: Validate groundedness grader output.
Input: JSON object with explanation and grounded from logs/.
Output: Normalized JSON object with explanation and grounded boolean.
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


def parse_groundedness_grade(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Validate groundedness grader output.
    Input: JSON object with explanation and grounded.
    Output: Normalized JSON object with explanation and grounded boolean.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/rag-grader.md
    """
    return normalize_boolean_grade(payload, "grounded")


if __name__ == "__main__":
    payload = load_json_input({"explanation": "Supported by sources.", "grounded": True})
    emit_json(parse_groundedness_grade(payload["data"]), payload["output"])
