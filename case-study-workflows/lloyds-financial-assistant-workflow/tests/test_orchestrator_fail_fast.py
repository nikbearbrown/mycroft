import unittest
from unittest.mock import patch

from lloyds_pipeline.mock_data import MOCK_TRANSACTIONS
from lloyds_pipeline.models import Query
from lloyds_pipeline.orchestrator import FinancialAssistantPipeline


def always_true(ctx):
    return True


class TestFailFastSequencing(unittest.TestCase):
    """
    These tests prove sequencing directly via mock/spy assertions --
    confirming not only that an escalated query carries the correct
    reason, but that LATER STAGES WERE NEVER CALLED AT ALL. That is the
    actual proof of the fail-fast guarantee, not an assumption resting on
    the design description alone.
    """

    def setUp(self):
        self.pipeline = FinancialAssistantPipeline(
            decision_fn=always_true, transactions=MOCK_TRANSACTIONS
        )

    @patch("lloyds_pipeline.orchestrator.retrieve_and_match")
    def test_malformed_raw_text_never_calls_retrieval(self, mock_retrieve):
        result = self.pipeline.process(Query(raw_text=None))
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "malformed_query_input")
        mock_retrieve.assert_not_called()

    @patch("lloyds_pipeline.orchestrator.retrieve_and_match")
    def test_malformed_amount_never_calls_retrieval(self, mock_retrieve):
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount="not a number", claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "malformed_query_input")
        mock_retrieve.assert_not_called()

    @patch("lloyds_pipeline.orchestrator.retrieve_and_match")
    def test_malformed_date_never_calls_retrieval(self, mock_retrieve):
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=42.50, claimed_date="2026-6-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "unparseable_date_format")
        mock_retrieve.assert_not_called()

    @patch("lloyds_pipeline.orchestrator.retrieve_and_match")
    def test_unclassifiable_query_never_calls_retrieval(self, mock_retrieve):
        result = self.pipeline.process(Query(raw_text="Please update my address"))
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "unclassified_query")
        mock_retrieve.assert_not_called()

    @patch("lloyds_pipeline.orchestrator.retrieve_and_match")
    def test_coaching_query_never_calls_retrieval(self, mock_retrieve):
        result = self.pipeline.process(Query(raw_text="Help me build a budget"))
        self.assertEqual(result.status, "recognized_not_modeled")
        self.assertEqual(result.reason, "coaching_out_of_scope")
        mock_retrieve.assert_not_called()

    @patch("lloyds_pipeline.orchestrator.retrieve_and_match")
    def test_incomplete_transaction_details_never_calls_retrieval(self, mock_retrieve):
        # A transaction-shaped query with no date supplied at all.
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=42.50, claimed_date=None)
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "incomplete_claim_details")
        mock_retrieve.assert_not_called()

    def test_no_matching_record_never_reaches_gate(self):
        # Spy on the Gate itself to prove it's never consulted.
        gate_spy_calls = []

        def spying_decision_fn(ctx):
            gate_spy_calls.append(ctx)
            return True

        pipeline = FinancialAssistantPipeline(
            decision_fn=spying_decision_fn, transactions=MOCK_TRANSACTIONS
        )
        result = pipeline.process(
            Query(raw_text="What was that payment?", claimed_amount=42.50, claimed_date="1999-01-01")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "no_matching_record")
        self.assertEqual(gate_spy_calls, [], "Gate's decision_fn must not be called on no_matching_record")

    def test_record_mismatch_never_reaches_gate(self):
        gate_spy_calls = []

        def spying_decision_fn(ctx):
            gate_spy_calls.append(ctx)
            return True

        pipeline = FinancialAssistantPipeline(
            decision_fn=spying_decision_fn, transactions=MOCK_TRANSACTIONS
        )
        result = pipeline.process(
            Query(raw_text="What was that payment?", claimed_amount=999.99, claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "escalated_to_human")
        self.assertEqual(result.reason, "record_mismatch")
        self.assertEqual(gate_spy_calls, [], "Gate's decision_fn must not be called on record_mismatch")

    def test_gate_is_reached_only_when_retrieval_actually_matched(self):
        gate_spy_calls = []

        def spying_decision_fn(ctx):
            gate_spy_calls.append(ctx)
            return True

        pipeline = FinancialAssistantPipeline(
            decision_fn=spying_decision_fn, transactions=MOCK_TRANSACTIONS
        )
        result = pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=42.50, claimed_date="2026-06-15")
        )
        self.assertEqual(result.status, "answered_directly")
        self.assertEqual(len(gate_spy_calls), 1, "Gate should be consulted exactly once on a real match")


if __name__ == "__main__":
    unittest.main()
