"""Purpose: Generate daily financial intelligence report.
Input: Risk records and optional email handoffs.
Output: Daily report JSON for reports/generated/.
Side effects: Optional file write only.
Idempotent: Yes except report date.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.mycroft_news_intelligence_shared import daily_report, emit, load_input
def mycroft_daily_intelligence_report(payload: dict[str, Any]) -> dict[str, Any]:
    return daily_report(payload.get("records", []), payload.get("email_handoffs", []))
if __name__ == "__main__":
    payload = load_input({"records":[{"risk_level":"LOW"}],"email_handoffs":[]})
    emit(mycroft_daily_intelligence_report(payload["data"]), payload["output"])
