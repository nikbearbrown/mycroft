"""Purpose: Load prototype researcher records from the original n8n workflow.
Input: No required input; optional local override JSON.
Output: Mock researcher records for data/raw/ai-talent-intelligence-agent/.
Side effects: Optional file write only; no network calls.
Idempotent: Yes except last_updated timestamps.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import emit, load_input, mock_researcher_rows


def load_mock_researchers(payload: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Purpose: Load prototype researcher records from the original n8n workflow.
    Input: Optional local override JSON.
    Output: Mock researcher records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes except timestamps.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    return payload if payload else mock_researcher_rows()


if __name__ == "__main__":
    payload = load_input(None)
    emit(load_mock_researchers(payload["data"]), payload["output"])
