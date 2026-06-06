"""Purpose: Fetch NewsAPI articles for a Mycroft company query.
Input: Query record; NEWSAPI_KEY must come from environment for live calls.
Output: NewsAPI payload or credential-required spec for data/raw/mycroft-news-intelligence-agent/.
Side effects: Performs HTTP GET only when NEWSAPI_KEY is set; optional file write.
Idempotent: Yes for unchanged API response.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.mycroft_news_intelligence_shared import emit, fetch_newsapi, load_input
def fetch_mycroft_newsapi(query: dict[str, Any]) -> dict[str, Any]:
    return fetch_newsapi(query)
if __name__ == "__main__":
    payload = load_input({"q":"NVDA OR NVIDIA Corporation","language":"en","pageSize":5})
    emit(fetch_mycroft_newsapi(payload["data"]), payload["output"])
