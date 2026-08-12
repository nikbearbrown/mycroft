"""
schemas.py
==========
Agentic Credit Memo Pipeline — Core Data Contracts

Every agent, every data source adapter, and every test fixture must
conform to these schemas. Do not pass raw dicts between pipeline components.

[DEV] POINTS IN THIS FILE:
  1. IndustryCode literal — add new industry codes here AND in
     credit_policy.json under 'ratio_thresholds' to keep them in sync.
  2. LoanType literal — extend for additional loan products your institution
     offers (e.g. ASSET_BASED_LENDING, MEZZANINE, SBA_LOAN).
  3. LoanApplication validators — adjust EIN format validation if your
     institution operates internationally and uses different entity IDs.
  4. FinancialStatements — add or remove line items to match the fields
     your financial data extraction system actually produces.

Dependencies:
    pip install pydantic>=2.0
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


# ─────────────────────────────────────────────────────────────
# ENUMS / LITERALS
# ─────────────────────────────────────────────────────────────

# [DEV] Add new industry codes here AND in credit_policy.json
# under 'ratio_thresholds'. The strings must match exactly.
IndustryCode = Literal[
    "INDUSTRIAL_MANUFACTURING",
    "TECHNOLOGY",
    "REAL_ESTATE",
    "HEALTHCARE",
    "RETAIL",
    "ENERGY",
    "FINANCIAL_SERVICES",
    "OTHER",
]

# [DEV] Add loan products your institution offers.
LoanType = Literal[
    "REVOLVING_CREDIT_FACILITY",
    "TERM_LOAN_A",
    "TERM_LOAN_B",
    "BRIDGE_LOAN",
    "LETTER_OF_CREDIT",
]

KYCRiskTier = Literal["LOW", "MEDIUM", "HIGH", "ENHANCED_DUE_DILIGENCE"]

# Status returned by each agent. 'escalate' halts the pipeline
# and routes to approval_routing.py before the next agent runs.
AgentStatus = Literal["ok", "escalate", "halt"]

CreditRecommendation = Literal[
    "APPROVE",
    "DECLINE",
    "APPROVE_WITH_CONDITIONS",
    "REFER_TO_COMMITTEE",
]


# ─────────────────────────────────────────────────────────────
# LOAN APPLICATION
# Entry point for the pipeline. Your loan origination system
# needs an adapter to map its internal format to this schema.
# ─────────────────────────────────────────────────────────────

class LoanApplication(BaseModel):
    application_id: UUID = Field(default_factory=uuid4)
    applicant_legal_name: str
    applicant_ein: str = Field(description="Employer Identification Number (XX-XXXXXXX).")

    # [DEV] Industry drives which ratio thresholds are applied from
    # credit_policy.json. Ensure this value matches a key in that file.
    applicant_industry: IndustryCode

    loan_type: LoanType
    requested_amount: Decimal = Field(gt=Decimal("0"))
    proposed_collateral_description: str

    # [DEV] relationship_manager_id is written to the audit trail and
    # determines who is notified when the memo is routed for approval.
    # Connect to your HR / CRM system to validate this ID.
    relationship_manager_id: str

    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("applicant_ein")
    @classmethod
    def validate_ein(cls, v: str) -> str:
        # [DEV] Adjust or remove this validator if your institution operates
        # internationally and uses LEI or other entity identifiers instead of EIN.
        cleaned = v.replace("-", "")
        if len(cleaned) != 9 or not cleaned.isdigit():
            raise ValueError(f"Invalid EIN '{v}'. Must be 9 digits (XX-XXXXXXX).")
        return v

    def to_pipeline_string(self) -> str:
        return (
            f"APPLICATION ID: {self.application_id}\n"
            f"APPLICANT: {self.applicant_legal_name} | EIN: {self.applicant_ein}\n"
            f"INDUSTRY: {self.applicant_industry}\n"
            f"LOAN TYPE: {self.loan_type}\n"
            f"REQUESTED AMOUNT: ${self.requested_amount:,.2f} USD\n"
            f"PROPOSED COLLATERAL: {self.proposed_collateral_description}\n"
            f"RELATIONSHIP MANAGER: {self.relationship_manager_id}"
        )


# ─────────────────────────────────────────────────────────────
# PRE-FETCHED DATA RECORDS
# All three are assembled into CreditContext before any agent runs.
# Agents never call data sources — they receive this context object.
# ─────────────────────────────────────────────────────────────

class KYCRecord(BaseModel):
    applicant_id: str
    kyc_risk_tier: KYCRiskTier
    kyc_last_reviewed: date
    beneficial_owners_verified: bool
    foreign_subsidiaries: list[str] = Field(default_factory=list)
    # Prior relationship data — directly referenced in the case study's Step 3 description.
    # Each entry is a plain descriptive string (e.g. "2021 revolving credit facility, $20M").
    prior_relationship_history: list[str] = Field(default_factory=list)
    # Payment history, covenant compliance, amendment requests from prior facilities.
    # Each entry is a plain descriptive string (e.g. "2021 facility: zero missed payments").
    facility_performance_history: list[str] = Field(default_factory=list)
    # [DEV] Populate flags from your KYC system's own alert/exception fields.
    flags: list[str] = Field(default_factory=list)
    raw_summary: str


class OSINTRecord(BaseModel):
    applicant_id: str
    adverse_media_found: bool
    findings: list[str] = Field(default_factory=list)
    # [DEV] Severity must match a key in credit_policy.json
    # under 'osint_policy.blocking_severities'.
    severity: Literal["NONE", "LOW", "MEDIUM", "HIGH"]
    raw_summary: str


class FinancialStatements(BaseModel):
    applicant_id: str
    years_available: list[int]

    # [DEV] Add or remove line items to match what your financial data
    # extraction system produces. All values are USD.
    revenue: dict[int, Decimal]
    ebitda: dict[int, Decimal]
    total_debt: dict[int, Decimal]
    interest_expense: dict[int, Decimal]
    net_operating_income: dict[int, Decimal]
    total_debt_service: dict[int, Decimal]
    current_assets: dict[int, Decimal]
    current_liabilities: dict[int, Decimal]
    capital_expenditures: dict[int, Decimal]
    operating_cash_flow: dict[int, Decimal]

    # [DEV] Extension points — not yet implemented in the Quantitative Agent.
    # Add these to unlock two ratios listed in the case study's Step 5 ratio list:
    #   inventory: dict[int, Decimal]
    #     → Quick Ratio = (Current Assets − Inventory) / Current Liabilities
    #       Follow the pattern of current_assets above. Add the threshold to
    #       credit_policy.json under each industry block once confirmed with
    #       your credit risk team.
    #   cost_of_goods_sold: dict[int, Decimal]  (or gross_profit — either works)
    #     → Gross Margin = (Revenue − COGS) / Revenue
    #       Follow the pattern of revenue above. Add threshold to credit_policy.json.
    # The Quantitative Agent prompt in orchestrator.py will need corresponding
    # calculation instructions added once these fields are populated.

    raw_summary: str


class CreditContext(BaseModel):
    """
    Assembled by the orchestrator before any agent runs.
    This is the single object every agent reasons over.
    Adding a new data source means adding a field here and a
    corresponding stub/adapter in data_sources.py.
    """
    application: LoanApplication
    kyc: KYCRecord
    osint: OSINTRecord
    financials: FinancialStatements
    assembled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ─────────────────────────────────────────────────────────────
# AGENT RESULT
# Returned by every agent. The orchestrator checks status before
# invoking the next agent — 'escalate' or 'halt' stops the pipeline.
# ─────────────────────────────────────────────────────────────

class AgentResult(BaseModel):
    agent_name: str
    status: AgentStatus
    output: str
    # [DEV] Citations are checked by the orchestrator to detect
    # uncited claims (hallucination signal). Minimum citation count
    # per agent is set in orchestrator.py — adjust per your quality bar.
    citations: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    produced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ─────────────────────────────────────────────────────────────
# CREDIT MEMO
# The pipeline's final output — a structured draft for the analyst.
# ─────────────────────────────────────────────────────────────

class CreditMemo(BaseModel):
    application_id: UUID
    executive_summary: str
    borrower_overview: str
    financial_analysis: str
    risk_assessment: str
    collateral_analysis: str
    covenant_package: str
    agent_recommendation: CreditRecommendation
    agent_reasoning: str
    # [DEV] agent_risk_tier is used by approval_routing.py to determine
    # which approval tier this memo is routed to. The Reasoning/Report
    # Agent must produce this field explicitly.
    agent_risk_tier: str = "MEDIUM"
    draft_produced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_review_string(self) -> str:
        return (
            f"{'='*60}\n"
            f"CREDIT MEMO DRAFT — Application {self.application_id}\n"
            f"AGENT RECOMMENDATION: {self.agent_recommendation} | RISK TIER: {self.agent_risk_tier}\n"
            f"{'='*60}\n\n"
            f"EXECUTIVE SUMMARY\n{self.executive_summary}\n\n"
            f"BORROWER OVERVIEW\n{self.borrower_overview}\n\n"
            f"FINANCIAL ANALYSIS\n{self.financial_analysis}\n\n"
            f"RISK ASSESSMENT\n{self.risk_assessment}\n\n"
            f"COLLATERAL ANALYSIS\n{self.collateral_analysis}\n\n"
            f"COVENANT PACKAGE\n{self.covenant_package}\n\n"
            f"AGENT REASONING\n{self.agent_reasoning}\n"
            f"{'='*60}\n"
            f"THIS IS A DRAFT. HUMAN ANALYST DECISION REQUIRED.\n"
            f"{'='*60}\n"
        )


# ─────────────────────────────────────────────────────────────
# CREDIT DECISION
# Submitted by the human reviewer after they have read the memo.
# This is the record the case study's Step 9 describes —
# the officer's name, credentials, decision, and rationale,
# attached permanently to the application's audit trail.
# ─────────────────────────────────────────────────────────────

class CreditDecision(BaseModel):
    application_id: UUID
    reviewing_officer_name: str
    # [DEV] Format: "SVP, Commercial Credit — NY Region" or equivalent.
    reviewing_officer_credentials: str
    decision: Literal["APPROVE", "DECLINE", "APPROVE_WITH_MODIFIED_TERMS"]
    # Narrative rationale — required, not optional. The audit trail must
    # explain why the decision was made, not just what it was.
    decision_rationale: str
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
