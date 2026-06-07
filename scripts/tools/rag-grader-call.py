"""Purpose: Prepare a local call record for the dependent rag grader workflow.
Input: JSON object with question, answer, and sources from logs/ or data/verified/.
Output: Grader handoff record requiring the rag grader recipe before scoring is trusted.
Side effects: Optional file write only; does not execute another workflow.
Idempotent: Yes; handoff record is deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input


def rag_grader_call(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Prepare a local call record for the dependent rag grader workflow.
    Input: JSON object with question, answer, and sources.
    Output: Grader handoff record.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same handoff.
    Recipe: recipes/news-monitoring-agent.md
    """
    return {"dependent_workflow": "rag grader", "status": "handoff_required", "payload": payload}


if __name__ == "__main__":
    payload = load_json_input({"question": "AI revenue", "answer": "Local answer", "sources": []})
    emit_json(rag_grader_call(payload["data"]), payload["output"])
