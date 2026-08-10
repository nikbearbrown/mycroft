"""
WHAT THIS FILE DOES: Proves each of the six named escalation reasons is
independently reachable, with the correct reason attached — not just that
"escalation happens sometimes." See docs/DESIGN_SPECS.md Section 5 for the
full ownership table this test file is proving end to end.
"""

from src.orchestrator import handle_query


def test_unclassified():
    result = handle_query("asdkjh random gibberish with no keywords at all", "cust_001")
    assert result["reason"] == "unclassified"


def test_no_record():
    message = "I was charged a late fee but I paid on time on 2024-02-28."
    result = handle_query(message, "cust_999")  # does not exist
    assert result["reason"] == "no_record"


def test_incomplete_claim():
    # Classifiable, but no date anywhere — late_fee_dispute's relevant field
    # is missing.
    message = "I was charged a late fee but I paid on time."
    result = handle_query(message, "cust_001")
    assert result["reason"] == "incomplete_claim"


def test_mismatch():
    # cust_002's actual payment_date is 2024-03-05. Claiming 2024-03-01 is a
    # plain disagreement, and cust_002 carries no delay_reason flag.
    message = "I was charged a late fee but I paid on time on 2024-03-01."
    result = handle_query(message, "cust_002")
    assert result["reason"] == "mismatch"


def test_ambiguous_delay():
    # cust_004's actual payment_date is 2024-03-04, but the record flags a
    # processing delay. Same shape of disagreement as test_mismatch above,
    # different record — proves the delay flag is what changes the reason.
    message = "I was charged a late fee but I paid on time on 2024-03-01."
    result = handle_query(message, "cust_004")
    assert result["reason"] == "ambiguous_delay"


def test_low_confidence():
    # Hits both keyword sets (late fee AND refund language) -> ambiguous
    # classification, confidence 0.5. The date given matches cust_001's
    # actual record exactly, so this escalates purely on confidence, not on
    # a record disagreement -- proving low_confidence is reachable on its
    # own, independent of mismatch.
    message = (
        "I was charged a late fee but I paid on time on 2024-02-28, "
        "though I'd also like a refund if possible."
    )
    result = handle_query(message, "cust_001")
    assert result["reason"] == "low_confidence"
