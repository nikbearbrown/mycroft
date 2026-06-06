"""Purpose: Prepare Airtable create-record payload for AI news sentiment.
Input: Sentiment record from data/verified/ai-news-sentiment-agent/.
Output: Airtable handoff payload requiring approval.
Side effects: Optional file write only; no Airtable write.
Idempotent: Yes; payload preparation is deterministic.
Recipe: recipes/ai-news-sentiment-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_news_sentiment_shared import airtable_payload, emit, load_input


def prepare_ai_news_airtable_record(record: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Prepare Airtable create-record payload for AI news sentiment.
    Input: Sentiment record.
    Output: Airtable handoff payload requiring approval.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes.
    Recipe: recipes/ai-news-sentiment-agent.md
    """
    return airtable_payload(record)


if __name__ == "__main__":
    payload = load_input({"title": "Nvidia shares drop", "sentiment": "negative", "source": "Example", "url": "u"})
    emit(prepare_ai_news_airtable_record(payload["data"]), payload["output"])
