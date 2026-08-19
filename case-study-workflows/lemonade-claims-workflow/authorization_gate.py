"""
WHAT THIS FILE DOES: Decides whether a verified claim gets settled
automatically or escalated to a human, by calling a caller-supplied policy
function - it contains no settlement criteria of its own.

This is the one file in the entire pipeline with zero [DEV] markers, and
that absence is itself meaningful. No dollar threshold, claim-type
restriction, or confidence cutoff is defined here, or anywhere in this file.
Lemonade has not disclosed what makes a claim eligible for automatic
settlement, and this scaffold does not invent one on their behalf - see
DESIGN_DECISIONS.md, "Authorization Gate - no shipped default."

This file deliberately does NOT validate that policy_fn exists or is
callable - that check happens once, at Orchestrator construction (see
orchestrator.py), not here and not per-claim.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GateOutcome:
    status: str  # "SETTLED" or "ESCALATED"
    reason: Optional[str] = None


class AuthorizationGate:
    def decide(self, verified_claim, policy_fn) -> GateOutcome:
        if policy_fn(verified_claim):
            return GateOutcome(status="SETTLED")
        return GateOutcome(status="ESCALATED", reason="not_authorized")
