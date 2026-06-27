"""
escalation.py
=============
Agentic AML Compliance Workflow — Escalation Sub-Workflow
US Equities · OFAC/BSA/FinCEN

Implements the _escalate() stub from orchestrator.py.

What this file defines:
  EscalationPackage   — what gets routed to the senior officer
  EscalationDecision  — what the senior officer returns
  RoutingRule         — a single routing condition
  EscalationRouter    — matches a package to a team using rules
  EscalationQueue     — concrete implementation (replace with your queue)

Integration:
  1. Pass an EscalationRouter to AMLOrchestrator at construction time.
  2. The orchestrator's _escalate() calls self.escalation_queue.enqueue()
     using a package built by EscalationPackageBuilder.
  3. Senior officer reviews via your review UI and submits EscalationDecision.
  4. Decision is read from the resolution store by the orchestrator or
     a separate resolution handler (see EscalationDecision.resolution_path).

Dependencies:
    pip install pydantic>=2.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# ESCALATION PACKAGE — what the senior officer receives
# ─────────────────────────────────────────────────────────────

class EscalationPackage(BaseModel):
    """
    The complete context package routed to the senior compliance officer.
    Built by the orchestrator at the point of escalation.
    Carried by the escalation queue to the review UI.

    The senior officer sees:
      - Why the escalation was triggered (escalation_reason)
      - Which step triggered it (escalation_source)
      - All agent outputs produced before escalation (agent_outputs)
      - The original trade data and AML flag (trade_summary)
      - Routing context (assigned_team, priority)
    """
    escalation_id: UUID = field(default_factory=uuid4)
    trade_id: UUID
    escalation_reason: str = field(
        description="Plain-English reason the pipeline escalated. "
                    "Written by the agent or validator that triggered escalation."
    )
    escalation_source: Literal[
        "triage_agent",
        "investigation_agent",
        "reasoning_agent",
        "report_agent",
        "prefetch",          # Data source unavailable during pre-fetch
        "loop_limit",        # MAX_STEPS exceeded
        "human_decision",    # Human officer chose to escalate
        "confidence_score",  # AML flag confidence above auto-escalate threshold
    ]
    agent_outputs: dict[str, str] = field(
        default_factory=dict,
        description="All agent outputs produced before escalation. "
                    "Keys: agent names. Values: raw output text."
    )
    trade_summary: str = field(
        description="The trade.to_pipeline_string() output. "
                    "Contains all trade fields and AML flag details."
    )
    flag_type: str = field(
        description="AML flag type from the trade. Used for routing."
    )
    desk_id: str = field(
        description="Trading desk identifier. Used for routing."
    )
    trade_value_usd: str = field(
        description="Trade value as a formatted string. Used for priority calculation."
    )
    assigned_team: str = field(
        default="senior-compliance-default",
        description="Team or officer assigned by EscalationRouter. "
                    "Set by the orchestrator after routing."
    )
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "HIGH"
    escalated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Config:
        arbitrary_types_allowed = True

    def to_review_summary(self) -> str:
        """
        Formats the package as a plain-text review summary for the senior officer.
        This is displayed in the escalation review UI.
        """
        outputs_text = ""
        for agent_name, output in self.agent_outputs.items():
            outputs_text += f"\n\n[{agent_name.upper()}]:\n{output}"

        return (
            f"ESCALATION REVIEW\n"
            f"{'=' * 60}\n"
            f"Escalation ID:  {self.escalation_id}\n"
            f"Trade ID:       {self.trade_id}\n"
            f"Assigned team:  {self.assigned_team}\n"
            f"Priority:       {self.priority}\n"
            f"Escalated at:   {self.escalated_at.isoformat()}\n"
            f"Source:         {self.escalation_source}\n"
            f"\nESCALATION REASON:\n{self.escalation_reason}\n"
            f"\nTRADE DATA:\n{self.trade_summary}"
            + (f"\n\nAGENT OUTPUTS BEFORE ESCALATION:{outputs_text}" if outputs_text else "")
        )


# ─────────────────────────────────────────────────────────────
# ESCALATION DECISION — what the senior officer returns
# ─────────────────────────────────────────────────────────────

EscalationOutcome = Literal[
    "APPROVED",          # Senior officer clears the trade — generate approval token
    "BLOCKED",           # Senior officer blocks the trade — initiate SAR assessment
    "ESCALATE_FURTHER",  # Route to compliance committee or legal
]


class EscalationDecision(BaseModel):
    """
    The senior compliance officer's decision on an escalated trade.
    Written to the audit log and drives the resolution path.
    """
    escalation_id: UUID
    trade_id: UUID
    officer_id: str
    outcome: EscalationOutcome
    rationale: str = field(
        description="Officer's written rationale. Required for all outcomes. "
                    "Written to the audit log and, if BLOCKED, accompanies the SAR assessment."
    )
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    further_escalation_target: str | None = field(
        default=None,
        description="Required when outcome=ESCALATE_FURTHER. "
                    "Names the team or committee this is escalated to. "
                    "Example: 'compliance-committee', 'legal-aml-team'"
    )

    @property
    def resolution_path(self) -> str:
        """
        Human-readable summary of the resolution path for audit logging.
        """
        if self.outcome == "APPROVED":
            return f"Approved by {self.officer_id} at {self.timestamp.isoformat()}"
        elif self.outcome == "BLOCKED":
            return f"Blocked by {self.officer_id} at {self.timestamp.isoformat()}"
        elif self.outcome == "ESCALATE_FURTHER":
            return (
                f"Escalated further by {self.officer_id} "
                f"to {self.further_escalation_target} "
                f"at {self.timestamp.isoformat()}"
            )
        return f"Unknown outcome: {self.outcome}"


# ─────────────────────────────────────────────────────────────
# ROUTING — who receives the escalation
# ─────────────────────────────────────────────────────────────

@dataclass
class RoutingRule:
    """
    A single routing condition.

    match_on:    "flag_type" or "desk"
    match_value: the value to match against
    assigned_team: the team or officer identifier to route to
    priority:    the escalation priority to assign

    Rules are checked in order. First match wins.
    """
    match_on: Literal["flag_type", "desk"]
    match_value: str
    assigned_team: str
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


# [DEV] CONFIGURE ROUTING RULES FOR YOUR INSTITUTION ─────────────────────────
# Replace team names (e.g. "sanctions-specialist") with the actual team
# identifiers used in your compliance management system.
# Replace desk_id values (e.g. "INST-EQ-NY") with your actual trading desk IDs
# (these come from Trade.desk_id — check what your trade capture system uses).
# Add, remove, or reorder rules as your institution requires.
# Rules are checked in order — first match wins.
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_ROUTING_RULES: list[RoutingRule] = [
    # Sanctions-specific cases route to sanctions specialist
    RoutingRule(
        match_on="flag_type",
        match_value="SANCTIONS_LEI_MATCH",
        assigned_team="sanctions-specialist",   # [DEV] Replace with your team name
        priority="CRITICAL",
    ),
    RoutingRule(
        match_on="flag_type",
        match_value="SANCTIONS_NAME_MATCH",
        assigned_team="sanctions-specialist",   # [DEV] Replace with your team name
        priority="HIGH",
    ),
    # Structuring and layering route to BSA specialist
    RoutingRule(
        match_on="flag_type",
        match_value="STRUCTURING",
        assigned_team="bsa-specialist",         # [DEV] Replace with your team name
        priority="HIGH",
    ),
    RoutingRule(
        match_on="flag_type",
        match_value="LAYERING",
        assigned_team="bsa-specialist",         # [DEV] Replace with your team name
        priority="HIGH",
    ),
    # Desk-based routing — [DEV] replace desk IDs and team names below
    RoutingRule(
        match_on="desk",
        match_value="INST-EQ-NY",               # [DEV] Replace with your desk ID
        assigned_team="senior-compliance-ny",   # [DEV] Replace with your team name
        priority="MEDIUM",
    ),
    RoutingRule(
        match_on="desk",
        match_value="INST-EQ-LDN",              # [DEV] Replace with your desk ID
        assigned_team="senior-compliance-ldn",  # [DEV] Replace with your team name
        priority="MEDIUM",
    ),
]

# [DEV] SET YOUR DEFAULT FALLBACK TEAM ────────────────────────────────────────
# Escalations that match no rule above go to this team.
# Set to the most senior compliance officer or team in your institution.
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_FALLBACK_TEAM = "senior-compliance-default"  # [DEV] Change this
DEFAULT_FALLBACK_PRIORITY: Literal["MEDIUM"] = "MEDIUM"


class EscalationRouter:
    """
    Matches an escalation package to a team using a rule list.
    Rules are checked in order. First match wins.
    Falls back to DEFAULT_FALLBACK_TEAM if no rule matches.

    To customize routing for your institution:
        router = EscalationRouter(rules=[
            RoutingRule("flag_type", "SANCTIONS_NAME_MATCH", "my-team", "CRITICAL"),
            ...
        ])
    """

    def __init__(
        self,
        rules: list[RoutingRule] | None = None,
        fallback_team: str = DEFAULT_FALLBACK_TEAM,
    ):
        self.rules = rules or DEFAULT_ROUTING_RULES
        self.fallback_team = fallback_team

    def route(self, package: EscalationPackage) -> EscalationPackage:
        """
        Assigns assigned_team and priority on the package in place.
        Returns the same package (mutated).
        """
        for rule in self.rules:
            if rule.match_on == "flag_type" and package.flag_type == rule.match_value:
                package.assigned_team = rule.assigned_team
                package.priority = rule.priority
                logger.info(
                    f"[{package.trade_id}] Escalation routed to "
                    f"'{rule.assigned_team}' (flag_type={package.flag_type})."
                )
                return package
            if rule.match_on == "desk" and package.desk_id == rule.match_value:
                package.assigned_team = rule.assigned_team
                package.priority = rule.priority
                logger.info(
                    f"[{package.trade_id}] Escalation routed to "
                    f"'{rule.assigned_team}' (desk={package.desk_id})."
                )
                return package

        # No rule matched — use fallback
        package.assigned_team = self.fallback_team
        package.priority = DEFAULT_FALLBACK_PRIORITY
        logger.warning(
            f"[{package.trade_id}] No routing rule matched "
            f"(flag_type={package.flag_type}, desk={package.desk_id}). "
            f"Routed to fallback team '{self.fallback_team}'."
        )
        return package


# ─────────────────────────────────────────────────────────────
# ESCALATION QUEUE — concrete implementation skeleton
# ─────────────────────────────────────────────────────────────

class ConcreteEscalationQueue:
    """
    Concrete implementation of the EscalationQueue interface.

    This skeleton shows the structure. Replace the TODO sections
    with your queue backend (PostgreSQL, AWS SQS, BullMQ, etc.).

    Requirements (same as HumanReviewQueue):
      - Durable: survives process restarts
      - The package must be queryable by trade_id and escalation_id
      - Decisions written back via submit_decision() must be retrievable
        by the orchestrator's resolution handler

    The simplest production implementation is a PostgreSQL table:
      - One row per escalation package
      - Status column: PENDING → IN_REVIEW → RESOLVED
      - Decision stored as JSONB when submitted
    """

    def __init__(self, router: EscalationRouter | None = None):
        self.router = router or EscalationRouter()
        # Replace with your queue client (e.g. psycopg2 connection pool, SQS client)
        self._queue: list[EscalationPackage] = []       # In-memory only — not production-safe
        self._decisions: dict[UUID, EscalationDecision] = {}

    def enqueue(self, package: EscalationPackage) -> None:
        """
        Routes the package and writes it to the queue.
        Called by AMLOrchestrator._escalate().
        """
        self.router.route(package)
        self._queue.append(package)
        logger.info(
            f"[{package.trade_id}] Escalation {package.escalation_id} enqueued. "
            f"Team: {package.assigned_team}, Priority: {package.priority}."
        )
        # [DEV] REPLACE WITH YOUR QUEUE BACKEND ──────────────────────────────
        # The in-memory list above (_queue) is NOT production-safe.
        # Replace with a durable write to PostgreSQL, AWS SQS, or BullMQ.
        # The package must survive process restarts.
        # Example (PostgreSQL):
        # self.db.execute(
        #     "INSERT INTO escalation_queue "
        #     "(id, trade_id, package, status, assigned_team, priority) "
        #     "VALUES (%s, %s, %s, 'PENDING', %s, %s)",
        #     (str(package.escalation_id), str(package.trade_id),
        #      package.model_dump_json(), package.assigned_team, package.priority)
        # )
        # ─────────────────────────────────────────────────────────────────────

    def wait_for_decision(self, escalation_id: UUID) -> EscalationDecision:
        """
        Blocks until the senior officer submits a decision for this escalation.
        In production: poll the decision store or use a callback/webhook.

        NOTE: This is a blocking call. The workflow is suspended here
        until the officer acts, just as it is at the primary human review gate.
        Your queue implementation must survive process restarts while waiting.
        """
        raise NotImplementedError(
            "wait_for_decision() is not implemented. "
            "Implement a durable polling loop against your queue backend. "
            "Example: poll every 30s checking for a decision row in escalation_queue "
            "where escalation_id = %s and status = 'RESOLVED'."
        )

    def submit_decision(self, decision: EscalationDecision) -> None:
        """
        Called by the senior officer's review UI when they submit a decision.
        Stores the decision so wait_for_decision() can return it.
        """
        self._decisions[decision.escalation_id] = decision
        logger.info(
            f"[{decision.trade_id}] Escalation {decision.escalation_id} resolved: "
            f"{decision.outcome} by {decision.officer_id}."
        )
        # TODO: Replace with durable write, e.g.:
        # self.db.execute(
        #     "UPDATE escalation_queue SET status='RESOLVED', decision=%s "
        #     "WHERE id=%s",
        #     (decision.model_dump_json(), str(decision.escalation_id))
        # )


# ─────────────────────────────────────────────────────────────
# _escalate() IMPLEMENTATION — replaces the stub in orchestrator.py
# ─────────────────────────────────────────────────────────────
# Paste this method into AMLOrchestrator, replacing the existing stub.
# Add `escalation_queue: ConcreteEscalationQueue` to __init__ parameters.

def build_escalate_method():
    """
    Returns the _escalate() implementation as a reference.
    Copy the method body into AMLOrchestrator.

    Required changes to AMLOrchestrator.__init__:
      - Accept `escalation_queue: ConcreteEscalationQueue` (already in the interface)
      - No other changes needed

    The method signature matches the existing stub exactly.
    """
    pass


# ── Paste this into AMLOrchestrator ──────────────────────────
#
# def _escalate(
#     self,
#     trade_id: UUID,
#     reason: str,
#     outputs_so_far: dict[str, str] | None = None,
# ) -> None:
#     from escalation import EscalationPackage
#
#     # Retrieve the trade from the current workflow context.
#     # The trade object must be accessible — store it on self during run().
#     trade = self._current_trade
#
#     package = EscalationPackage(
#         trade_id=trade_id,
#         escalation_reason=reason,
#         escalation_source=self._determine_escalation_source(reason),
#         agent_outputs=outputs_so_far or {},
#         trade_summary=trade.to_pipeline_string(),
#         flag_type=trade.aml_flag.flag_type if trade.aml_flag else "UNKNOWN",
#         desk_id=trade.desk_id,
#         trade_value_usd=f"USD {trade.trade_value:,.2f}",
#     )
#
#     self.escalation_queue.enqueue(package)
#     self.audit.write(trade_id, "escalation_queued", {
#         "escalation_id": str(package.escalation_id),
#         "assigned_team": package.assigned_team,
#         "priority": package.priority,
#         "reason": reason,
#     })
#     logger.info(
#         f"[{trade_id}] Trade escalated to '{package.assigned_team}' "
#         f"(priority: {package.priority}). "
#         f"Escalation ID: {package.escalation_id}."
#     )
#
# def _determine_escalation_source(self, reason: str) -> str:
#     """Infers the escalation source from the reason string for audit logging."""
#     if "triage" in reason.lower():      return "triage_agent"
#     if "investigation" in reason.lower(): return "investigation_agent"
#     if "prefetch" in reason.lower():    return "prefetch"
#     if "step limit" in reason.lower():  return "loop_limit"
#     if "human" in reason.lower():       return "human_decision"
#     return "mid_pipeline"
#
# ─────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────
# THREE RESOLUTION PATHS — what happens after a decision
# ─────────────────────────────────────────────────────────────

def handle_escalation_decision(
    decision: EscalationDecision,
    orchestrator: Any,
    trade_id: UUID,
) -> None:
    """
    Processes the senior officer's decision and drives the resolution path.

    Called after wait_for_decision() returns — either by the orchestrator
    (synchronous flow) or a separate resolution handler (async flow).

    Three paths:

    APPROVED:
      Generates an approval token scoped to the trade.
      Calls settlement API exactly as the primary human review path does.
      The audit log records that approval came via escalation.

    BLOCKED:
      Flags the counterparty LEI in the KYC system for enhanced due diligence.
      Initiates the SAR assessment process.
      See Leak 7 resolution for the SAR assessment specification.

    ESCALATE_FURTHER:
      Creates a new EscalationPackage targeting decision.further_escalation_target.
      The current escalation closes. A new escalation opens.
      The audit log links the two escalation IDs.
    """
    orchestrator.audit.write(
        trade_id,
        "escalation_resolution",
        {"outcome": decision.outcome, "resolution_path": decision.resolution_path},
    )

    if decision.outcome == "APPROVED":
        # Generate token and execute settlement
        # (token generation is in the human review system — reuse that path)
        logger.info(f"[{trade_id}] Escalation resolved: APPROVED by {decision.officer_id}.")
        # TODO: token = token_store.generate(trade_id, decision.officer_id)
        # orchestrator.settlement.execute(trade_id, token)

    elif decision.outcome == "BLOCKED":
        orchestrator._block_and_flag(trade_id, decision.rationale)
        logger.info(f"[{trade_id}] Escalation resolved: BLOCKED by {decision.officer_id}.")

    elif decision.outcome == "ESCALATE_FURTHER":
        logger.info(
            f"[{trade_id}] Escalation resolved: ESCALATE_FURTHER "
            f"to '{decision.further_escalation_target}' by {decision.officer_id}."
        )
        # TODO: Create a new EscalationPackage targeting further_escalation_target
        # and enqueue it with elevated priority.
        raise NotImplementedError(
            "ESCALATE_FURTHER path: create a new EscalationPackage targeting "
            f"'{decision.further_escalation_target}' and enqueue it. "
            "Link the new escalation_id to the original via the audit log."
        )
