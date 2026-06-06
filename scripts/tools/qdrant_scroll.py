"""Purpose: Prepare a local representation of a Qdrant scroll request.
Input: JSON object with collection and optional documents from data/verified/news-monitoring-agent/.
Output: Payload records that would be inspected during RAG evaluation.
Side effects: Optional file write only; no Qdrant network calls.
Idempotent: Yes; pass-through behavior is deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input


def qdrant_scroll(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Prepare a local representation of a Qdrant scroll request.
    Input: JSON object with collection and optional documents.
    Output: Payload records that would be inspected during RAG evaluation.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    return {"collection": payload.get("collection", "news_articles_a"), "points": payload.get("documents", [])}


if __name__ == "__main__":
    payload = load_json_input({"collection": "news_articles_a", "documents": [{"id": "1"}]})
    emit_json(qdrant_scroll(payload["data"]), payload["output"])
