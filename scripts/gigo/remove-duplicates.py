"""Purpose: Deduplicate news articles by URL and title.
Input: List of normalized article records from data/verified/news-monitoring-agent/.
Output: First-seen unique article records.
Side effects: Optional file write only.
Idempotent: Yes; deduplication preserves deterministic first-seen order.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import dedupe_articles, emit_json, load_json_input


def remove_duplicates(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Purpose: Deduplicate news articles by URL and title.
    Input: List of normalized article records.
    Output: First-seen unique article records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    return dedupe_articles(items)


if __name__ == "__main__":
    payload = load_json_input([{"title": "x", "url": "u"}, {"title": "x", "url": "u"}])
    emit_json(remove_duplicates(payload["data"]), payload["output"])
