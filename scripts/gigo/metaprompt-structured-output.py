"""Purpose: Validate metaprompt structured output for refined retrieval queries.
Input: JSON refined-query object from data/verified/news-monitoring-agent/.
Output: Normalized refined query object.
Side effects: Optional file write only.
Idempotent: Yes; delegates to deterministic schema validation.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.gigo.parse_refined_queries import parse_refined_queries
from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input


def metaprompt_structured_output(payload: dict[str, Any]) -> dict[str, list[str]]:
    """Purpose: Validate metaprompt structured output for refined retrieval queries.
    Input: JSON refined-query object.
    Output: Normalized refined query object.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    return parse_refined_queries(payload)


if __name__ == "__main__":
    payload = load_json_input({"refined_queries": ["AI revenue"]})
    emit_json(metaprompt_structured_output(payload["data"]), payload["output"])
