"""
tests/test_workflow.py

Runs all three stub scenarios (data/stub_scenarios.py) through the
orchestrator using FakeProvider — no API keys, no network access, and
deterministic results. This tests the WORKFLOW LOGIC (ordering, fail-fast
behavior, the Fraud/Weather dependency, the flagged-branch halt) — it does
NOT test whether any of the three real provider adapters correctly talks
to a live model. See README.md, "Provider Verification Status", for why
that's a separate, still-outstanding step.

Run with: python -m pytest tests/test_workflow.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.orchestrator import NemoOrchestrator, WorkflowHaltedError
from data.stub_scenarios import HAPPY_PATH, UNCOVERED_CLAIM, NO_WEATHER_MATCH
from tests.fake_provider import FakeProvider


def _planner_response(claim_id, policy_id, claimed_amount, location, timestamp_iso, description):
    return {
        "claim_id": claim_id,
        "policy_id": policy_id,
        "claimed_amount": claimed_amount,
        "location": location,
        "incident_timestamp": timestamp_iso,
        "description": description,
        "missing_fields": [],
    }


def test_happy_path_reaches_human_review():
    scripted = {
        "planner": _planner_response(
            "AUS-CLAIM-001", "AUS-POL-88213", 250.0, "Adelaide, SA",
            "2026-03-14T14:00:00", "Storm-caused outage, food spoiled.",
        ),
        "coverage": {
            "determination": "covered",
            "policy_clause_cited": "Home Contents - Food Spoilage, Severe Weather Outage",
            "exceeds_threshold": False,
            "reasoning": "Policy covers food spoilage from severe-weather outages; claim is within limit.",
        },
        "weather": {
            "match_status": "matched",
            "event_description": "Severe storm, Adelaide metro, 2026-03-14",
            "confidence": "high",
            "data_source_cited": "Bureau of Meteorology severe weather warning",
            "reasoning": "Confirmed warning matches claimed location and time window.",
        },
        "fraud": {"conclusion": "clear", "reasoning": "Weather matched; no history flags."},
        "payout": {"recommended_amount_aud": 250.0, "reasoning": "Matches claimed spoilage value, within threshold."},
        "audit": {
            "summary_text": (
                "CLAIM SUMMARY: Claim AUS-CLAIM-001, $250 spoilage.\n"
                "COVERAGE & WEATHER FINDINGS: Covered; weather matched.\n"
                "FRAUD SCREENING RESULT: Clear.\n"
                "RECOMMENDED SETTLEMENT: $250."
            )
        },
    }
    provider = FakeProvider(scripted)
    orchestrator = NemoOrchestrator(provider, threshold_aud=500.0)

    result = orchestrator.run(
        HAPPY_PATH.raw_claim_event, HAPPY_PATH.policy_record,
        HAPPY_PATH.meteorological_data, HAPPY_PATH.claim_history_summary,
    )

    assert result.status == "awaiting_human_review"
    assert result.recommended_amount_aud == 250.0
    assert provider.call_log == ["planner", "coverage", "weather", "fraud", "payout", "audit"]
    print("test_happy_path_reaches_human_review: PASSED")


def test_uncovered_claim_exits_at_coverage():
    scripted = {
        "planner": _planner_response(
            "AUS-CLAIM-002", "AUS-POL-40217", 180.0, "Perth, WA",
            "2026-02-02T09:00:00", "Outage, food spoiled.",
        ),
        "coverage": {
            "determination": "not_covered",
            "policy_clause_cited": "Home Contents - Food Spoilage (severe-weather outage excluded)",
            "exceeds_threshold": False,
            "reasoning": "Policy does not cover severe-weather-outage spoilage for this policyholder.",
        },
        # weather/fraud/payout/audit intentionally NOT scripted — if the
        # orchestrator calls any of them, FakeProvider raises KeyError,
        # which would fail this test and correctly expose a fail-fast bug.
    }
    provider = FakeProvider(scripted)
    orchestrator = NemoOrchestrator(provider, threshold_aud=500.0)

    try:
        orchestrator.run(
            UNCOVERED_CLAIM.raw_claim_event, UNCOVERED_CLAIM.policy_record,
            UNCOVERED_CLAIM.meteorological_data, UNCOVERED_CLAIM.claim_history_summary,
        )
        assert False, "Expected WorkflowHaltedError"
    except WorkflowHaltedError as e:
        assert e.stage == "coverage"

    assert provider.call_log == ["planner", "coverage"], (
        f"Fail-fast violated — Weather/Fraud/Payout/Audit should never run "
        f"for an uncovered claim. Actual calls: {provider.call_log}"
    )
    print("test_uncovered_claim_exits_at_coverage: PASSED")


def test_no_weather_match_feeds_fraud_and_can_flag():
    scripted = {
        "planner": _planner_response(
            "AUS-CLAIM-003", "AUS-POL-77105", 220.0, "Brisbane, QLD",
            "2026-04-01T20:00:00", "Outage, food spoiled, storm-related per claimant.",
        ),
        "coverage": {
            "determination": "covered",
            "policy_clause_cited": "Home Contents - Food Spoilage, Severe Weather Outage",
            "exceeds_threshold": False,
            "reasoning": "Policy covers this claim type.",
        },
        "weather": {
            "match_status": "not_matched",
            "event_description": "No severe weather recorded for this location/date.",
            "confidence": "high",
            "data_source_cited": "Bureau of Meteorology records",
            "reasoning": "No warnings or reports match the claimed time and location.",
        },
        "fraud": {
            "conclusion": "flagged",
            "reasoning": "No corroborating weather event, plus two prior similar claims in 8 months.",
        },
        # payout/audit intentionally NOT scripted — a flagged claim must
        # never reach Payout.
    }
    provider = FakeProvider(scripted)
    orchestrator = NemoOrchestrator(provider, threshold_aud=500.0)

    try:
        orchestrator.run(
            NO_WEATHER_MATCH.raw_claim_event, NO_WEATHER_MATCH.policy_record,
            NO_WEATHER_MATCH.meteorological_data, NO_WEATHER_MATCH.claim_history_summary,
        )
        assert False, "Expected WorkflowHaltedError"
    except WorkflowHaltedError as e:
        assert e.stage == "fraud"

    assert provider.call_log == ["planner", "coverage", "weather", "fraud"], (
        f"Payout/Audit should never run for a flagged claim. Actual calls: {provider.call_log}"
    )
    print("test_no_weather_match_feeds_fraud_and_can_flag: PASSED")


if __name__ == "__main__":
    test_happy_path_reaches_human_review()
    test_uncovered_claim_exits_at_coverage()
    test_no_weather_match_feeds_fraud_and_can_flag()
    print("\nAll tests passed.")
