"""
WHAT THIS FILE DOES: Provides a small, clearly fabricated set of policy and
visit records that Verification looks up by customer/policy identifier -
standing in for a real database, with no fraud information mixed in.

[DEV] The records themselves are fabricated for illustration - not derived
from any real data. Replace this entire file with a real data-access layer.

NOTE: the records returned here must never contain a fraud-related field.
Fraud signals live entirely in mock_fraud_signal.py - see that file and
/v2's fix. This module has no import of, or dependency on, mock_fraud_signal
(enforced by tests/test_mock_policy_visit_records.py).
"""
from fixtures import MOCK_VISIT_RECORDS


def lookup(customer_id: str, policy_id: str):
    """Returns the record dict {diagnosis, amount, date}, or None if no record exists."""
    return MOCK_VISIT_RECORDS.get((customer_id, policy_id))
