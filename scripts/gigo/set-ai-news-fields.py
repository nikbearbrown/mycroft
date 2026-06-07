"""Purpose: Set default query fields for AI news sentiment monitoring.
Input: Optional JSON config with ticker/query.
Output: Normalized ticker/query config.
Side effects: Optional file write only.
Idempotent: Yes; defaults are deterministic.
Recipe: recipes/ai-news-sentiment-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_news_sentiment_shared import emit, load_input, ticker_config


def set_ai_news_fields(payload: dict[str, Any] | None = None) -> dict[str, str]:
    """Purpose: Set default query fields for AI news sentiment monitoring.
    Input: Optional JSON config with ticker/query.
    Output: Normalized ticker/query config.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes.
    Recipe: recipes/ai-news-sentiment-agent.md
    """
    return ticker_config(payload)


if __name__ == "__main__":
    payload = load_input({"ticker": "AI", "query": "nvidia"})
    emit(set_ai_news_fields(payload["data"]), payload["output"])
