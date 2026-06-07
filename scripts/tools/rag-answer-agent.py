"""Purpose: Produce an extractive, source-grounded answer from local news documents.
Input: JSON object with question and documents from data/verified/news-monitoring-agent/.
Output: Agent answer, matched sources, and review note for logs/.
Side effects: Optional file write only; no external LLM calls.
Idempotent: Yes; extractive answer generation is deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import answer_from_documents, emit_json, load_json_input


def rag_answer_agent(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Produce an extractive, source-grounded answer from local news documents.
    Input: JSON object with question and documents.
    Output: Agent answer, matched sources, and review note.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same answer.
    Recipe: recipes/news-monitoring-agent.md
    """
    return answer_from_documents(
        str(payload.get("question") or payload.get("query") or ""),
        payload.get("documents") or [],
        str(payload.get("agent_name") or "RAG Agent"),
    )


if __name__ == "__main__":
    payload = load_json_input({"question": "AI revenue", "documents": [{"text": "AI revenue growth", "metadata": {"url": "u"}}]})
    emit_json(rag_answer_agent(payload["data"]), payload["output"])
