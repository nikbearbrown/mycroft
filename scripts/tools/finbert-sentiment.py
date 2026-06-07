"""Purpose: Add financial sentiment labels to verified news articles.
Input: Article record or list of article records from data/verified/news-monitoring-agent/.
Output: Article records with sentiment.label and sentiment.score fields.
Side effects: Optional file write only; no external service calls.
Idempotent: Yes; local lexicon scoring is deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, lexical_sentiment, load_json_input


def finbert_sentiment(payload: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any] | list[dict[str, Any]]:
    """Purpose: Add financial sentiment labels to verified news articles.
    Input: Article record or list of article records.
    Output: Article records with sentiment.label and sentiment.score fields.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same score.
    Recipe: recipes/news-monitoring-agent.md
    """
    if isinstance(payload, list):
        return [lexical_sentiment(item) for item in payload]
    return lexical_sentiment(payload)


if __name__ == "__main__":
    payload = load_json_input({"title": "AI revenue beats expectations", "content": "Strong growth and profit."})
    emit_json(finbert_sentiment(payload["data"]), payload["output"])
