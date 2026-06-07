"""Purpose: Convert question constraints into a Qdrant-style metadata filter.
Input: JSON object with question from data/verified/news-monitoring-agent/.
Output: JSON object containing filter.must conditions.
Side effects: Optional file write only; no external LLM call.
Idempotent: Yes; rule-based filter generation is deterministic for the same date.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input, metadata_filter


def metadata_filter_agent(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Convert question constraints into a Qdrant-style metadata filter.
    Input: JSON object with question.
    Output: JSON object containing filter.must conditions.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes within the same run date.
    Recipe: recipes/news-monitoring-agent.md
    """
    return metadata_filter(str(payload.get("question") or payload.get("text") or ""))


if __name__ == "__main__":
    payload = load_json_input({"question": "latest positive AI news today"})
    emit_json(metadata_filter_agent(payload["data"]), payload["output"])
