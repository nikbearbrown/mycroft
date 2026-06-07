"""Purpose: Prepare a Groq LLM invocation spec for AI talent analysis.
Input: Signal or aggregate JSON from data/verified/ai-talent-intelligence-agent/.
Output: Auditable Groq invocation spec for logs/.
Side effects: Optional file write only; no Groq call.
Idempotent: Yes; same input yields same spec.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import emit, llm_invocation_spec, load_input


def groq_ai_talent_invocation(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Prepare a Groq LLM invocation spec for AI talent analysis.
    Input: Signal or aggregate JSON.
    Output: Auditable Groq invocation spec.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same spec.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    return llm_invocation_spec(payload)


if __name__ == "__main__":
    payload = load_input({"title": "OpenAI hired researcher"})
    emit(groq_ai_talent_invocation(payload["data"]), payload["output"])
