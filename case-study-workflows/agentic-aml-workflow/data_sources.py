"""
data_sources.py
===============
Agentic AML Compliance Workflow — External Data Source Contracts
US Equities · OFAC/BSA/FinCEN

Defines the interface contracts, Pydantic response models, and error
hierarchy for the four data sources queried during AML investigation.

CRITICAL DESIGN NOTE:
  These interfaces are called by InvestigationPrefetcher (see
  investigation_prefetch.py), NOT by the investigation agent directly.
  The investigation agent receives a pre-built InvestigationContext
  object containing all query results. It reasons over pre-loaded data.
  It does not call any of these interfaces.

  This distinction is architectural, not stylistic. Every data source
  query must be logged, sequenced, and validated by the orchestrator
  before any agent sees the results. A model that decides whether to
  check OFAC is not an AML system.

Dependencies:
    pip install pydantic>=2.0
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────
# ERROR HIERARCHY
# ─────────────────────────────────────────────────────────────

class DataSourceError(Exception):
    """
    Base class for all data source query failures.
    Always carries the source name so the orchestrator can log
    which source failed without catching generic exceptions.
    """
    def __init__(self, source: str, reason: str):
        self.source = source
        self.reason = reason
        super().__init__(f"[{source}] {reason}")


class DataSourceTimeout(DataSourceError):
    """
    Query did not return within the configured timeout window.

    ORCHESTRATOR BEHAVIOR:
      LEI or sanctions timeout → escalate immediately.
      KYC or TX history timeout → log warning, continue with reduced confidence.
    """


class DataSourceUnavailable(DataSourceError):
    """
    Data source is unreachable (connection refused, DNS failure, circuit open).

    ORCHESTRATOR BEHAVIOR: same as DataSourceTimeout by source criticality.
    Also alerts operations — unavailability persists across trades.
    """


class DataSourceAuthError(DataSourceError):
    """
    Authentication to the data source failed (expired credential, wrong key).

    ORCHESTRATOR BEHAVIOR: escalate AND alert operations immediately.
    This failure will affect all trades, not just the current one.
    """


class DataSourceStaleError(DataSourceError):
    """
    The data source returned data, but its list/record date exceeds the
    acceptable staleness threshold for compliance use.

    ORCHESTRATOR BEHAVIOR: escalate. Do not use stale sanctions data.
    """


# ─────────────────────────────────────────────────────────────
# 1. LEI DATABASE
# ─────────────────────────────────────────────────────────────
#
# Real-world implementation target:
#   GLEIF (Global LEI Foundation) public REST API
#   Endpoint: GET https://api.gleif.org/api/v1/lei-records/{lei}
#   Rate limit: ~60 req/min unauthenticated, higher with API key
#   Response time: typically 200–500ms
#   Auth: API key in X-Api-Key header (optional for low volume)
#
# Why LEI, not name:
#   The counterparty's legal name may be abbreviated, transliterated,
#   or share substrings with sanctioned entities. LEI is a globally
#   unique 20-character identifier issued by a GLEIF-accredited LOU.
#   Name-based queries produce false positives. LEI queries do not.
#   The investigation agent MUST use counterparty_lei, never counterparty_name.

class LEIRecord(BaseModel):
    """
    Response schema for a single LEI query result.
    Maps to the GLEIF API response structure.
    """
    lei: str = Field(description="The 20-character LEI that was queried.")
    legal_name: str = Field(description="Registered legal name of the entity.")
    jurisdiction: str = Field(
        description="Jurisdiction of incorporation. ISO 3166-1 alpha-2. "
                    "Used for jurisdiction risk assessment."
    )
    entity_status: Literal["ACTIVE", "INACTIVE"] = Field(
        description="Whether the entity is currently active. "
                    "INACTIVE entities warrant heightened scrutiny."
    )
    registration_status: Literal[
        "ISSUED",
        "LAPSED",           # LEI not renewed — entity may still exist
        "RETIRED",          # Entity no longer exists (merged, dissolved)
        "DUPLICATE",        # Duplicate LEI — points to a canonical LEI
        "ANNULLED",         # Issued in error
        "CANCELLED",
        "TRANSFERRED",
        "PENDING_TRANSFER",
        "PENDING_ARCHIVAL",
    ] = Field(
        description="GLEIF registration status. ISSUED = valid and current. "
                    "Any other status warrants escalation."
    )
    parent_lei: str | None = Field(
        default=None,
        description="LEI of the direct parent entity, if any. "
                    "Critical for sanctions screening — a clean counterparty LEI "
                    "does not guarantee a clean parent entity."
    )
    parent_legal_name: str | None = Field(
        default=None,
        description="Legal name of the parent entity. "
                    "A SANCTIONS_NAME_MATCH on the counterparty may be a false "
                    "positive from a parent entity with a similar name."
    )
    last_updated: datetime = Field(
        description="Timestamp of the most recent GLEIF record update."
    )
    found: bool = Field(
        default=True,
        description="False when the LEI is not in the GLEIF database. "
                    "A valid LEI that GLEIF does not recognize is itself an AML signal. "
                    "Route directly to human review — do not proceed to investigation agent."
    )


class LEIDatabase:
    """
    Interface contract for LEI database queries.

    Concrete implementations:
      - GLEIFLEIDatabase: calls GLEIF REST API (production)
      - StubLEIDatabase: returns fixture data (development/test)

    Error handling:
      - DataSourceTimeout: query exceeded timeout window
      - DataSourceUnavailable: GLEIF API unreachable
      - DataSourceAuthError: API key invalid or missing

    Note: GLEIF API has no authentication requirement for low-volume
    use, but production deployments should use an API key for higher
    rate limits and SLA guarantees.
    """

    def query(self, lei: str) -> LEIRecord:
        """
        Query GLEIF for the entity registered under this LEI.
        lei: the 20-character alphanumeric LEI (from Trade.counterparty_lei).
        Returns LEIRecord with found=False if LEI is not in database.
        Raises DataSourceError subclass on connectivity or auth failure.
        """
        raise NotImplementedError


class StubLEIDatabase(LEIDatabase):
    """
    Development stub. Returns a clean, active record for any LEI.
    Override _fixtures to return specific records for test cases.

    Usage:
        db = StubLEIDatabase()
        db._fixtures["7H6GLXDRUGQFU57RNE97"] = LEIRecord(
            lei="7H6GLXDRUGQFU57RNE97",
            legal_name="Acme Capital Partners Ltd",
            ...
        )
    """

    def __init__(self):
        self._fixtures: dict[str, LEIRecord] = {}

    def query(self, lei: str) -> LEIRecord:
        if lei in self._fixtures:
            return self._fixtures[lei]
        return LEIRecord(
            lei=lei,
            legal_name=f"[STUB] Entity for LEI {lei}",
            jurisdiction="US",
            entity_status="ACTIVE",
            registration_status="ISSUED",
            parent_lei=None,
            parent_legal_name=None,
            last_updated=datetime.now(timezone.utc),
            found=True,
        )


# ─────────────────────────────────────────────────────────────
# 2. KYC RECORDS
# ─────────────────────────────────────────────────────────────
#
# Real-world implementation target:
#   Your institution's internal KYC records management system.
#   No public API — you build an adapter to your internal store.
#   Common underlying systems: Fenergo, Broadridge, custom PostgreSQL.
#
# Review cycle thresholds (reference defaults — institution defines actual values):
# [DEV] REVIEW CYCLE THRESHOLDS — SET BY YOUR COMPLIANCE POLICY ──────────────
# The values below are reference defaults based on FinCEN CDD Rule guidance.
# Your institution's AML compliance program defines the actual thresholds.
# Update these comments AND the matching values in aml_taxonomy.json under
# "policy_library" → "kyc_review_cycles" to keep them in sync.
# ─────────────────────────────────────────────────────────────────────────────
#   LOW/MEDIUM risk:  18-month review cycle
#   HIGH risk:        12-month review cycle
#   ENHANCED EDD:      6-month review cycle
#
# The investigation agent uses days_since_last_review and
# review_overdue to flag counterparties approaching or exceeding
# their review cycle, as seen in the Goldman case study workflow.

class KYCRecord(BaseModel):
    """
    Response schema for a KYC record query.
    Represents the current KYC status of a counterparty in your
    institution's internal KYC management system.
    """
    lei: str
    entity_name: str = Field(description="Entity name as recorded in KYC system.")
    kyc_status: Literal[
        "CURRENT",      # Within review cycle threshold
        "APPROACHING",  # Within 60 days of review cycle deadline
        "STALE",        # Exceeds review cycle threshold — requires refresh
        "ENHANCED",     # Under enhanced due diligence program
        "PENDING",      # KYC review currently in progress
        "NOT_FOUND",    # No KYC record exists for this counterparty
    ]
    risk_tier: Literal["LOW", "MEDIUM", "HIGH", "PROHIBITED"] = Field(
        description="Risk classification assigned at last KYC review. "
                    "PROHIBITED = this counterparty must not be traded with."
    )
    last_review_date: date | None = Field(
        default=None,
        description="Date of last completed KYC review."
    )
    next_review_due: date | None = Field(
        default=None,
        description="Scheduled date for next KYC review, based on risk tier cycle."
    )
    days_since_last_review: int | None = Field(
        default=None,
        description="Calendar days since last completed review. "
                    "Used by the investigation agent to flag staleness."
    )
    review_overdue: bool = Field(
        default=False,
        description="True if current date is past the next_review_due date."
    )
    beneficial_owners: list[str] = Field(
        default_factory=list,
        description="List of beneficial owner legal names as recorded in KYC. "
                    "Used for cross-reference with sanctions screening."
    )
    prior_aml_flags: int = Field(
        default=0,
        description="Count of prior AML flags recorded in the KYC file "
                    "for this counterparty. Contextualizes the current flag."
    )
    found: bool = Field(
        default=True,
        description="False when no KYC record exists. Not an error — "
                    "new counterparties may not yet be onboarded."
    )


class KYCStore:
    """
    Interface contract for internal KYC records queries.

    # [DEV] IMPLEMENT YourKYCAdapter ─────────────────────────────────────────
    # Subclass this and implement query() to connect to your KYC system.
    # See the adapter pattern in config.py for a complete skeleton.
    # When ready, set KYCSourceConfig.use_stub = False.
    # ─────────────────────────────────────────────────────────────────────────

    Concrete implementations:
      - YourKYCSystemAdapter: adapts to your internal KYC system
      - StubKYCStore: returns fixture data (development/test)

    Error handling:
      - DataSourceTimeout: KYC system did not respond in time
      - DataSourceUnavailable: KYC system unreachable
      - DataSourceAuthError: service account credential invalid
    """

    def query(self, lei: str) -> KYCRecord:
        raise NotImplementedError


class StubKYCStore(KYCStore):
    """Development stub. Returns a current, low-risk record for any LEI."""

    def __init__(self):
        self._fixtures: dict[str, KYCRecord] = {}

    def query(self, lei: str) -> KYCRecord:
        if lei in self._fixtures:
            return self._fixtures[lei]
        return KYCRecord(
            lei=lei,
            entity_name=f"[STUB] Entity for LEI {lei}",
            kyc_status="CURRENT",
            risk_tier="LOW",
            last_review_date=date(2024, 6, 1),
            next_review_due=date(2025, 12, 1),
            days_since_last_review=420,
            review_overdue=False,
            beneficial_owners=[],
            prior_aml_flags=0,
            found=True,
        )


# ─────────────────────────────────────────────────────────────
# 3. SANCTIONS DATABASE
# ─────────────────────────────────────────────────────────────
#
# Real-world implementation targets (US-centric):
#   OFAC SDN:           https://ofac.treasury.gov/specially-designated-nationals-list
#   OFAC Consolidated:  https://ofac.treasury.gov/consolidated-sanctions-list
#   FinCEN 314(a):      FinCEN 314(a) program — restricted access, institution-specific
#
# OFAC provides a downloadable XML/CSV list and a REST API:
#   GET https://api.ofac.treas.gov/v1/screening/entity?id={LEI}
#   (As of 2025 — verify current endpoint in OFAC developer documentation)
#
# Query by LEI, not by name:
#   The upstream screening system already ran a name-match query and
#   generated the SANCTIONS_NAME_MATCH flag. This pipeline's job is to
#   resolve the ambiguity using the LEI — a globally unique identifier
#   that the upstream name-match algorithm could not use.
#   Querying by name again would reproduce the same false-positive result.
#
# Staleness threshold:
#   OFAC updates the SDN list multiple times per week. For compliance
#   purposes, a list older than 24 hours is considered stale for
#   sanctions screening. Your institution defines the actual threshold.

class SanctionsMatch(BaseModel):
    """A single match result within a sanctions check."""
    matched_name: str = Field(description="The name that matched on the list.")
    matched_list: Literal["OFAC_SDN", "OFAC_CONSOLIDATED", "FINCEN_314A"]
    match_type: Literal[
        "EXACT",    # LEI matches exactly to a listed entity's LEI
        "PARTIAL",  # Partial name match (should not occur in LEI queries — flag if seen)
        "ALIAS",    # Matched an alias or alternate name on the list
    ]
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Match confidence. EXACT = 1.0. "
                    "Any score below 1.0 on a LEI query is unusual and should be noted."
    )
    program: str = Field(
        default="",
        description="OFAC sanctions program name (e.g. 'IRAN', 'RUSSIA', 'SDGT'). "
                    "Informs the regulatory assessment section of the exception report."
    )


class SanctionsCheckResult(BaseModel):
    """
    Result of checking a counterparty against OFAC SDN, OFAC Consolidated,
    and FinCEN 314(a) sanctions lists.
    """
    lei_queried: str = Field(
        description="The LEI used as the primary query key. "
                    "The investigation agent must confirm this matches the trade's counterparty_lei."
    )
    name_cross_referenced: str | None = Field(
        default=None,
        description="Counterparty name provided for cross-reference only. "
                    "Not used as the primary query key."
    )
    match_found: bool
    matches: list[SanctionsMatch] = Field(default_factory=list)
    lists_checked: list[str] = Field(
        description="Which lists were included in this check. "
                    "Must include at minimum OFAC_SDN for US equities compliance."
    )
    list_last_updated: dict[str, datetime] = Field(
        description="Per-list timestamp of the most recent update. "
                    "A stale list timestamp is itself a compliance finding."
    )
    check_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this check was performed. Written to audit log."
    )


class SanctionsDatabase:
    """
    Interface contract for OFAC SDN, OFAC Consolidated, and FinCEN 314(a) queries.

    Concrete implementations:
      - OFACRestAPIDatabase: calls OFAC REST API (production)
      - LocalListSanctionsDatabase: checks against a locally cached list (production fallback)
      - StubSanctionsDatabase: returns fixture data (development/test)

    Critical error handling:
      DataSourceTimeout, DataSourceUnavailable, DataSourceStaleError
      → always escalate immediately. Do not clear a trade without a sanctions check.
    """

    def query_by_lei(
        self,
        lei: str,
        counterparty_name: str | None = None,
    ) -> SanctionsCheckResult:
        """
        Queries OFAC SDN and related lists using the LEI as the primary key.
        counterparty_name is optional and used for cross-reference logging only.
        Raises DataSourceError subclass on any failure.
        """
        raise NotImplementedError


class StubSanctionsDatabase(SanctionsDatabase):
    """Development stub. Returns a clean result (no match) for any LEI."""

    def __init__(self):
        self._fixtures: dict[str, SanctionsCheckResult] = {}

    def query_by_lei(
        self,
        lei: str,
        counterparty_name: str | None = None,
    ) -> SanctionsCheckResult:
        if lei in self._fixtures:
            return self._fixtures[lei]
        return SanctionsCheckResult(
            lei_queried=lei,
            name_cross_referenced=counterparty_name,
            match_found=False,
            matches=[],
            lists_checked=["OFAC_SDN", "OFAC_CONSOLIDATED"],
            list_last_updated={
                "OFAC_SDN": datetime.now(timezone.utc),
                "OFAC_CONSOLIDATED": datetime.now(timezone.utc),
            },
        )


# ─────────────────────────────────────────────────────────────
# 4. TRANSACTION HISTORY
# ─────────────────────────────────────────────────────────────
#
# Real-world implementation target:
#   Your institution's internal trade history / transaction monitoring system.
#   No public API — adapter to your internal store.
#   Common underlying systems: trade surveillance platforms, PostgreSQL, Kafka.
#
# Lookback period: 24 months is standard for BSA/AML typology analysis.
#   Your compliance policy governs the actual lookback period.
#
# AML typologies detected (BSA-aligned):
#   STRUCTURING: trades structured to avoid BSA Currency Transaction Report
#     threshold ($10,000 USD equivalent or institution-defined equivalent)
#   LAYERING: rapid buy/sell with same or related counterparty
#   ROUND_TRIPPING: funds return to originator through intermediaries
#   UNUSUAL_VOLUME: single trade anomalous vs. 24M history (z-score threshold)
#   JURISDICTION_HOP: cross-border pattern inconsistent with stated purpose
#
# new_counterparty flag:
#   A counterparty with no history is NOT an error. It may be a legitimate
#   new client relationship. The investigation agent should note this
#   explicitly in the investigation findings.

class AMLPatternIndicator(BaseModel):
    """A detected AML typology pattern in the counterparty's transaction history."""
    pattern_type: Literal[
        "STRUCTURING",
        "LAYERING",
        "ROUND_TRIPPING",
        "UNUSUAL_VOLUME",
        "JURISDICTION_HOP",
    ]
    description: str = Field(
        description="Human-readable description of the detected pattern. "
                    "Written verbatim into the exception report if this field is populated."
    )
    transaction_count: int = Field(
        description="Number of transactions contributing to this pattern."
    )
    first_observed: date
    last_observed: date
    pattern_value_usd: Decimal | None = Field(
        default=None,
        description="Aggregate USD value of transactions in this pattern, if calculable."
    )


class TransactionHistorySummary(BaseModel):
    """
    24-month transaction history summary for a counterparty.
    Used by the investigation agent to assess whether the current trade
    is consistent with the counterparty's historical behavior.
    """
    counterparty_lei: str
    lookback_months: int = 24
    total_trades: int
    total_buy_value_usd: Decimal
    total_sell_value_usd: Decimal
    average_trade_value_usd: Decimal
    prior_aml_flags: int = Field(
        description="Count of AML flags raised for this counterparty in the lookback period."
    )
    prior_escalations: int = Field(
        description="Count of flags that were escalated to senior review."
    )
    prior_sars: int = Field(
        default=0,
        description="Count of prior SARs filed involving this counterparty, "
                    "if accessible to this system. "
                    "Note: SAR existence is itself a confidential record — "
                    "access must comply with BSA confidentiality requirements."
    )
    aml_pattern_indicators: list[AMLPatternIndicator] = Field(
        default_factory=list,
        description="Detected typology patterns. Empty list = no patterns detected."
    )
    new_counterparty: bool = Field(
        default=False,
        description="True when no prior transaction history exists. "
                    "Not an error — set found=True when this is the case."
    )
    found: bool = Field(
        default=True,
        description="False only on query error. new_counterparty handles the "
                    "'no history' case separately."
    )


class TransactionHistoryStore:
    """
    Interface contract for the internal transaction history store.

    # [DEV] IMPLEMENT YourTXHistoryAdapter ───────────────────────────────────
    # Subclass this and implement query() to connect to your transaction history
    # or trade surveillance system (e.g. Actimize, NICE, custom Kafka/PostgreSQL).
    # See the adapter pattern in config.py for a complete skeleton.
    # When ready, set TXHistorySourceConfig.use_stub = False.
    # ─────────────────────────────────────────────────────────────────────────

    Concrete implementations:
      - YourTradeSurveillanceAdapter: adapts to your internal system
      - StubTransactionHistoryStore: returns fixture data (development/test)

    Error handling:
      DataSourceTimeout or DataSourceUnavailable on TX history
      → log warning and proceed with reduced confidence.
      Investigation can complete without TX history, but the
      exception report must note the missing data.
    """

    def query(self, lei: str, lookback_months: int = 24) -> TransactionHistorySummary:
        raise NotImplementedError


class StubTransactionHistoryStore(TransactionHistoryStore):
    """Development stub. Returns a clean 24-month history for any LEI."""

    def __init__(self):
        self._fixtures: dict[str, TransactionHistorySummary] = {}

    def query(self, lei: str, lookback_months: int = 24) -> TransactionHistorySummary:
        if lei in self._fixtures:
            return self._fixtures[lei]
        return TransactionHistorySummary(
            counterparty_lei=lei,
            lookback_months=lookback_months,
            total_trades=47,
            total_buy_value_usd=Decimal("142_000_000"),
            total_sell_value_usd=Decimal("139_500_000"),
            average_trade_value_usd=Decimal("2_990_000"),
            prior_aml_flags=0,
            prior_escalations=0,
            prior_sars=0,
            aml_pattern_indicators=[],
            new_counterparty=False,
            found=True,
        )
