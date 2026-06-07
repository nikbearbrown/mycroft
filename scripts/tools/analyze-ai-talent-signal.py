"""Purpose: Produce a local LLM-analysis equivalent for AI talent signals.
Input: Talent signal JSON from data/verified/ai-talent-intelligence-agent/.
Output: JSON object with companies, researchers, technologies, sentiment, and significance.
Side effects: Optional file write only; no Groq call; GROQ_API_KEY is for future live adapter.
Idempotent: Yes; local extraction is deterministic.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import emit, extract_companies, extract_researchers, extract_technologies, load_input


def analyze_ai_talent_signal(signal: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Produce a local LLM-analysis equivalent for AI talent signals.
    Input: Talent signal JSON.
    Output: JSON object with companies, researchers, technologies, sentiment, and significance.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    text = f"{signal.get('title', '')} {signal.get('snippet', '')} {signal.get('raw_content', '')}"
    companies = signal.get("companies") or extract_companies(text)
    researchers = signal.get("researchers") or extract_researchers(text)
    technologies = signal.get("technologies") or extract_technologies(text)
    significance = int(signal.get("significance") or min(10, 3 + len(companies) + len(researchers) + len(technologies)))
    return {"companies": companies, "researchers": researchers, "technologies": technologies, "sentiment": "positive" if significance > 5 else "neutral", "significance": significance, "source": signal}


if __name__ == "__main__":
    payload = load_input({"title": "OpenAI hired researcher for GPT-4", "snippet": "AI researcher joined OpenAI"})
    emit(analyze_ai_talent_signal(payload["data"]), payload["output"])
