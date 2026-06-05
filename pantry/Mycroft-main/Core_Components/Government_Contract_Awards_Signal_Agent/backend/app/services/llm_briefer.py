"""
LLM Briefer — generates analyst-grade summaries for high-signal awards using Claude.

Only called for awards with signal_score >= 0.7 to keep API costs low.
"""
import os
import asyncio
import anthropic
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.award import Award

_client: Optional[anthropic.AsyncAnthropic] = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set in environment")
        _client = anthropic.AsyncAnthropic(api_key=api_key)
    return _client


def _build_prompt(award: "Award") -> str:
    amount = f"${award.award_amount:,.0f}" if award.award_amount else "undisclosed"
    return f"""You are a defense and government contracting analyst. Write a concise 2–3 sentence analyst brief for the following federal contract award. Focus on what this award signals strategically — who won, what it means for their position, and why it matters to investors or competitors tracking this space.

Contract details:
- Recipient: {award.recipient_name}
- Awarding agency: {award.awarding_agency} ({award.agency_type or "Unknown type"})
- Amount: {amount}
- Date: {award.award_date or "Unknown"}
- NAICS code: {award.naics_code or "Not specified"}
- Description: {award.description or "Not available"}

Write only the brief — no preamble, no headers, no bullet points. Plain prose, 2–3 sentences."""


async def generate_brief(award: "Award") -> str:
    """Call Claude to generate an analyst brief. Returns empty string on failure."""
    try:
        client = _get_client()
        response = await client.messages.create(
            model="claude-opus-4-6",
            max_tokens=300,
            thinking={"type": "adaptive"},
            messages=[{"role": "user", "content": _build_prompt(award)}],
        )
        # Extract the text block from the response
        for block in response.content:
            if block.type == "text":
                return block.text.strip()
        return ""
    except Exception as e:
        # Never crash the main pipeline — return empty and log
        print(f"[llm_briefer] Failed to generate brief for {award.award_id}: {e}")
        return ""


async def enrich_with_briefs(awards: list, threshold: float = 0.7) -> list:
    """Concurrently generate briefs for all awards above the score threshold."""
    high_signal = [a for a in awards if (a.signal_score or 0) >= threshold]
    if not high_signal:
        return awards

    # Run all brief generations concurrently
    briefs = await asyncio.gather(*[generate_brief(a) for a in high_signal])

    for award, brief in zip(high_signal, briefs):
        award.ai_brief = brief or None

    return awards
