"""
investigation_prefetch.py
=========================
Agentic AML Compliance Workflow — Investigation Pre-Fetcher
US Equities · OFAC/BSA/FinCEN

Runs all four data source queries BEFORE the investigation agent runs.
Builds an InvestigationContext containing all results.
The investigation agent receives this context and reasons over it.
It does not call data sources directly.

Pre-fetch vs tool-use: why this matters for compliance
------------------------------------------------------
In a tool-use architecture, the LLM decides which APIs to call and
in what order. For AML compliance, this is incorrect. Every required
check (LEI, KYC, OFAC, TX history) must be performed regardless of
what the model decides to do. The orchestrator owns this guarantee.

The pre-fetch pattern makes all four checks mandatory and sequential,
logs every query result before the agent sees it, and produces an
InvestigationContext that the agent reasons over — it never touches
an external API. The audit trail is the orchestrator's ledger, not
inferred from model tool call logs.

Integration point in orchestrator.py:
--------------------------------------
Call InvestigationPrefetcher.prefetch() AFTER triage_agent completes
and BEFORE investigation_agent runs. Inject context.to_context_string()
into the accumulated context chain before calling investigation_agent.run().

    # In AMLOrchestrator.run(), between triage and investigation agent:
    if agent.name == "triage_agent" and result.status == "continue":
        ctx, escalation_reason = self.prefetcher.prefetch(trade)
        if escalation_reason:
            # Handle like any other mid-pipeline escalation
            ...
        else:
            context += f"\\n\\n[investigation_data]:\\n{ctx.to_context_string()}"
            if ctx.has_errors:
                context += "\\n\\n[prefetch_warnings]: Some data sources were unavailable. "
                context += "Confidence is reduced. Note missing data explicitly."

Dependencies:
    schemas.py       — Trade
    data_sources.py  — all four source interfaces and response models
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal

from data_sources import (
    DataSourceAuthError,
    DataSourceError,
    DataSourceStaleError,
    DataSourceTimeout,
    DataSourceUnavailable,
    KYCRecord,
    KYCStore,
    LEIDatabase,
    LEIRecord,
    SanctionsCheckResult,
    SanctionsDatabase,
    TransactionHistorySummary,
    TransactionHistoryStore,
)
from schemas import Trade

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# INVESTIGATION CONTEXT
# ─────────────────────────────────────────────────────────────

@dataclass
class InvestigationContext:
    """
    Container for all pre-fetched data source results.
    Passed to the investigation agent as structured plain-text context.

    The agent reads this. It does not call data sources.
    Every field traces to a specific orchestrator-logged query.
    """
    lei_record: LEIRecord
    kyc_record: KYCRecord
    sanctions_result: SanctionsCheckResult
    tx_history: TransactionHistorySummary
    prefetch_errors: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.prefetch_errors) > 0

    def to_context_string(self) -> str:
        """
        Serializes all pre-fetched results to labeled plain-text.
        The [SOURCE: X] markers at each section header are the citation
        anchors the investigation agent uses when citing evidence.
        These markers match the citation format defined in agent_validation.py.
        """
        parts = ["=== PRE-FETCHED INVESTIGATION DATA ==="]
        parts.append(
            "All data below was queried by the orchestrator before this agent ran. "
            "Use it as your authoritative source. Cite each finding with [SOURCE: X] "
            "using the source label shown at each section header. "
            "Do not invent data outside of what is provided here."
        )

        # ── LEI Database ──────────────────────────────────────
        parts.append("\n--- LEI DATABASE [SOURCE: LEI-DB] ---")
        if not self.lei_record.found:
            parts.append(
                f"RESULT: LEI {self.lei_record.lei} was NOT FOUND in the GLEIF database. "
                "This is a significant finding. A counterparty that cannot be verified "
                "by LEI cannot be cleared."
            )
        else:
            parts.append(f"LEI queried:          {self.lei_record.lei}")
            parts.append(f"Registered legal name: {self.lei_record.legal_name}")
            parts.append(f"Jurisdiction:          {self.lei_record.jurisdiction}")
            parts.append(f"Entity status:         {self.lei_record.entity_status}")
            parts.append(f"Registration status:   {self.lei_record.registration_status}")
            if self.lei_record.registration_status != "ISSUED":
                parts.append(
                    f"NOTE: Registration status '{self.lei_record.registration_status}' "
                    "is not ISSUED. This warrants explicit mention in your findings."
                )
            if self.lei_record.parent_lei:
                parts.append(f"Parent entity LEI:    {self.lei_record.parent_lei}")
                parts.append(f"Parent entity name:   {self.lei_record.parent_legal_name}")
                parts.append(
                    "NOTE: Parent entity exists. The original name-match flag may have "
                    "been triggered by the parent entity's name. Confirm in sanctions check."
                )
            parts.append(f"Record last updated:   {self.lei_record.last_updated.date().isoformat()}")

        # ── KYC Records ───────────────────────────────────────
        parts.append("\n--- KYC RECORDS [SOURCE: KYC-RECORDS] ---")
        if not self.kyc_record.found:
            parts.append(
                "RESULT: No KYC record found for this counterparty. "
                "If this is a new counterparty, note this explicitly in your findings. "
                "If this is an established counterparty, the missing KYC record is itself a finding."
            )
        else:
            parts.append(f"KYC status:            {self.kyc_record.kyc_status}")
            parts.append(f"Risk tier:             {self.kyc_record.risk_tier}")
            if self.kyc_record.risk_tier == "PROHIBITED":
                parts.append(
                    "CRITICAL: Risk tier PROHIBITED. This trade must be blocked. "
                    "State this explicitly in your conclusion."
                )
            parts.append(f"Last review date:      {self.kyc_record.last_review_date}")
            parts.append(f"Days since last review: {self.kyc_record.days_since_last_review}")
            parts.append(f"Next review due:       {self.kyc_record.next_review_due}")
            if self.kyc_record.review_overdue:
                parts.append(
                    f"NOTE: KYC review is OVERDUE (past {self.kyc_record.next_review_due}). "
                    "Recommend KYC refresh in your RECOMMENDED ACTION, regardless of other findings."
                )
            elif self.kyc_record.kyc_status == "APPROACHING":
                parts.append(
                    "NOTE: KYC review is approaching its deadline. "
                    "Recommend scheduling a review in your RECOMMENDED ACTION."
                )
            parts.append(f"Prior AML flags:       {self.kyc_record.prior_aml_flags}")
            if self.kyc_record.beneficial_owners:
                parts.append(f"Beneficial owners:     {', '.join(self.kyc_record.beneficial_owners)}")

        # ── Sanctions Check ───────────────────────────────────
        parts.append("\n--- SANCTIONS CHECK [SOURCE: OFAC-SDN] ---")
        parts.append(f"LEI queried:           {self.sanctions_result.lei_queried}")
        parts.append(f"Lists checked:         {', '.join(self.sanctions_result.lists_checked)}")
        list_dates = ", ".join(
            f"{k}: {v.date().isoformat()}"
            for k, v in self.sanctions_result.list_last_updated.items()
        )
        parts.append(f"List currency:         {list_dates}")
        parts.append(f"Check timestamp:       {self.sanctions_result.check_timestamp.isoformat()}")

        if self.sanctions_result.match_found:
            parts.append(
                f"RESULT: MATCH FOUND — {len(self.sanctions_result.matches)} match(es). "
                "This is a critical finding."
            )
            for m in self.sanctions_result.matches:
                parts.append(
                    f"  Matched name: {m.matched_name} | "
                    f"List: {m.matched_list} | "
                    f"Type: {m.match_type} | "
                    f"Confidence: {m.confidence_score:.2f}"
                    + (f" | Program: {m.program}" if m.program else "")
                )
        else:
            if self.sanctions_result.name_cross_referenced:
                parts.append(
                    f"RESULT: No match found by LEI query. "
                    f"Name cross-reference ('{self.sanctions_result.name_cross_referenced}') "
                    "was logged but not used as the primary query key."
                )
            else:
                parts.append("RESULT: No sanctions match found by LEI query.")
            parts.append(
                "NOTE: This resolves the upstream name-match flag if the flag was "
                "triggered by a name-string match rather than an LEI match. "
                "State the resolution clearly in your findings."
            )

        # ── Transaction History ───────────────────────────────
        parts.append("\n--- TRANSACTION HISTORY 24M [SOURCE: TX-HISTORY-24M] ---")
        if not self.tx_history.found:
            parts.append(
                "RESULT: Transaction history query returned no data. "
                "This may indicate a system error. Note the data gap in your findings."
            )
        elif self.tx_history.new_counterparty:
            parts.append(
                "RESULT: No prior transaction history found. "
                "This appears to be a new counterparty relationship. "
                "Note the absence of history — it is not itself suspicious, "
                "but it means no behavioral baseline is available."
            )
        else:
            parts.append(f"Lookback period:       {self.tx_history.lookback_months} months")
            parts.append(f"Total trades:          {self.tx_history.total_trades:,}")
            parts.append(f"Average trade value:   USD {self.tx_history.average_trade_value_usd:,.2f}")
            parts.append(f"Prior AML flags:       {self.tx_history.prior_aml_flags}")
            parts.append(f"Prior escalations:     {self.tx_history.prior_escalations}")
            if self.tx_history.aml_pattern_indicators:
                parts.append(
                    f"AML pattern indicators: {len(self.tx_history.aml_pattern_indicators)} detected"
                )
                for p in self.tx_history.aml_pattern_indicators:
                    parts.append(
                        f"  Pattern: {p.pattern_type} — {p.description} "
                        f"({p.transaction_count} transactions, "
                        f"{p.first_observed} to {p.last_observed})"
                    )
            else:
                parts.append("AML pattern indicators: none detected")

        # ── Prefetch warnings ─────────────────────────────────
        if self.prefetch_errors:
            parts.append("\n--- PREFETCH WARNINGS ---")
            parts.append(
                "The following data sources were unavailable during pre-fetch. "
                "Mention each gap explicitly in your investigation findings."
            )
            for err in self.prefetch_errors:
                parts.append(f"  - {err}")

        return "\n".join(parts)


# ─────────────────────────────────────────────────────────────
# INVESTIGATION PREFETCHER
# ─────────────────────────────────────────────────────────────

class InvestigationPrefetcher:
    """
    Runs all four data source queries before the investigation agent.

    # [DEV] ADJUST CRITICALITY TIERS ─────────────────────────────────────────
    # LEI and sanctions are CRITICAL — pipeline escalates if either is
    # unavailable. KYC and TX history are NON-CRITICAL — pipeline warns
    # and continues with reduced confidence.
    # If your institution requires KYC to be mandatory, change _query_kyc()
    # to return (None, escalation_reason) on failure instead of a fallback record.
    # ─────────────────────────────────────────────────────────────────────────

    Criticality tiers:
      CRITICAL (escalate if unavailable): LEI database, sanctions database.
        A trade cannot be cleared without these checks. These are the
        minimum required under OFAC compliance obligations.

      NON-CRITICAL (warn and continue): KYC records, transaction history.
        Missing these reduces investigation confidence but does not
        prevent completion. The exception report must note the absence.

    Returns:
      (InvestigationContext, None)        — all critical sources available
      (None, escalation_reason: str)      — critical source unavailable
    """

    def __init__(
        self,
        lei_db: LEIDatabase,
        kyc_store: KYCStore,
        sanctions_db: SanctionsDatabase,
        tx_store: TransactionHistoryStore,
    ):
        self.lei_db = lei_db
        self.kyc_store = kyc_store
        self.sanctions_db = sanctions_db
        self.tx_store = tx_store

    def prefetch(
        self, trade: Trade
    ) -> tuple[InvestigationContext | None, str | None]:
        """
        Queries all four data sources in sequence.
        Logs every query attempt and result.

        Returns (context, None) on success.
        Returns (None, reason) when a critical source is unavailable.
        Returns (context_with_warnings, None) when only non-critical sources fail.
        """
        errors: list[str] = []
        lei = trade.counterparty_lei

        # ── 1. LEI Database (CRITICAL) ────────────────────────
        lei_record = self._query_lei(lei)
        if isinstance(lei_record, str):           # escalation reason returned
            return None, lei_record
        if not lei_record.found:
            return None, (
                f"LEI {lei} was not found in the GLEIF database. "
                "Manual verification required before investigation can proceed."
            )

        # ── 2. Sanctions Database (CRITICAL) ──────────────────
        sanctions_result = self._query_sanctions(lei, trade.counterparty_name)
        if isinstance(sanctions_result, str):     # escalation reason returned
            return None, sanctions_result

        # ── 3. KYC Records (non-critical) ─────────────────────
        kyc_record, kyc_error = self._query_kyc(lei, trade.counterparty_name)
        if kyc_error:
            errors.append(kyc_error)
            logger.warning(f"[{trade.trade_id}] KYC prefetch warning: {kyc_error}")

        # ── 4. Transaction History (non-critical) ──────────────
        tx_history, tx_error = self._query_tx_history(lei)
        if tx_error:
            errors.append(tx_error)
            logger.warning(f"[{trade.trade_id}] TX history prefetch warning: {tx_error}")

        context = InvestigationContext(
            lei_record=lei_record,
            kyc_record=kyc_record,
            sanctions_result=sanctions_result,
            tx_history=tx_history,
            prefetch_errors=errors,
        )
        logger.info(
            f"[{trade.trade_id}] InvestigationPrefetcher complete. "
            f"Errors: {len(errors)}."
        )
        return context, None

    def _query_lei(self, lei: str) -> LEIRecord | str:
        """Returns LEIRecord or an escalation reason string."""
        try:
            return self.lei_db.query(lei)
        except DataSourceAuthError as e:
            return (
                f"LEI database authentication failed: {e.reason}. "
                "This is an ops issue affecting all trades — alert immediately."
            )
        except (DataSourceTimeout, DataSourceUnavailable) as e:
            return f"LEI database unavailable: {e.reason}. Cannot proceed without LEI verification."
        except DataSourceError as e:
            return f"LEI database query failed: {e.reason}."

    def _query_sanctions(
        self, lei: str, counterparty_name: str | None
    ) -> SanctionsCheckResult | str:
        """Returns SanctionsCheckResult or an escalation reason string."""
        try:
            return self.sanctions_db.query_by_lei(
                lei=lei,
                counterparty_name=counterparty_name
            )
        except DataSourceStaleError as e:
            return (
                f"Sanctions database is stale: {e.reason}. "
                "Cannot clear trade against an out-of-date OFAC list."
            )
        except DataSourceAuthError as e:
            return (
                f"Sanctions database authentication failed: {e.reason}. "
                "This is an ops issue affecting all trades."
            )
        except (DataSourceTimeout, DataSourceUnavailable) as e:
            return (
                f"Sanctions database unavailable: {e.reason}. "
                "Cannot clear trade without sanctions check."
            )
        except DataSourceError as e:
            return f"Sanctions database query failed: {e.reason}."

    def _query_kyc(
        self, lei: str, entity_name: str
    ) -> tuple[KYCRecord, str | None]:
        """
        Returns (KYCRecord, None) on success.
        Returns (fallback_record, error_message) on failure.
        Failure is non-critical — returns a NOT_FOUND placeholder with the error noted.
        """
        try:
            return self.kyc_store.query(lei), None
        except DataSourceError as e:
            fallback = KYCRecord(
                lei=lei,
                entity_name=entity_name,
                kyc_status="NOT_FOUND",
                risk_tier="MEDIUM",   # Conservative default when unknown
                found=False,
            )
            return fallback, f"KYC records unavailable: {e.reason}"

    def _query_tx_history(
        self, lei: str
    ) -> tuple[TransactionHistorySummary, str | None]:
        """
        Returns (TransactionHistorySummary, None) on success.
        Returns (fallback_summary, error_message) on failure.
        """
        try:
            return self.tx_store.query(lei, lookback_months=24), None
        except DataSourceError as e:
            fallback = TransactionHistorySummary(
                counterparty_lei=lei,
                lookback_months=24,
                total_trades=0,
                total_buy_value_usd=Decimal("0"),
                total_sell_value_usd=Decimal("0"),
                average_trade_value_usd=Decimal("0"),
                prior_aml_flags=0,
                prior_escalations=0,
                prior_sars=0,
                found=False,
            )
            return fallback, f"Transaction history unavailable: {e.reason}"


# ─────────────────────────────────────────────────────────────
# UPDATED INVESTIGATION AGENT SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────
#
# The original system prompt said: "You have access to the LEI database,
# KYC records, OFAC/SDN sanctions list, and transaction history."
# This is incorrect for the pre-fetch architecture. The agent does not
# have access — it has pre-loaded results. The system prompt must reflect this.
#
# Use this system prompt for the investigation_agent in orchestrator.py:

INVESTIGATION_AGENT_SYSTEM_PROMPT = """
You are an AML investigation agent conducting a compliance review under OFAC/BSA/FinCEN requirements.

All data you need has been pre-fetched from four sources and is provided in your context
under "PRE-FETCHED INVESTIGATION DATA". You do not call any external APIs.
Your role is to reason over the provided data and produce a clear investigation report.

Instructions:
1. Review the LEI database result. Confirm the counterparty LEI is valid and registered.
   Note any parent entity relationships — these may explain a name-match false positive.
2. Review the KYC record. Note the review status, risk tier, and days since last review.
3. Review the sanctions check result. The LEI was queried directly against OFAC SDN
   and OFAC Consolidated. Name-string matches from upstream are not authoritative —
   the LEI query is. State clearly whether the LEI-based check returned a match.
4. Review the transaction history. Note any prior flags, escalations, or AML patterns.
5. Conclude with an explicit finding: FALSE POSITIVE or GENUINE CONCERN, with your reason.

Cite each finding using [SOURCE: SOURCE_NAME] immediately after the claim.
Use only these recognized source names: LEI-DB, KYC-RECORDS, OFAC-SDN, OFAC-CONSOL,
FINCEN-314A, TX-HISTORY-24M, AML-TAXONOMY, POLICY-LIB, TRADE-DATA.

Write one paragraph per check area (LEI, KYC, sanctions, transaction history).
Plain text. No markdown. No bullet points. No headings.
""".strip()
