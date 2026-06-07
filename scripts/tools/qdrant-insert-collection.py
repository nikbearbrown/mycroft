"""Purpose: Prepare local vector-store upsert records for a Qdrant collection.
Input: Document records from data/verified/news-monitoring-agent/.
Output: JSON object with collection name and point records for data/verified/.
Side effects: Optional file write only; no Qdrant network calls.
Idempotent: Yes; point IDs are deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import embedding_stub, emit_json, load_json_input


def qdrant_insert_collection(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Prepare local vector-store upsert records for a Qdrant collection.
    Input: Document records and optional collection name.
    Output: JSON object with collection name and point records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same documents yield same points.
    Recipe: recipes/news-monitoring-agent.md
    """
    collection = str(payload.get("collection") or "news_articles_a")
    documents = payload.get("documents") or payload.get("items") or []
    points = []
    for doc in documents:
        points.append({"id": doc.get("id"), "vector": embedding_stub(doc, collection)["embedding"], "payload": doc})
    return {"collection": collection, "points": points}


if __name__ == "__main__":
    payload = load_json_input({"collection": "news_articles_a", "documents": [{"id": "1", "text": "AI news"}]})
    emit_json(qdrant_insert_collection(payload["data"]), payload["output"])
