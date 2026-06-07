"""Purpose: Prepare an email-send handoff record for the AI talent report.
Input: Email payload with subject and html from logs/.
Output: Handoff record requiring human approval and SMTP configuration.
Side effects: Optional file write only; no email is sent.
Idempotent: Yes; handoff generation is deterministic.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import emit, load_input


def send_ai_talent_email_handoff(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Prepare an email-send handoff record for the AI talent report.
    Input: Email payload with subject and html.
    Output: Handoff record requiring human approval and SMTP configuration.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same handoff.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    return {"status": "approval_required", "smtp_env": ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"], "email": payload, "sent": False}


if __name__ == "__main__":
    payload = load_input({"subject": "AI Talent Intelligence Report", "html": "<h1>Report</h1>"})
    emit(send_ai_talent_email_handoff(payload["data"]), payload["output"])
