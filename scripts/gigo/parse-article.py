"""Purpose: Normalize raw article payloads into the verified article schema.
Input: JSON article or articles array from data/raw/news-monitoring-agent/.
Output: Normalized article records for data/verified/news-monitoring-agent/.
Side effects: Optional file write only.
Idempotent: Yes; normalization is deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input, normalize_article, split_articles


def parse_article(payload: dict[str, Any] | list[Any]) -> list[dict[str, Any]]:
    """Purpose: Normalize raw article payloads into the verified article schema.
    Input: JSON article or articles array from data/raw/news-monitoring-agent/.
    Output: Normalized article records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    if isinstance(payload, dict) and "articles" not in payload:
        return [normalize_article(payload)]
    return split_articles(payload)


if __name__ == "__main__":
    payload = load_json_input({"articles": [{"title": "AI revenue beats", "url": "u", "content": "Growth beat expectations."}]})
    emit_json(parse_article(payload["data"]), payload["output"])
