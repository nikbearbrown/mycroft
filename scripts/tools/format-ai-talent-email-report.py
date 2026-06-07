"""Purpose: Format an AI talent intelligence report as an email payload.
Input: AI talent report JSON from reports/generated/ or logs/.
Output: Subject and HTML body for human-approved email sending.
Side effects: Optional file write only; no email is sent.
Idempotent: Yes; formatting is deterministic for the same report.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import email_payload, emit, load_input


def format_ai_talent_email_report(report: dict[str, Any]) -> dict[str, str]:
    """Purpose: Format an AI talent intelligence report as an email payload.
    Input: AI talent report JSON.
    Output: Subject and HTML body.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same report yields same payload.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    return email_payload(report)


if __name__ == "__main__":
    payload = load_input({"summary": {"total_signals": 1}, "companies": ["OpenAI"]})
    emit(format_ai_talent_email_report(payload["data"]), payload["output"])
