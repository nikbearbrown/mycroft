"""Purpose: Prepare financial-risk email alert handoff.
Input: Alert payload from scripts/tools/mycroft_alert_generator.py.
Output: Approval-required email handoff.
Side effects: Optional file write only; no email is sent.
Idempotent: Yes; handoff is deterministic except date.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.mycroft_news_intelligence_shared import email_handoff, emit, load_input
def send_mycroft_risk_email_handoff(payload: dict[str, Any]) -> dict[str, Any]:
    return email_handoff(payload)
if __name__ == "__main__":
    payload = load_input({"alert_count":1,"summary":{"total_articles":1}})
    emit(send_mycroft_risk_email_handoff(payload["data"]), payload["output"])
