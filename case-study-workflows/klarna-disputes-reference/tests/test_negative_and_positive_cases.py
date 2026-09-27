"""
WHAT THIS FILE DOES: Proves at least one clean case actually auto-resolves
for EACH dispute type — not just that escalation works, which the other
test files already cover exhaustively. Without a positive case for
refund_request specifically, that dispute type would only ever be proven by
how it fails, never by it working (see docs/DESIGN_SPECS.md Section 7).
Also exercises the ambiguous_delay mock record end to end, to confirm
DD-002's weakest criterion actually produces an observable, correct result
rather than being dead code.
"""

from src.orchestrator import handle_query


def test_clean_late_fee_dispute_resolves():
    # cust_001's actual payment_date is 2024-02-28 — an exact match.
    message = "I was charged a late fee but I paid on time on 2024-02-28."
    result = handle_query(message, "cust_001")

    assert result == {"resolved": True, "escalated": False, "reason": None}


def test_clean_refund_request_resolves():
    # cust_001's actual amount_paid is 100.00 — an exact match.
    message = "I want a refund of $100.00 please."
    result = handle_query(message, "cust_001")

    assert result == {"resolved": True, "escalated": False, "reason": None}


def test_ambiguous_delay_case_produces_observable_correct_output():
    # cust_004 carries a delay_reason flag. This proves the flag actually
    # changes the caller-visible output, not just an internal value that
    # never surfaces.
    message = "I was charged a late fee but I paid on time on 2024-03-01."
    result = handle_query(message, "cust_004")

    assert result == {"resolved": False, "escalated": True, "reason": "ambiguous_delay"}
