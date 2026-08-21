"""
Accountability Layer — Structural Contract
Defines what any agent's output must look like, regardless of provider.

The accountability layer is LLM-agnostic. This module only knows about
the structural contract: two XML blocks, nothing outside them.
Any agent — OpenClaw, Gemini, GPT, local model — must satisfy this contract.

ADR-01b: Directive injection is the mechanism that enforces this contract upstream.
ADR-07:  StructuralParseError triggers the validation loop in middleware.py.
SEC-01:  thought_log is extracted here; middleware decides which tier sees it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# re.MULTILINE makes ^ match at the start of each line.
# This prevents false matches on inline backtick references like `<thought_log>`
# or pre-amble text that mentions the tag names mid-sentence.
_THOUGHT_LOG_RE = re.compile(r"^\s*<thought_log>(.*?)</thought_log>", re.DOTALL | re.MULTILINE)
_CONCLUSION_RE  = re.compile(r"^\s*<conclusion>(.*?)</conclusion>",   re.DOTALL | re.MULTILINE)


class StructuralParseError(Exception):
    """
    Raised when an agent's response fails structural validation.
    Carries the raw response so the middleware can log it as PARSE_FAILURE.
    """

    def __init__(self, message: str, raw_response: str) -> None:
        super().__init__(message)
        self.raw_response = raw_response


@dataclass(frozen=True)
class AgentResponse:
    """
    A structurally valid agent response.
    Provider-agnostic — produced from any raw text that satisfies the contract.
    """
    thought_log: str   # content of <thought_log> block
    conclusion: str    # content of <conclusion> block
    raw_text: str      # full original response, preserved for audit


def _parse_response(raw: str) -> AgentResponse:
    """
    Parse raw agent output into AgentResponse.

    Raises StructuralParseError if:
    - Either block is missing
    - Both blocks are missing
    - Any text exists outside the two blocks

    Note: <conclusion> is searched only in the text AFTER </thought_log> to
    avoid false matches when the model describes the format using backtick-wrapped
    tag names (e.g. `<conclusion>`) inside the thought_log content.
    """
    thought_match = _THOUGHT_LOG_RE.search(raw)

    # Search for <conclusion> starting from the end of <thought_log> block.
    # Falls back to full-string search if thought_log is missing (so we can
    # still report the correct missing-block error below).
    search_from = thought_match.end() if thought_match else 0
    conclusion_match = _CONCLUSION_RE.search(raw, search_from)

    if not thought_match and not conclusion_match:
        raise StructuralParseError(
            "Response missing both <thought_log> and <conclusion> blocks", raw
        )
    if not thought_match:
        raise StructuralParseError("Response missing <thought_log> block", raw)
    if not conclusion_match:
        raise StructuralParseError("Response missing <conclusion> block", raw)

    # Remainder check: remove both matched spans (position-aware) so we don't
    # accidentally re-match the fake tags inside the thought_log content.
    spans = sorted([thought_match.span(), conclusion_match.span()])
    remainder = raw[: spans[0][0]] + raw[spans[0][1] : spans[1][0]] + raw[spans[1][1] :]
    if remainder.strip():
        raise StructuralParseError(
            "Response contains text outside XML blocks", raw
        )

    return AgentResponse(
        thought_log=thought_match.group(1).strip(),
        conclusion=conclusion_match.group(1).strip(),
        raw_text=raw,
    )
