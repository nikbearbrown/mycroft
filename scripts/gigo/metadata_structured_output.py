"""Purpose: Validate metadata structured output for filtered retrieval.
Input: JSON metadata filter object from data/verified/news-monitoring-agent/.
Output: Normalized filter object.
Side effects: Optional file write only.
Idempotent: Yes; delegates to deterministic schema validation.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.gigo.parse_metadata_filter import parse_metadata_filter
from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input


def metadata_structured_output(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Validate metadata structured output for filtered retrieval.
    Input: JSON metadata filter object.
    Output: Normalized filter object.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    return parse_metadata_filter(payload)


if __name__ == "__main__":
    payload = load_json_input({"filter": {"must": []}})
    emit_json(metadata_structured_output(payload["data"]), payload["output"])
