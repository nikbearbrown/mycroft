import unittest

from lloyds_pipeline.intake import classify_query
from lloyds_pipeline.models import Query


class TestIntakeClassification(unittest.TestCase):

    def test_classifies_transaction_query(self):
        q = Query(raw_text="What was that £42.50 charge on 15 June?",
                  claimed_amount=42.50, claimed_date="2026-06-15")
        result = classify_query(q)
        self.assertEqual(result.query_type, "transaction_lookup")

    def test_transaction_classification_carries_extracted_details_forward(self):
        q = Query(raw_text="I don't recognize a payment for £89.99",
                  claimed_amount=89.99, claimed_date="2026-06-10")
        result = classify_query(q)
        self.assertEqual(result.extracted_amount, 89.99)
        self.assertEqual(result.extracted_date, "2026-06-10")

    def test_classifies_coaching_query(self):
        q = Query(raw_text="Can you help me set a budget so I can start saving?")
        result = classify_query(q)
        self.assertEqual(result.query_type, "coaching")

    def test_unclassifiable_on_query_matching_neither_keyword_set(self):
        q = Query(raw_text="Can you update my home address on file?")
        result = classify_query(q)
        self.assertEqual(result.query_type, "unclassifiable")

    def test_unclassifiable_on_query_matching_both_keyword_sets(self):
        # A query that plausibly touches both a specific charge and a
        # general savings goal is treated as ambiguous rather than
        # arbitrarily assigned to one category.
        q = Query(raw_text="That withdrawal is throwing off my savings budget")
        result = classify_query(q)
        self.assertEqual(result.query_type, "unclassifiable")


if __name__ == "__main__":
    unittest.main()
