"""Purpose: Convert sentiment scores into financial risk records.
Input: Sentiment score rows from logs/ or local fallback.
Output: Risk record with dominant sentiment, risk score, and risk level.
Side effects: Optional file write only.
Idempotent: Yes except processed timestamp.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.mycroft_news_intelligence_shared import emit, load_input, risk_record
def mycroft_risk_calculator(payload: dict[str, Any]) -> dict[str, Any]:
    return risk_record(payload.get("scores", payload if isinstance(payload, list) else []), int(payload.get("item_number", 0)) if isinstance(payload, dict) else 0, float(payload.get("riskMultiplier", 1.0)) if isinstance(payload, dict) else 1.0)
if __name__ == "__main__":
    payload = load_input({"scores":[{"label":"negative","score":0.8},{"label":"positive","score":0.1},{"label":"neutral","score":0.1}]})
    emit(mycroft_risk_calculator(payload["data"]), payload["output"])
