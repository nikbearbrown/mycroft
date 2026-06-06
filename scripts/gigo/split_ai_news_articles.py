"""Purpose: Split NewsAPI articles into individual records.
Input: NewsAPI-style JSON payload from data/raw/ai-news-sentiment-agent/.
Output: Article records for data/verified/ai-news-sentiment-agent/.
Side effects: Optional file write only.
Idempotent: Yes; splitting is deterministic.
Recipe: recipes/ai-news-sentiment-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_news_sentiment_shared import emit, load_input, split_articles


def split_ai_news_articles(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Purpose: Split NewsAPI articles into individual records.
    Input: NewsAPI-style JSON payload.
    Output: Article records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes.
    Recipe: recipes/ai-news-sentiment-agent.md
    """
    return split_articles(payload)


if __name__ == "__main__":
    payload = load_input({"articles": [{"title": "Nvidia shares drop", "source": {"name": "Example"}, "url": "u"}]})
    emit(split_ai_news_articles(payload["data"]), payload["output"])
