"""Purpose: Split a fetched feed payload into article records.
Input: JSON object with an articles array from data/raw/news-monitoring-agent/.
Output: Normalized article records for downstream validation.
Side effects: Optional file write only.
Idempotent: Yes; splitting and normalization are deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input, split_articles as split_payload_articles


def split_articles(payload: dict[str, Any] | list[Any]) -> list[dict[str, Any]]:
    """Purpose: Split a fetched feed payload into article records.
    Input: JSON object with an articles array.
    Output: Normalized article records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    return split_payload_articles(payload)


if __name__ == "__main__":
    payload = load_json_input({"articles": [{"title": "x", "content": "body", "url": "u"}]})
    emit_json(split_articles(payload["data"]), payload["output"])
