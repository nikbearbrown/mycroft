"""
WHAT THIS FILE DOES: Evaluates an extracted claim against a mock policy
record. Owns four responsibilities, executed in a fixed order locked
during /review (Decision C): (1) cross-document contradiction check,
(2) policy record fetch, (3) three interacting coverage rules, (4) sub-
claim dependency check. The order is fixed specifically so a claim that
could trigger both a contradiction and a missing-policy halt has a
deterministic, designed answer for which fires — not an implementation
accident.

Deliberately impure: this module fetches its own policy record from
mock_data.py rather than receiving one pre-fetched (locked Option B in
/v2), a logged departure from this series' usual data/logic separation
(see DBS precedent). Rationale: for a thin-sourced build, the test-
isolation cost of a pure Coverage Check was judged not worth a sixth
module the blueprint never specified.

The *existence* of conditional multi-variable coverage logic here is this
case study's own construction (blueprint Section 4.3), not a Zurich
disclosure. Minimum three interacting rules is a hard floor, locked at
/v1 as one of the three non-negotiable structural guarantees — do not
collapse this into a single flat threshold under any "keep it short"
reasoning.
"""

from mock_data import get_policy_record


def check_coverage(claim_id, policy_id, documents):
    """
    Returns a status object:
      {"status": "ok", "coverage_result": {...}}
      {"status": "halted", "reason": "cross_document_contradiction", ...}
      {"status": "halted", "reason": "no_matching_policy", ...}
      {"status": "halted", "reason": "unresolvable_sub_claim_dependency", ...}
    """
    # Step 1 — contradiction check (fixed first per Decision C; does not
    # require a policy record).
    contradiction = _check_cross_document_contradiction(documents)
    if contradiction:
        return {"status": "halted", "reason": "cross_document_contradiction", "detail": contradiction}

    # Step 2 — policy fetch.
    policy = get_policy_record(policy_id)
    if policy is None:
        return {"status": "halted", "reason": "no_matching_policy", "detail": f"policy_id={policy_id}"}

    # Step 3 — three interacting coverage rules.
    flight_doc = _find_document(documents, "flight_notice")
    reason_covered = (
        flight_doc is not None
        and flight_doc.get("extracted_reason") in policy["covered_cancellation_reasons"]
    )
    timing_covered = (
        flight_doc is not None
        and policy["covered_window_start"] <= flight_doc.get("extracted_date") <= policy["covered_window_end"]
    )
    flight_cancellation_covered = reason_covered and timing_covered

    # Step 4 — sub-claim dependency check (last; depends on step 3's output).
    tour_doc = _find_document_by_dependency(documents, "flight_notice")
    if tour_doc is not None:
        tour_booked_before_disruption = (
            flight_doc is not None
            and tour_doc.get("tour_booking_date") is not None
            and tour_doc["tour_booking_date"] < flight_doc.get("extracted_date")
        )
        if flight_cancellation_covered:
            tour_covered = tour_booked_before_disruption
        elif policy.get("covers_dependent_sub_claims") is None:
            # Flight cancellation itself not covered, AND the policy's stance
            # on dependent sub-claims is ambiguous -- genuinely unresolvable,
            # not a guess.
            return {
                "status": "halted",
                "reason": "unresolvable_sub_claim_dependency",
                "detail": "flight cancellation not covered and policy's dependent-sub-claim coverage is ambiguous",
            }
        else:
            tour_covered = False
    else:
        tour_covered = None  # no dependent sub-claim present in this submission

    return {
        "status": "ok",
        "coverage_result": {
            "flight_cancellation_covered": flight_cancellation_covered,
            "tour_covered": tour_covered,
        },
    }


def _check_cross_document_contradiction(documents):
    """
    [DEV] illustrative contradiction rule: a medical receipt dated before
    the flight-cancellation date contradicts the claim's own narrative
    (treatment for an injury sustained during the disrupted travel).
    """
    flight_doc = _find_document(documents, "flight_notice")
    receipt_doc = _find_document(documents, "medical_receipt")
    if flight_doc is None or receipt_doc is None:
        return None

    flight_date = flight_doc.get("extracted_date")
    receipt_date = receipt_doc.get("extracted_date")
    if flight_date is not None and receipt_date is not None and receipt_date < flight_date:
        return f"medical receipt dated {receipt_date} precedes flight cancellation dated {flight_date}"

    return None


def _find_document(documents, doc_type):
    for doc in documents:
        if doc.get("type") == doc_type:
            return doc
    return None


def _find_document_by_dependency(documents, depends_on_type):
    for doc in documents:
        if doc.get("claims_dependent_on") == depends_on_type:
            return doc
    return None
