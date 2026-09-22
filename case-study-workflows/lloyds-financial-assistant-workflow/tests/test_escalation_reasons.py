import unittest

from lloyds_pipeline.mock_data import MOCK_TRANSACTIONS
from lloyds_pipeline.models import Query
from lloyds_pipeline.orchestrator import FinancialAssistantPipeline


def always_true(ctx):
    return True


def always_false(ctx):
    return False


class TestEveryEscalationReasonIsIndependentlyReachable(unittest.TestCase):
    """
    Confirms all six terminal outcomes named in the Section 4 workflow
    summary table are each independently reachable, with the correct
    status/reason attached -- not just that the pipeline runs without
    crashing.
    """

    def setUp(self):
        self.pipeline = FinancialAssistantPipeline(
            decision_fn=always_true, transactions=MOCK_TRANSACTIONS
        )

    def test_malformed_query_input(self):
        result = self.pipeline.process(Query(raw_text=None))
        self.assertEqual((result.status, result.reason),
                          ("escalated_to_human", "malformed_query_input"))

    def test_unparseable_date_format(self):
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=42.50, claimed_date="2026-6-15")
        )
        self.assertEqual((result.status, result.reason),
                          ("escalated_to_human", "unparseable_date_format"))

    def test_unclassified_query(self):
        result = self.pipeline.process(Query(raw_text="Please close my account"))
        self.assertEqual((result.status, result.reason),
                          ("escalated_to_human", "unclassified_query"))

    def test_coaching_out_of_scope(self):
        result = self.pipeline.process(Query(raw_text="How can I save more each month?"))
        self.assertEqual((result.status, result.reason),
                          ("recognized_not_modeled", "coaching_out_of_scope"))

    def test_incomplete_claim_details_missing_date(self):
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=42.50, claimed_date=None)
        )
        self.assertEqual((result.status, result.reason),
                          ("escalated_to_human", "incomplete_claim_details"))

    def test_incomplete_claim_details_missing_amount(self):
        result = self.pipeline.process(
            Query(raw_text="What was that payment on 15 June?", claimed_amount=None, claimed_date="2026-06-15")
        )
        self.assertEqual((result.status, result.reason),
                          ("escalated_to_human", "incomplete_claim_details"))

    def test_no_matching_record(self):
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=42.50, claimed_date="2020-01-01")
        )
        self.assertEqual((result.status, result.reason),
                          ("escalated_to_human", "no_matching_record"))

    def test_record_mismatch(self):
        result = self.pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=1.00, claimed_date="2026-06-15")
        )
        self.assertEqual((result.status, result.reason),
                          ("escalated_to_human", "record_mismatch"))

    def test_gate_declined(self):
        pipeline = FinancialAssistantPipeline(
            decision_fn=always_false, transactions=MOCK_TRANSACTIONS
        )
        result = pipeline.process(
            Query(raw_text="What was that charge?", claimed_amount=42.50, claimed_date="2026-06-15")
        )
        self.assertEqual((result.status, result.reason),
                          ("escalated_to_human", "gate_declined"))


if __name__ == "__main__":
    unittest.main()
