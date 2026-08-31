"""
orchestrator.py
===============
Agentic Credit Memo Pipeline — Orchestrator

Coordinates the three-agent assembly pipeline and the approval routing step.

Agent sequence:
  KYC/Data Agent and OSINT Agent run sequentially in this reference
  implementation. The design intent is parallel — they draw from independent
  data domains with no dependency on each other — but sequential execution
  is easier to follow for a first-time reader of the codebase.
  See the [DEV] comment in run() for how to switch to true parallel execution.

  Quantitative Agent runs after both complete — it does not depend on KYC/OSINT
  content, but we wait to confirm the correct entity was identified before
  running ratio calculations.

  Reasoning/Report Agent runs last — it synthesizes all three prior outputs
  plus the credit policy thresholds into the memo draft.

After the memo is produced, approval_routing.py determines which approval tier
it is sent to based on loan size and the agent's risk tier assessment.

No credit decision is recorded by this system. The approval queue receives the
routed memo and a human analyst or committee makes the final decision.

[DEV] POINTS IN THIS FILE:
  1. LLM provider — currently Anthropic only. See _call_llm() to add
     OpenAI or Gemini support.
  2. Agent prompts — each prompt is a module-level constant. Edit them
     directly when your credit policy or memo template changes.
  3. Citation minimum — MIN_CITATIONS_PER_AGENT controls the hallucination
     detection threshold. Increase it for a stricter quality bar.
  4. Retry logic — _run_agent() retries once on a failed citation check.
     Add more sophisticated retry logic here for production.
  5. Parallel execution — KYC and OSINT agents run sequentially in this
     reference implementation for simplicity. See [DEV] in run() for
     how to make them truly parallel with asyncio or ThreadPoolExecutor.

Dependencies:
    pip install pydantic>=2.0 anthropic>=0.25
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from schemas import AgentResult, AgentStatus, CreditContext, CreditMemo, LoanApplication
from policy_loader import get_loader
from approval_routing import route_memo, escalation_routing, ApprovalQueue

logger = logging.getLogger(__name__)

# [DEV] Minimum number of [SOURCE: ...] citations required in each agent's
# output before it is passed to the next agent. An agent that cannot cite
# its claims is asserting without evidence — the hallucination risk that
# directly corrupts credit decisions.
MIN_CITATIONS_PER_AGENT = 3


# ─────────────────────────────────────────────────────────────
# AGENT PROMPTS
# Edit these when your credit policy or memo format changes.
# Each prompt is specific to one agent's data domain.
# ─────────────────────────────────────────────────────────────

# [DEV] KYC_AGENT_PROMPT — this agent acts as the relationship due diligence
# reviewer. Adjust the output format if your memo template uses different
# KYC section headings.
KYC_AGENT_PROMPT = """You are the KYC and Relationship Due Diligence Agent in a commercial credit underwriting pipeline at a large US bank.

Your role: review the KYC record and surface everything a credit analyst needs to know about who this borrower actually is before the financial analysis begins.

Produce a structured assessment covering:
1. Entity verification — legal name, EIN, incorporation details, KYC risk tier
2. Beneficial ownership — verified or gaps identified
3. Foreign subsidiaries — list each one, note any Enhanced Due Diligence (EDD) requirements
4. KYC recency — how long ago was the last review, is it within the required cycle for this risk tier?
5. Prior credit relationships — any prior credit facilities or products with this institution,
   relationship tenure, and how the borrower previously used the facility
6. Prior facility performance — payment history, covenant compliance record,
   amendment requests on any prior facilities; note trends (clean, one amendment, waivers)
7. Outstanding items — anything that must be resolved before credit can close

Every assertion must be tagged [SOURCE: KYC_RECORD] or [SOURCE: RELATIONSHIP_HISTORY].
If a required data point is absent, state the gap explicitly. Do not infer or estimate.

End your response with exactly one of:
  KYC STATUS: CLEAR
  KYC STATUS: FLAG (followed by a one-line description of the flag)
  KYC STATUS: BLOCK (followed by a one-line reason — this halts the pipeline)"""

# [DEV] OSINT_AGENT_PROMPT — this agent acts as the adverse intelligence
# reviewer. Severity classification must align with the keys in
# credit_policy.json under 'osint_policy'.
OSINT_AGENT_PROMPT = """You are the OSINT and Adverse Media Agent in a commercial credit underwriting pipeline at a large US bank.

Your role: assess what the public record says about this borrower's risk profile — litigation, regulatory actions, adverse media, sanctions — and classify each finding by severity.

Produce a structured assessment covering:
1. Adverse media — any negative press, reputational risk, or public controversy
2. Litigation — active lawsuits, prior judgments, regulatory enforcement actions
3. Sanctions — any matches against OFAC SDN, FinCEN, or other watchlists
4. Principal review — key executives or beneficial owners flagged in any public record
5. Severity classification — for each finding: NONE / LOW / MEDIUM / HIGH
6. Disclosure requirement — state explicitly whether each finding requires disclosure in the credit memo

Every assertion must be tagged [SOURCE: OSINT_RECORD] or [SOURCE: PUBLIC_RECORDS].
Do not speculate about findings not in the provided record.

End your response with exactly one of:
  ADVERSE MEDIA SEVERITY: NONE
  ADVERSE MEDIA SEVERITY: LOW
  ADVERSE MEDIA SEVERITY: MEDIUM
  ADVERSE MEDIA SEVERITY: HIGH (this halts the pipeline — route immediately to Senior Credit Officer)"""

# [DEV] QUANTITATIVE_AGENT_PROMPT — this agent does the arithmetic a credit
# analyst would otherwise do in a spreadsheet. The policy thresholds are
# injected at runtime from credit_policy.json via policy_loader.py — do not
# hardcode threshold values into this prompt string.
QUANTITATIVE_AGENT_PROMPT = """You are the Quantitative Analysis Agent in a commercial credit underwriting pipeline at a large US bank.

Your role: calculate the required financial ratios from the borrower's statements and assess each one against the provided credit policy thresholds.

Calculate for each available year:
1. Leverage Ratio = Total Debt / EBITDA
2. Interest Coverage Ratio = EBITDA / Interest Expense
3. Debt Service Coverage Ratio (DSCR) = Net Operating Income / Total Debt Service
4. Current Ratio = Current Assets / Current Liabilities
5. Free Cash Flow = Operating Cash Flow - Capital Expenditures
6. Revenue growth rate (year-over-year %)
7. EBITDA margin (EBITDA / Revenue %)

For each ratio:
- Show the calculation with the exact source line items and year used, e.g.:
  Leverage (2024) = $35,000,000 / $16,100,000 = 2.17x [SOURCE: FINANCIAL_STATEMENTS_2024]
- State whether the result is PASS, WATCH, or FAIL against the policy threshold
- Note any deteriorating trend (e.g. DSCR declining three years in a row)

Do not estimate or interpolate any missing line item. State gaps explicitly.

{policy_thresholds}

End your response with exactly one of:
  FINANCIAL RISK ASSESSMENT: LOW
  FINANCIAL RISK ASSESSMENT: MEDIUM
  FINANCIAL RISK ASSESSMENT: HIGH
  FINANCIAL RISK ASSESSMENT: FAIL (one or more ratios below minimum threshold — escalate before proceeding)"""

# [DEV] REASONING_AGENT_PROMPT — this agent writes the memo draft.
# Edit the section list here if your institution uses a different
# standard memo template. The agent_risk_tier field it produces is
# used by approval_routing.py — ensure the values it outputs match
# the tier keys in credit_policy.json.
REASONING_AGENT_PROMPT = """You are the Reasoning and Credit Memo Agent in a commercial credit underwriting pipeline at a large US bank.

Your role: synthesize the KYC assessment, OSINT findings, and quantitative analysis into a complete credit memo draft for human analyst review. This draft will be reviewed and finalized by a licensed credit analyst before any lending decision is made.

The memo must contain exactly these sections with these headers:
## EXECUTIVE SUMMARY
## BORROWER OVERVIEW
## FINANCIAL ANALYSIS
## RISK ASSESSMENT
## COLLATERAL ANALYSIS
## COVENANT PACKAGE
## AGENT RECOMMENDATION
## AGENT REASONING

Rules:
- Every assertion must cite its source: [SOURCE: KYC_AGENT], [SOURCE: OSINT_AGENT], [SOURCE: QUANTITATIVE_AGENT], or [SOURCE: CREDIT_POLICY]
- Label model judgments explicitly as judgments, not facts
- The COVENANT PACKAGE section must propose specific covenant levels using the policy headroom guidelines provided
- AGENT RECOMMENDATION must be exactly one of: APPROVE / DECLINE / APPROVE_WITH_CONDITIONS / REFER_TO_COMMITTEE
- AGENT REASONING must be a numbered chain of 5-10 steps connecting evidence to recommendation
- Factor the MACROECONOMIC OVERLAY (provided below) into the risk narrative — if it flags
  elevated caution for this industry, reflect that in the Risk Assessment section and
  your recommendation rationale
- Include at the top of the memo: "DRAFT — FOR ANALYST REVIEW ONLY. NO CREDIT DECISION HAS BEEN MADE."
- End the memo with: AGENT RISK TIER: [LOW / MEDIUM / HIGH / WATCH_LIST]"""


# ─────────────────────────────────────────────────────────────
# DEPENDENCY INTERFACES
# ─────────────────────────────────────────────────────────────

class AuditLog:
    def write(self, application_id: UUID, event_type: str, content: Any) -> None:
        raise NotImplementedError

    def seal(self, application_id: UUID, routing: Any) -> None:
        raise NotImplementedError

    def record_decision(self, application_id: UUID, decision: Any) -> None:
        """
        Appends the human reviewer's final credit decision to the audit trail.
        Called by the /applications/{id}/decision endpoint after validation.
        The decision record must be immutable once written — it is the
        authoritative record of who approved or declined the credit and why.
        """
        raise NotImplementedError


# ─────────────────────────────────────────────────────────────
# WORKFLOW RESULT
# ─────────────────────────────────────────────────────────────

@dataclass
class WorkflowResult:
    application_id: UUID
    status: str  # 'completed' | 'escalated' | 'blocked'
    agent_outputs: dict[str, str] = field(default_factory=dict)
    memo: CreditMemo | None = None
    routing_tier: str | None = None
    routing_reason: str | None = None
    escalation_reason: str | None = None


# ─────────────────────────────────────────────────────────────
# LLM CALL
# ─────────────────────────────────────────────────────────────

def _call_llm(system_prompt: str, user_message: str, model: str, api_key: str) -> str:
    # [DEV] This implementation uses Anthropic Claude only.
    # To add OpenAI or Gemini support, check the LLM_PROVIDER env var here
    # and dispatch to the appropriate client. Match the return type: a plain string.
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": user_message}],
        system=system_prompt,
    )
    return message.content[0].text


# ─────────────────────────────────────────────────────────────
# ORCHESTRATOR
# ─────────────────────────────────────────────────────────────

class CreditMemoOrchestrator:

    def __init__(
        self,
        model: str,
        api_key: str,
        audit_log: AuditLog,
        approval_queue: ApprovalQueue,
    ):
        self.model = model
        self.api_key = api_key
        self.audit_log = audit_log
        self.approval_queue = approval_queue

    def run(self, application: LoanApplication, context: CreditContext) -> WorkflowResult:
        app_id = application.application_id
        loader = get_loader()
        agent_outputs: dict[str, str] = {}

        logger.info(f"[PIPELINE] Starting credit memo pipeline for {application.applicant_legal_name}")
        self.audit_log.write(app_id, "pipeline_started", {"applicant": application.applicant_legal_name})

        # ── KYC Agent and OSINT Agent ─────────────────────────
        # [DEV] These run sequentially here for simplicity. To run them
        # truly in parallel, wrap each in a ThreadPoolExecutor future or
        # use asyncio.gather() if you convert this to async.
        kyc_result = self._run_agent("kyc_agent", KYC_AGENT_PROMPT, self._kyc_message(context))
        self.audit_log.write(app_id, "kyc_agent_complete", {"status": kyc_result.status})
        agent_outputs["kyc_agent"] = kyc_result.output

        if kyc_result.status in ("escalate", "halt"):
            return self._block(app_id, agent_outputs, f"KYC block: {kyc_result.flags}")

        osint_result = self._run_agent("osint_agent", OSINT_AGENT_PROMPT, self._osint_message(context))
        self.audit_log.write(app_id, "osint_agent_complete", {"status": osint_result.status})
        agent_outputs["osint_agent"] = osint_result.output

        # OSINT HIGH severity is a credit block — check policy
        if osint_result.status in ("escalate", "halt") or loader.is_osint_severity_blocking(
            self._extract_osint_severity(osint_result.output)
        ):
            return self._block(app_id, agent_outputs, f"OSINT block: {osint_result.flags}")

        # ── Quantitative Agent ────────────────────────────────
        policy_summary = loader.get_policy_summary_for_agent(application.applicant_industry)
        quant_prompt = QUANTITATIVE_AGENT_PROMPT.format(policy_thresholds=policy_summary)
        quant_result = self._run_agent("quantitative_agent", quant_prompt, self._quant_message(context))
        self.audit_log.write(app_id, "quantitative_agent_complete", {"status": quant_result.status})
        agent_outputs["quantitative_agent"] = quant_result.output

        if quant_result.status in ("escalate", "halt"):
            return self._block(app_id, agent_outputs, f"Quantitative fail: {quant_result.flags}")

        # ── Reasoning/Report Agent ────────────────────────────
        macro_overlay = loader.get_macro_overlay(application.applicant_industry)
        reasoning_result = self._run_agent(
            "reasoning_agent",
            REASONING_AGENT_PROMPT,
            self._reasoning_message(context, agent_outputs, policy_summary, macro_overlay),
        )
        self.audit_log.write(app_id, "reasoning_agent_complete", {"status": reasoning_result.status})
        agent_outputs["reasoning_agent"] = reasoning_result.output

        if reasoning_result.status in ("escalate", "halt"):
            return self._block(app_id, agent_outputs, f"Reasoning agent: {reasoning_result.flags}")

        # ── Assemble Memo and Route for Approval ──────────────
        memo = self._parse_memo(app_id, reasoning_result.output)
        routing = route_memo(app_id, application.requested_amount, memo.agent_risk_tier, memo)
        self.approval_queue.submit(routing, memo)
        self.audit_log.seal(app_id, routing)

        return WorkflowResult(
            application_id=app_id,
            status="completed",
            agent_outputs=agent_outputs,
            memo=memo,
            routing_tier=routing.approval_tier,
            routing_reason=routing.routing_reason,
        )

    def _run_agent(self, name: str, system_prompt: str, user_message: str) -> AgentResult:
        try:
            output = _call_llm(system_prompt, user_message, self.model, self.api_key)
            citations = [w for w in output.split() if w.startswith("[SOURCE:")]
            status: AgentStatus = "ok"
            flags: list[str] = []

            # Citation check — hallucination signal
            if len(citations) < MIN_CITATIONS_PER_AGENT:
                logger.warning(f"[{name}] Low citation count ({len(citations)}). Retrying with reminder.")
                # [DEV] One retry with an explicit citation reminder.
                # Extend this logic for more sophisticated retry strategies.
                reminder = (
                    f"{user_message}\n\n"
                    f"REMINDER: Every assertion must include a [SOURCE: ...] tag. "
                    f"You provided {len(citations)} citations. Minimum required: {MIN_CITATIONS_PER_AGENT}."
                )
                output = _call_llm(system_prompt, reminder, self.model, self.api_key)
                citations = [w for w in output.split() if w.startswith("[SOURCE:")]
                if len(citations) < MIN_CITATIONS_PER_AGENT:
                    status = "escalate"
                    flags = [f"Insufficient citations after retry ({len(citations)} of {MIN_CITATIONS_PER_AGENT} required)"]

            # Status detection from agent output
            lower = output.lower()
            if "kyc status: block" in lower:
                status = "escalate"
                flags.append("KYC BLOCK detected")
            elif "adverse media severity: high" in lower:
                status = "escalate"
                flags.append("HIGH severity OSINT finding")
            elif "financial risk assessment: fail" in lower:
                status = "escalate"
                flags.append("Financial ratios below policy minimum")

            return AgentResult(agent_name=name, status=status, output=output, citations=citations, flags=flags)

        except Exception as e:
            logger.exception(f"Agent {name} failed: {e}")
            return AgentResult(agent_name=name, status="halt", output=str(e), flags=[str(e)])

    def _block(self, app_id: UUID, outputs: dict, reason: str) -> WorkflowResult:
        logger.warning(f"[PIPELINE] Pipeline blocked for {app_id}: {reason}")
        self.audit_log.write(app_id, "pipeline_blocked", {"reason": reason})

        # Build a placeholder memo so the ApprovalQueue interface stays uniform.
        # Synthesis never ran — the memo fields contain the available evidence
        # rather than a synthesized narrative. The reviewer receives whatever
        # the agents produced up to the point the pipeline halted.
        placeholder_memo = CreditMemo(
            application_id=app_id,
            executive_summary=f"PIPELINE HALTED — {reason}. Synthesis agent was not invoked.",
            borrower_overview=outputs.get("kyc_agent", "KYC agent output not available."),
            financial_analysis=outputs.get("quantitative_agent", "Quantitative agent did not run."),
            risk_assessment=outputs.get("osint_agent", "OSINT agent output not available."),
            collateral_analysis="Not assessed — pipeline halted before synthesis.",
            covenant_package="Not assessed — pipeline halted before synthesis.",
            agent_recommendation="REFER_TO_COMMITTEE",
            agent_reasoning=f"Pipeline blocked: {reason}",
            agent_risk_tier="HIGH",
        )

        routing = escalation_routing(app_id, reason)
        self.approval_queue.submit(routing, placeholder_memo)
        self.audit_log.seal(app_id, routing)

        # Include the placeholder memo in the result so the API response,
        # ApplicationStore, and the /decision endpoint all have consistent data.
        return WorkflowResult(
            application_id=app_id,
            status="blocked",
            agent_outputs=outputs,
            memo=placeholder_memo,
            escalation_reason=reason,
            routing_tier=routing.approval_tier,
            routing_reason=routing.routing_reason,
        )

    @staticmethod
    def _extract_osint_severity(output: str) -> str:
        for line in output.upper().split("\n"):
            if "ADVERSE MEDIA SEVERITY:" in line:
                for s in ["HIGH", "MEDIUM", "LOW", "NONE"]:
                    if s in line:
                        return s
        return "LOW"

    def _parse_memo(self, app_id: UUID, output: str) -> CreditMemo:
        recommendation = "REFER_TO_COMMITTEE"
        for rec in ("APPROVE_WITH_CONDITIONS", "APPROVE", "DECLINE", "REFER_TO_COMMITTEE"):
            if rec in output.upper():
                recommendation = rec  # type: ignore[assignment]
                break

        risk_tier = "MEDIUM"
        for line in output.upper().split("\n"):
            if "AGENT RISK TIER:" in line:
                for t in ["WATCH_LIST", "HIGH", "MEDIUM", "LOW"]:
                    if t in line:
                        risk_tier = t
                        break

        def section(header: str) -> str:
            lines = output.split("\n")
            capturing, buf = False, []
            for line in lines:
                if header.lower() in line.lower() and line.strip().startswith("#"):
                    capturing = True
                    continue
                if capturing and line.strip().startswith("##") and header.lower() not in line.lower():
                    break
                if capturing:
                    buf.append(line)
            return "\n".join(buf).strip() or output[:400]

        return CreditMemo(
            application_id=app_id,
            executive_summary=section("EXECUTIVE SUMMARY"),
            borrower_overview=section("BORROWER OVERVIEW"),
            financial_analysis=section("FINANCIAL ANALYSIS"),
            risk_assessment=section("RISK ASSESSMENT"),
            collateral_analysis=section("COLLATERAL ANALYSIS"),
            covenant_package=section("COVENANT PACKAGE"),
            agent_recommendation=recommendation,  # type: ignore[arg-type]
            agent_reasoning=section("AGENT REASONING"),
            agent_risk_tier=risk_tier,
        )

    @staticmethod
    def _kyc_message(ctx: CreditContext) -> str:
        return (
            f"LOAN APPLICATION:\n{ctx.application.to_pipeline_string()}\n\n"
            f"KYC RECORD:\n{ctx.kyc.raw_summary}\n\n"
            f"FLAGS:\n" + ("\n".join(ctx.kyc.flags) or "None") + "\n\n"
            f"FOREIGN SUBSIDIARIES:\n" + (", ".join(ctx.kyc.foreign_subsidiaries) or "None") + "\n\n"
            f"PRIOR CREDIT RELATIONSHIPS:\n" + ("\n".join(ctx.kyc.prior_relationship_history) or "None") + "\n\n"
            f"PRIOR FACILITY PERFORMANCE:\n" + ("\n".join(ctx.kyc.facility_performance_history) or "None")
        )

    @staticmethod
    def _osint_message(ctx: CreditContext) -> str:
        return (
            f"LOAN APPLICATION:\n{ctx.application.to_pipeline_string()}\n\n"
            f"OSINT RECORD:\n{ctx.osint.raw_summary}\n\n"
            f"FINDINGS:\n" + ("\n".join(ctx.osint.findings) or "None")
        )

    @staticmethod
    def _quant_message(ctx: CreditContext) -> str:
        fin = ctx.financials
        rows = [
            f"  {yr}: Revenue=${fin.revenue[yr]:,.0f} | EBITDA=${fin.ebitda[yr]:,.0f} | "
            f"TotalDebt=${fin.total_debt[yr]:,.0f} | InterestExp=${fin.interest_expense[yr]:,.0f} | "
            f"NOI=${fin.net_operating_income[yr]:,.0f} | DebtService=${fin.total_debt_service[yr]:,.0f} | "
            f"CurrAssets=${fin.current_assets[yr]:,.0f} | CurrLiab=${fin.current_liabilities[yr]:,.0f} | "
            f"CapEx=${fin.capital_expenditures[yr]:,.0f} | OpCF=${fin.operating_cash_flow[yr]:,.0f}"
            for yr in fin.years_available
        ]
        return (
            f"LOAN APPLICATION:\n{ctx.application.to_pipeline_string()}\n\n"
            f"FINANCIAL STATEMENTS (USD):\n" + "\n".join(rows) + "\n\n"
            f"SUMMARY: {fin.raw_summary}"
        )

    @staticmethod
    def _reasoning_message(ctx: CreditContext, outputs: dict, policy_summary: str, macro_overlay: str) -> str:
        overlay_block = f"MACROECONOMIC OVERLAY:\n{macro_overlay}\n\n" if macro_overlay else ""
        return (
            f"LOAN APPLICATION:\n{ctx.application.to_pipeline_string()}\n\n"
            f"CREDIT POLICY:\n{policy_summary}\n\n"
            f"{overlay_block}"
            f"KYC AGENT OUTPUT:\n{outputs.get('kyc_agent', 'Not available')}\n\n"
            f"OSINT AGENT OUTPUT:\n{outputs.get('osint_agent', 'Not available')}\n\n"
            f"QUANTITATIVE AGENT OUTPUT:\n{outputs.get('quantitative_agent', 'Not available')}\n\n"
            f"Synthesize the above into a complete credit memo draft."
        )
