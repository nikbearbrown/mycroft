import sys
import os
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from coverage_check import check_coverage
import mock_data


class TestCoverageCheck(unittest.TestCase):
    def test_happy_path_resolves_covered(self):
        claim = mock_data.CLAIM_KWAME_HAPPY_PATH
        result = check_coverage(claim["claim_id"], claim["policy_id"], claim["documents"])
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["coverage_result"]["flight_cancellation_covered"])
        self.assertTrue(result["coverage_result"]["tour_covered"])

    def test_cross_document_contradiction_halts(self):
        claim = mock_data.CLAIM_CROSS_DOCUMENT_CONTRADICTION
        result = check_coverage(claim["claim_id"], claim["policy_id"], claim["documents"])
        self.assertEqual(result["status"], "halted")
        self.assertEqual(result["reason"], "cross_document_contradiction")

    def test_no_matching_policy_halts(self):
        claim = mock_data.CLAIM_NO_MATCHING_POLICY
        result = check_coverage(claim["claim_id"], claim["policy_id"], claim["documents"])
        self.assertEqual(result["status"], "halted")
        self.assertEqual(result["reason"], "no_matching_policy")

    def test_unresolvable_sub_claim_dependency_halts(self):
        claim = mock_data.CLAIM_UNRESOLVABLE_DEPENDENCY
        result = check_coverage(claim["claim_id"], claim["policy_id"], claim["documents"])
        self.assertEqual(result["status"], "halted")
        self.assertEqual(result["reason"], "unresolvable_sub_claim_dependency")

    def test_tour_sub_claim_outcome_changes_with_flight_outcome(self):
        """
        Proves the multi-sub-claim dependency logic actually changes based on
        the flight-cancellation sub-claim's outcome, not just described as
        dependent (blueprint Sec 7 requirement).
        """
        covered_claim = mock_data.CLAIM_KWAME_HAPPY_PATH
        covered_result = check_coverage(
            covered_claim["claim_id"], covered_claim["policy_id"], covered_claim["documents"]
        )
        self.assertTrue(covered_result["coverage_result"]["flight_cancellation_covered"])
        self.assertTrue(covered_result["coverage_result"]["tour_covered"])

        # Same shape of claim, but flight reason is NOT a covered reason,
        # and the policy has a definite (non-ambiguous) stance on dependent
        # sub-claims, so the tour claim resolves to explicitly not covered
        # rather than unresolvable.
        not_covered_documents = [
            {
                "type": "flight_notice",
                "language": "en",
                "extraction_confidence": 0.95,
                "translation_confidence": None,
                "extracted_date": date(2026, 6, 10),
                "extracted_reason": "voluntary_change",  # not a covered reason
            },
            {
                "type": "free_text_note",
                "language": "en",
                "extraction_confidence": 0.9,
                "translation_confidence": None,
                "extracted_amount": 200.0,
                "extracted_currency": "USD",
                "tour_booking_date": date(2026, 5, 1),
                "claims_dependent_on": "flight_notice",
            },
        ]
        not_covered_result = check_coverage("CLAIM-VARIANT", "POLICY-001", not_covered_documents)
        self.assertEqual(not_covered_result["status"], "ok")
        self.assertFalse(not_covered_result["coverage_result"]["flight_cancellation_covered"])
        self.assertFalse(not_covered_result["coverage_result"]["tour_covered"])

        self.assertNotEqual(
            covered_result["coverage_result"]["tour_covered"],
            not_covered_result["coverage_result"]["tour_covered"],
        )

    def test_contradiction_fires_before_no_matching_policy_when_both_present(self):
        """
        Locks Decision C's ordering: contradiction check runs before policy
        fetch, so a claim triggering both conditions deterministically
        returns cross_document_contradiction, not no_matching_policy.
        """
        documents = [
            {
                "type": "flight_notice",
                "language": "en",
                "extraction_confidence": 0.95,
                "translation_confidence": None,
                "extracted_date": date(2026, 6, 10),
                "extracted_reason": "airline_operational",
            },
            {
                "type": "medical_receipt",
                "language": "th",
                "extraction_confidence": 0.94,
                "translation_confidence": 0.9,
                "extracted_date": date(2026, 3, 1),  # contradicts flight date
                "extracted_amount": 80.0,
                "extracted_currency": "USD",
            },
        ]
        result = check_coverage("CLAIM-BOTH", "POLICY-DOES-NOT-EXIST", documents)
        self.assertEqual(result["status"], "halted")
        self.assertEqual(result["reason"], "cross_document_contradiction")


if __name__ == "__main__":
    unittest.main()
