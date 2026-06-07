"""Purpose: Select negative AI news sentiment records.
Input: List of sentiment records from data/verified/ai-news-sentiment-agent/.
Output: Negative sentiment records for alert review.
Side effects: Optional file write only.
Idempotent: Yes; filtering is deterministic.
Recipe: recipes/ai-news-sentiment-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_news_sentiment_shared import emit, load_input, negative_records


def filter_negative_ai_news(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Purpose: Select negative AI news sentiment records.
    Input: List of sentiment records.
    Output: Negative sentiment records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes.
    Recipe: recipes/ai-news-sentiment-agent.md
    """
    return negative_records(records)


if __name__ == "__main__":
    payload = load_input([{"title": "x", "sentiment": "negative"}, {"title": "y", "sentiment": "positive"}])
    emit(filter_negative_ai_news(payload["data"]), payload["output"])
