"""Purpose: Normalize NewsAPI articles.
Input: NewsAPI payload from data/raw/mycroft-news-intelligence-agent/.
Output: Normalized article records.
Side effects: Optional file write only.
Idempotent: Yes; normalization is deterministic.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.mycroft_news_intelligence_shared import emit, load_input, normalize_newsapi
def normalize_mycroft_newsapi(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return normalize_newsapi(payload)
if __name__ == "__main__":
    payload = load_input({"articles":[{"title":"NVIDIA shares fall","description":"risk news","url":"u","source":{"name":"Example"}}]})
    emit(normalize_mycroft_newsapi(payload["data"]), payload["output"])
