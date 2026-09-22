import unittest

from lloyds_pipeline.mock_data import MOCK_TRANSACTIONS
from lloyds_pipeline.models import Query
from lloyds_pipeline.orchestrator import FinancialAssistantPipeline


def always_true(ctx):
    return True


class TestHappyPath(unittest.TestCase):
    """Proves the resolution path works end-to-end, not only the halts."""

    def test_fiona_clean_transaction_query_is_answered_directly(self):
        pipeline = FinancialAssistantPipeline(
            decision_fn=always_true, transactions=MOCK_TRANSACTIONS
        )
        fiona_query = Query(
            raw_text="What was that £42.50 charge on 15 June?",
            claimed_amount=42.50,
            claimed_date="2026-06-15",
        )
        result = pipeline.process(fiona_query)

        self.assertEqual(result.status, "answered_directly")
        self.assertIsNone(result.reason)
        self.assertIsNotNone(result.record)
        self.assertEqual(result.record.merchant, "Greggs")
        self.assertIn("Greggs", result.detail)
        self.assertIn("42.50", result.detail)


if __name__ == "__main__":
    unittest.main()
