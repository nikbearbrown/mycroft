"""Purpose: Remove empty article records before embedding and storage.
Input: List of normalized article records from data/verified/news-monitoring-agent/.
Output: List of records with non-empty content.
Side effects: Optional file write only.
Idempotent: Yes; filtering is deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, filter_complete_articles, load_json_input


def filter_not_null(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Purpose: Remove empty article records before embedding and storage.
    Input: List of normalized article records.
    Output: List of records with non-empty content.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    return filter_complete_articles(items)


if __name__ == "__main__":
    payload = load_json_input([{"title": "x", "content": ""}, {"title": "y", "content": "body"}])
    emit_json(filter_not_null(payload["data"]), payload["output"])
