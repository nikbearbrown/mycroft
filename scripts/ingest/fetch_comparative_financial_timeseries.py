"""Purpose: Fetch Alpha Vantage daily time series for a peer company.
Input: Peer record with ticker; ALPHA_VANTAGE_API_KEY is read from environment for live calls.
Output: Time-series payload or credential-required spec.
Side effects: Performs HTTP GET only when env key is present; optional file write.
Idempotent: Yes for unchanged API response.
Recipe: recipes/comparativeanalysisagent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.comparative_analysis_shared import emit, fetch_alpha_vantage, load_input
def fetch_comparative_financial_timeseries(peer: dict[str, Any]) -> dict[str, Any]:
    return fetch_alpha_vantage("TIME_SERIES_DAILY", str(peer.get("ticker", "")))
if __name__ == "__main__":
    payload = load_input({"ticker":"MSFT"})
    emit(fetch_comparative_financial_timeseries(payload["data"]), payload["output"])
