"""Purpose: Fetch AI-related news from NewsAPI.
Input: JSON config with query/pageSize; NEWSAPI_KEY must come from environment for live calls.
Output: NewsAPI-style JSON payload or credential-required spec for data/raw/ai-news-sentiment-agent/.
Side effects: Performs one HTTP GET only when NEWSAPI_KEY is present; optional file write.
Idempotent: Yes for unchanged API response.
Recipe: recipes/ai-news-sentiment-agent.md
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_news_sentiment_shared import emit, load_input


def fetch_ai_newsapi(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Purpose: Fetch AI-related news from NewsAPI.
    Input: JSON config with query/pageSize.
    Output: NewsAPI-style JSON payload or credential-required spec.
    Side effects: HTTP GET only when NEWSAPI_KEY is present.
    Idempotent: Yes for unchanged API response.
    Recipe: recipes/ai-news-sentiment-agent.md
    """
    config = config or {}
    query = str(config.get("query") or "nvidia")
    api_key = os.environ.get("NEWSAPI_KEY")
    if not api_key:
        return {"source_name": "NewsAPI", "query": query, "credential_env": "NEWSAPI_KEY", "live_call_performed": False, "articles": []}
    params = urllib.parse.urlencode({"q": query, "language": "en", "pageSize": int(config.get("pageSize", 5)), "sortBy": "publishedAt", "apiKey": api_key})
    with urllib.request.urlopen(f"https://newsapi.org/v2/everything?{params}", timeout=20) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


if __name__ == "__main__":
    payload = load_input({"query": "nvidia", "pageSize": 5})
    emit(fetch_ai_newsapi(payload["data"]), payload["output"])
