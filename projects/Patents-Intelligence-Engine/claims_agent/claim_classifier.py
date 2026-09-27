"""
claim_classifier.py — classifies an independent claim's protection scope
(broad/narrow, defensive/offensive/exploratory) using the Claude API.

Real basis for this: our own inspection (inspect_independent_claims.py)
showed word count and limitation-marker count do NOT cleanly separate
broad from narrow scope across our 9 known independent claims — this
is a genuinely judgment-based task, not a mechanical pattern match,
which is why it's implemented as an LLM call rather than a heuristic.
"""
import os
import json
from dataclasses import dataclass
from typing import Optional

import anthropic


@dataclass
class ScopeClassification:
    claim_number: int
    breadth: str          # "broad" | "narrow" | "unclear"
    posture: str          # "defensive" | "offensive" | "exploratory" | "unclear"
    reasoning: str
    confidence_caveat: str  # REQUIRED — what the reading is not sure about


CLASSIFICATION_PROMPT = """You are reading a single independent patent claim to assess its protection scope. You are not a lawyer, and this is not legal advice — you are producing a structured, honest first read for someone doing patent research.

Claim text:
{claim_text}

Classify this claim on two dimensions:

1. BREADTH — "broad" or "narrow". A broad claim uses fewer, more general limitations, covering more ways the invention could be implemented. A narrow claim adds specific structural, numerical, or functional limitations that reduce what falls inside its scope.

2. POSTURE — "defensive", "offensive", or "exploratory".
   - Defensive: claims a specific implementation, likely meant to protect what was actually built, hard to design around without changing the underlying approach.
   - Offensive: claims broadly enough to cover competitors' likely alternative implementations, meant to block a wider space.
   - Exploratory: claims a novel combination or approach where the applicant may be testing the boundaries of what the patent office will allow, without a clear defensive or offensive posture yet.

You must also state a confidence_caveat: one honest sentence naming what this reading is NOT sure about. Do not skip this.

Respond with ONLY a JSON object, no other text:
{{
  "breadth": "broad" | "narrow" | "unclear",
  "posture": "defensive" | "offensive" | "exploratory" | "unclear",
  "reasoning": "one or two sentences on why",
  "confidence_caveat": "one sentence on what this reading is not sure about"
}}
"""


def classify_claim(claim_number: int, claim_text: str, api_key: Optional[str] = None) -> ScopeClassification:
    """
    Classify a single independent claim's protection scope using Claude.

    NOTE: this has not yet been tested against real claims — the prompt
    is designed but unverified. Before trusting any output, run it
    against the 9 known independent claims we already have and read
    the results by hand.
    """
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": CLASSIFICATION_PROMPT.format(claim_text=claim_text),
        }],
    )

    if not message.content:
        return ScopeClassification(
            claim_number=claim_number,
            breadth="unclear",
            posture="unclear",
            reasoning="",
            confidence_caveat=(
                f"Classification was declined by the model (stop_reason={message.stop_reason}). "
                "This claim's subject matter may touch a sensitive category — read the raw "
                "claim text directly rather than relying on an automated scope reading."
            ),
        )

    response_text = message.content[0].text.strip()

    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse Claude's response as JSON: {response_text!r}") from e

    return ScopeClassification(
        claim_number=claim_number,
        breadth=parsed.get("breadth", "unclear"),
        posture=parsed.get("posture", "unclear"),
        reasoning=parsed.get("reasoning", ""),
        confidence_caveat=parsed.get("confidence_caveat", ""),
    )
