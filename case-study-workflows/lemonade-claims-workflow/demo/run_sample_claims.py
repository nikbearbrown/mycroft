"""
WHAT THIS FILE DOES: Constructs one Orchestrator with a demo-only
authorization policy and runs a fixed set of sample claims through it, so a
person cloning this repo can watch the full pipeline work - settlement
included - without supplying an API key or writing any code first.

This script is also the reference pattern for wiring this pipeline
together: build your own llm_client, your own record/fraud lookups, and
your own policy_fn, then pass all four already-built components into the
same Orchestrator constructor shown below.

This file is not imported by, or a runtime dependency of, any other
component's actual pipeline logic - it is a reference for how to wire them
together, not a dependency of them.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
import mock_policy_visit_records
import mock_fraud_signal
from llm_provider.factory import build_llm_client
from intake import Intake
from verification import Verification
from authorization_gate import AuthorizationGate
from orchestrator import Orchestrator
from fixtures import (
    SOFIA_VALID_CLAIM_TEXT, SOFIA_CUSTOMER_ID, SOFIA_POLICY_ID,
    UNCLASSIFIABLE_CLAIM_TEXT,
    LOW_CONFIDENCE_CLAIM_TEXT,
    INCOMPLETE_CLAIM_TEXT,
    NO_RECORD_CLAIM_TEXT, NO_RECORD_CUSTOMER_ID, NO_RECORD_POLICY_ID,
    FRAUD_FLAG_CLAIM_TEXT, FRAUD_CUSTOMER_ID, FRAUD_POLICY_ID,
    MISMATCH_CLAIM_TEXT, MISMATCH_CUSTOMER_ID, MISMATCH_POLICY_ID,
    OVER_AUTHORIZATION_CLAIM_TEXT, OVER_AUTH_CUSTOMER_ID, OVER_AUTH_POLICY_ID,
)


# This policy is NOT Lemonade's mechanism and is NOT a shipped default.
# It exists only so this script can exercise every branch of the pipeline,
# including automatic settlement. Replace entirely before using this
# pipeline for anything real. Deliberately carries no [DEV] marker - see
# DESIGN_DECISIONS.md for why.
def demo_only_policy(claim) -> bool:
    return claim.amount < 500


def build_pipeline():
    """The reference wiring sequence: build each swappable dependency, inject
    it into the component that needs it, then hand all four already-built
    components to the Orchestrator."""
    cfg = config.Configuration()

    llm_client = build_llm_client(cfg)
    policy_visit_lookup = mock_policy_visit_records.lookup
    fraud_signal_lookup = mock_fraud_signal.check

    intake = Intake(llm_client=llm_client, confidence_threshold=cfg.confidence_threshold)
    verification = Verification(
        policy_visit_lookup=policy_visit_lookup,
        fraud_signal_lookup=fraud_signal_lookup,
        matching_tolerance=cfg.matching_tolerance,
    )
    gate = AuthorizationGate()

    return Orchestrator(intake, verification, gate, demo_only_policy)


SCENARIOS = [
    ("Sofia - valid claim, low amount", SOFIA_VALID_CLAIM_TEXT, SOFIA_CUSTOMER_ID, SOFIA_POLICY_ID),
    ("Unclassifiable text", UNCLASSIFIABLE_CLAIM_TEXT, "n/a", "n/a"),
    ("Low-confidence classification", LOW_CONFIDENCE_CLAIM_TEXT, "n/a", "n/a"),
    ("Missing diagnosis/amount/date", INCOMPLETE_CLAIM_TEXT, "n/a", "n/a"),
    ("Unknown customer/policy", NO_RECORD_CLAIM_TEXT, NO_RECORD_CUSTOMER_ID, NO_RECORD_POLICY_ID),
    ("Fraud signal present, record otherwise matches", FRAUD_FLAG_CLAIM_TEXT, FRAUD_CUSTOMER_ID, FRAUD_POLICY_ID),
    ("Record found, amount mismatch", MISMATCH_CLAIM_TEXT, MISMATCH_CUSTOMER_ID, MISMATCH_POLICY_ID),
    ("Verified claim, over demo policy's $500 line", OVER_AUTHORIZATION_CLAIM_TEXT, OVER_AUTH_CUSTOMER_ID, OVER_AUTH_POLICY_ID),
]


def main():
    orchestrator = build_pipeline()
    print("Lemonade Pet Insurance Claims Pipeline - Demo Run")
    print("=" * 60)
    for label, claim_text, customer_id, policy_id in SCENARIOS:
        result = orchestrator.process_claim(claim_text, customer_id, policy_id)
        outcome = result.status if result.reason is None else f"{result.status} ({result.reason})"
        print(f"[{label}]")
        print(f"  Claim text : {claim_text}")
        print(f"  Outcome    : {outcome}")
        print()


if __name__ == "__main__":
    main()
