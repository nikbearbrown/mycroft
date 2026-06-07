"""Purpose: Prepare a negative-news email alert handoff.
Input: Negative sentiment record from data/verified/ai-news-sentiment-agent/.
Output: Email handoff requiring human approval and SMTP env vars.
Side effects: Optional file write only; no email is sent.
Idempotent: Yes; handoff generation is deterministic.
Recipe: recipes/ai-news-sentiment-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_news_sentiment_shared import email_handoff, emit, load_input


def send_negative_ai_news_email_handoff(record: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Prepare a negative-news email alert handoff.
    Input: Negative sentiment record.
    Output: Email handoff requiring human approval and SMTP env vars.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes.
    Recipe: recipes/ai-news-sentiment-agent.md
    """
    return email_handoff(record)


if __name__ == "__main__":
    payload = load_input({"title": "Nvidia shares drop", "url": "u"})
    emit(send_negative_ai_news_email_handoff(payload["data"]), payload["output"])
