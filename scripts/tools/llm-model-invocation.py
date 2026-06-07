"""Purpose: Create an auditable invocation spec for chat-model nodes.
Input: JSON object with prompt, model, provider, and optional node_name from verified data.
Output: Invocation spec suitable for logs/ without calling an external LLM.
Side effects: Optional file write only; no external service calls; provider API keys are future live-run environment variables.
Idempotent: Yes; same input yields same invocation spec.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input


def llm_model_invocation(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Create an auditable invocation spec for chat-model nodes.
    Input: JSON object with prompt, model, provider, and optional node_name.
    Output: Invocation spec suitable for logs/.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    provider = payload.get("provider", "google_gemini")
    return {
        "node_name": payload.get("node_name", "chat model"),
        "provider": provider,
        "model": payload.get("model", "configured-in-environment"),
        "prompt_preview": str(payload.get("prompt", ""))[:500],
        "credential_env": "GOOGLE_API_KEY" if provider == "google_gemini" else "OPENROUTER_API_KEY",
        "live_call_performed": False,
    }


if __name__ == "__main__":
    payload = load_json_input({"node_name": "Google Gemini Chat Model", "prompt": "Summarize AI news"})
    emit_json(llm_model_invocation(payload["data"]), payload["output"])
