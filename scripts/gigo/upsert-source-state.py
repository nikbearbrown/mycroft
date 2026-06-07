"""Purpose: Prepare source freshness updates after a successful feed fetch.
Input: JSON object with feed_url/url and last_updated from verified fetch metadata.
Output: Source-state upsert record for data/verified/news-monitoring-agent/.
Side effects: Optional file write only; does not mutate external n8n data tables.
Idempotent: Yes; same source metadata yields the same upsert record.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input


def upsert_source_state(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Prepare source freshness updates after a successful feed fetch.
    Input: JSON object with feed_url/url and last_updated.
    Output: Source-state upsert record.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    return {
        "url": payload.get("feed_url") or payload.get("url"),
        "feed_last_updated": payload.get("last_updated") or payload.get("feed_last_updated"),
    }


if __name__ == "__main__":
    payload = load_json_input({"feed_url": "https://example.com/feed.xml", "last_updated": "2026-06-06T00:00:00Z"})
    emit_json(upsert_source_state(payload["data"]), payload["output"])
