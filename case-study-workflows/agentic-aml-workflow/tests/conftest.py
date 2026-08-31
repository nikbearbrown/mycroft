"""
tests/conftest.py
=================
Agentic AML Compliance Workflow — Test Fixtures
US Equities · OFAC/BSA/FinCEN

Shared fixtures for all test files. Import via pytest's conftest mechanism.

Each fixture covers a distinct scenario:
  1. sanctions_name_match_false_positive  — Goldman scenario: name match, LEI clean
  2. sanctions_genuine_concern            — LEI matches OFAC SDN directly
  3. auto_escalate_trade                  — confidence score above 0.85 threshold
  4. unusual_volume_trade                 — volume anomaly, no prior flags
  5. malformed_trade_event                — missing required fields (schema rejection)
  6. mock_approved_decision               — human review approves
  7. mock_blocked_decision                — human review blocks

Usage:
    # In any test file:
    from tests.conftest import sanctions_name_match_false_positive

    # Or with pytest fixtures:
    def test_something(sanctions_name_match_false_positive):
        trade = Trade.from_event(sanctions_name_match_false_positive)
        ...

Dependencies:
    pip install pytest>=8.0 pydantic>=2.0
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

import pytest

# ─────────────────────────────────────────────────────────────
# RAW EVENT DICTS
# These represent the raw payload from your upstream trade system.
# Trade.from_event() validates and parses them.
# ─────────────────────────────────────────────────────────────

# Scenario 1: SANCTIONS_NAME_MATCH false positive
# The Goldman case study scenario. Counterparty name partially matches
# a parent entity on OFAC SDN. LEI query will return clean.
SANCTIONS_NAME_MATCH_EVENT = {
    "trade_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "security_isin": "US0378331005",
    "security_cusip": "037833100",
    "security_description": "Apple Inc. Common Stock",
    "counterparty_name": "Acme Capital Partners Ltd",
    "counterparty_lei": "7H6GLXDRUGQFU57RNE97",
    "counterparty_country": "GB",
    "trade_side": "BUY",
    "quantity": 50000,
    "execution_price": "182.45",
    "trade_value": "9122500.00",
    "currency": "USD",
    "settlement_date": "2025-06-17",
    "execution_timestamp": "2025-06-15T17:42:00+00:00",
    "trader_id": "TRADER-001",
    "desk_id": "INST-EQ-NY",
    "aml_flag": {
        "flag_type": "SANCTIONS_NAME_MATCH",
        "confidence_score": 0.67,
        "matched_entity": "Acme Holdings SA",
        "matched_list": "OFAC_SDN",
        "generating_system": "OFAC-SCREENER-V2",
    },
}

# Scenario 2: Genuine OFAC concern
# LEI itself is on the OFAC SDN list. High-confidence, not a name match.
SANCTIONS_GENUINE_CONCERN_EVENT = {
    "trade_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "security_isin": "US5949181045",
    "security_cusip": "594918104",
    "security_description": "Microsoft Corporation Common Stock",
    "counterparty_name": "GlobalTrade Finance Ltd",
    "counterparty_lei": "SANCTIONED00LEI000001",
    "counterparty_country": "IR",
    "trade_side": "SELL",
    "quantity": 25000,
    "execution_price": "415.20",
    "trade_value": "10380000.00",
    "currency": "USD",
    "settlement_date": "2025-06-17",
    "execution_timestamp": "2025-06-15T14:30:00+00:00",
    "trader_id": "TRADER-002",
    "desk_id": "INST-EQ-NY",
    "aml_flag": {
        "flag_type": "SANCTIONS_NAME_MATCH",
        "confidence_score": 0.82,
        "matched_entity": "GlobalTrade Finance Ltd",
        "matched_list": "OFAC_SDN",
        "generating_system": "OFAC-SCREENER-V2",
    },
}

# Scenario 3: Auto-escalate (confidence score above threshold)
# Should never enter the autonomous pipeline — routed directly to escalation.
AUTO_ESCALATE_EVENT = {
    "trade_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "security_isin": "US88160R1014",
    "security_description": "Tesla Inc. Common Stock",
    "counterparty_name": "Restricted Entity LLC",
    "counterparty_lei": "HIGHCONFIDENCE000001",
    "counterparty_country": "RU",
    "trade_side": "BUY",
    "quantity": 100000,
    "execution_price": "248.75",
    "trade_value": "24875000.00",
    "currency": "USD",
    "settlement_date": "2025-06-17",
    "execution_timestamp": "2025-06-15T16:00:00+00:00",
    "trader_id": "TRADER-003",
    "desk_id": "INST-EQ-NY",
    "aml_flag": {
        "flag_type": "SANCTIONS_LEI_MATCH",
        "confidence_score": 0.92,    # Above 0.85 auto-escalate threshold
        "matched_entity": "Restricted Entity LLC",
        "matched_list": "OFAC_SDN",
        "generating_system": "OFAC-SCREENER-V2",
    },
}

# Scenario 4: Unusual volume, no prior flags
# Clean counterparty with an unusually large one-off trade.
UNUSUAL_VOLUME_EVENT = {
    "trade_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
    "security_isin": "US02079K3059",
    "security_description": "Alphabet Inc. Class A",
    "counterparty_name": "Summit Asset Management LLC",
    "counterparty_lei": "SUMMITAML00000001234",
    "counterparty_country": "US",
    "trade_side": "BUY",
    "quantity": 200000,
    "execution_price": "172.30",
    "trade_value": "34460000.00",
    "currency": "USD",
    "settlement_date": "2025-06-17",
    "execution_timestamp": "2025-06-15T10:15:00+00:00",
    "trader_id": "TRADER-004",
    "desk_id": "INST-EQ-NY",
    "aml_flag": {
        "flag_type": "UNUSUAL_VOLUME",
        "confidence_score": 0.55,
        "matched_entity": "Summit Asset Management LLC",
        "matched_list": "NONE",
        "generating_system": "INTERNAL-AML-ENGINE",
    },
}

# Scenario 5: Malformed event — missing required fields
# Trade.from_event() must raise ValidationError on this.
MALFORMED_EVENT = {
    "security_isin": "US0378331005",
    # Missing: trade_id, counterparty_name, counterparty_lei, quantity, etc.
    "trade_side": "BUY",
    "aml_flag": {
        "flag_type": "SANCTIONS_NAME_MATCH",
        "confidence_score": 0.67,
        "matched_entity": "Incomplete",
        "matched_list": "OFAC_SDN",
        "generating_system": "TEST",
    },
}

# Scenario 6: Invalid LEI (too short — schema validation catches this)
INVALID_LEI_EVENT = {
    **SANCTIONS_NAME_MATCH_EVENT,
    "trade_id": "e5f6a7b8-c9d0-1234-efab-345678901234",
    "counterparty_lei": "TOOSHORT",   # Must be 20 chars — Pydantic rejects this
}


# ─────────────────────────────────────────────────────────────
# PYTEST FIXTURES
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def sanctions_name_match_false_positive():
    """Clean SANCTIONS_NAME_MATCH scenario. Investigation should conclude FALSE POSITIVE."""
    return SANCTIONS_NAME_MATCH_EVENT.copy()


@pytest.fixture
def sanctions_genuine_concern():
    """SANCTIONS_NAME_MATCH with high-confidence genuine concern. Should block."""
    return SANCTIONS_GENUINE_CONCERN_EVENT.copy()


@pytest.fixture
def auto_escalate_trade():
    """Confidence score 0.92 — above auto-escalate threshold. Should skip pipeline."""
    return AUTO_ESCALATE_EVENT.copy()


@pytest.fixture
def unusual_volume_trade():
    """UNUSUAL_VOLUME flag with no prior concerns. Should investigate and likely clear."""
    return UNUSUAL_VOLUME_EVENT.copy()


@pytest.fixture
def malformed_event():
    """Missing required fields. Trade.from_event() must raise ValidationError."""
    return MALFORMED_EVENT.copy()


@pytest.fixture
def invalid_lei_event():
    """LEI is too short. Pydantic validation must reject this."""
    return INVALID_LEI_EVENT.copy()


# ─────────────────────────────────────────────────────────────
# MOCK DEPENDENCIES
# ─────────────────────────────────────────────────────────────

from data_sources import (
    KYCRecord,
    LEIRecord,
    SanctionsCheckResult,
    StubKYCStore,
    StubLEIDatabase,
    StubSanctionsDatabase,
    StubTransactionHistoryStore,
    TransactionHistorySummary,
    SanctionsMatch,
)


def make_clean_stubs():
    """
    Returns a set of stubs configured for the false positive scenario.
    LEI is clean, KYC is current, OFAC returns no match.
    """
    lei_db = StubLEIDatabase()
    lei_db._fixtures["7H6GLXDRUGQFU57RNE97"] = LEIRecord(
        lei="7H6GLXDRUGQFU57RNE97",
        legal_name="Acme Capital Partners Ltd",
        jurisdiction="GB",
        entity_status="ACTIVE",
        registration_status="ISSUED",
        parent_lei="ACMEHOLDINGSPARENT001",
        parent_legal_name="Acme Holdings SA",  # This is the entity that triggered name match
        last_updated=datetime.now(timezone.utc),
        found=True,
    )

    kyc_store = StubKYCStore()
    kyc_store._fixtures["7H6GLXDRUGQFU57RNE97"] = KYCRecord(
        lei="7H6GLXDRUGQFU57RNE97",
        entity_name="Acme Capital Partners Ltd",
        kyc_status="CURRENT",
        risk_tier="LOW",
        last_review_date=date(2024, 4, 1),
        next_review_due=date(2025, 10, 1),
        days_since_last_review=440,
        review_overdue=False,
        prior_aml_flags=0,
        found=True,
    )

    sanctions_db = StubSanctionsDatabase()
    # LEI query returns clean — the name match was from the parent entity
    sanctions_db._fixtures["7H6GLXDRUGQFU57RNE97"] = SanctionsCheckResult(
        lei_queried="7H6GLXDRUGQFU57RNE97",
        name_cross_referenced="Acme Capital Partners Ltd",
        match_found=False,
        matches=[],
        lists_checked=["OFAC_SDN", "OFAC_CONSOLIDATED"],
        list_last_updated={
            "OFAC_SDN": datetime.now(timezone.utc),
            "OFAC_CONSOLIDATED": datetime.now(timezone.utc),
        },
    )

    tx_store = StubTransactionHistoryStore()

    return lei_db, kyc_store, sanctions_db, tx_store


def make_genuine_concern_stubs():
    """
    Returns stubs configured for the genuine concern scenario.
    OFAC query returns a direct LEI match.
    """
    lei_db, kyc_store, _, tx_store = make_clean_stubs()

    sanctions_db = StubSanctionsDatabase()
    sanctions_db._fixtures["SANCTIONED00LEI000001"] = SanctionsCheckResult(
        lei_queried="SANCTIONED00LEI000001",
        match_found=True,
        matches=[
            SanctionsMatch(
                matched_name="GlobalTrade Finance Ltd",
                matched_list="OFAC_SDN",
                match_type="EXACT",
                confidence_score=1.0,
                program="IRAN",
            )
        ],
        lists_checked=["OFAC_SDN", "OFAC_CONSOLIDATED"],
        list_last_updated={
            "OFAC_SDN": datetime.now(timezone.utc),
            "OFAC_CONSOLIDATED": datetime.now(timezone.utc),
        },
    )

    return lei_db, kyc_store, sanctions_db, tx_store


class MockApprovedReviewQueue:
    """Human review queue that always approves. Use in happy path tests."""

    def request_approval(self, trade_id, report):
        from orchestrator import ApprovalDecision

        class _Token:
            token_id = UUID("00000000-0000-0000-0000-000000000001")
            def is_valid_for(self, tid): return True

        return ApprovalDecision(
            approved=True,
            officer_id="TEST-OFFICER-001",
            timestamp=datetime.now(timezone.utc),
            rationale="Approved in test — false positive confirmed.",
            token=_Token(),
        )


class MockBlockedReviewQueue:
    """Human review queue that always blocks. Use in block/SAR tests."""

    def request_approval(self, trade_id, report):
        from orchestrator import ApprovalDecision
        return ApprovalDecision(
            approved=False,
            officer_id="TEST-OFFICER-001",
            timestamp=datetime.now(timezone.utc),
            rationale="Blocked in test — genuine concern confirmed.",
            action="reject",
            reason="OFAC SDN direct match confirmed.",
        )


class MockSettlementAPI:
    """Settlement API that records calls without executing. Use in all tests."""
    def __init__(self):
        self.calls: list[dict] = []

    def execute(self, trade_id, token):
        self.calls.append({"trade_id": trade_id, "token": token})


class MockAuditLog:
    """In-memory audit log. Inspect .entries in assertions."""
    def __init__(self):
        self.entries: list[dict] = []

    def write(self, trade_id, event_type, content):
        self.entries.append({
            "trade_id": str(trade_id),
            "event_type": event_type,
            "content": content,
        })

    def seal(self, trade_id, decision):
        self.entries.append({
            "trade_id": str(trade_id),
            "event_type": "audit_sealed",
            "content": {"decision": str(decision)},
        })
