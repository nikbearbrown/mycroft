"""Purpose: Fetch SerpAPI Google Patents results for a peer company.
Input: Peer record with company_name; SERPAPI_KEY is read from environment for live calls.
Output: Patent payload or credential-required spec.
Side effects: Performs HTTP GET only when env key is present; optional file write.
Idempotent: Yes for unchanged API response.
Recipe: recipes/comparativeanalysisagent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.comparative_analysis_shared import emit, fetch_patents, load_input
def fetch_comparative_patents(peer: dict[str, Any]) -> dict[str, Any]:
    return fetch_patents(str(peer.get("company_name") or peer.get("ticker") or ""))
if __name__ == "__main__":
    payload = load_input({"company_name":"Microsoft"})
    emit(fetch_comparative_patents(payload["data"]), payload["output"])
