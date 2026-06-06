"""Purpose: Prepare FinBERT sentiment invocation or local fallback scores.
Input: Normalized article record.
Output: Hugging Face invocation spec and local lexical sentiment scores.
Side effects: Optional file write only; no model call.
Idempotent: Yes; local fallback is deterministic.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.mycroft_news_intelligence_shared import emit, finbert_spec, lexical_sentiment_scores, load_input
def mycroft_finbert_sentiment_spec(article: dict[str, Any]) -> dict[str, Any]:
    return {"spec": finbert_spec(article), "scores": lexical_sentiment_scores(article.get("processed_text") or article.get("title", ""))}
if __name__ == "__main__":
    payload = load_input({"title":"NVIDIA shares fall","processed_text":"NVIDIA shares fall on risk"})
    emit(mycroft_finbert_sentiment_spec(payload["data"]), payload["output"])
