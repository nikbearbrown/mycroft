"""Purpose: Aggregate comparative financial metric records.
Input: List of financial metric records.
Output: Aggregate report payload.
Side effects: Optional file write only.
Idempotent: Yes except generated timestamp.
Recipe: recipes/comparativeanalysisagent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.comparative_analysis_shared import aggregate_records, emit, load_input
def aggregate_comparative_financials(records: list[dict[str, Any]]) -> dict[str, Any]:
    return aggregate_records(records)
if __name__ == "__main__":
    payload = load_input([{"ticker":"MSFT","financial_health_score":0.2}])
    emit(aggregate_comparative_financials(payload["data"]), payload["output"])
