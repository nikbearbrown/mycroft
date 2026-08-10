"""
approval_routing.py
===================
Agentic Credit Memo Pipeline — Approval Tier Routing

Why this file exists:
  In commercial banking, a completed credit memo does not go to a single
  approver. Who reviews it depends on the loan size and the risk tier
  the agents assigned. A $10M low-risk revolving facility goes to a Senior
  Credit Officer. A $80M term loan goes to the Credit Committee. A $300M
  facility with a HIGH risk flag goes to the Executive Credit Committee.

  This routing logic is specific to commercial credit — it has no equivalent
  in the AML compliance workflow. It is not "escalation" (a failure path);
  it is the normal approval workflow, tiered by credit authority.

  The routing rules are read from credit_policy.json so they can be updated
  by the credit risk team without touching code.

[DEV] POINTS IN THIS FILE:
  1. Approval tier definitions — edit in credit_policy.json, not here.
  2. ApprovalQueue implementations — replace the dev stubs with real
     routing to your loan origination system's workflow engine.
  3. Risk tier override logic — see _determine_effective_risk_tier() if
     your institution uses composite risk scoring rather than a single tier.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID

from policy_loader import get_loader
from schemas import CreditMemo, CreditRecommendation

logger = logging.getLogger(__name__)

ApprovalTier = Literal[
    "SENIOR_CREDIT_OFFICER",
    "CREDIT_COMMITTEE",
    "EXECUTIVE_CREDIT_COMMITTEE",
]


@dataclass
class RoutingDecision:
    application_id: UUID
    approval_tier: ApprovalTier
    routing_reason: str
    routed_at: datetime


# ─────────────────────────────────────────────────────────────
# ROUTING LOGIC
# ─────────────────────────────────────────────────────────────

def route_memo(
    application_id: UUID,
    requested_amount: Decimal,
    agent_risk_tier: str,
    memo: CreditMemo,
) -> RoutingDecision:
    """
    Determines which approval tier this memo is routed to based on:
      1. The requested loan amount
      2. The risk tier the agents assigned
      3. The agent's recommendation

    The tier boundaries are read from credit_policy.json.

    [DEV] If your institution uses a composite risk score (e.g. combining
    internal rating, external rating, and OSINT severity into a single number),
    replace the agent_risk_tier string with your composite score and update
    _determine_effective_risk_tier() below.
    """
    loader = get_loader()
    tiers = loader.get_approval_tiers()

    # Agent DECLINE recommendations always go to Senior Credit Officer
    # for a human second opinion — do not route declines to committee.
    # [DEV] Adjust this logic if your policy requires committee review of
    # all declines above a certain amount.
    if memo.agent_recommendation == "DECLINE":
        return RoutingDecision(
            application_id=application_id,
            approval_tier="SENIOR_CREDIT_OFFICER",
            routing_reason="Agent recommendation is DECLINE — Senior Credit Officer review required.",
            routed_at=datetime.now(timezone.utc),
        )

    amount = float(requested_amount)
    effective_tier = _determine_effective_risk_tier(agent_risk_tier)

    # Executive Credit Committee: HIGH/WATCH_LIST risk or no amount cap
    exec_config = tiers.get("executive_credit_committee", {})
    if effective_tier in exec_config.get("applies_to_risk_tiers", []):
        max_amt = exec_config.get("max_loan_amount_usd")
        if max_amt is None or amount > max_amt:
            return RoutingDecision(
                application_id=application_id,
                approval_tier="EXECUTIVE_CREDIT_COMMITTEE",
                routing_reason=(
                    f"Risk tier '{effective_tier}' requires Executive Credit Committee review. "
                    f"Requested amount: ${amount:,.0f}."
                ),
                routed_at=datetime.now(timezone.utc),
            )

    # Credit Committee: mid-range amounts
    committee_config = tiers.get("credit_committee", {})
    committee_max = committee_config.get("max_loan_amount_usd", 150_000_000)
    if amount > tiers.get("senior_credit_officer", {}).get("max_loan_amount_usd", 25_000_000):
        return RoutingDecision(
            application_id=application_id,
            approval_tier="CREDIT_COMMITTEE",
            routing_reason=(
                f"Requested amount ${amount:,.0f} exceeds Senior Credit Officer authority. "
                f"Routing to Credit Committee."
            ),
            routed_at=datetime.now(timezone.utc),
        )

    # Default: Senior Credit Officer
    return RoutingDecision(
        application_id=application_id,
        approval_tier="SENIOR_CREDIT_OFFICER",
        routing_reason=(
            f"Requested amount ${amount:,.0f} within Senior Credit Officer authority. "
            f"Risk tier: {effective_tier}."
        ),
        routed_at=datetime.now(timezone.utc),
    )


def _determine_effective_risk_tier(agent_risk_tier: str) -> str:
    """
    Maps agent output risk tier strings to the policy tier keys.

    [DEV] If your agents produce a numeric credit score (e.g. 1–10) rather
    than a tier label, convert it here to the policy tier keys:
    LOW / MEDIUM / HIGH / WATCH_LIST.
    """
    mapping = {
        "LOW": "LOW",
        "MEDIUM": "MEDIUM",
        "HIGH": "HIGH",
        "WATCH": "WATCH_LIST",
        "WATCH_LIST": "WATCH_LIST",
    }
    return mapping.get(agent_risk_tier.upper(), "MEDIUM")


# ─────────────────────────────────────────────────────────────
# ESCALATION ROUTING (blocking path)
# ─────────────────────────────────────────────────────────────

def escalation_routing(application_id: UUID, reason: str) -> RoutingDecision:
    """
    Builds a RoutingDecision for a pipeline that was halted by a blocking
    signal (KYC block, HIGH OSINT, or FAIL ratio) before memo synthesis ran.

    All blocked applications route to SENIOR_CREDIT_OFFICER regardless of
    loan size — the blocking finding must be reviewed before any credit
    authority is applied.

    [DEV] If your policy requires a different escalation target (e.g. a
    dedicated Compliance team queue for KYC blocks vs. a Credit Risk queue
    for ratio failures), add a `block_type` parameter and dispatch here.
    """
    return RoutingDecision(
        application_id=application_id,
        approval_tier="SENIOR_CREDIT_OFFICER",
        routing_reason=f"Pipeline halted — blocking condition: {reason}",
        routed_at=datetime.now(timezone.utc),
    )


# ─────────────────────────────────────────────────────────────
# APPROVAL QUEUE INTERFACE
# ─────────────────────────────────────────────────────────────

class ApprovalQueue(ABC):
    """
    Interface for routing a memo to the correct approval tier.

    submit() is called on both the successful path (a complete CreditMemo)
    and the blocked path. On the blocked path, orchestrator._block() constructs
    a placeholder CreditMemo: standard fields are populated with whatever agent
    outputs were available before the halt, and fields that synthesis would have
    produced are set to explicit "not assessed" strings. The memo argument is
    never None — this interface stays uniform across both paths.

    [DEV] Implement one class per approval tier, or a single class that
    dispatches based on the RoutingDecision. Connect to your loan
    origination system's workflow engine (e.g. nCino, Salesforce Financial
    Services Cloud, or an internal queue backed by PostgreSQL or SQS).
    """

    @abstractmethod
    def submit(self, routing: RoutingDecision, memo: CreditMemo) -> None:
        """Submit the memo (or blocking placeholder) to the approval queue."""
