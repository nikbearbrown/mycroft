"""
workflow/payout_gate.py

The architectural answer to "payout decisions are never automated." A
Payout agent's recommendation is just a recommendation — nothing executes
until a human-generated, claim-scoped, single-use ClaimDecisionToken is
presented to PayoutExecutionAPI. No agent anywhere in this codebase has
write access to the token store; only HumanReviewSystem can create one.

This is this repo's own construction of how to satisfy Allianz's publicly
stated design principle — it is not a disclosure of how any real insurer's
system actually enforces it. See README.md for the full reasoning,
including why a behavioral instruction (a system prompt telling the model
not to finalize payout) was rejected in favor of this.
"""

import secrets
from dataclasses import dataclass
from datetime import datetime


class TokenAlreadyUsedError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


@dataclass
class ClaimDecisionToken:
    token_value: str
    claim_id: str
    approved: bool
    issued_at: datetime
    used: bool = False


class HumanReviewSystem:
    """
    The ONLY component in this codebase that can create a
    ClaimDecisionToken. No agent imports or instantiates this class.

    [DEV] EXTENSION POINT: this stub takes a plain approved: bool and a
    reviewer identity string with no authentication behind it — a real
    system would authenticate the claims professional (SSO, session
    token, etc.) before issuing a decision token. That authentication
    layer is out of scope for this reference implementation; add it here
    if you're adapting this for anything beyond a demo.
    """

    def __init__(self):
        self._issued_tokens: dict = {}

    def submit_decision(self, claim_id: str, approved: bool, reviewer_id: str) -> ClaimDecisionToken:
        token_value = secrets.token_urlsafe(24)
        token = ClaimDecisionToken(
            token_value=token_value,
            claim_id=claim_id,
            approved=approved,
            issued_at=datetime.utcnow(),
        )
        self._issued_tokens[token_value] = token
        return token


class PayoutExecutionAPI:
    """
    Requires a valid, matching, single-use ClaimDecisionToken as a
    mandatory parameter. This is the enforcement point — nothing upstream
    of this class (no agent, no orchestrator logic) can execute a payout
    without going through here.
    """

    def __init__(self):
        self._executed_claim_ids: set = set()

    def execute_payout(self, claim_id: str, amount_aud: float, token: ClaimDecisionToken) -> str:
        if token.claim_id != claim_id:
            raise InvalidTokenError(
                f"Token is scoped to claim '{token.claim_id}', not '{claim_id}'."
            )
        if token.used:
            raise TokenAlreadyUsedError(f"Token for claim '{claim_id}' has already been used.")
        if not token.approved:
            raise InvalidTokenError(f"Token for claim '{claim_id}' represents a DECLINE, not an approval.")

        token.used = True
        self._executed_claim_ids.add(claim_id)

        # [DEV] EXTENSION POINT: this returns a fake confirmation string.
        # A real implementation would call an actual payment/settlement
        # system here and return its confirmation reference instead.
        return f"EXECUTED:{claim_id}:{amount_aud}"
