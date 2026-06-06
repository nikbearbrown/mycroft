"""Purpose: Prepare company_metrics database upsert payloads.
Input: AI talent report JSON from reports/generated/ or logs/.
Output: Idempotent database operation payloads for human-approved writes.
Side effects: Optional file write only; no database writes.
Idempotent: Yes; payload preparation is deterministic.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import database_payload, emit, load_input


def prepare_ai_talent_database_payload(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Purpose: Prepare company_metrics database upsert payloads.
    Input: AI talent report JSON.
    Output: Idempotent database operation payloads.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same report yields same company rows for the day.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    return database_payload(report)


if __name__ == "__main__":
    payload = load_input({"companies": ["OpenAI"]})
    emit(prepare_ai_talent_database_payload(payload["data"]), payload["output"])
