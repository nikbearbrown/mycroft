"""Purpose: Summarize peer-company news sentiment.
Input: NewsAPI-style payload from data/raw/comparativeanalysisagent/.
Output: Sentiment summary for the company.
Side effects: Optional file write only.
Idempotent: Yes; lexical analysis is deterministic.
Recipe: recipes/comparativeanalysisagent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.comparative_analysis_shared import emit, load_input, news_sentiment
def analyze_comparative_news_sentiment(payload: dict[str, Any]) -> dict[str, Any]:
    return news_sentiment(payload)
if __name__ == "__main__":
    payload = load_input({"company_name":"Microsoft","articles":[{"title":"Microsoft reports strong growth"}]})
    emit(analyze_comparative_news_sentiment(payload["data"]), payload["output"])
