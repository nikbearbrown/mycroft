"""
sar_assessment.py
=================
Agentic AML Compliance Workflow — SAR Assessment Scope Boundary
US Equities · OFAC/BSA/FinCEN

SCOPE DECLARATION — READ THIS FIRST
─────────────────────────────────────────────────────────────────
This system NEVER files a Suspicious Activity Report (SAR).

Filing a SAR is a legal act with specific regulatory deadlines,
confidentiality obligations, and professional liability consequences.
It requires human judgment: a BSA Officer and, in many cases, legal
counsel must evaluate whether the specific facts meet the filing
threshold under 31 U.S.C. § 5318(g).

What this system does when a trade is blocked:
  1. Creates a SARAssessment record with all relevant context
  2. Writes it to the audit log
  3. Notifies the BSA Officer via the configured notification channel
  4. Exposes the record in the compliance review interface

What happens next is entirely the BSA Officer's responsibility.
This system has no further involvement.

The original architecture document said "SAR filing process initiated
if warranted." That phrase is replaced by this specification.
─────────────────────────────────────────────────────────────────

Dependencies:
    pip install pydantic>=2.0
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# SAR ASSESSMENT MODEL
# ─────────────────────────────────────────────────────────────

class SARAssessment(BaseModel):
    """
    A record created when the pipeline blocks a trade and escalates
    to the BSA Officer for SAR filing consideration.

    This record is:
      - Written to the compliance audit log (append-only)
      - Sent to the BSA Officer notification channel
      - Accessible in the compliance review interface

    It is NOT a SAR. It is the input package for the BSA Officer
    to determine whether a SAR should be filed.

    BSA Officer responsibilities (outside this system):
      - Evaluate whether the facts meet the SAR filing threshold
        (31 CFR § 1023.320: $5,000 USD or more involving insider abuse;
         $25,000 involving other suspicious activity)
      - File the SAR within 30 calendar days of initial detection
        (60 days if no subject is identified)
      - Ensure SAR confidentiality per 31 U.S.C. § 5318(g)(2)
        — do not disclose SAR existence to the subject of the SAR
    """
    assessment_id: UUID = Field(default_factory=uuid4)
    trade_id: UUID
    counterparty_lei: str
    counterparty_name: str
    flag_type: str
    trade_value_usd: str             # Formatted string for readability in review UI
    block_reason: str                # Why the trade was blocked — from the decision rationale
    agent_outputs: dict[str, str]    # All pipeline outputs available at block time
    escalation_source: str           # "autonomous_pipeline" or "human_decision"
    initiated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    status: Literal[
        "PENDING_BSO_REVIEW",  # Awaiting BSA Officer review (initial state)
        "UNDER_REVIEW",        # BSA Officer has opened the assessment
        "SAR_FILED",           # BSA Officer determined SAR filing required — filed externally
        "NO_SAR_REQUIRED",     # BSA Officer determined SAR is not warranted
        "ESCALATED_TO_LEGAL",  # Referred to legal counsel before BSA Officer decision
    ] = "PENDING_BSO_REVIEW"

    def to_notification_text(self) -> str:
        """
        Plain-text notification sent to the BSA Officer when a new
        SAR assessment is created.
        """
        return (
            f"SAR ASSESSMENT REQUIRED — Trade {self.trade_id}\n"
            f"{'─' * 50}\n"
            f"Assessment ID:     {self.assessment_id}\n"
            f"Trade ID:          {self.trade_id}\n"
            f"Counterparty:      {self.counterparty_name} (LEI: {self.counterparty_lei})\n"
            f"AML flag type:     {self.flag_type}\n"
            f"Trade value:       {self.trade_value_usd}\n"
            f"Block reason:      {self.block_reason}\n"
            f"Initiated:         {self.initiated_at.isoformat()}\n\n"
            f"Action required: Review this assessment and determine whether a SAR "
            f"filing is warranted under 31 CFR § 1023.320.\n\n"
            f"CONFIDENTIALITY REMINDER: Do not disclose the existence of any SAR "
            f"to the subject of the SAR (31 U.S.C. § 5318(g)(2))."
        )


# ─────────────────────────────────────────────────────────────
# SAR ASSESSMENT INITIATION
# ─────────────────────────────────────────────────────────────

def initiate_sar_assessment(
    trade_id: UUID,
    counterparty_lei: str,
    counterparty_name: str,
    flag_type: str,
    trade_value_usd: str,
    block_reason: str,
    agent_outputs: dict[str, str],
    escalation_source: str,
    audit_log: object,
    notifier: "BSONotifier | None" = None,
) -> SARAssessment:
    """
    Creates and records a SAR assessment when a trade is blocked.
    Called from AMLOrchestrator._block_and_flag().

    Steps:
      1. Creates SARAssessment record
      2. Writes to audit log (append-only — always succeeds or raises)
      3. Notifies BSA Officer via notifier (if configured)

    Returns the SARAssessment so the caller can include the
    assessment_id in the workflow result.

    If the notifier is not configured (None), the assessment is still
    written to the audit log. The BSA Officer can query it from there.
    A missing notifier is logged as a warning — it is not a blocking error.
    """
    assessment = SARAssessment(
        trade_id=trade_id,
        counterparty_lei=counterparty_lei,
        counterparty_name=counterparty_name,
        flag_type=flag_type,
        trade_value_usd=trade_value_usd,
        block_reason=block_reason,
        agent_outputs=agent_outputs,
        escalation_source=escalation_source,
    )

    # Step 1: Write to audit log — this is mandatory and must not fail silently
    audit_log.write(
        trade_id,
        "sar_assessment_initiated",
        {
            "assessment_id": str(assessment.assessment_id),
            "counterparty_lei": counterparty_lei,
            "flag_type": flag_type,
            "trade_value_usd": trade_value_usd,
            "status": assessment.status,
        },
    )
    logger.info(
        f"[{trade_id}] SAR assessment {assessment.assessment_id} created. "
        f"Status: {assessment.status}. BSA Officer review required."
    )

    # Step 2: Notify BSA Officer
    if notifier:
        try:
            notifier.send(assessment)
        except Exception as e:
            # Notification failure must not suppress the assessment record.
            # Log the failure — the BSA Officer can query the audit log directly.
            logger.error(
                f"[{trade_id}] BSA Officer notification failed for assessment "
                f"{assessment.assessment_id}: {e}. "
                "Assessment is recorded in audit log. Manual follow-up required."
            )
    else:
        logger.warning(
            f"[{trade_id}] No BSONotifier configured. SAR assessment "
            f"{assessment.assessment_id} written to audit log only. "
            "Ensure your BSA Officer has a process to review pending assessments."
        )

    return assessment


# ─────────────────────────────────────────────────────────────
# BSO NOTIFIER INTERFACE
# ─────────────────────────────────────────────────────────────

class BSONotifier:
    """
    Interface for notifying the BSA Officer when a SAR assessment is created.

    # [DEV] IMPLEMENT ONE CONCRETE NOTIFIER ──────────────────────────────────
    # Choose the channel your BSA Officer uses and implement it here.
    # Options:
    #   EmailBSONotifier   — sends email via SMTP or SendGrid
    #   SlackBSONotifier   — posts to a compliance Slack channel
    #   WebhookBSONotifier — calls a compliance workflow system webhook (e.g. Jira, ServiceNow)
    #   SMSBSONotifier     — sends SMS for CRITICAL priority assessments
    #
    # Implement the send() method. It receives the SARAssessment and should
    # send assessment.to_notification_text() to the BSA Officer.
    #
    # Then pass your implementation to initiate_sar_assessment():
    #   notifier = YourBSONotifier(api_key="...", channel="compliance-alerts")
    #   initiate_sar_assessment(..., notifier=notifier)
    #
    # If no notifier is configured, the assessment is still written to the
    # audit log — but the BSA Officer must have a separate process to
    # discover pending assessments. A notifier is strongly recommended.
    # ─────────────────────────────────────────────────────────────────────────

    Implement one concrete notifier for your institution:
      - EmailBSONotifier:  sends email via SMTP or SendGrid
      - SlackBSONotifier:  posts to a compliance Slack channel
      - SMSBSONotifier:    sends SMS for critical flag types
      - WebhookBSONotifier: calls a compliance workflow webhook

    The notifier receives the SARAssessment object and sends
    assessment.to_notification_text() to the BSA Officer.
    """

    def send(self, assessment: SARAssessment) -> None:
        raise NotImplementedError
