"""Purpose: Validate refined query JSON used by RAG agents.
Input: JSON object with refined_queries from data/verified/news-monitoring-agent/.
Output: Object with one to three non-empty refined query strings.
Side effects: Optional file write only.
Idempotent: Yes; validation is deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input


def parse_refined_queries(payload: dict[str, Any]) -> dict[str, list[str]]:
    """Purpose: Validate refined query JSON used by RAG agents.
    Input: JSON object with refined_queries.
    Output: Object with one to three non-empty refined query strings.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    queries = payload.get("refined_queries", [])
    if isinstance(queries, str):
        queries = [queries]
    return {"refined_queries": [str(q).strip() for q in queries if str(q).strip()][:3]}


if __name__ == "__main__":
    payload = load_json_input({"refined_queries": ["AI capex", "latest AI revenue"]})
    emit_json(parse_refined_queries(payload["data"]), payload["output"])
