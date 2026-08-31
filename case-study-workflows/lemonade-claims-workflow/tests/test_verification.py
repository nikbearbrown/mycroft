import unittest
from unittest.mock import Mock

from verification import Verification, VerifiedClaim, VerificationEscalation
from intake import ExtractedFields


def make_extracted(diagnosis="kennel cough", amount=120.0, date="2026-05-01"):
    return ExtractedFields(
        claim_type="pet_illness_reimbursement", diagnosis=diagnosis,
        amount=amount, date=date, confidence=0.95,
    )


class VerificationTests(unittest.TestCase):
    def test_missing_fields_escalates_before_any_lookup(self):
        policy_visit_lookup = Mock()
        fraud_signal_lookup = Mock()
        verification = Verification(policy_visit_lookup, fraud_signal_lookup, matching_tolerance=0.05)

        extracted = make_extracted(amount=None)
        result = verification.process(extracted, "cust", "policy")

        self.assertIsInstance(result, VerificationEscalation)
        self.assertEqual(result.reason, "incomplete_extraction")
        policy_visit_lookup.assert_not_called()
        fraud_signal_lookup.assert_not_called()

    def test_no_record_found_escalates_before_fraud_check_and_comparison(self):
        policy_visit_lookup = Mock(return_value=None)
        fraud_signal_lookup = Mock()
        verification = Verification(policy_visit_lookup, fraud_signal_lookup, matching_tolerance=0.05)

        result = verification.process(make_extracted(), "unknown_cust", "unknown_policy")

        self.assertIsInstance(result, VerificationEscalation)
        self.assertEqual(result.reason, "no_record_found")
        fraud_signal_lookup.assert_not_called()

    def test_fraud_flag_fires_even_when_record_otherwise_matches_perfectly(self):
        # This is the test that actually proves the two mock sources are
        # independent, not just the /v2 diagram.
        record = {"diagnosis": "kennel cough", "amount": 120.0, "date": "2026-05-01"}
        policy_visit_lookup = Mock(return_value=record)
        fraud_signal_lookup = Mock(return_value=True)
        verification = Verification(policy_visit_lookup, fraud_signal_lookup, matching_tolerance=0.05)

        result = verification.process(make_extracted(), "cust", "policy")

        self.assertIsInstance(result, VerificationEscalation)
        self.assertEqual(result.reason, "fraud_flag")

    def test_amount_outside_tolerance_escalates_as_mismatch(self):
        record = {"diagnosis": "ear infection", "amount": 200.0, "date": "2026-03-01"}
        policy_visit_lookup = Mock(return_value=record)
        fraud_signal_lookup = Mock(return_value=False)
        verification = Verification(policy_visit_lookup, fraud_signal_lookup, matching_tolerance=0.05)

        extracted = make_extracted(diagnosis="ear infection", amount=50.0, date="2026-03-01")
        result = verification.process(extracted, "cust", "policy")

        self.assertIsInstance(result, VerificationEscalation)
        self.assertEqual(result.reason, "mismatch")

    def test_everything_within_tolerance_returns_verified_claim(self):
        record = {"diagnosis": "kennel cough", "amount": 120.0, "date": "2026-05-01"}
        policy_visit_lookup = Mock(return_value=record)
        fraud_signal_lookup = Mock(return_value=False)
        verification = Verification(policy_visit_lookup, fraud_signal_lookup, matching_tolerance=0.05)

        result = verification.process(make_extracted(), "cust", "policy")

        self.assertIsInstance(result, VerifiedClaim)
        self.assertEqual(result.diagnosis, "kennel cough")
        self.assertEqual(result.amount, 120.0)

    def test_matching_tolerance_is_read_from_configuration_not_hardcoded(self):
        # Same claim/record pair, two different tolerances -> two different
        # outcomes. Proves the second /v2 Configuration-edge fix holds in code.
        record = {"diagnosis": "kennel cough", "amount": 100.0, "date": "2026-05-01"}
        extracted = make_extracted(diagnosis="kennel cough", amount=110.0, date="2026-05-01")

        strict = Verification(Mock(return_value=record), Mock(return_value=False), matching_tolerance=0.01)
        lenient = Verification(Mock(return_value=record), Mock(return_value=False), matching_tolerance=0.20)

        strict_result = strict.process(extracted, "cust", "policy")
        lenient_result = lenient.process(extracted, "cust", "policy")

        self.assertIsInstance(strict_result, VerificationEscalation)
        self.assertEqual(strict_result.reason, "mismatch")
        self.assertIsInstance(lenient_result, VerifiedClaim)


if __name__ == "__main__":
    unittest.main()
