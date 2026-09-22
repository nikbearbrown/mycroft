import unittest

from lloyds_pipeline.mock_data import MOCK_TRANSACTIONS
from lloyds_pipeline.models import ClassificationResult
from lloyds_pipeline.retrieval import retrieve_and_match


class TestRetrieval(unittest.TestCase):

    def test_no_matching_record_when_date_has_no_transactions(self):
        classification = ClassificationResult(
            query_type="transaction_lookup",
            extracted_amount=42.50,
            extracted_date="1999-01-01",
        )
        result = retrieve_and_match(classification, MOCK_TRANSACTIONS)
        self.assertEqual(result.status, "no_matching_record")
        self.assertIsNone(result.record)

    def test_record_mismatch_when_date_has_transactions_but_amount_disagrees(self):
        classification = ClassificationResult(
            query_type="transaction_lookup",
            extracted_amount=999.99,
            extracted_date="2026-06-15",
        )
        result = retrieve_and_match(classification, MOCK_TRANSACTIONS)
        self.assertEqual(result.status, "record_mismatch")
        self.assertIsNone(result.record)

    def test_matched_when_amount_and_date_agree(self):
        classification = ClassificationResult(
            query_type="transaction_lookup",
            extracted_amount=42.50,
            extracted_date="2026-06-15",
        )
        result = retrieve_and_match(classification, MOCK_TRANSACTIONS)
        self.assertEqual(result.status, "matched")
        self.assertIsNotNone(result.record)
        self.assertEqual(result.record.merchant, "Greggs")

    def test_matched_correctly_picks_among_multiple_same_day_transactions(self):
        # 2026-06-10 has two transactions; the amount should disambiguate.
        classification = ClassificationResult(
            query_type="transaction_lookup",
            extracted_amount=12.30,
            extracted_date="2026-06-10",
        )
        result = retrieve_and_match(classification, MOCK_TRANSACTIONS)
        self.assertEqual(result.status, "matched")
        self.assertEqual(result.record.merchant, "TfL")


if __name__ == "__main__":
    unittest.main()
