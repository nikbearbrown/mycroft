"""Purpose: Convert verified articles into collection A document records.
Input: List of verified article records from data/verified/news-monitoring-agent/.
Output: Chunk-ready document records for collection news_articles_a.
Side effects: Optional file write only.
Idempotent: Yes; document IDs are deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import build_documents, emit_json, load_json_input


def load_documents_a(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Purpose: Convert verified articles into collection A document records.
    Input: List of verified article records.
    Output: Document records for collection news_articles_a.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    return build_documents(items, "news_articles_a")


if __name__ == "__main__":
    payload = load_json_input([{"title": "x", "content": "body", "url": "u"}])
    emit_json(load_documents_a(payload["data"]), payload["output"])
