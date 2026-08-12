"""
agent_validation.py
===================
Agentic AML Compliance Workflow — Per-Agent Validation Logic
US Equities · OFAC SDN / BSA / FinCEN

Implements the _validate() method for each agent subclass.
Also defines the canonical citation format used across all agents.

These validators are the quality gate that makes hallucination detection
structural rather than behavioral. Each validator is specific to the
output contract defined in the agent's system prompt.

CITATION FORMAT (canonical — propagate into all system prompts):
  [SOURCE: <SOURCE_NAME>]
  Placed inline, immediately after the claim it supports.

  Recognized source names:
    LEI-DB          — LEI database query result
    KYC-RECORDS     — Internal KYC records store
    OFAC-SDN        — OFAC Specially Designated Nationals list query
    OFAC-CONSOL     — OFAC Consolidated Sanctions list query
    FINCEN-314A     — FinCEN 314(a) list query
    TX-HISTORY-24M  — 24-month transaction history query
    AML-TAXONOMY    — Internal AML flag taxonomy document
    POLICY-LIB      — Internal compliance policy library
    TRADE-DATA      — Fields from the trade record itself

  Example:
    "The LEI query returned a clean result with no sanctions match [SOURCE: OFAC-SDN]."
    "KYC review was last completed 14 months ago [SOURCE: KYC-RECORDS]."

Dependencies:
    pip install pydantic>=2.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import ClassVar

from schemas import AgentResult, AgentStatus, Trade


# ─────────────────────────────────────────────────────────────
# CITATION FORMAT — single definition, used by all validators
# ─────────────────────────────────────────────────────────────

# This regex matches [SOURCE: <name>] anywhere in text.
# The source name may contain letters, digits, and hyphens.
CITATION_PATTERN = re.compile(r"\[SOURCE:\s*([A-Z0-9\-]+)\]")

RECOGNIZED_SOURCES = {
    "LEI-DB",
    "KYC-RECORDS",
    "OFAC-SDN",
    "OFAC-CONSOL",
    "FINCEN-314A",
    "TX-HISTORY-24M",
    "AML-TAXONOMY",
    "POLICY-LIB",
    "TRADE-DATA",
}

MARKDOWN_PATTERN = re.compile(r"(\*\*|__|\*|_|#{1,6} |`|\- |\d+\. )")


@dataclass
class ValidationFailure:
    """
    Returned when validation fails.
    Contains enough context for the orchestrator to log and escalate.
    """
    agent_name: str
    reason: str
    output_excerpt: str = field(default="")

    def to_escalation_reason(self) -> str:
        return (
            f"Agent '{self.agent_name}' failed validation: {self.reason}. "
            + (f"Output excerpt: '{self.output_excerpt[:120]}...'" if self.output_excerpt else "")
        )


# ─────────────────────────────────────────────────────────────
# BASE VALIDATOR
# ─────────────────────────────────────────────────────────────

class AgentValidator:
    """
    Base class for agent output validators.
    Subclass one validator per agent. Override validate().
    """

    AGENT_NAME: ClassVar[str] = "base"

    def validate(self, output: str, trade: Trade) -> ValidationFailure | None:
        """
        Returns None if validation passes.
        Returns ValidationFailure if validation fails.
        The orchestrator converts a ValidationFailure into an escalation or retry.
        """
        raise NotImplementedError

    # ── Shared helpers ────────────────────────────────────────

    def _check_no_markdown(self, output: str) -> ValidationFailure | None:
        """All agent outputs must be plain text. No markdown."""
        match = MARKDOWN_PATTERN.search(output)
        if match:
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason=f"Output contains markdown formatting ('{match.group()}') — "
                       "agents must produce plain text only.",
                output_excerpt=output[:200],
            )
        return None

    def _count_citations(self, output: str) -> list[str]:
        """Returns list of source names found in the output."""
        return [m.group(1) for m in CITATION_PATTERN.finditer(output)]

    def _check_unrecognized_citations(
        self, citations: list[str]
    ) -> ValidationFailure | None:
        """Warn if an agent is citing sources outside the recognized set."""
        unrecognized = [c for c in citations if c not in RECOGNIZED_SOURCES]
        if unrecognized:
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason=f"Output contains unrecognized source citations: {unrecognized}. "
                       f"Recognized sources are: {sorted(RECOGNIZED_SOURCES)}. "
                       "Check whether the agent invented a source name.",
            )
        return None


# ─────────────────────────────────────────────────────────────
# AGENT 1 — TRIAGE VALIDATOR
# ─────────────────────────────────────────────────────────────

class TriageValidator(AgentValidator):
    """
    Validates output from the Trade Reconciliation & Triage Agent.

    Contract (from system prompt):
      - Exactly 3 paragraphs
      - Risk level assigned as exactly one of: LOW, MED, HIGH
      - Plain text, no markdown
      - Flag type from the input must be referenced

    Failure → escalate directly to human review.
    Do NOT pass malformed triage output to the investigation agent.
    """

    AGENT_NAME = "triage_agent"
    # [DEV] TUNE VALIDATION THRESHOLDS ───────────────────────────────────────
    # These paragraph/step counts match the system prompts in orchestrator.py.
    # If you change a system prompt (e.g. triage outputs 4 paragraphs instead
    # of 3), update the corresponding constant here to match.
    # ─────────────────────────────────────────────────────────────────────────
    VALID_RISK_LEVELS = {"LOW", "MED", "HIGH"}

    def validate(self, output: str, trade: Trade) -> ValidationFailure | None:
        # 1. No markdown
        if failure := self._check_no_markdown(output):
            return failure

        # 2. Must contain a valid risk level
        found_levels = {level for level in self.VALID_RISK_LEVELS if level in output}
        if not found_levels:
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason="Output does not contain a risk level assignment. "
                       "Expected exactly one of: LOW, MED, HIGH.",
                output_excerpt=output[:200],
            )
        if len(found_levels) > 1:
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason=f"Output contains multiple risk level terms: {found_levels}. "
                       "Triage must assign exactly one risk level.",
                output_excerpt=output[:200],
            )

        # 3. Exactly 3 paragraphs
        # Paragraphs are separated by double newlines (blank line).
        paragraphs = [p.strip() for p in output.strip().split("\n\n") if p.strip()]
        if len(paragraphs) != 3:
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason=f"Expected 3 paragraphs, found {len(paragraphs)}. "
                       "Triage output must be exactly 3 paragraphs separated by blank lines.",
                output_excerpt=output[:200],
            )

        # 4. Flag type from the input trade must appear in the output.
        # This confirms the agent actually processed the flag, not a generic template.
        if trade.aml_flag:
            flag_type = trade.aml_flag.flag_type
            if flag_type not in output:
                return ValidationFailure(
                    agent_name=self.AGENT_NAME,
                    reason=f"Output does not reference the AML flag type '{flag_type}' "
                           "from the input trade. Agent may have processed a cached or "
                           "incorrect context.",
                )

        return None  # Validation passed


# ─────────────────────────────────────────────────────────────
# AGENT 2 — INVESTIGATION VALIDATOR
# ─────────────────────────────────────────────────────────────

class InvestigationValidator(AgentValidator):
    """
    Validates output from the AML Investigation Agent.

    Contract (from system prompt):
      - Four check areas must each appear as a paragraph:
        LEI verification, KYC review, sanctions check, transaction history
      - Each paragraph must contain at least one [SOURCE: X] citation
      - Explicit conclusion must appear: "FALSE POSITIVE" or "GENUINE CONCERN"
      - Plain text, no markdown

    Failure → escalate directly to human review.
    An investigation with missing check areas is not a usable investigation.
    """

    AGENT_NAME = "investigation_agent"

    REQUIRED_CHECK_AREAS = [
        ("LEI", ["LEI", "Legal Entity Identifier"]),
        ("KYC", ["KYC", "know your customer", "Know Your Customer"]),
        ("SANCTIONS", ["sanctions", "OFAC", "SDN", "sanctioned"]),
        ("TX_HISTORY", ["transaction history", "Transaction History", "24-month", "24 month"]),
    ]
    REQUIRED_CONCLUSIONS = ["FALSE POSITIVE", "GENUINE CONCERN"]

    def validate(self, output: str, trade: Trade) -> ValidationFailure | None:
        # 1. No markdown
        if failure := self._check_no_markdown(output):
            return failure

        # 2. All four check areas must be present
        for area_name, area_terms in self.REQUIRED_CHECK_AREAS:
            if not any(term in output for term in area_terms):
                return ValidationFailure(
                    agent_name=self.AGENT_NAME,
                    reason=f"Investigation output is missing the '{area_name}' check area. "
                           f"Expected one of these terms: {area_terms}. "
                           "All four check areas (LEI, KYC, sanctions, transaction history) "
                           "are required.",
                    output_excerpt=output[:200],
                )

        # 3. Citations — at least 3 required (one per major check area is the floor)
        # [DEV] TUNE MINIMUM CITATIONS ────────────────────────────────────────
        # 3 is the minimum (one per major data source: LEI, KYC/Sanctions, TX).
        # Increase if your compliance team requires more granular citation density.
        # ─────────────────────────────────────────────────────────────────────
        citations = self._count_citations(output)
        if len(citations) < 3:
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason=f"Investigation output contains only {len(citations)} citation(s). "
                       "Minimum 3 [SOURCE: X] citations required — one per major data source queried. "
                       "Undercited investigation output cannot be considered reliable.",
                output_excerpt=output[-300:],
            )

        # 4. Check for unrecognized source names
        if failure := self._check_unrecognized_citations(citations):
            return failure

        # 5. Explicit conclusion is required
        if not any(conclusion in output for conclusion in self.REQUIRED_CONCLUSIONS):
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason="Investigation output does not contain an explicit conclusion. "
                       "Output must include exactly one of: 'FALSE POSITIVE' or 'GENUINE CONCERN'. "
                       "Ambiguous conclusions cannot be passed to the reasoning agent.",
                output_excerpt=output[-300:],
            )

        return None  # Validation passed


# ─────────────────────────────────────────────────────────────
# AGENT 3 — REASONING VALIDATOR
# ─────────────────────────────────────────────────────────────

class ReasoningValidator(AgentValidator):
    """
    Validates output from the Compliance Reasoning Agent.

    Contract (from system prompt):
      - Between 3 and 7 numbered steps
      - Step format: "N. [Evidence examined] — [Finding]."
      - Every step must contain a [SOURCE: X] citation
      - Plain text, no markdown

    Failure → escalate before routing to report agent.
    A reasoning chain that regulators cannot follow is not a reasoning chain.
    """

    AGENT_NAME = "reasoning_agent"
    # [DEV] TUNE REASONING CHAIN LENGTH ──────────────────────────────────────
    # 3–7 steps reflects regulatory audit expectations for a standard AML
    # investigation chain. Adjust if your regulator or internal policy
    # specifies a different range. Also update the reasoning_agent system
    # prompt in orchestrator.py to match ("Minimum N steps. Maximum M steps.")
    # ─────────────────────────────────────────────────────────────────────────
    MIN_STEPS = 3
    MAX_STEPS = 7

    # Matches numbered steps: "1. ...", "2. ...", etc.
    STEP_PATTERN = re.compile(r"^\d+\.", re.MULTILINE)

    def validate(self, output: str, trade: Trade) -> ValidationFailure | None:
        # 1. No markdown
        if failure := self._check_no_markdown(output):
            return failure

        # 2. Count numbered steps
        steps = self.STEP_PATTERN.findall(output)
        step_count = len(steps)

        if step_count < self.MIN_STEPS:
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason=f"Reasoning chain contains only {step_count} step(s). "
                       f"Minimum is {self.MIN_STEPS}. A chain this short cannot represent "
                       "a complete AML investigation and will not satisfy regulatory audit.",
                output_excerpt=output[:300],
            )
        if step_count > self.MAX_STEPS:
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason=f"Reasoning chain contains {step_count} steps. "
                       f"Maximum is {self.MAX_STEPS}. Trim to the most evidentially significant steps. "
                       "Excessively long chains dilute the key findings for the compliance officer.",
                output_excerpt=output[:300],
            )

        # 3. Every step must contain a citation.
        # Split on numbered step markers and check each segment.
        step_segments = re.split(r"\n(?=\d+\.)", output.strip())
        steps_missing_citations = []
        for i, segment in enumerate(step_segments, start=1):
            if not CITATION_PATTERN.search(segment):
                steps_missing_citations.append(i)

        if steps_missing_citations:
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason=f"Step(s) {steps_missing_citations} are missing [SOURCE: X] citations. "
                       "Every step in the reasoning chain must cite a specific source. "
                       "Uncited steps will not hold up under regulatory review.",
                output_excerpt=output[:300],
            )

        # 4. Check for unrecognized source names
        citations = self._count_citations(output)
        if failure := self._check_unrecognized_citations(citations):
            return failure

        return None  # Validation passed


# ─────────────────────────────────────────────────────────────
# AGENT 4 — REPORT VALIDATOR
# ─────────────────────────────────────────────────────────────

class ReportValidator(AgentValidator):
    """
    Validates output from the Exception Report Agent.

    Contract (from system prompt):
      - Exactly four section headers, in this order:
          FLAG SUMMARY
          INVESTIGATION FINDINGS
          REGULATORY ASSESSMENT
          RECOMMENDED ACTION
      - RECOMMENDED ACTION must begin with "Recommend:"
      - Plain text, no markdown

    On failure: re-invoke agent with explicit format reminder,
    once. If it fails again, escalate to human review.

    This is the document the compliance officer reads to make their
    decision. Format is non-negotiable.
    """

    AGENT_NAME = "report_agent"

    REQUIRED_SECTIONS = [
        "FLAG SUMMARY",
        "INVESTIGATION FINDINGS",
        "REGULATORY ASSESSMENT",
        "RECOMMENDED ACTION",
    ]

    def validate(self, output: str, trade: Trade) -> ValidationFailure | None:
        # 1. No markdown
        if failure := self._check_no_markdown(output):
            return failure

        # 2. All four section headers must be present
        missing_sections = [
            section for section in self.REQUIRED_SECTIONS
            if section not in output
        ]
        if missing_sections:
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason=f"Exception report is missing required section(s): {missing_sections}. "
                       f"All four sections are required: {self.REQUIRED_SECTIONS}. "
                       "Re-invoke with explicit format reminder.",
                output_excerpt=output[:300],
            )

        # 3. Sections must appear in correct order
        section_positions = [output.find(s) for s in self.REQUIRED_SECTIONS]
        if section_positions != sorted(section_positions):
            return ValidationFailure(
                agent_name=self.AGENT_NAME,
                reason="Section headers appear out of order. Required order: "
                       + " → ".join(self.REQUIRED_SECTIONS),
                output_excerpt=output[:300],
            )

        # 4. RECOMMENDED ACTION section must begin with "Recommend:"
        rec_action_idx = output.find("RECOMMENDED ACTION")
        if rec_action_idx != -1:
            rec_section = output[rec_action_idx:]
            # Find the content after the section header
            content_after_header = rec_section[len("RECOMMENDED ACTION"):].strip()
            # Remove a leading colon or newline if the header uses "RECOMMENDED ACTION:"
            content_after_header = content_after_header.lstrip(":").strip()
            if not content_after_header.startswith("Recommend:"):
                return ValidationFailure(
                    agent_name=self.AGENT_NAME,
                    reason="The RECOMMENDED ACTION section does not begin with 'Recommend:'. "
                           "This is required for downstream parsing and audit log tagging.",
                    output_excerpt=rec_section[:200],
                )

        return None  # Validation passed


# ─────────────────────────────────────────────────────────────
# VALIDATOR REGISTRY — keyed by agent name
# ─────────────────────────────────────────────────────────────

VALIDATORS: dict[str, AgentValidator] = {
    "triage_agent":        TriageValidator(),
    "investigation_agent": InvestigationValidator(),
    "reasoning_agent":     ReasoningValidator(),
    "report_agent":        ReportValidator(),
}


def validate_agent_output(
    agent_name: str,
    output: str,
    trade: Trade,
) -> ValidationFailure | None:
    """
    Public interface for the orchestrator.
    Call this after every agent.run().

    Returns None if validation passes.
    Returns ValidationFailure if validation fails — orchestrator should
    convert this to an AgentResult with status='escalate'.

    Usage:
        result = agent.run(trade_str, context)
        failure = validate_agent_output(agent.name, result, trade)
        if failure:
            return AgentResult(
                agent_name=agent.name,
                output=result,
                status="escalate",
                reason=failure.to_escalation_reason(),
            )
    """
    validator = VALIDATORS.get(agent_name)
    if not validator:
        # Unknown agent — pass through with a warning rather than blocking.
        # Log this: it means an agent was added without a corresponding validator.
        return None
    return validator.validate(output, trade)
