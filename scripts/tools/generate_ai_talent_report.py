"""Purpose: Generate a structured AI talent intelligence report.
Input: Aggregate statistics from logs/ or data/verified/ai-talent-intelligence-agent/.
Output: Report JSON for reports/generated/.
Side effects: Optional file write only.
Idempotent: Yes except generated_at timestamp.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import emit, intelligence_report, load_input


def generate_ai_talent_report(stats: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Generate a structured AI talent intelligence report.
    Input: Aggregate statistics.
    Output: Report JSON.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes except timestamp.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    return intelligence_report(stats)


if __name__ == "__main__":
    payload = load_input({"total_signals": 1, "companies": ["OpenAI"], "researchers": ["Ilya Sutskever"], "avg_significance": 8})
    emit(generate_ai_talent_report(payload["data"]), payload["output"])
