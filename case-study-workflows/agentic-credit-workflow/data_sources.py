"""
data_sources.py
===============
Agentic Credit Memo Pipeline — Data Source Interfaces and Stubs

Why this file exists:
  The orchestrator queries all three data sources before any agent runs
  and passes the results as a single CreditContext object. This design
  makes every data check mandatory and logged — agents cannot skip a
  data source because the model decided not to call it.

  Each interface below maps to one of the three distinct data problems
  in commercial credit underwriting:
    - KYCRepository    → who is this borrower, and are their records current?
    - OSINTProvider    → what does the public record say about their risk?
    - FinancialDataStore → what do their financials actually show?

[DEV] REPLACING STUBS WITH REAL ADAPTERS:
  1. Subclass the interface (KYCRepository, OSINTProvider, FinancialDataStore)
  2. Implement the query() method connecting to your real system
  3. In main.py, replace the Stub class with your adapter:
       app.state.kyc_repo = YourKYCAdapter()
  4. Common real-system targets:
       KYC        → your internal KYC management platform (e.g. Fenergo, Appian)
       OSINT      → Refinitiv World-Check, LexisNexis Bridger, or a PACER feed
       Financials → S&P Capital IQ, Bloomberg, or your internal document
                    extraction pipeline (e.g. built on COIN-style ML extraction)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from schemas import FinancialStatements, KYCRecord, OSINTRecord

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# INTERFACES
# ─────────────────────────────────────────────────────────────

class KYCRepository(ABC):
    @abstractmethod
    def query(self, applicant_ein: str) -> KYCRecord:
        """
        Return the current KYC record for this applicant.
        Query by EIN — never by name. Name matching introduces
        false positives and is not a reliable entity identifier.

        [DEV] If your institution uses LEI as the primary entity identifier
        (common for institutional clients), change the parameter to lei: str
        and update LoanApplication.applicant_lei in schemas.py accordingly.
        """


class OSINTProvider(ABC):
    @abstractmethod
    def query(self, applicant_name: str, applicant_ein: str) -> OSINTRecord:
        """
        Screen for adverse media, civil litigation, regulatory enforcement.

        [DEV] The OSINT Agent receives raw_summary and findings[] from this
        record. Your adapter should apply your institution's severity taxonomy
        before returning the OSINTRecord — do not leave taxonomy mapping to
        the agent, as that introduces inconsistency across runs.
        """


class FinancialDataStore(ABC):
    @abstractmethod
    def query(self, applicant_ein: str) -> FinancialStatements:
        """
        Return financial statements for the applicant.

        [DEV] For a COIN-style deployment, this adapter would call your
        internal ML extraction pipeline that parses audited PDF statements
        and maps extracted values to the FinancialStatements schema fields.
        The Quantitative Agent does the ratio math — this adapter's job is
        clean, accurate extraction only.
        """


# ─────────────────────────────────────────────────────────────
# SCENARIO REGISTRY
# Four EINs, each wired to a distinct pipeline outcome.
# Use these exact EIN/industry pairings when submitting test
# applications — applicant_legal_name and applicant_industry
# are not cross-validated against the EIN in stub mode.
# ─────────────────────────────────────────────────────────────

SCENARIOS = {
    "12-3456789": {
        "company": "Apex Industrial Supply LLC",
        "industry": "INDUSTRIAL_MANUFACTURING",
        "expected_outcome": "Clean pass — all agents clear, memo drafted, routes to Credit Committee",
    },
    "45-6789012": {
        "company": "Meridian Fabrication Group LLC",
        "industry": "INDUSTRIAL_MANUFACTURING",
        "expected_outcome": "KYC BLOCK — pipeline halts after KYC agent, routes to Senior Credit Officer",
    },
    "78-9012345": {
        "company": "Cascade Retail Holdings Inc",
        "industry": "RETAIL",
        "expected_outcome": "HIGH OSINT — pipeline halts after OSINT agent, routes to Senior Credit Officer",
    },
    "23-4567890": {
        "company": "Titan Steel Works Corp",
        "industry": "ENERGY",
        "expected_outcome": "FAIL ratio — pipeline halts after Quantitative agent, routes to Senior Credit Officer",
    },
}

# NOTE: The stubs make each outcome highly likely, not guaranteed.
# Agent outputs are LLM judgments on strong fixture evidence — an unexpected
# result is a live example of the agent-consistency risk Section 6.1 of the
# case study describes, not a broken scenario to be dismissed.


# ─────────────────────────────────────────────────────────────
# STUB IMPLEMENTATIONS
# Return fixture data for local development and testing.
# Replace each stub with a real adapter for production.
# ─────────────────────────────────────────────────────────────

class StubKYCRepository(KYCRepository):
    """
    [DEV] Replace with your KYC management platform adapter.
    Returns scenario-specific fixture data keyed by applicant_ein.
    See SCENARIOS registry above for the four available EINs.
    """

    def query(self, applicant_ein: str) -> KYCRecord:
        logger.info(f"[STUB] KYC query for EIN {applicant_ein}")

        # ── Scenario: KYC BLOCK (Meridian Fabrication Group LLC) ──────────
        if applicant_ein == "45-6789012":
            return KYCRecord(
                applicant_id=applicant_ein,
                kyc_risk_tier="HIGH",
                kyc_last_reviewed=date(2023, 4, 2),
                beneficial_owners_verified=False,
                foreign_subsidiaries=[
                    "Meridian Fabrication Holdings Ltd (Cayman Islands, added 2023-Q1 — "
                    "beneficial ownership chain not fully resolved)"
                ],
                prior_relationship_history=["No prior credit relationship on record."],
                facility_performance_history=["No prior facility performance data available."],
                flags=[
                    "BLOCK: Beneficial ownership unverified — UBO chain for Cayman holding "
                    "company incomplete. FinCEN CDD Rule compliance cannot be confirmed. "
                    "Credit cannot proceed until UBO documentation is filed and reviewed.",
                    "KYC review overdue: last review April 2023 (26 months ago). "
                    "HIGH-tier policy requires review every 12 months.",
                ],
                raw_summary=(
                    "KYC risk tier: HIGH. Beneficial ownership NOT verified — "
                    "Cayman holding structure with unresolved UBO chain. "
                    "KYC review overdue by 14 months. No prior relationship. "
                    "BLOCK condition present: pipeline must halt."
                ),
            )

        # ── Scenario: Clean pass (Apex Industrial Supply LLC, default) ────
        return KYCRecord(
            applicant_id=applicant_ein,
            kyc_risk_tier="MEDIUM",
            kyc_last_reviewed=date(2024, 11, 15),
            beneficial_owners_verified=True,
            foreign_subsidiaries=["Apex Industrial Supply GmbH (Germany, added 2024-Q3)"],
            prior_relationship_history=[
                "2021: $20M revolving credit facility (matured 2024-Q1, not renewed — "
                "borrower refinanced with existing lender at lower spread).",
                "2019–2021: FX hedging and treasury services relationship, "
                "average notional $8M.",
            ],
            facility_performance_history=[
                "2021 revolving facility: zero missed payments across 36-month term. "
                "Covenant compliance maintained throughout; no waivers requested.",
                "One covenant amendment in 2023-Q2 to reset leverage ratio test "
                "to 3.75x following acquisition of a smaller distributor; "
                "amendment approved at Senior Credit Officer level.",
            ],
            flags=[
                "Foreign subsidiary added 2024-Q3 — Enhanced Due Diligence documentation "
                "required before credit close per KYC policy Section 4.2."
            ],
            raw_summary=(
                "KYC risk tier: MEDIUM. Beneficial ownership verified. "
                "One foreign subsidiary (Germany, recent addition). "
                "Prior relationship: $20M revolver (2021–2024), clean performance. "
                "Last full review: November 2024. EDD documentation pending."
            ),
        )


class StubOSINTProvider(OSINTProvider):
    """
    [DEV] Replace with your adverse media provider adapter
    (e.g. Refinitiv World-Check API, LexisNexis Bridger).
    Returns scenario-specific fixture data keyed by applicant_ein.
    See SCENARIOS registry above for the four available EINs.
    """

    def query(self, applicant_name: str, applicant_ein: str) -> OSINTRecord:
        logger.info(f"[STUB] OSINT query for {applicant_name}")

        # ── Scenario: HIGH OSINT block (Cascade Retail Holdings Inc) ──────
        if applicant_ein == "78-9012345":
            return OSINTRecord(
                applicant_id=applicant_ein,
                adverse_media_found=True,
                findings=[
                    "REGULATORY ENFORCEMENT: SEC enforcement action filed 2025-01-09 against "
                    "Cascade Retail Holdings Inc for alleged material misstatement in 2023 "
                    "annual report (revenue recognition). Civil penalty sought: $4.2M. "
                    "Status: consent order under negotiation. [Source: SEC EDGAR Litigation "
                    "Release No. 25841]",
                    "ADVERSE MEDIA: CFO resignation announced 2025-02-14, concurrent with "
                    "SEC action disclosure. No successor named. Multiple financial news "
                    "outlets reporting accounting irregularities under investigation. "
                    "[Source: Reuters, WSJ, 2025-02-14]",
                    "PRINCIPAL REVIEW: CEO flagged in prior enforcement action at a previous "
                    "employer (2019, FINRA). Disclosure was made at onboarding but "
                    "circumstances have materially changed given current SEC action.",
                ],
                severity="HIGH",
                raw_summary=(
                    "HIGH severity: active SEC enforcement action for financial misstatement, "
                    "CFO departure, adverse media across multiple outlets, principal with "
                    "prior regulatory history. Credit-blocking condition — pipeline must halt."
                ),
            )

        # ── Scenario: Clean pass (Apex / Meridian / Titan — OSINT is clean) ─
        # The KYC-block and FAIL-ratio scenarios have clean OSINT so the
        # blocking agent is isolated to exactly one mechanism per scenario.
        if applicant_ein == "45-6789012":
            return OSINTRecord(
                applicant_id=applicant_ein,
                adverse_media_found=False,
                findings=[],
                severity="NONE",
                raw_summary=(
                    "No adverse media, litigation, sanctions, or enforcement actions found. "
                    "Principals clear on all screened watchlists."
                ),
            )

        if applicant_ein == "23-4567890":
            return OSINTRecord(
                applicant_id=applicant_ein,
                adverse_media_found=False,
                findings=[],
                severity="NONE",
                raw_summary=(
                    "No adverse media, litigation, sanctions, or enforcement actions found. "
                    "Principals clear on all screened watchlists."
                ),
            )

        # ── Default: Apex Industrial Supply LLC (LOW severity litigation) ──
        return OSINTRecord(
            applicant_id=applicant_ein,
            adverse_media_found=True,
            findings=[
                "Civil lawsuit filed 2025-03-14: Pacific Parts LLC v. Apex Industrial Supply LLC. "
                "Allegation: breach of supply contract, claimed damages $1.2M. "
                "Status: discovery phase, no judgment entered. [Source: PACER Case 2:25-cv-04471]"
            ],
            severity="LOW",
            raw_summary=(
                "One LOW severity item: pending commercial litigation. "
                "No sanctions matches. No regulatory enforcement actions. "
                "No adverse media on principals. No criminal proceedings."
            ),
        )


class StubFinancialDataStore(FinancialDataStore):
    """
    [DEV] Replace with your financial data extraction adapter.
    In a COIN-style deployment, this would call your ML extraction
    pipeline that parses audited PDF statements into structured fields.
    Returns scenario-specific fixture data keyed by applicant_ein.
    See SCENARIOS registry above for the four available EINs.
    """

    def query(self, applicant_ein: str) -> FinancialStatements:
        logger.info(f"[STUB] Financial data query for EIN {applicant_ein}")

        # ── Scenario: FAIL ratio (Titan Steel Works Corp, ENERGY) ─────────
        # All four ENERGY thresholds breached simultaneously:
        #   Leverage max 4.0x  → actual ~6.1x (FAIL)
        #   Interest coverage min 2.5x → actual ~1.7x (FAIL)
        #   DSCR min 1.25x → actual ~0.97x (FAIL)
        #   Current ratio min 1.3x → actual ~1.1x (FAIL)
        if applicant_ein == "23-4567890":
            return FinancialStatements(
                applicant_id=applicant_ein,
                years_available=[2022, 2023, 2024],
                revenue={
                    2022: Decimal("95_000_000"),
                    2023: Decimal("88_400_000"),
                    2024: Decimal("79_200_000"),
                },
                ebitda={
                    2022: Decimal("11_200_000"),
                    2023: Decimal("8_900_000"),
                    2024: Decimal("6_500_000"),
                },
                total_debt={
                    2022: Decimal("32_000_000"),
                    2023: Decimal("36_500_000"),
                    2024: Decimal("39_800_000"),
                },
                interest_expense={
                    2022: Decimal("2_880_000"),
                    2023: Decimal("3_285_000"),
                    2024: Decimal("3_782_000"),
                },
                net_operating_income={
                    2022: Decimal("8_100_000"),
                    2023: Decimal("6_200_000"),
                    2024: Decimal("4_400_000"),
                },
                total_debt_service={
                    2022: Decimal("6_500_000"),
                    2023: Decimal("5_900_000"),
                    2024: Decimal("4_540_000"),
                },
                current_assets={
                    2022: Decimal("18_200_000"),
                    2023: Decimal("16_900_000"),
                    2024: Decimal("15_400_000"),
                },
                current_liabilities={
                    2022: Decimal("13_500_000"),
                    2023: Decimal("14_200_000"),
                    2024: Decimal("14_000_000"),
                },
                capital_expenditures={
                    2022: Decimal("5_800_000"),
                    2023: Decimal("6_200_000"),
                    2024: Decimal("5_500_000"),
                },
                operating_cash_flow={
                    2022: Decimal("9_100_000"),
                    2023: Decimal("7_400_000"),
                    2024: Decimal("5_200_000"),
                },
                raw_summary=(
                    "Three years audited financials (2022–2024). "
                    "Revenue declining ~9% YoY. EBITDA compressed from 11.8% to 8.2% margin. "
                    "Debt increasing while earnings shrink. All four ENERGY policy ratio "
                    "thresholds breached in 2024: leverage 6.1x (max 4.0x), "
                    "interest coverage 1.72x (min 2.5x), DSCR 0.97x (min 1.25x), "
                    "current ratio 1.10x (min 1.3x)."
                ),
            )

        # ── Scenarios: KYC-block and OSINT-block use healthy financials ───
        # These scenarios halt before the Quantitative Agent runs, but the
        # data must exist. Healthy financials ensure the block is attributed
        # to the correct agent, not a spurious ratio failure.
        if applicant_ein in ("45-6789012", "78-9012345"):
            return FinancialStatements(
                applicant_id=applicant_ein,
                years_available=[2022, 2023, 2024],
                revenue={
                    2022: Decimal("74_000_000"),
                    2023: Decimal("81_500_000"),
                    2024: Decimal("88_300_000"),
                },
                ebitda={
                    2022: Decimal("13_100_000"),
                    2023: Decimal("14_700_000"),
                    2024: Decimal("15_200_000"),
                },
                total_debt={
                    2022: Decimal("24_000_000"),
                    2023: Decimal("27_000_000"),
                    2024: Decimal("29_500_000"),
                },
                interest_expense={
                    2022: Decimal("1_440_000"),
                    2023: Decimal("1_620_000"),
                    2024: Decimal("1_770_000"),
                },
                net_operating_income={
                    2022: Decimal("10_500_000"),
                    2023: Decimal("12_100_000"),
                    2024: Decimal("12_800_000"),
                },
                total_debt_service={
                    2022: Decimal("6_800_000"),
                    2023: Decimal("7_500_000"),
                    2024: Decimal("8_200_000"),
                },
                current_assets={
                    2022: Decimal("19_500_000"),
                    2023: Decimal("21_800_000"),
                    2024: Decimal("23_400_000"),
                },
                current_liabilities={
                    2022: Decimal("10_200_000"),
                    2023: Decimal("11_100_000"),
                    2024: Decimal("11_800_000"),
                },
                capital_expenditures={
                    2022: Decimal("2_800_000"),
                    2023: Decimal("3_100_000"),
                    2024: Decimal("3_400_000"),
                },
                operating_cash_flow={
                    2022: Decimal("11_800_000"),
                    2023: Decimal("13_200_000"),
                    2024: Decimal("14_100_000"),
                },
                raw_summary=(
                    "Three years audited financials (2022–2024). "
                    "Revenue CAGR ~9.2%. EBITDA margins 17–18%. "
                    "Leverage and coverage ratios comfortably within policy thresholds. "
                    "Note: pipeline halted before Quantitative Agent ran in this scenario."
                ),
            )

        # ── Default: Apex Industrial Supply LLC ───────────────────────────
        return FinancialStatements(
            applicant_id=applicant_ein,
            years_available=[2022, 2023, 2024],
            revenue={
                2022: Decimal("82_500_000"),
                2023: Decimal("91_200_000"),
                2024: Decimal("98_750_000"),
            },
            ebitda={
                2022: Decimal("14_200_000"),
                2023: Decimal("15_600_000"),
                2024: Decimal("16_100_000"),
            },
            total_debt={
                2022: Decimal("28_000_000"),
                2023: Decimal("31_500_000"),
                2024: Decimal("35_000_000"),
            },
            interest_expense={
                2022: Decimal("1_680_000"),
                2023: Decimal("1_890_000"),
                2024: Decimal("2_100_000"),
            },
            net_operating_income={
                2022: Decimal("11_500_000"),
                2023: Decimal("12_800_000"),
                2024: Decimal("13_200_000"),
            },
            total_debt_service={
                2022: Decimal("7_800_000"),
                2023: Decimal("8_700_000"),
                2024: Decimal("10_050_000"),
            },
            current_assets={
                2022: Decimal("22_100_000"),
                2023: Decimal("24_600_000"),
                2024: Decimal("26_300_000"),
            },
            current_liabilities={
                2022: Decimal("11_200_000"),
                2023: Decimal("12_400_000"),
                2024: Decimal("13_100_000"),
            },
            capital_expenditures={
                2022: Decimal("3_200_000"),
                2023: Decimal("3_800_000"),
                2024: Decimal("4_100_000"),
            },
            operating_cash_flow={
                2022: Decimal("13_100_000"),
                2023: Decimal("14_500_000"),
                2024: Decimal("15_200_000"),
            },
            raw_summary=(
                "Three years audited financials (2022–2024). "
                "Revenue CAGR ~9.5%. EBITDA margins 16–17%. "
                "Total debt increasing year-over-year with proposed facility. "
                "Operating cash flow consistently covers debt service."
            ),
        )
