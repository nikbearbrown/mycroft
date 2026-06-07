"""Purpose: Retrieve locally stored document records using simple lexical matching.
Input: JSON object with question/query and documents from data/verified/news-monitoring-agent/.
Output: Ranked local document matches for logs/.
Side effects: Optional file write only; no Qdrant network calls.
Idempotent: Yes; ranking is deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import json
import re
from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input


def qdrant_retrieve(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Retrieve locally stored document records using simple lexical matching.
    Input: JSON object with question/query and documents.
    Output: Ranked local document matches.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same ranking.
    Recipe: recipes/news-monitoring-agent.md
    """
    query = str(payload.get("question") or payload.get("query") or "")
    terms = {term.lower() for term in re.findall(r"[A-Za-z0-9$.-]+", query) if len(term) > 2}
    documents = payload.get("documents") or []
    scored = []
    for doc in documents:
        haystack = json.dumps(doc, default=str).lower()
        scored.append({"score": sum(1 for term in terms if term in haystack), "document": doc})
    return {"matches": [item for item in sorted(scored, key=lambda row: row["score"], reverse=True) if item["score"] > 0]}


if __name__ == "__main__":
    payload = load_json_input({"query": "AI revenue", "documents": [{"text": "AI revenue growth"}]})
    emit_json(qdrant_retrieve(payload["data"]), payload["output"])
