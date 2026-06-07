"""Purpose: Score article-title sentiment for AI news.
Input: Article record from data/verified/ai-news-sentiment-agent/.
Output: Sentiment record with title, sentiment, source, publishedAt, and URL.
Side effects: Optional file write only.
Idempotent: Yes; lexical scoring is deterministic.
Recipe: recipes/ai-news-sentiment-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_news_sentiment_shared import emit, load_input, score_sentiment


def score_ai_news_sentiment(article: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Score article-title sentiment for AI news.
    Input: Article record.
    Output: Sentiment record.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes.
    Recipe: recipes/ai-news-sentiment-agent.md
    """
    return score_sentiment(article)


if __name__ == "__main__":
    payload = load_input({"title": "Nvidia shares drop", "source": {"name": "Example"}, "publishedAt": "2026-06-06", "url": "u"})
    emit(score_ai_news_sentiment(payload["data"]), payload["output"])
