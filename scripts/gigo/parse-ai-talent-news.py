"""Purpose: Parse Serper news payloads into AI talent movement signals.
Input: Serper-style news JSON from data/raw/ai-talent-intelligence-agent/.
Output: News signal records for data/verified/ai-talent-intelligence-agent/.
Side effects: Optional file write only.
Idempotent: Yes; parsing is deterministic except discovered_at timestamps.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import emit, load_input, parse_news_payload


def parse_ai_talent_news(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Purpose: Parse Serper news payloads into AI talent movement signals.
    Input: Serper-style news JSON.
    Output: News signal records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes except timestamps.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    return parse_news_payload(payload)


if __name__ == "__main__":
    sample = {"news": [{"title": "OpenAI hired an AI researcher", "snippet": "Researcher joined OpenAI to work on GPT-4", "link": "https://example.com/n", "date": "2026-06-06"}]}
    payload = load_input(sample)
    emit(parse_ai_talent_news(payload["data"]), payload["output"])
