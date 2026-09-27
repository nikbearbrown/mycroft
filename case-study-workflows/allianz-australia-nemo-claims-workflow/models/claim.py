"""
Core data models for the Nemo claims workflow.

These are the shapes every agent reads and writes. Defining them once, here,
is what lets each agent file stay focused on its own logic instead of
re-describing what a "claim" or a "policy record" looks like.

[DEV] These models are illustrative and intentionally minimal — they cover
exactly what this reference workflow's 7 agents need. A real claims system
would have many more fields (claim history, adjuster notes, document
attachments, etc.). Extend these dataclasses if your use case needs more,
but keep every agent's input/output shape matching what's declared here,
or the provider adapters' schema validation (providers/base.py) will reject
malformed agent calls.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ClaimStatus(str, Enum):
    """Where a claim currently sits in the pipeline. Used for CLI/API display
    and for the Audit agent's summary — not itself a business decision."""
    SUBMITTED = "submitted"
    COVERAGE_REJECTED = "coverage_rejected"
    WEATHER_UNMATCHED = "weather_unmatched"          # still proceeds to Fraud — see fraud.py
    FRAUD_FLAGGED = "fraud_flagged"                   # [DEV] extension point, see fraud.py
    PAYOUT_RECOMMENDED = "payout_recommended"
    AWAITING_HUMAN_REVIEW = "awaiting_human_review"
    HUMAN_APPROVED = "human_approved"
    HUMAN_DECLINED = "human_declined"


@dataclass
class Claim:
    """A single food-spoilage claim as it enters the pipeline via Planner.

    [DEV] claim_id/policy_id are strings here for simplicity. A real system
    would validate these against actual policy-system identifiers before
    Planner ever creates this object.
    """
    claim_id: str
    policy_id: str
    customer_name: str
    description: str
    claimed_amount: float          # AUD
    location: str                  # suburb/postcode-level, matches Weather's lookup key
    outage_timestamp: datetime
    filed_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PolicyRecord:
    """Stub policy lookup result. In production this is a call to Allianz's
    actual policy database — here it's a fixture (see data/stub_scenarios.py).

    [DEV] covers_food_spoilage and covers_severe_weather are modeled as two
    separate booleans on purpose: a real policy could cover one without the
    other (e.g. a policy that covers spoilage from fridge breakdown but not
    from weather-caused outages). Coverage agent must check both.
    """
    policy_id: str
    active: bool
    covers_food_spoilage: bool
    covers_severe_weather_outage: bool
    policy_limit_aud: float


@dataclass
class AgentOutput:
    """Common wrapper every agent returns. Audit agent's summary is built by
    reading a list of these — one per agent that has run so far.

    [DEV] `provider_name` is carried through specifically so the Audit
    summary and the append-only log can show which LLM provider produced
    each agent's conclusion — relevant given this workflow supports 3
    providers and none has been runtime-verified against live model
    behavior in this build (see README, "Provider Verification Status").
    """
    agent_name: str
    conclusion: str                # short label: "covered" / "not_covered" / "clear" / "flagged" / etc.
    reasoning: str
    provider_name: str
    raw_response: Optional[str] = None
