"""Purpose: Produce deterministic local embedding placeholders for Gemini embedding nodes.
Input: Text, article, or document record from data/verified/news-monitoring-agent/.
Output: JSON object with model name, embedding dimension, and placeholder vector.
Side effects: Optional file write only; no external service calls; GOOGLE_API_KEY is required only for a future live adapter.
Idempotent: Yes; vector is a deterministic hash of input text.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import embedding_stub, emit_json, load_json_input


def embedding_gemini(record: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Produce deterministic local embedding placeholders for Gemini embedding nodes.
    Input: Text, article, or document record.
    Output: JSON object with model name, embedding dimension, and placeholder vector.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same text yields same vector.
    Recipe: recipes/news-monitoring-agent.md
    """
    return embedding_stub(record, "google-gemini-embedding-placeholder")


if __name__ == "__main__":
    payload = load_json_input({"text": "AI capex demand"})
    emit_json(embedding_gemini(payload["data"]), payload["output"])
