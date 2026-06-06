"""Purpose: Aggregate high-significance AI talent signals.
Input: High-significance signal list from data/verified/ai-talent-intelligence-agent/.
Output: Summary statistics for reports and database payloads.
Side effects: Optional file write only.
Idempotent: Yes; aggregation is deterministic.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import aggregate_statistics, emit, load_input


def aggregate_ai_talent_statistics(signals: list[dict[str, Any]]) -> dict[str, Any]:
    """Purpose: Aggregate high-significance AI talent signals.
    Input: High-significance signal list.
    Output: Summary statistics.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    return aggregate_statistics(signals)


if __name__ == "__main__":
    payload = load_input([{"companies": ["OpenAI"], "researchers": ["Ilya Sutskever"], "technologies": ["GPT-4"], "significance": 8}])
    emit(aggregate_ai_talent_statistics(payload["data"]), payload["output"])
