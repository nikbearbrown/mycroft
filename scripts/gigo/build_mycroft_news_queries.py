"""Purpose: Build per-company NewsAPI query payloads.
Input: Company records from scripts/gigo/mycroft_company_list.py.
Output: Query records for data/verified/mycroft-news-intelligence-agent/.
Side effects: Optional file write only.
Idempotent: Yes except lookback timestamp.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.mycroft_news_intelligence_shared import build_queries, emit, load_input
def build_mycroft_news_queries(companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return build_queries(companies)
if __name__ == "__main__":
    payload = load_input([{"symbol":"NVDA","name":"NVIDIA Corporation","riskMultiplier":1.0}])
    emit(build_mycroft_news_queries(payload["data"]), payload["output"])
