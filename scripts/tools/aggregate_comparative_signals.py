"""Purpose: Aggregate comparative news and patent signal records.
Input: List of sentiment and patent records.
Output: Aggregate signal report payload.
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
def aggregate_comparative_signals(records: list[dict[str, Any]]) -> dict[str, Any]:
    return aggregate_records(records)
if __name__ == "__main__":
    payload = load_input([{"company_name":"Microsoft","dominant_sentiment":"positive"},{"company_name":"Microsoft","patent_count":1}])
    emit(aggregate_comparative_signals(payload["data"]), payload["output"])
