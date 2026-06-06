"""Purpose: Validate and pass through collection A document chunks.
Input: Document records from data/verified/news-monitoring-agent/.
Output: Non-empty document chunks for collection news_articles_a.
Side effects: Optional file write only.
Idempotent: Yes; filtering is deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input


def split_documents_a(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Purpose: Validate and pass through collection A document chunks.
    Input: Document records.
    Output: Non-empty document chunks.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    return [item for item in items if str(item.get("text") or "").strip()]


if __name__ == "__main__":
    payload = load_json_input([{"text": "body"}, {"text": ""}])
    emit_json(split_documents_a(payload["data"]), payload["output"])
