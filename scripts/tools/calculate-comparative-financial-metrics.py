"""Purpose: Calculate financial health metrics from overview and time-series payloads.
Input: JSON object with overview, time_series, ticker, and company_name.
Output: Financial metric record.
Side effects: Optional file write only.
Idempotent: Yes; calculations are deterministic.
Recipe: recipes/comparativeanalysisagent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.comparative_analysis_shared import emit, financial_metrics, load_input
def calculate_comparative_financial_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    return financial_metrics(payload)
if __name__ == "__main__":
    sample = {"ticker":"MSFT","overview":{"Symbol":"MSFT","ProfitMargin":"0.3","PERatio":"35"},"time_series":{"Time Series (Daily)":{"2026-06-06":{"4. close":"100"}}}}
    payload = load_input(sample)
    emit(calculate_comparative_financial_metrics(payload["data"]), payload["output"])
