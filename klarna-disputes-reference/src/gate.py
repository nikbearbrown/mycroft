"""
WHAT THIS FILE DOES: Decides whether a case gets auto-resolved or escalated
to a human. This is the file with the least confirmed basis in the entire
repo — Klarna states only, in general terms, that humans handle "nuanced,"
"complex," and "high-value" cases. No numeric axis, no rule set, nothing
mechanical is disclosed. This file's entire job is to make that invented
decision visible and swappable, not to make it sound more principled than
it is.

See docs/DESIGN_DECISIONS.md DD-002, DD-003, DD-005, DD-012.
"""

from dataclasses import dataclass
from typing import Optional

from .verification import VerificationResult
from .intake import IntakeResult


# [DEV] Not derived from any Klarna data or tuning process. Kept at 0.6 for
# consistency with this series' prior precedent, not because 0.6 is
# defensible on its own. Replace this with a value suited to your own data
# if you adopt this repo (DD-005).
CONFIDENCE_THRESHOLD = 0.6


@dataclass
class GateDecision:
    """
    outcome: "resolved" | "escalated"
    reason:  None | "mismatch" | "ambiguous_delay" | "low_confidence" —
             only populated when outcome == "escalated". These three reasons
             are Gate's alone; "unclassified", "no_record", and
             "incomplete_claim" belong to the orchestrator and never reach
             here (DD-002) — see the precondition check below.
    """
    outcome: str
    reason: Optional[str]


def evaluate(verification_result: VerificationResult, intake_result: IntakeResult) -> GateDecision:
    """
    Decision order is locked (DD-012) and matters:

      1. If the record mismatches the claim, escalate on that basis —
         regardless of how confident Intake was about classification.
      2. Only if the record MATCHES, check confidence.
      3. Otherwise, resolve.

    Rationale for checking mismatch before confidence: a disagreement with
    Klarna's own record is a finding about the CLAIM itself. Low confidence
    is a finding about Intake's own uncertainty. Those aren't the same kind
    of problem — a human agent seeing reason="low_confidence" should be able
    to trust that means "we weren't sure what was being asked," not "we
    checked and it's also wrong." Collapsing the two into one signal would
    make low_confidence a strictly less useful flag for whoever reviews it.
    """
    # Defended precondition, not assumed: this function must never be called
    # with a structural-failure status. If it is, that's an orchestrator
    # contract violation — fail loudly here rather than silently
    # mis-evaluating a status this function was never designed to handle.
    if verification_result.status not in ("match", "mismatch"):
        raise ValueError(
            f"gate.evaluate() called with an invalid VerificationResult.status: "
            f"{verification_result.status!r}. Gate must only ever be called "
            f"after Verification returns 'match' or 'mismatch' — structural "
            f"failures ('escalate_no_record', 'escalate_incomplete_claim') "
            f"belong to the orchestrator and should never reach this function."
        )

    if verification_result.status == "mismatch":
        if verification_result.mismatch_reason == "processing_delay_noted":
            return GateDecision(outcome="escalated", reason="ambiguous_delay")
        return GateDecision(outcome="escalated", reason="mismatch")

    # status == "match" from here on.
    if intake_result.confidence < CONFIDENCE_THRESHOLD:
        return GateDecision(outcome="escalated", reason="low_confidence")

    return GateDecision(outcome="resolved", reason=None)
