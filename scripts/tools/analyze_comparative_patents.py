"""Purpose: Summarize AI patent signal for a peer company.
Input: SerpAPI Google Patents payload.
Output: Patent count, assignee list, and AI patent signal label.
Side effects: Optional file write only.
Idempotent: Yes; analysis is deterministic.
Recipe: recipes/comparativeanalysisagent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.comparative_analysis_shared import emit, load_input, patent_summary
def analyze_comparative_patents(payload: dict[str, Any]) -> dict[str, Any]:
    return patent_summary(payload)
if __name__ == "__main__":
    payload = load_input({"company_name":"Microsoft","organic_results":[{"assignee":"Microsoft"}]})
    emit(analyze_comparative_patents(payload["data"]), payload["output"])
