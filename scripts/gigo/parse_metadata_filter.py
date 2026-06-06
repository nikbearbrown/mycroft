"""Purpose: Validate metadata filter JSON produced for Qdrant retrieval.
Input: JSON object from an agent or parser in data/verified/news-monitoring-agent/.
Output: Qdrant-style filter object with a must array.
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


def parse_metadata_filter(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Validate metadata filter JSON produced for Qdrant retrieval.
    Input: JSON object from an agent or parser.
    Output: Qdrant-style filter object with a must array.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    filter_obj = payload.get("filter", payload)
    must = filter_obj.get("must", []) if isinstance(filter_obj, dict) else []
    return {"filter": {"must": must if isinstance(must, list) else []}}


if __name__ == "__main__":
    payload = load_json_input({"filter": {"must": []}})
    emit_json(parse_metadata_filter(payload["data"]), payload["output"])
