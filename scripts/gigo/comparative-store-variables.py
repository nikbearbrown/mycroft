"""Purpose: Add analysis metadata and env-var credential names to peers.
Input: Peer company records.
Output: Peer records with metadata and credential env-var names.
Side effects: Optional file write only; no secrets.
Idempotent: Yes except timestamp.
Recipe: recipes/comparativeanalysisagent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.comparative_analysis_shared import config_for, emit, load_input
def comparative_store_variables(companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return config_for(companies)
if __name__ == "__main__":
    payload = load_input([{"ticker":"MSFT","company_name":"Microsoft","subsector":"Cloud Infrastructure"}])
    emit(comparative_store_variables(payload["data"]), payload["output"])
