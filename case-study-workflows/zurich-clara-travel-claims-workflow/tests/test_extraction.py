import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from extraction import extract
import mock_data


class TestExtraction(unittest.TestCase):
    def test_happy_path_passes(self):
        result = extract(mock_data.CLAIM_KWAME_HAPPY_PATH["documents"])
        self.assertEqual(result["status"], "ok")

    def test_low_extraction_confidence_halts(self):
        result = extract(mock_data.CLAIM_LOW_EXTRACTION_CONFIDENCE["documents"])
        self.assertEqual(result["status"], "halted")
        self.assertEqual(result["reason"], "low_extraction_confidence")

    def test_low_translation_confidence_halts(self):
        result = extract(mock_data.CLAIM_LOW_TRANSLATION_CONFIDENCE["documents"])
        self.assertEqual(result["status"], "halted")
        self.assertEqual(result["reason"], "low_translation_confidence")

    def test_extraction_and_translation_confidence_are_independent(self):
        """
        Proves the separation matters, per blueprint Sec 4.2 / 7: a case with
        high translation confidence but low extraction confidence, and the
        reverse, must produce DIFFERENT escalation reasons.
        """
        low_extraction_result = extract(mock_data.CLAIM_LOW_EXTRACTION_CONFIDENCE["documents"])
        low_translation_result = extract(mock_data.CLAIM_LOW_TRANSLATION_CONFIDENCE["documents"])

        self.assertNotEqual(low_extraction_result["reason"], low_translation_result["reason"])
        self.assertEqual(low_extraction_result["reason"], "low_extraction_confidence")
        self.assertEqual(low_translation_result["reason"], "low_translation_confidence")


if __name__ == "__main__":
    unittest.main()
