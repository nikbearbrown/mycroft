"""Purpose: Select peer companies for a subsector.
Input: JSON with subsector, default Cloud Infrastructure.
Output: Peer company records.
Side effects: Optional file write only.
Idempotent: Yes; peer table is deterministic.
Recipe: recipes/comparativeanalysisagent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.comparative_analysis_shared import emit, load_input, peer_companies
def comparative_peer_company_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return peer_companies(str(payload.get("subsector") or "Cloud Infrastructure"))
if __name__ == "__main__":
    payload = load_input({"subsector":"Cloud Infrastructure"})
    emit(comparative_peer_company_list(payload["data"]), payload["output"])
