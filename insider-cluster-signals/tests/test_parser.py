"""Tests for parser.py: multi-transaction filings, price-0 gifts, ticker validation.
Run from insider-cluster-signals/: python -m unittest discover tests
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, MODULE_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


parser = _load("parser")


class TestParseForm4(unittest.TestCase):
    def setUp(self):
        self.records = parser.parse_form4(FIXTURES / "multi_transaction_gift.xml")

    def test_multi_transaction_filing_yields_one_record_per_transaction(self):
        self.assertEqual(len(self.records), 2)

    def test_shared_filing_fields_propagate_to_every_record(self):
        for r in self.records:
            self.assertEqual(r["ticker"], "FIXT")
            self.assertEqual(r["owner_name"], "DOE JANE")
            self.assertTrue(r["is_officer"])
            self.assertEqual(r["officer_title"], "Chief Financial Officer")

    def test_purchase_and_gift_transactions_parsed_distinctly(self):
        codes = sorted(r["transaction_code"] for r in self.records)
        self.assertEqual(codes, ["G", "P"])

    def test_gift_with_price_zero_passes_validation(self):
        gift = next(r for r in self.records if r["transaction_code"] == "G")
        self.assertEqual(parser.validate(gift), [])


class TestValidate(unittest.TestCase):
    def _record(self, **overrides):
        base = {
            "ticker": "FIXT", "owner_name": "DOE JANE", "transaction_code": "P",
            "acquired_disposed": "A", "transaction_date": "2026-03-04",
            "shares": "1000", "price_per_share": "25.50",
        }
        base.update(overrides)
        return base

    def test_clean_record_passes(self):
        self.assertEqual(parser.validate(self._record()), [])

    def test_placeholder_ticker_none_rejected(self):
        failures = parser.validate(self._record(ticker="NONE"))
        self.assertTrue(any("placeholder ticker" in f for f in failures))

    def test_implausible_ticker_rejected(self):
        failures = parser.validate(self._record(ticker="not a symbol!"))
        self.assertTrue(any("not a plausible exchange symbol" in f for f in failures))

    def test_empty_ticker_rejected(self):
        self.assertIn("missing ticker", parser.validate(self._record(ticker="")))

    def test_unknown_transaction_code_rejected(self):
        failures = parser.validate(self._record(transaction_code="Q"))
        self.assertTrue(any("unknown transaction code" in f for f in failures))

    def test_bad_date_rejected(self):
        failures = parser.validate(self._record(transaction_date="03/04/2026"))
        self.assertTrue(any("unparseable transaction date" in f for f in failures))

    def test_non_numeric_shares_rejected(self):
        failures = parser.validate(self._record(shares="one thousand"))
        self.assertTrue(any("non-numeric shares" in f for f in failures))


if __name__ == "__main__":
    unittest.main()
