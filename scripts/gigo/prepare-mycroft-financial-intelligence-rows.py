"""Purpose: Prepare financial_intelligence database rows.
Input: Risk records from data/verified/mycroft-news-intelligence-agent/.
Output: Approval-required database insert payloads.
Side effects: Optional file write only; no database writes.
Idempotent: Yes; payload preparation is deterministic.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.mycroft_news_intelligence_shared import db_payload, emit, load_input
def prepare_mycroft_financial_intelligence_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return db_payload(records)
if __name__ == "__main__":
    payload = load_input([{"item_number":0,"risk_level":"HIGH"}])
    emit(prepare_mycroft_financial_intelligence_rows(payload["data"]), payload["output"])
