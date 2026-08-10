"""
agents/audit.py

Audit Agent — reviews the complete accumulated process and produces a
structured summary for a human claims professional. This is the final
autonomous step before the human checkpoint (see workflow/payout_gate.py).

This is an illustrative implementation, not a disclosure of any real
insurer's actual system. See README.md for the full design reasoning.

DEPENDENCY NOTE: Audit requires ALL prior agents' outputs — it cannot
summarize a process that hasn't finished. This is a genuine convergence
point at the end of the pipeline, not a sequencing preference.
"""

from dataclasses import dataclass

from models.claim import Claim, AgentOutput
from providers.base import LLMProvider, ProviderResponseError


REQUIRED_SECTIONS = [
    "CLAIM SUMMARY",
    "COVERAGE & WEATHER FINDINGS",
    "FRAUD SCREENING RESULT",
    "RECOMMENDED SETTLEMENT",
]

AUDIT_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "summary_text": {
            "type": "string",
            "description": "Must contain all four required section labels, in order.",
        },
    },
    "required": ["summary_text"],
}


AUDIT_SYSTEM_PROMPT = """You are a claims-audit summarization agent.

Produce a summary using exactly these four section labels, in this order: \
CLAIM SUMMARY, COVERAGE & WEATHER FINDINGS, FRAUD SCREENING RESULT, \
RECOMMENDED SETTLEMENT. The claims professional who reads this will make \
the final payout decision based solely on what you write here — be \
complete and precise, and do not omit any of the four sections."""


class AuditSummaryError(Exception):
    """Raised when Audit's response is missing a required section after
    one retry — routes to human review with a note that the summary
    itself needs manual attention."""
    pass


@dataclass
class AuditResult:
    summary_text: str
    agent_output: AgentOutput


class AuditAgent:

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def run(self, claim: Claim, prior_outputs: list[AgentOutput]) -> AuditResult:
        """
        [DEV] EXTENSION POINT: on a missing-section failure, this retries
        once with an explicit reminder before raising AuditSummaryError.
        If you want more retries or a different reminder strategy, change
        it here — this is the one agent where a single malformed response
        is worth one automatic retry rather than an immediate halt, since
        the fix (reminding the model of the format) is simple and cheap
        compared to escalating a perfectly good underlying claim decision
        just because the summary's formatting slipped.
        """
        user_message = self._build_user_message(claim, prior_outputs)

        response = self._call_with_retry(user_message, retry_reminder=False)
        if not self._has_all_sections(response.data["summary_text"]):
            response = self._call_with_retry(user_message, retry_reminder=True)
            if not self._has_all_sections(response.data["summary_text"]):
                raise AuditSummaryError(
                    "Audit summary missing required section(s) after retry — "
                    "routing to human review for manual summary construction."
                )

        return AuditResult(
            summary_text=response.data["summary_text"],
            agent_output=AgentOutput(
                agent_name="audit",
                conclusion="summary_complete",
                reasoning=response.data["summary_text"],
                provider_name=response.provider_name,
                raw_response=response.raw_text,
            ),
        )

    def _call_with_retry(self, user_message: str, retry_reminder: bool):
        prompt = AUDIT_SYSTEM_PROMPT
        if retry_reminder:
            prompt += (
                "\n\nYour previous response was missing one or more of the four "
                "required section labels. Include all four, exactly as named, "
                "before responding again."
            )
        try:
            return self.provider.complete_structured(
                system_prompt=prompt,
                user_message=user_message,
                output_schema=AUDIT_OUTPUT_SCHEMA,
                max_tokens=400,
            )
        except ProviderResponseError as e:
            raise AuditSummaryError(f"Audit agent could not get a valid response: {e.detail}") from e

    @staticmethod
    def _has_all_sections(summary_text: str) -> bool:
        return all(section in summary_text for section in REQUIRED_SECTIONS)

    @staticmethod
    def _build_user_message(claim: Claim, prior_outputs: list[AgentOutput]) -> str:
        lines = [f"Claim ID: {claim.claim_id}", f"Claimed amount (AUD): {claim.claimed_amount}", ""]
        for output in prior_outputs:
            lines.append(f"--- {output.agent_name.upper()} ---")
            lines.append(f"Conclusion: {output.conclusion}")
            lines.append(f"Reasoning: {output.reasoning}")
            lines.append("")
        return "\n".join(lines)
