"""
WHAT THIS FILE DOES: Answers one question - does this claim have a fraud
signal - as a fabricated, standalone source, independent of the policy/visit
record, standing in for Lemonade's real, separate Forensic Graph system.

[DEV] The fraud signals themselves are fabricated for illustration - not
derived from any real fraud-detection output. Replace this entire file with
a call to your own fraud system (or Forensic-Graph-equivalent).

NOTE: this module has no import of, or dependency on,
mock_policy_visit_records - enforced by tests/test_mock_fraud_signal.py.
Fraud detection is a separate system in Lemonade's own account (case study
Section 6.5), and this scaffold's data-sourcing shape mirrors that
separation rather than the narrative-fusion risk that section names.
"""
from fixtures import MOCK_FRAUD_SIGNALS


def check(customer_id: str, policy_id: str, claim_details: dict) -> bool:
    """Returns True if a fraud signal is present for this customer/policy."""
    return MOCK_FRAUD_SIGNALS.get((customer_id, policy_id), False)
