"""
orchestrator.py
===============
Agentic AML Compliance Workflow — Corrected Orchestrator
US Equities · OFAC/BSA/FinCEN

Closes the following architectural leaks from the original skeleton:
  Leak 8a — Mid-pipeline escape hatch: orchestrator now reads AgentResult.status
             after every agent call and halts the pipeline before invoking the
             next agent when status is 'escalate' or 'halt'.
  Leak 8b — Validation integration: validate_agent_output() is called after
             every agent run. Validation failure triggers escalation.
  Leak 5  — Report agent retry: one retry with format reminder before escalation.

Depends on:
  schemas.py          — Trade, AMLFlag, AgentResult, AgentStatus
  agent_validation.py — validate_agent_output(), ValidationFailure

Dependencies:
  pip install pydantic>=2.0 anthropic>=0.25
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from schemas import AgentResult, AgentStatus, Trade
from agent_validation import validate_agent_output

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# RESULT TYPES
# ─────────────────────────────────────────────────────────────

@dataclass
class ApprovalDecision:
    """
    Returned by HumanReviewQueue.request_approval().
    When approved, carries the signed approval token required
    by the SettlementAPI.
    """
    approved: bool
    officer_id: str
    timestamp: datetime
    rationale: str
    token: "ApprovalToken | None" = None
    action: str | None = None    # "escalate" or "reject" when approved=False
    reason: str | None = None

    def to_dict(self) -> dict:
        return {
            "approved": self.approved,
            "officer_id": self.officer_id,
            "timestamp": self.timestamp.isoformat(),
            "rationale": self.rationale,
            "action": self.action,
            "reason": self.reason,
            "token_id": str(self.token.token_id) if self.token else None,
        }


@dataclass
class WorkflowResult:
    """
    Returned by AMLOrchestrator.run().
    Carries the complete record of what happened — every agent output,
    the pipeline terminal status, and the human decision if reached.
    """
    trade_id: UUID
    outputs: dict[str, str]            # agent_name → output text
    status: str                        # "approved" | "rejected" | "escalated" | "halted" | "blocked"
    decision: ApprovalDecision | None = None
    escalation_reason: str | None = None


# ─────────────────────────────────────────────────────────────
# PIPELINE ERRORS
# ─────────────────────────────────────────────────────────────

class LoopLimitError(Exception):
    """Raised when the orchestrator exceeds MAX_STEPS."""
    pass


class EscalationError(Exception):
    """
    Raised when escalation fails to route (e.g., escalation queue is down).
    Distinct from a normal escalation — this is a system failure, not a
    compliance decision.
    """
    pass


# ─────────────────────────────────────────────────────────────
# AGENT BASE CLASS
# ─────────────────────────────────────────────────────────────

class Agent:
    """
    Base class for pipeline agents.
    Each agent has a name, system prompt, and permission scope.

    run() calls the LLM and returns raw text.
    The orchestrator calls validate_agent_output() separately —
    validation is the orchestrator's responsibility, not the agent's.
    This keeps agents simple and validation logic testable in isolation.
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        max_tokens: int = 500,
        permissions: list[str] | None = None,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.permissions = permissions or []

    def run(self, trade_str: str, context: str) -> str:
        """
        Calls the LLM with the trade data and accumulated prior context.
        Returns the raw output string.

        The LLM client is injected via the module-level `llm` reference
        (see build_orchestrator() for how to inject your client).
        """
        prompt = f"Trade data:\n{trade_str}"
        if context.strip():
            prompt += f"\n\nPrior agent outputs:\n{context}"

        response = llm.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=self.max_tokens,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()


# ─────────────────────────────────────────────────────────────
# ORCHESTRATOR
# ─────────────────────────────────────────────────────────────

class AMLOrchestrator:
    """
    Orchestrates the four-agent AML compliance pipeline.

    Pipeline phases:
      1. Autonomous agent pipeline (Triage → Investigation → Reasoning → Report)
      2. Human checkpoint gate (blocks until compliance officer decision)
      3. Execution (settlement, escalation, or block — post-approval only)
      4. Audit seal (cryptographic hash of complete workflow record)

    Key invariants:
      - validate_agent_output() is called after every agent run
      - AgentResult.status is checked before invoking the next agent
      - No agent can cause settlement execution directly
      - Every state transition is written to the audit log
    """

    # [DEV] TUNE LOOP LIMIT ───────────────────────────────────────────────────
    # MAX_STEPS = 8 is set for a 4-agent pipeline with headroom for retries.
    # If you extend the pipeline (more agents, sub-agents), increase this value.
    # If your pipeline is shorter, lower it to fail faster on runaway loops.
    # ─────────────────────────────────────────────────────────────────────────
    MAX_STEPS = 8  # Hard loop prevention. Exceeding this is an automatic escalation.

    # The Report Agent gets one retry on validation failure before escalation.
    # All other agents escalate immediately on validation failure.
    REPORT_AGENT_NAME = "report_agent"

    def __init__(
        self,
        agents: list[Agent],
        review_queue: "HumanReviewQueue",
        settlement_api: "SettlementAPI",
        audit_log: "AuditLog",
        escalation_queue: "EscalationQueue",
    ):
        self.agents = agents
        self.review_queue = review_queue
        self.settlement = settlement_api
        self.audit = audit_log
        self.escalation_queue = escalation_queue

    # ─────────────────────────────────────────────────────────
    # MAIN ENTRY POINT
    # ─────────────────────────────────────────────────────────

    def run(self, trade: Trade) -> WorkflowResult:
        """
        Executes the full AML compliance workflow for a flagged trade.

        Returns a WorkflowResult regardless of outcome — every path
        (approval, rejection, escalation, halt) produces a result.
        The orchestrator never raises an unhandled exception to the caller
        after the trade is accepted. All failure modes produce a result
        and write to the audit log.
        """
        logger.info(f"[{trade.trade_id}] Workflow started.")

        context = ""
        outputs: dict[str, str] = {}
        steps = 0

        # ── Phase 1: Autonomous agent pipeline ────────────────
        for agent in self.agents:
            steps += 1

            # Hard loop limit — catches runaway recursive or injected behavior
            if steps > self.MAX_STEPS:
                reason = (
                    f"Step limit exceeded ({steps} > {self.MAX_STEPS}). "
                    "Automatic escalation to human review."
                )
                logger.warning(f"[{trade.trade_id}] {reason}")
                self.audit.write(trade.trade_id, "loop_limit_exceeded", {"steps": steps})
                self._escalate(trade.trade_id, reason, outputs)
                return WorkflowResult(
                    trade_id=trade.trade_id,
                    outputs=outputs,
                    status="escalated",
                    escalation_reason=reason,
                )

            # Run agent
            logger.info(f"[{trade.trade_id}] Running {agent.name} (step {steps}).")
            raw_output = agent.run(trade.to_pipeline_string(), context)

            # Validate output — the orchestrator's responsibility, not the agent's
            result = self._validate_and_wrap(agent, raw_output, trade)

            # Write agent output to audit log regardless of status
            self.audit.write(trade.trade_id, agent.name, raw_output)

            # ── Mid-pipeline escape hatch ──────────────────────
            # This is the fix for Leak 8. The original skeleton had no
            # check here — the loop simply continued to the next agent
            # regardless of what the current agent returned.
            if result.status == "escalate":
                logger.warning(
                    f"[{trade.trade_id}] Agent '{agent.name}' triggered escalation: "
                    f"{result.reason}"
                )
                self.audit.write(
                    trade.trade_id,
                    "mid_pipeline_escalation",
                    {"agent": agent.name, "reason": result.reason},
                )
                self._escalate(trade.trade_id, result.reason, outputs)
                return WorkflowResult(
                    trade_id=trade.trade_id,
                    outputs=outputs,
                    status="escalated",
                    escalation_reason=result.reason,
                )

            if result.status == "halt":
                logger.warning(
                    f"[{trade.trade_id}] Agent '{agent.name}' triggered halt: "
                    f"{result.reason}"
                )
                self.audit.write(
                    trade.trade_id,
                    "mid_pipeline_halt",
                    {"agent": agent.name, "reason": result.reason},
                )
                self._block_and_flag(trade.trade_id, result.reason)
                return WorkflowResult(
                    trade_id=trade.trade_id,
                    outputs=outputs,
                    status="halted",
                    escalation_reason=result.reason,
                )

            # Status is "continue" — accumulate context and proceed
            context += f"\n\n[{agent.name}]:\n{result.output}"
            outputs[agent.name] = result.output
            logger.info(f"[{trade.trade_id}] {agent.name} completed.")

        # ── Phase 2: Human checkpoint gate ────────────────────
        # Workflow blocks here until the compliance officer submits a decision.
        # The review queue must be durable — see architecture reference Section 7.
        logger.info(f"[{trade.trade_id}] Routing to human review queue.")
        decision = self.review_queue.request_approval(
            trade_id=trade.trade_id,
            report=outputs[self.REPORT_AGENT_NAME],
        )
        self.audit.write(trade.trade_id, "human_decision", decision.to_dict())
        logger.info(
            f"[{trade.trade_id}] Human decision received: "
            f"approved={decision.approved}, officer={decision.officer_id}."
        )

        # ── Phase 3: Execution (post-approval only) ────────────
        if decision.approved:
            self.settlement.execute(trade.trade_id, decision.token)
            logger.info(f"[{trade.trade_id}] Settlement instruction released.")
            status = "approved"
        elif decision.action == "escalate":
            self._escalate(trade.trade_id, decision.reason, outputs)
            status = "escalated"
        else:
            self._block_and_flag(trade.trade_id, decision.reason)
            status = "rejected"

        # ── Phase 4: Seal the audit record ────────────────────
        self.audit.seal(trade.trade_id, decision)
        logger.info(f"[{trade.trade_id}] Audit record sealed. Workflow complete.")

        return WorkflowResult(
            trade_id=trade.trade_id,
            outputs=outputs,
            status=status,
            decision=decision,
        )

    # ─────────────────────────────────────────────────────────
    # VALIDATION + RESULT WRAPPING
    # ─────────────────────────────────────────────────────────

    def _validate_and_wrap(
        self,
        agent: Agent,
        raw_output: str,
        trade: Trade,
    ) -> AgentResult:
        """
        Validates agent output and wraps it in an AgentResult.

        Report agent gets one retry on failure (formatting errors are common
        and cheap to fix). All other agents escalate immediately.

        Returns an AgentResult with status "continue", "escalate", or "halt".
        """
        failure = validate_agent_output(agent.name, raw_output, trade)

        if failure is None:
            return AgentResult(
                agent_name=agent.name,
                output=raw_output,
                status="continue",
            )

        # Report agent: one retry with explicit format reminder
        if agent.name == self.REPORT_AGENT_NAME:
            logger.warning(
                f"[{trade.trade_id}] Report agent validation failed on first attempt. "
                f"Retrying with format reminder. Reason: {failure.reason}"
            )
            self.audit.write(
                trade.trade_id,
                "report_agent_retry",
                {"first_attempt_failure": failure.reason},
            )
            retry_output = self._retry_report_agent(agent, trade, raw_output, failure.reason)
            retry_failure = validate_agent_output(agent.name, retry_output, trade)

            if retry_failure is None:
                logger.info(f"[{trade.trade_id}] Report agent retry succeeded.")
                return AgentResult(
                    agent_name=agent.name,
                    output=retry_output,
                    status="continue",
                )

            # Both attempts failed — escalate
            logger.warning(
                f"[{trade.trade_id}] Report agent retry also failed. Escalating. "
                f"Retry failure: {retry_failure.reason}"
            )
            return AgentResult(
                agent_name=agent.name,
                output=retry_output,
                status="escalate",
                reason=(
                    f"Report agent failed validation on both attempts. "
                    f"First failure: {failure.reason}. "
                    f"Retry failure: {retry_failure.reason}."
                ),
            )

        # All other agents: escalate immediately on validation failure
        return AgentResult(
            agent_name=agent.name,
            output=raw_output,
            status="escalate",
            reason=failure.to_escalation_reason(),
        )

    def _retry_report_agent(
        self,
        agent: Agent,
        trade: Trade,
        failed_output: str,
        failure_reason: str,
    ) -> str:
        """
        Re-invokes the report agent with an explicit format reminder appended
        to the prompt. Only called when the first attempt fails validation.
        """
        format_reminder = (
            "\n\nYour previous output did not meet the required format. "
            f"Failure reason: {failure_reason}\n\n"
            "Rewrite the exception report using EXACTLY these four section headers "
            "in this exact order, each on its own line:\n"
            "FLAG SUMMARY\n"
            "INVESTIGATION FINDINGS\n"
            "REGULATORY ASSESSMENT\n"
            "RECOMMENDED ACTION\n\n"
            "The RECOMMENDED ACTION section must begin with 'Recommend:'\n"
            "No markdown. No bullet points. No asterisks. Plain text only.\n\n"
            "Previous output for reference:\n"
            f"{failed_output}"
        )
        # Build a modified prompt that includes the format reminder
        original_prompt = f"Trade data:\n{trade.to_pipeline_string()}"
        retry_response = llm.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=agent.max_tokens,
            system=agent.system_prompt,
            messages=[
                {"role": "user", "content": original_prompt + format_reminder}
            ],
        )
        return retry_response.content[0].text.strip()

    # ─────────────────────────────────────────────────────────
    # ESCALATION AND BLOCK — STUBBED WITH EXPLICIT CONTRACTS
    # ─────────────────────────────────────────────────────────

    def _escalate(
        self,
        trade_id: UUID,
        reason: str,
        outputs_so_far: dict[str, str] | None = None,
    ) -> None:
        """
        Routes the trade to the escalation queue for senior compliance review.

        CONTRACT (what this method must do — implement against this spec):
          1. Build an EscalationPackage containing:
               - trade_id
               - reason for escalation
               - all agent outputs produced before escalation
               - escalation timestamp (UTC)
          2. Enqueue to the escalation queue (must be durable)
          3. Write escalation event to audit log
          4. Notify the assigned senior compliance officer (routing by desk_id
             or rule-based assignment — YOUR INSTITUTION DEFINES THIS)

        WHAT THIS METHOD MUST NOT DO:
          - Execute any settlement action
          - Generate or use an approval token
          - Silently swallow failures (raise EscalationError if queue is unavailable)

        STATUS: STUB — replace with your escalation queue implementation.
        See architecture reference Section 5A (Escalation Sub-Workflow) for
        the full specification of what happens after this call.

        NOTE: This is Leak 6 in the architectural audit. The escalation
        sub-workflow — what the senior officer receives, how the sub-workflow
        is instantiated, and how it reconnects to this workflow on resolution —
        is specified in the next architecture supplement.
        """
        logger.warning(
            f"[{trade_id}] ESCALATION: {reason}. "
            "EscalationQueue.enqueue() not yet implemented — see Leak 6."
        )
        # TODO: Replace with:
        # package = EscalationPackage(
        #     trade_id=trade_id,
        #     reason=reason,
        #     agent_outputs=outputs_so_far or {},
        #     escalated_at=datetime.now(timezone.utc),
        # )
        # self.escalation_queue.enqueue(package)
        # self.audit.write(trade_id, "escalation_queued", package.to_dict())
        raise NotImplementedError(
            f"_escalate() is not implemented. "
            f"Trade {trade_id} requires escalation. Reason: {reason}. "
            "See architecture reference Section 5A and Leak 6 resolution."
        )

    def _block_and_flag(self, trade_id: UUID, reason: str) -> None:
        """
        Blocks the trade and flags the counterparty for enhanced due diligence.

        CONTRACT (what this method must do — implement against this spec):
          1. Write TRADE_BLOCKED status to trade state store
          2. Flag counterparty LEI in KYC system for enhanced due diligence
          3. Write block event to audit log with reason
          4. Initiate SAR assessment process (see note below)
          5. Notify relevant compliance staff

        SAR ASSESSMENT NOTE:
          Whether a blocked trade warrants a Suspicious Activity Report (SAR)
          filing under FinCEN requirements is a LEGAL AND COMPLIANCE DECISION,
          not a system decision. This method initiates the assessment process —
          it does not file a SAR autonomously.

          The assessment process must be defined by your institution's compliance
          team and legal counsel. This method should trigger that process
          (e.g., by creating a SAR assessment task in your compliance workflow
          system) and record that it did so in the audit log.

          "SAR filing process initiated if warranted" (from the original
          architecture doc) is not a sufficient specification. See Leak 7
          resolution for the full SAR declaration.

        STATUS: STUB — replace with your block/flag implementation.
        """
        logger.warning(
            f"[{trade_id}] BLOCK AND FLAG: {reason}. "
            "_block_and_flag() not yet implemented — see Leak 7."
        )
        # TODO: Replace with:
        # self.trade_store.set_status(trade_id, "BLOCKED", reason=reason)
        # self.kyc_system.flag_for_edd(counterparty_lei, reason=reason)
        # self.audit.write(trade_id, "trade_blocked", {"reason": reason})
        # self.sar_assessment.initiate(trade_id, reason=reason)  # See Leak 7
        raise NotImplementedError(
            f"_block_and_flag() is not implemented. "
            f"Trade {trade_id} must be blocked. Reason: {reason}. "
            "See architecture reference Leak 7 resolution."
        )


# ─────────────────────────────────────────────────────────────
# DEPENDENCY INTERFACES
# These define the contracts that concrete implementations must satisfy.
# ─────────────────────────────────────────────────────────────

class HumanReviewQueue:
    """
    Posts exception reports to the compliance officer review UI and
    blocks until the officer submits a decision.

    The queue MUST be durable. If the orchestrator process restarts
    while waiting for a decision, the pending request must survive.
    Do not use an in-memory queue.

    Recommended implementations: PostgreSQL queue, AWS SQS, BullMQ.
    See architecture reference Section 7 for options.

    # [DEV] IMPLEMENT THIS CLASS ──────────────────────────────────────────────
    # This is the human review gate — the most critical integration point.
    # Steps:
    #   1. Subclass HumanReviewQueue (or replace it directly).
    #   2. In request_approval(): write the report to your queue backend,
    #      then block (poll or await) until the officer submits a decision.
    #   3. The officer submits via your review UI → writes an ApprovalDecision
    #      to the queue. Your blocking call returns it.
    #   4. Pass your implementation to AMLOrchestrator via build_orchestrator().
    # ─────────────────────────────────────────────────────────────────────────
    """

    def request_approval(
        self,
        trade_id: UUID,
        report: str,
    ) -> ApprovalDecision:
        raise NotImplementedError


class SettlementAPI:
    """
    Executes settlement instructions post-approval.
    Requires a valid, trade-scoped, single-use ApprovalToken.
    No agent has write access to the token store — this is an
    architectural constraint, not a behavioral instruction.

    # [DEV] IMPLEMENT THIS CLASS ──────────────────────────────────────────────
    # Connect to your settlement system in the execute() method.
    # The token validation check (is_valid_for) must remain — do not remove it.
    # ─────────────────────────────────────────────────────────────────────────
    """

    def execute(self, trade_id: UUID, token: "ApprovalToken") -> None:
        if not token.is_valid_for(trade_id):
            raise PermissionError(
                f"ApprovalToken is not valid for trade {trade_id}. "
                "Token may have expired, been used, or been issued for a different trade."
            )
        raise NotImplementedError


class AuditLog:
    """
    Append-only record of every agent output, human decision,
    and execution action in the workflow.

    Implementation requirements:
      - Append only. No UPDATE or DELETE on workflow rows.
      - seal() computes and stores a cryptographic hash of the
        complete workflow record. Any post-seal tampering invalidates
        the hash.
      - Must be queryable by trade_id for regulatory review.

    Recommended implementation: PostgreSQL with INSERT-only row
    security policy. See architecture reference Section 6.

    # [DEV] IMPLEMENT THIS CLASS ──────────────────────────────────────────────
    # write(): INSERT one row per event. Include: trade_id, event_type,
    #          content (JSONB), timestamp.
    # seal():  Compute SHA-256 of all rows for this trade_id in insertion
    #          order. Store the hash. Any tampering invalidates it.
    # ─────────────────────────────────────────────────────────────────────────
    """

    def write(self, trade_id: UUID, event_type: str, content: Any) -> None:
        raise NotImplementedError

    def seal(self, trade_id: UUID, decision: ApprovalDecision) -> None:
        raise NotImplementedError


class EscalationQueue:
    """
    Routes escalated trades to the senior compliance review workflow.

    CONTRACT:
      - Must be durable (survives process restarts)
      - Must carry the full EscalationPackage (trade_id, reason,
        all prior agent outputs, escalation timestamp)
      - Routing logic (which officer receives the escalation) is
        institution-defined — see architecture reference Section 5A

    STATUS: Interface defined. Full escalation sub-workflow
    specification is in the next architecture supplement (Leak 6).
    """

    def enqueue(self, package: "EscalationPackage") -> None:
        raise NotImplementedError


# ─────────────────────────────────────────────────────────────
# FACTORY
# ─────────────────────────────────────────────────────────────

def build_orchestrator(llm_client=None) -> AMLOrchestrator:
    """
    Constructs the orchestrator with all dependencies injected.

    Pass llm_client for testing (allows mock injection).
    In production, the global `llm` reference is used by Agent.run().

    Agent system prompts are defined here. They must include the
    citation format instruction for agents that require citations.
    See architecture reference Section 2B.
    """
    global llm
    if llm_client:
        llm = llm_client

    CITATION_INSTRUCTION = (
        "When citing a source, use the format [SOURCE: SOURCE_NAME] "
        "immediately after the claim. Use only recognized source names: "
        "LEI-DB, KYC-RECORDS, OFAC-SDN, OFAC-CONSOL, FINCEN-314A, "
        "TX-HISTORY-24M, AML-TAXONOMY, POLICY-LIB, TRADE-DATA."
    )

    agents = [
        Agent(
            name="triage_agent",
            system_prompt=(
                "You are a trade reconciliation and triage agent for a US institutional "
                "equity trading desk operating under BSA/AML compliance requirements. "
                "Confirm the trade fields. Characterize the AML flag type and confidence level. "
                "Assign a risk level (LOW / MED / HIGH). "
                "State precisely what the investigation agent must check. "
                "Write in plain paragraphs. Exactly 3 paragraphs. "
                "No markdown, no bullet points, no bold text."
            ),
            max_tokens=450,
            permissions=["read:trade_data", "read:aml_taxonomy"],
        ),
        Agent(
            name="investigation_agent",
            system_prompt=(
                "You are an AML investigation agent operating under OFAC/BSA/FinCEN requirements. "
                "You have access to the LEI database, internal KYC records, "
                "OFAC SDN and Consolidated sanctions lists, and 24-month transaction history. "
                "Run LEI verification using the counterparty_lei field — NEVER query by name. "
                "Review KYC record currency. Check transaction history for BSA AML typologies. "
                "Check OFAC SDN and Consolidated lists by LEI. "
                "Write one paragraph per check area (LEI, KYC, sanctions, transaction history). "
                "Conclude with explicit finding: FALSE POSITIVE or GENUINE CONCERN, and why. "
                "No markdown. "
                + CITATION_INSTRUCTION
            ),
            max_tokens=550,
            permissions=["read:lei_db", "read:kyc_records", "read:ofac_sdn",
                         "read:ofac_consolidated", "read:tx_history"],
        ),
        Agent(
            name="reasoning_agent",
            system_prompt=(
                "You are a compliance audit agent preparing a regulatory reasoning chain "
                "under BSA/AML requirements for FinCEN audit purposes. "
                "Generate a numbered reasoning chain for this investigation. "
                "Each step must name the specific evidence examined and the finding it produced. "
                "Minimum 3 steps. Maximum 7 steps. "
                "Plain text. No markdown. "
                + CITATION_INSTRUCTION
            ),
            max_tokens=450,
            permissions=["read:accumulated_context", "read:policy_lib"],
        ),
        Agent(
            name="report_agent",
            system_prompt=(
                "You are a compliance reporting agent. "
                "Produce a formal exception report for compliance officer review. "
                "Use EXACTLY these four section labels on their own lines, in this order:\n"
                "FLAG SUMMARY\n"
                "INVESTIGATION FINDINGS\n"
                "REGULATORY ASSESSMENT\n"
                "RECOMMENDED ACTION\n\n"
                "FLAG SUMMARY: 2 sentences. "
                "INVESTIGATION FINDINGS: 3 sentences. "
                "REGULATORY ASSESSMENT: 2 sentences. "
                "RECOMMENDED ACTION: 1 sentence beginning exactly with 'Recommend:'\n\n"
                "No markdown. No bullet points. No bold text. Plain text only. "
                "The compliance officer makes the final decision based solely on this document."
            ),
            max_tokens=500,
            permissions=["read:accumulated_context", "read:report_template"],
        ),
    ]

    return AMLOrchestrator(
        agents=agents,
        review_queue=HumanReviewQueue(),       # Replace with concrete implementation
        settlement_api=SettlementAPI(),         # Replace with concrete implementation
        audit_log=AuditLog(),                   # Replace with concrete implementation
        escalation_queue=EscalationQueue(),     # Replace with concrete implementation
    )


# ─────────────────────────────────────────────────────────────
# LLM CLIENT — module-level reference, injected via build_orchestrator
# ─────────────────────────────────────────────────────────────
# Initialize with your Anthropic client:
#   import anthropic
#   llm = anthropic.Anthropic(api_key="...")
#   build_orchestrator(llm_client=llm)

llm = None  # Injected at startup


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

def handle_aml_flag(trade_event: dict) -> WorkflowResult:
    """
    Pipeline entry point. Called when the upstream screening system
    routes a flagged trade to this workflow.

    Validates the trade schema at the boundary before any agent sees
    the data. A ValidationError here means the upstream system sent
    a malformed event — log it and reject it at the boundary.
    """
    from pydantic import ValidationError

    try:
        trade = Trade.from_event(trade_event)
    except ValidationError as e:
        logger.error(
            f"Trade event failed schema validation at pipeline boundary: {e}. "
            "Event rejected. Check upstream trade capture system."
        )
        raise

    orchestrator = build_orchestrator()
    return orchestrator.run(trade)
