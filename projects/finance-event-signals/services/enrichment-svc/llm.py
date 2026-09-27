"""Pluggable LLM behind the enrichment graph.

- DeterministicLLM  : offline, rule-based, seeded. Default. The graph STRUCTURE
                      (classify -> extract -> self-consistency -> verify -> emit|withhold)
                      is identical whichever LLM is used.
- AnthropicLLM      : real model. Enabled with LLM_PROVIDER=anthropic + ANTHROPIC_API_KEY.
                      Self-consistency across temperatures is only meaningful here.
"""

from __future__ import annotations

import json
import os
import re

DIRECTIONS = {"up", "down", "unclear"}
MAGNITUDES = {"small", "medium", "large"}

# 8-K items that carry a strong directional prior regardless of wording.
_DOWN_TYPES = {
    "bankruptcy", "restatement", "impairment", "delisting",
    "debt_acceleration", "restructuring_costs", "material_agreement_termination",
    "auditor_change",
}
_STRONG_TYPES = {"bankruptcy", "restatement", "delisting", "earnings", "impairment"}

_DOWN_KW = (
    "going concern", "default", "chapter 11", "investigation", "subpoena",
    "resign", "steps down", "lowers guidance", "miss", "below expectations",
    "impairment", "delist", "restat", "shortfall", "cut",
)
_UP_KW = (
    "beat", "exceed", "record", "raises guidance", "above expectations",
    "approval", "authorized", "buyback", "repurchase", "upsized", "wins",
)


class DeterministicLLM:
    provider = "deterministic"

    def extract(self, event_type: str, title: str, items: list[str], temperature: float = 0.0) -> dict:
        t = (title or "").lower()
        direction = "unclear"

        if event_type == "earnings":
            if any(k in t for k in _UP_KW):
                direction = "up"
            elif any(k in t for k in _DOWN_KW):
                direction = "down"
        elif event_type in _DOWN_TYPES:
            direction = "down"
        elif any(k in t for k in _UP_KW):
            direction = "up"
        elif any(k in t for k in _DOWN_KW):
            direction = "down"

        # strong keyword override
        if any(k in t for k in ("going concern", "chapter 11", "default", "delist")):
            direction = "down"

        if direction == "unclear":
            magnitude, confidence = "small", 0.3
        elif event_type in _STRONG_TYPES:
            magnitude, confidence = "large", 0.85
        else:
            magnitude, confidence = "medium", 0.6

        return {
            "direction": direction,
            "magnitude": magnitude,
            "confidence": confidence,
            "rationale": f"deterministic: event_type={event_type}, title keywords -> {direction}",
        }

    def critique(self, event_type: str, title: str, extraction: dict) -> dict:
        ok = extraction["confidence"] >= 0.5 and extraction["direction"] in ("up", "down")
        return {
            "ok": ok,
            "reason": "" if ok else "second look: direction unclear or confidence below 0.5",
        }


_SYS_EXTRACT = (
    "You read SEC 8-K filing metadata (event type, title, item codes) and estimate the "
    "likely SHORT-TERM effect on the filer's own stock price. Output a JSON object ONLY, "
    "no prose:\n"
    '{"direction":"up|down|unclear","magnitude":"small|medium|large",'
    '"confidence":<0.0-1.0>,"rationale":"<one sentence>"}\n'
    "Use 'unclear' whenever the metadata genuinely does not indicate a direction. "
    "Do not guess to seem decisive. You are not giving investment advice."
)
_SYS_CRITIQUE = (
    "You are a skeptical reviewer. Given an 8-K's metadata and a proposed read, decide if the "
    'read is defensible from the metadata alone. Output JSON ONLY: {"ok":true|false,"reason":"..."} '
    "Reject reads that overstate confidence, infer a direction the metadata does not support, or "
    "treat routine filings as material."
)


class AnthropicLLM:
    provider = "anthropic"

    def __init__(self, model: str):
        import anthropic

        self._client = anthropic.Anthropic()
        self._model = model

    def _json(self, system: str, user: str, temperature: float) -> dict:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=400,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        m = re.search(r"\{.*\}", text, re.S)
        return json.loads(m.group(0) if m else text)

    def extract(self, event_type: str, title: str, items: list[str], temperature: float = 0.3) -> dict:
        user = f"event_type: {event_type}\ntitle: {title}\nitem codes: {', '.join(items) or 'none'}"
        d = self._json(_SYS_EXTRACT, user, temperature)
        d["direction"] = d.get("direction") if d.get("direction") in DIRECTIONS else "unclear"
        d["magnitude"] = d.get("magnitude") if d.get("magnitude") in MAGNITUDES else "small"
        d["confidence"] = float(d.get("confidence", 0.0))
        d["rationale"] = str(d.get("rationale", ""))[:400]
        return d

    def critique(self, event_type: str, title: str, extraction: dict) -> dict:
        user = (
            f"event_type: {event_type}\ntitle: {title}\n"
            f"proposed read: {json.dumps(extraction)}"
        )
        d = self._json(_SYS_CRITIQUE, user, 0.0)
        return {"ok": bool(d.get("ok")), "reason": str(d.get("reason", ""))[:300]}


def make_llm() -> object:
    provider = os.getenv("LLM_PROVIDER", "deterministic").lower()
    if provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicLLM(os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"))
    return DeterministicLLM()
