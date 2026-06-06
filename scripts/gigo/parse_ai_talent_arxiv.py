"""Purpose: Parse ArXiv AI paper payloads into talent intelligence signals.
Input: Raw ArXiv XML/API payload from data/raw/ai-talent-intelligence-agent/.
Output: Research-paper signal records for data/verified/ai-talent-intelligence-agent/.
Side effects: Optional file write only.
Idempotent: Yes; parsing is deterministic except discovered_at timestamps.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import emit, load_input, parse_arxiv_payload


def parse_ai_talent_arxiv(payload: dict[str, Any] | str) -> list[dict[str, Any]]:
    """Purpose: Parse ArXiv AI paper payloads into talent intelligence signals.
    Input: Raw ArXiv XML/API payload.
    Output: Research-paper signal records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes except timestamps.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    return parse_arxiv_payload(payload)


if __name__ == "__main__":
    sample = {"raw": "<feed xmlns='http://www.w3.org/2005/Atom'><entry><title>GPT-4 Technical Report</title><summary>OpenAI LLM paper</summary><id>https://arxiv.org/abs/1</id><author><name>OpenAI Team</name></author></entry></feed>"}
    payload = load_input(sample)
    emit(parse_ai_talent_arxiv(payload["data"]), payload["output"])
