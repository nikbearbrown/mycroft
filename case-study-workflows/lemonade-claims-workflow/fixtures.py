"""
WHAT THIS FILE DOES: Provides one canonical set of scenario data - claim
texts, mock policy/visit records, mock fraud signals, and canned LLM
responses - reused by the test suite, FakeAdapter, and the demo harness.

This exists specifically to satisfy the /v2 decision against a second,
drifting copy of demo/test data: every scenario appears here exactly once.

[DEV] Every value below is fabricated for illustration. None of it is
derived from, or represents, any real Lemonade customer, claim, or record.
"""

# --- Claim texts (used as FakeAdapter lookup keys and as Intake inputs) ---

SOFIA_VALID_CLAIM_TEXT = (
    "My dog Biscuit had a vet visit for kennel cough, cost $120, seen on 2026-05-01."
)
UNCLASSIFIABLE_CLAIM_TEXT = "asdkfj alksdjf not a real claim at all"
LOW_CONFIDENCE_CLAIM_TEXT = "something about my pet maybe being sick idk"
INCOMPLETE_CLAIM_TEXT = "My cat was treated but I don't remember the cost or date"
NO_RECORD_CLAIM_TEXT = "My dog Rex had surgery for $800 on 2026-06-01"
FRAUD_FLAG_CLAIM_TEXT = "My dog Max had a checkup for $90 on 2026-04-15"
MISMATCH_CLAIM_TEXT = "My cat Luna had a $50 visit on 2026-03-01"
OVER_AUTHORIZATION_CLAIM_TEXT = "My dog Zeus had surgery for $700 on 2026-07-01"

# --- Customer/policy identifiers tied to each scenario ---

SOFIA_CUSTOMER_ID, SOFIA_POLICY_ID = "sofia_customer", "sofia_policy"
NO_RECORD_CUSTOMER_ID, NO_RECORD_POLICY_ID = "unknown_customer", "unknown_policy"
FRAUD_CUSTOMER_ID, FRAUD_POLICY_ID = "max_customer", "max_policy"
MISMATCH_CUSTOMER_ID, MISMATCH_POLICY_ID = "luna_customer", "luna_policy"
OVER_AUTH_CUSTOMER_ID, OVER_AUTH_POLICY_ID = "zeus_customer", "zeus_policy"
# Sofia's own claim doesn't need a "no record" test partner; incomplete/
# unclassifiable/low-confidence scenarios never reach a record lookup at all.

# --- Mock Policy/Visit Records data ---
# NOTE: this table must never contain a fraud-related field. Fraud signals
# live entirely in MOCK_FRAUD_SIGNALS below. See mock_policy_visit_records.py
# and mock_fraud_signal.py for the enforced independence.

MOCK_VISIT_RECORDS = {
    (SOFIA_CUSTOMER_ID, SOFIA_POLICY_ID): {
        "diagnosis": "kennel cough", "amount": 120.0, "date": "2026-05-01",
    },
    (FRAUD_CUSTOMER_ID, FRAUD_POLICY_ID): {
        "diagnosis": "routine checkup", "amount": 90.0, "date": "2026-04-15",
    },
    (MISMATCH_CUSTOMER_ID, MISMATCH_POLICY_ID): {
        "diagnosis": "ear infection", "amount": 200.0, "date": "2026-03-01",
    },
    (OVER_AUTH_CUSTOMER_ID, OVER_AUTH_POLICY_ID): {
        "diagnosis": "surgery", "amount": 700.0, "date": "2026-07-01",
    },
}

# --- Mock Fraud Signal data - deliberately separate table and separate file ---

MOCK_FRAUD_SIGNALS = {
    (FRAUD_CUSTOMER_ID, FRAUD_POLICY_ID): True,
}

# --- FakeAdapter canned LLM responses, keyed by exact claim text ---
# Format matches what Intake expects to parse.

FAKE_LLM_RESPONSES = {
    SOFIA_VALID_CLAIM_TEXT: {
        "claim_type": "pet_illness_reimbursement", "diagnosis": "kennel cough",
        "amount": 120.0, "date": "2026-05-01", "confidence": 0.95,
    },
    NO_RECORD_CLAIM_TEXT: {
        "claim_type": "pet_illness_reimbursement", "diagnosis": "surgery",
        "amount": 800.0, "date": "2026-06-01", "confidence": 0.90,
    },
    FRAUD_FLAG_CLAIM_TEXT: {
        "claim_type": "pet_illness_reimbursement", "diagnosis": "routine checkup",
        "amount": 90.0, "date": "2026-04-15", "confidence": 0.93,
    },
    MISMATCH_CLAIM_TEXT: {
        "claim_type": "pet_illness_reimbursement", "diagnosis": "ear infection",
        "amount": 50.0, "date": "2026-03-01", "confidence": 0.92,
    },
    OVER_AUTHORIZATION_CLAIM_TEXT: {
        "claim_type": "pet_illness_reimbursement", "diagnosis": "surgery",
        "amount": 700.0, "date": "2026-07-01", "confidence": 0.97,
    },
    INCOMPLETE_CLAIM_TEXT: {
        "claim_type": "pet_illness_reimbursement", "diagnosis": None,
        "amount": None, "date": None, "confidence": 0.90,
    },
    LOW_CONFIDENCE_CLAIM_TEXT: {
        "claim_type": "pet_illness_reimbursement", "diagnosis": "unknown",
        "amount": None, "date": None, "confidence": 0.20,
    },
    UNCLASSIFIABLE_CLAIM_TEXT: {"claim_type": "unclassified", "confidence": 0.0},
}
