"""Purpose: Fetch Google News RSS for a company query.
Input: JSON object with company.
Output: Raw RSS payload for data/raw/mycroft-news-intelligence-agent/.
Side effects: Performs one HTTP GET; optional file write.
Idempotent: Yes for unchanged RSS response.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.mycroft_news_intelligence_shared import emit, fetch_google_rss, load_input
def fetch_mycroft_google_rss(payload: dict[str, Any]) -> dict[str, Any]:
    return fetch_google_rss(str(payload.get("company") or payload.get("q") or "NVDA"))
if __name__ == "__main__":
    payload = load_input({"company":"NVDA"})
    try:
        result = fetch_mycroft_google_rss(payload["data"])
    except Exception as exc:
        result = {"source":"Google News RSS","error":str(exc)}
    emit(result, payload["output"])
