"""Purpose: Refine a financial-news question into vector retrieval queries.
Input: JSON object with question from data/verified/news-monitoring-agent/.
Output: JSON object with one to three refined_queries.
Side effects: Optional file write only; no external LLM call.
Idempotent: Yes; rule-based refinement is deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input, refine_query


def query_refinement_agent(payload: dict[str, Any]) -> dict[str, list[str]]:
    """Purpose: Refine a financial-news question into vector retrieval queries.
    Input: JSON object with question.
    Output: JSON object with one to three refined_queries.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same question yields same queries.
    Recipe: recipes/news-monitoring-agent.md
    """
    return refine_query(str(payload.get("question") or payload.get("text") or ""))


if __name__ == "__main__":
    payload = load_json_input({"question": "What is the latest AI revenue news for Nvidia?"})
    emit_json(query_refinement_agent(payload["data"]), payload["output"])
