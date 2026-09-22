import math
import unittest

from lloyds_pipeline.intake import classify_query
from lloyds_pipeline.models import Query
from lloyds_pipeline.orchestrator import FinancialAssistantPipeline
from lloyds_pipeline.mock_data import MOCK_TRANSACTIONS


def always_true(ctx):
    return True


class TestAdversarialEdgeCases(unittest.TestCase):
    """
    Regression tests for defects an adversarial testing pass actually
    found in an earlier version of this pipeline (see README, 'What
    building it surfaced'). Each test here corresponds to a real,
    reproduced failure before the corresponding fix in intake.py:

      1. raw_text=None or a non-string raw_text crashed with an
         unhandled AttributeError.
      2. A non-numeric claimed_amount (e.g. the string "42.50") crashed
         with an unhandled TypeError once it reached Retrieval's
         arithmetic.
      3. A non-zero-padded or otherwise malformed date SILENTLY reported
         no_matching_record -- a false claim, since the transaction
         existed under a different date-string representation. This is
         arguably worse than a crash: it looked like a correct answer.

    These tests exist so none of the three can silently regress.
    """

    def setUp(self):
        self.pipeline = FinancialAssistantPipeline(
            decision_fn=always_true, transactions=MOCK_TRANSACTIONS
        )

    # --- Defect 1: non-string raw_text -----------------------------------

    def test_none_raw_text_does_not_crash_and_escalates_as_malformed(self):
        result = self.pipeline.process(
            Query(raw_text=None, claimed_amount=42.50, claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "malformed_query_input")

    def test_integer_raw_text_does_not_crash_and_escalates_as_malformed(self):
        result = self.pipeline.process(
            Query(raw_text=12345, claimed_amount=42.50, claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "malformed_query_input")

    # --- Defect 2: non-numeric claimed_amount -----------------------------

    def test_string_amount_does_not_crash_and_escalates_as_malformed(self):
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount="42.50", claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "malformed_query_input")

    def test_nan_amount_is_rejected_as_malformed_rather_than_silently_mismatched(self):
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=float("nan"), claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "malformed_query_input")

    def test_bool_amount_is_rejected_even_though_bool_is_a_python_int_subclass(self):
        # Python's bool is technically a subclass of int -- True == 1.
        # Without an explicit check, this would silently pass as amount=1.
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=True, claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "malformed_query_input")

    # --- Defect 3: malformed date silently misreported as no_matching_record --

    def test_non_zero_padded_date_is_flagged_as_unparseable_not_no_matching_record(self):
        # 2026-06-15 genuinely has a transaction in mock_data.py. Claiming
        # it as "2026-6-15" must NOT come back as "no_matching_record" --
        # that would assert a transaction doesn't exist when it does.
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=42.50, claimed_date="2026-6-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "unparseable_date_format")
        self.assertNotEqual(result.reason, "no_matching_record")

    def test_integer_date_is_flagged_as_unparseable(self):
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=42.50, claimed_date=20260615)
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "unparseable_date_format")

    # --- Regression checks: things that were NEVER broken, confirmed still fine --

    def test_clean_valid_query_is_unaffected_by_the_new_validation(self):
        result = self.pipeline.process(
            Query(raw_text="What was that £42.50 charge on 15 June?",
                  claimed_amount=42.50, claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "answered_directly")

    def test_negative_amount_is_a_valid_number_and_safely_mismatches(self):
        # A negative amount is a real, finite number -- just the wrong
        # one. It should reach Retrieval and mismatch, not be rejected
        # as malformed input.
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=-42.50, claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "record_mismatch")

    def test_infinite_amount_is_a_valid_float_and_safely_mismatches(self):
        # math.isnan(inf) is False -- infinity is finite-typed and not
        # rejected by the NaN check. It correctly falls through to a
        # mismatch rather than a crash or a false match.
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=float("inf"), claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "record_mismatch")

    def test_floating_point_boundary_exactly_at_tolerance_still_matches(self):
        # 42.51 - 42.50 in floating point is 0.00999999999999801, not
        # exactly 0.01 -- confirms the <= tolerance check isn't broken
        # by float imprecision at the boundary.
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=42.51, claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "answered_directly")

    def test_amount_just_outside_tolerance_correctly_mismatches(self):
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=42.52, claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "record_mismatch")


class TestIntakeValidationHelpersDirectly(unittest.TestCase):
    """Unit-level tests on the two new validation helpers, in isolation."""

    def test_classify_query_rejects_non_string_raw_text_before_any_keyword_logic(self):
        result = classify_query(Query(raw_text=None))
        self.assertEqual(result.query_type, "malformed_input")

    def test_classify_query_accepts_valid_iso_date(self):
        result = classify_query(
            Query(raw_text="What was that charge?", claimed_amount=1.0, claimed_date="2026-01-05")
        )
        self.assertEqual(result.query_type, "transaction_lookup")

    def test_classify_query_rejects_date_missing_zero_padding(self):
        result = classify_query(
            Query(raw_text="What was that charge?", claimed_amount=1.0, claimed_date="2026-1-5")
        )
        self.assertEqual(result.query_type, "malformed_date")


if __name__ == "__main__":
    unittest.main()
