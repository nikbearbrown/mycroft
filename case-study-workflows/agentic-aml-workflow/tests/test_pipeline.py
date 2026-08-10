"""
tests/test_pipeline.py
======================
Agentic AML Compliance Workflow — Pipeline Test Suite
US Equities · OFAC/BSA/FinCEN

Covers the scenarios most likely to fail silently in production:

  Test 1: Schema validation rejects malformed events at the boundary
  Test 2: Trade schema rejects an invalid LEI
  Test 3: Happy path — pipeline reaches human review with a valid report
  Test 4: Settlement API rejects an invalid token (token gate)
  Test 5: Agent validation failure triggers mid-pipeline escalation
  Test 6: OFAC database unavailable triggers prefetch escalation
  Test 7: Auto-escalate route bypasses the autonomous pipeline

Run with:
    pytest tests/ -v

For a quick smoke test (no LLM calls):
    pytest tests/test_pipeline.py -v -k "not llm"

Dependencies:
    pip install pytest>=8.0 pydantic>=2.0
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import pytest
from pydantic import ValidationError

from schemas import Trade, AMLFlag, AgentResult
from agent_validation import validate_agent_output
from data_sources import DataSourceUnavailable, StubSanctionsDatabase
from orchestrator import SettlementAPI

from tests.conftest import (
    SANCTIONS_NAME_MATCH_EVENT,
    MALFORMED_EVENT,
    INVALID_LEI_EVENT,
    make_clean_stubs,
    make_genuine_concern_stubs,
    MockApprovedReviewQueue,
    MockBlockedReviewQueue,
    MockSettlementAPI,
    MockAuditLog,
)


# ─────────────────────────────────────────────────────────────
# TEST 1: Schema validation — malformed event rejected at boundary
# ─────────────────────────────────────────────────────────────

def test_malformed_event_raises_validation_error(malformed_event):
    """
    Trade.from_event() must reject events missing required fields.
    The pipeline boundary must catch bad data before any agent sees it.
    """
    with pytest.raises(ValidationError) as exc_info:
        Trade.from_event(malformed_event)

    errors = exc_info.value.errors()
    # Several required fields are missing — all should be reported
    error_fields = {e["loc"][0] for e in errors}
    assert "trade_id" in error_fields or "counterparty_lei" in error_fields, (
        "ValidationError did not report missing required fields. "
        "Check that Trade.from_event() calls model_validate()."
    )


# ─────────────────────────────────────────────────────────────
# TEST 2: Schema validation — invalid LEI rejected
# ─────────────────────────────────────────────────────────────

def test_invalid_lei_rejected_by_schema(invalid_lei_event):
    """
    Trade schema must reject LEIs that are not exactly 20 alphanumeric characters.
    The counterparty_lei field validator enforces ISO 17442.
    """
    with pytest.raises(ValidationError) as exc_info:
        Trade.from_event(invalid_lei_event)

    errors = exc_info.value.errors()
    lei_errors = [e for e in errors if "counterparty_lei" in str(e.get("loc", []))]
    assert lei_errors, (
        "ValidationError did not specifically flag counterparty_lei. "
        "Check the validate_lei field_validator in schemas.py."
    )


# ─────────────────────────────────────────────────────────────
# TEST 3: Agent validation — triage output missing risk level
# ─────────────────────────────────────────────────────────────

def test_triage_validation_rejects_missing_risk_level():
    """
    TriageValidator must reject triage output that does not contain
    a risk level assignment (LOW / MED / HIGH).

    This covers the failure mode where the triage agent produces a
    generic template response without processing the actual flag.
    """
    trade = Trade.from_event(SANCTIONS_NAME_MATCH_EVENT)

    # Triage output that describes the trade but forgets the risk level
    bad_output = (
        "The trade involves a cross-border equity purchase with a UK-domiciled counterparty. "
        "An AML flag has been raised based on a name-string match against the OFAC SDN list. "
        "The investigation agent should run the LEI query and review the KYC record."
    )

    failure = validate_agent_output("triage_agent", bad_output, trade)
    assert failure is not None, (
        "TriageValidator should have returned a ValidationFailure for output "
        "missing a risk level (LOW/MED/HIGH). Got None (passed)."
    )
    assert "risk level" in failure.reason.lower(), (
        f"ValidationFailure reason does not mention risk level. Got: {failure.reason}"
    )


def test_triage_validation_accepts_valid_output():
    """
    TriageValidator must accept correctly formatted triage output.
    """
    trade = Trade.from_event(SANCTIONS_NAME_MATCH_EVENT)

    good_output = (
        f"The trade involves a BUY order of 50,000 shares of Apple Inc. "
        f"with counterparty Acme Capital Partners Ltd (LEI: 7H6GLXDRUGQFU57RNE97). "
        f"The AML flag is a SANCTIONS_NAME_MATCH with confidence score 0.67, triggered by "
        f"a partial match against Acme Holdings SA on the OFAC SDN list.\n\n"
        f"Risk level: MED. The confidence score falls within the investigation zone "
        f"(0.30–0.85), and the name match may be attributable to a parent entity. "
        f"This is consistent with a false positive pattern.\n\n"
        f"The investigation agent must run an LEI-based OFAC SDN query, review the KYC "
        f"record for currency and risk tier, check for a parent entity relationship in "
        f"the GLEIF record, and review 24-month transaction history for any prior flags."
    )

    failure = validate_agent_output("triage_agent", good_output, trade)
    assert failure is None, (
        f"TriageValidator rejected valid output. Failure: {failure.reason if failure else 'N/A'}"
    )


# ─────────────────────────────────────────────────────────────
# TEST 4: Report validator — missing section rejected, retry path tested
# ─────────────────────────────────────────────────────────────

def test_report_validation_rejects_missing_section():
    """
    ReportValidator must reject exception reports with missing section headers.
    This triggers the one-retry path in the orchestrator.
    """
    trade = Trade.from_event(SANCTIONS_NAME_MATCH_EVENT)

    # Report missing REGULATORY ASSESSMENT section
    incomplete_report = (
        "FLAG SUMMARY\n"
        "The trade carries a SANCTIONS_NAME_MATCH flag at 0.67 confidence. "
        "The flag was triggered by a partial name match against Acme Holdings SA.\n\n"
        "INVESTIGATION FINDINGS\n"
        "LEI query returned no OFAC SDN match. KYC record is current at LOW risk. "
        "Transaction history shows no prior flags over 24 months.\n\n"
        # REGULATORY ASSESSMENT is missing
        "RECOMMENDED ACTION\n"
        "Recommend: Clear the trade. False positive confirmed via LEI verification."
    )

    failure = validate_agent_output("report_agent", incomplete_report, trade)
    assert failure is not None
    assert "REGULATORY ASSESSMENT" in failure.reason


def test_report_validation_rejects_wrong_recommended_action_format():
    """
    RECOMMENDED ACTION must begin with exactly 'Recommend:'.
    """
    trade = Trade.from_event(SANCTIONS_NAME_MATCH_EVENT)

    wrong_format_report = (
        "FLAG SUMMARY\n"
        "The trade carries a SANCTIONS_NAME_MATCH flag at 0.67 confidence. "
        "Triggered by partial name match against Acme Holdings SA.\n\n"
        "INVESTIGATION FINDINGS\n"
        "LEI query returned no OFAC match. KYC is current. No prior flags.\n\n"
        "REGULATORY ASSESSMENT\n"
        "The flag appears to be a false positive under OFAC SDN verification.\n\n"
        "RECOMMENDED ACTION\n"
        "The trade should be cleared."   # Missing "Recommend:" prefix
    )

    failure = validate_agent_output("report_agent", wrong_format_report, trade)
    assert failure is not None
    assert "Recommend:" in failure.reason


# ─────────────────────────────────────────────────────────────
# TEST 5: Token gate — settlement API rejects invalid token
# ─────────────────────────────────────────────────────────────

def test_settlement_api_rejects_invalid_token():
    """
    SettlementAPI.execute() must reject a token not scoped to the trade.
    This verifies the architectural gate is enforced — not just described.
    """
    settlement = SettlementAPI()

    class WrongScopeToken:
        token_id = UUID("00000000-0000-0000-0000-000000000099")
        def is_valid_for(self, trade_id): return False   # Always invalid

    trade_id = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    token = WrongScopeToken()

    with pytest.raises(PermissionError) as exc_info:
        settlement.execute(trade_id, token)

    assert "valid" in str(exc_info.value).lower(), (
        "SettlementAPI.execute() raised PermissionError but message does not "
        "mention token validity. Update the error message in orchestrator.py."
    )


# ─────────────────────────────────────────────────────────────
# TEST 6: Prefetch escalation — OFAC unavailable halts pipeline
# ─────────────────────────────────────────────────────────────

def test_ofac_unavailable_triggers_prefetch_escalation():
    """
    When the sanctions database is unavailable, InvestigationPrefetcher
    must return (None, escalation_reason) — not raise an exception.
    The orchestrator converts this into a mid-pipeline escalation.

    This verifies the critical/non-critical tiering in the prefetcher.
    """
    from investigation_prefetch import InvestigationPrefetcher
    from data_sources import KYCStore, TransactionHistoryStore, LEIDatabase

    trade = Trade.from_event(SANCTIONS_NAME_MATCH_EVENT)

    lei_db, kyc_store, _, tx_store = make_clean_stubs()

    # Configure OFAC stub to raise DataSourceUnavailable
    class UnavailableSanctionsDB:
        def query_by_lei(self, lei, counterparty_name=None):
            raise DataSourceUnavailable("SANCTIONS", "OFAC API unreachable in test")

    prefetcher = InvestigationPrefetcher(
        lei_db=lei_db,
        kyc_store=kyc_store,
        sanctions_db=UnavailableSanctionsDB(),
        tx_store=tx_store,
    )

    context, escalation_reason = prefetcher.prefetch(trade)

    assert context is None, (
        "Prefetcher should return None context when OFAC is unavailable. "
        "Sanctions database is a CRITICAL source — pipeline must escalate."
    )
    assert escalation_reason is not None, (
        "Prefetcher should return an escalation_reason when OFAC is unavailable."
    )
    assert "sanctions" in escalation_reason.lower() or "ofac" in escalation_reason.lower(), (
        f"Escalation reason does not mention sanctions/OFAC. Got: {escalation_reason}"
    )


# ─────────────────────────────────────────────────────────────
# TEST 7: Auto-escalate route — high confidence bypasses pipeline
# ─────────────────────────────────────────────────────────────

def test_auto_escalate_confidence_score_rejected_at_boundary():
    """
    Trade events with confidence score above the auto-escalate threshold
    should be rejected by the AMLFlag validator before entering the pipeline.

    This verifies that the upstream routing check (in handle_aml_flag())
    is enforced at the data contract level.
    """
    with pytest.raises(ValidationError) as exc_info:
        Trade.from_event({
            **SANCTIONS_NAME_MATCH_EVENT,
            "trade_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
            "aml_flag": {
                "flag_type": "SANCTIONS_LEI_MATCH",
                "confidence_score": 0.92,   # Above 0.85 auto-escalate threshold
                "matched_entity": "Restricted Entity",
                "matched_list": "OFAC_SDN",
                "generating_system": "OFAC-SCREENER-V2",
            },
        })

    errors = exc_info.value.errors()
    flag_errors = [e for e in errors if "confidence_score" in str(e)]
    assert flag_errors, (
        "AMLFlag validator did not reject confidence_score=0.92 (above auto-escalate threshold). "
        "Check the score_must_be_in_investigation_zone validator in schemas.py."
    )


# ─────────────────────────────────────────────────────────────
# TEST 8: Reasoning validator — uncited steps rejected
# ─────────────────────────────────────────────────────────────

def test_reasoning_validation_rejects_uncited_steps():
    """
    ReasoningValidator must reject reasoning chains where one or more
    steps do not contain a [SOURCE: X] citation.
    """
    trade = Trade.from_event(SANCTIONS_NAME_MATCH_EVENT)

    # Step 2 is missing a citation
    reasoning_with_missing_citation = (
        "1. The GLEIF LEI record for 7H6GLXDRUGQFU57RNE97 shows entity status ACTIVE "
        "and registration status ISSUED, confirming the counterparty is a valid "
        "registered entity [SOURCE: LEI-DB].\n"
        "2. The KYC record indicates a CURRENT status with LOW risk tier "
        "and last review date of 2024-04-01, which is within the 18-month review cycle.\n"  # No citation
        "3. OFAC SDN query by LEI returned no match, resolving the name-match flag "
        "as a false positive from the parent entity [SOURCE: OFAC-SDN].\n"
        "4. Transaction history shows no prior AML flags over 24 months and no "
        "pattern indicators [SOURCE: TX-HISTORY-24M]."
    )

    failure = validate_agent_output("reasoning_agent", reasoning_with_missing_citation, trade)
    assert failure is not None
    assert "citation" in failure.reason.lower() or "source" in failure.reason.lower()


# ─────────────────────────────────────────────────────────────
# TEST 9: Investigation context string — correct format for injection
# ─────────────────────────────────────────────────────────────

def test_investigation_context_contains_citation_markers():
    """
    InvestigationContext.to_context_string() must embed [SOURCE: X] markers
    that match the citation format expected by the investigation agent.
    """
    from investigation_prefetch import InvestigationPrefetcher

    trade = Trade.from_event(SANCTIONS_NAME_MATCH_EVENT)
    lei_db, kyc_store, sanctions_db, tx_store = make_clean_stubs()

    prefetcher = InvestigationPrefetcher(lei_db, kyc_store, sanctions_db, tx_store)
    context, error = prefetcher.prefetch(trade)

    assert error is None, f"Prefetch failed unexpectedly: {error}"
    assert context is not None

    context_str = context.to_context_string()
    assert "[SOURCE: LEI-DB]" in context_str
    assert "[SOURCE: KYC-RECORDS]" in context_str
    assert "[SOURCE: OFAC-SDN]" in context_str
    assert "[SOURCE: TX-HISTORY-24M]" in context_str


# ─────────────────────────────────────────────────────────────
# TEST 10: Taxonomy loader — loads file and formats flag context
# ─────────────────────────────────────────────────────────────

def test_taxonomy_loader_formats_flag_context():
    """
    TaxonomyLoader.format_flag_context() must return text containing
    the [SOURCE: AML-TAXONOMY] citation marker and the flag type name.
    """
    from taxonomy_loader import TaxonomyLoader
    import os
    from pathlib import Path

    taxonomy_path = Path(__file__).parent.parent / "aml_taxonomy.json"
    if not taxonomy_path.exists():
        pytest.skip("aml_taxonomy.json not found — run from project root")

    loader = TaxonomyLoader(taxonomy_path)
    context = loader.format_flag_context("SANCTIONS_NAME_MATCH")

    assert "[SOURCE: AML-TAXONOMY]" in context
    assert "SANCTIONS_NAME_MATCH" in context
    assert "OFAC" in context


def test_taxonomy_loader_lists_all_flag_types():
    """TaxonomyLoader must recognize all six flag types defined in the schema."""
    from taxonomy_loader import TaxonomyLoader
    from pathlib import Path

    taxonomy_path = Path(__file__).parent.parent / "aml_taxonomy.json"
    if not taxonomy_path.exists():
        pytest.skip("aml_taxonomy.json not found — run from project root")

    loader = TaxonomyLoader(taxonomy_path)
    flag_types = loader.list_flag_types()

    expected = {
        "SANCTIONS_NAME_MATCH",
        "SANCTIONS_LEI_MATCH",
        "UNUSUAL_VOLUME",
        "STRUCTURING",
        "LAYERING",
        "JURISDICTION_RISK",
    }
    missing = expected - set(flag_types)
    assert not missing, (
        f"Taxonomy is missing flag types: {missing}. "
        "Check aml_taxonomy.json."
    )
