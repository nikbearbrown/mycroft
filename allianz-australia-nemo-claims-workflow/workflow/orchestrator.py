"""
workflow/orchestrator.py

Runs the pipeline: Planner -> Coverage -> Weather -> Fraud -> Payout ->
Audit -> human checkpoint. Every agent call is wrapped by Cyber (see
agents/cyber.py) — Cyber is applied here, consistently, rather than each
agent guarding itself.

Coverage runs before Weather as a fail-fast choice. Weather runs before
Fraud because Fraud has a genuine data dependency on Weather's output.
See README.md for the full reasoning behind this ordering.

This orchestrator STOPS at the human checkpoint — it does not execute
payout. See cli/demo.py and api/main.py for how a caller submits a human
decision and completes the workflow via workflow/payout_gate.py.
"""

from dataclasses import dataclass, field

from agents.planner import PlannerAgent, PlannerParsingError
from agents.coverage import CoverageAgent, CoverageDecisionError
from agents.weather import WeatherAgent, WeatherCheckError
from agents.fraud import FraudAgent, FraudCheckError, FraudFlaggedForReview
from agents.payout import PayoutAgent, PayoutCalculationError
from agents.audit import AuditAgent, AuditSummaryError
from agents.cyber import CyberWrapper, CyberPolicyViolation
from models.claim import AgentOutput
from providers.base import LLMProvider


class WorkflowHaltedError(Exception):
    """Raised whenever the pipeline stops before reaching the human
    checkpoint — always carries a reason and which stage halted it, since
    the caller (CLI/API) needs to show the user something specific, not
    a generic failure."""
    def __init__(self, stage: str, reason: str):
        self.stage = stage
        self.reason = reason
        super().__init__(f"Workflow halted at '{stage}': {reason}")


@dataclass
class WorkflowResult:
    claim_id: str
    status: str                          # matches models.claim.ClaimStatus values
    agent_outputs: list = field(default_factory=list)
    audit_summary: str = ""
    recommended_amount_aud: float | None = None


class NemoOrchestrator:

    def __init__(self, provider: LLMProvider, threshold_aud: float):
        self.provider = provider
        self.threshold_aud = threshold_aud
        self.planner = PlannerAgent(provider)
        self.coverage = CoverageAgent(provider, threshold_aud)
        self.weather = WeatherAgent(provider)
        self.fraud = FraudAgent(provider)
        self.payout = PayoutAgent(provider, threshold_aud)
        self.audit = AuditAgent(provider)
        self.cyber = CyberWrapper()

    def run(self, raw_claim_event: str, policy_record, meteorological_data: str, claim_history_summary: str) -> WorkflowResult:
        """
        NOTE: policy_record is passed in by the caller (see cli/demo.py),
        not looked up internally — this reference implementation uses
        stub data (data/stub_scenarios.py) rather than a real policy
        database. Wire an actual database lookup in the caller if you're
        adapting this beyond the stub scenarios; the orchestrator itself
        doesn't need to change.
        """
        outputs: list[AgentOutput] = []

        # --- Planner ---
        try:
            planner_result = self.cyber.guard(
                "planner", {"claim_intake"},
                lambda: self.planner.run(raw_claim_event),
            )
        except (PlannerParsingError, CyberPolicyViolation) as e:
            raise WorkflowHaltedError("planner", str(e))
        outputs.append(planner_result.agent_output)
        claim = planner_result.claim

        # --- Coverage (fail-fast: exits here without spending Weather/Fraud calls) ---
        try:
            coverage_result = self.cyber.guard(
                "coverage", {"policy_database"},
                lambda: self.coverage.run(claim, policy_record),
            )
        except (CoverageDecisionError, CyberPolicyViolation) as e:
            raise WorkflowHaltedError("coverage", str(e))
        outputs.append(coverage_result.agent_output)

        if coverage_result.determination != "covered" or coverage_result.exceeds_threshold:
            raise WorkflowHaltedError(
                "coverage",
                f"Claim not eligible for automated handling: determination="
                f"{coverage_result.determination}, exceeds_threshold="
                f"{coverage_result.exceeds_threshold}. Weather and Fraud did not run.",
            )

        # --- Weather ---
        try:
            weather_result = self.cyber.guard(
                "weather", {"meteorological_data"},
                lambda: self.weather.run(claim, meteorological_data),
            )
        except (WeatherCheckError, CyberPolicyViolation) as e:
            raise WorkflowHaltedError("weather", str(e))
        outputs.append(weather_result.agent_output)

        # --- Fraud (hard dependency on Weather's result) ---
        try:
            fraud_result = self.cyber.guard(
                "fraud", {"accumulated_context", "claim_history"},
                lambda: self.fraud.run(
                    claim,
                    coverage_conclusion=coverage_result.determination,
                    weather_match_status=weather_result.match_status,
                    weather_reasoning=weather_result.reasoning,
                    claim_history_summary=claim_history_summary,
                ),
            )
        except FraudFlaggedForReview as e:
            outputs.append(e.agent_output)
            # [DEV] EXTENSION POINT: see agents/fraud.py module docstring —
            # this is where you'd route into a real investigation workflow
            # instead of simply halting here.
            raise WorkflowHaltedError("fraud", str(e))
        except (FraudCheckError, CyberPolicyViolation) as e:
            raise WorkflowHaltedError("fraud", str(e))
        outputs.append(fraud_result.agent_output)

        # --- Payout (hard dependency on both Coverage and Fraud) ---
        try:
            payout_result = self.cyber.guard(
                "payout", {"accumulated_context"},
                lambda: self.payout.run(
                    claim,
                    coverage_conclusion=coverage_result.determination,
                    fraud_conclusion=fraud_result.conclusion,
                ),
            )
        except (PayoutCalculationError, CyberPolicyViolation) as e:
            raise WorkflowHaltedError("payout", str(e))
        outputs.append(payout_result.agent_output)

        # --- Audit (convergence point: needs every prior output) ---
        try:
            audit_result = self.cyber.guard(
                "audit", {"accumulated_context"},
                lambda: self.audit.run(claim, outputs),
            )
        except (AuditSummaryError, CyberPolicyViolation) as e:
            raise WorkflowHaltedError("audit", str(e))
        outputs.append(audit_result.agent_output)

        return WorkflowResult(
            claim_id=claim.claim_id,
            status="awaiting_human_review",
            agent_outputs=outputs,
            audit_summary=audit_result.summary_text,
            recommended_amount_aud=payout_result.recommended_amount_aud,
        )
