import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from intake import validate_intake
import mock_data


class TestIntake(unittest.TestCase):
    def test_happy_path_passes(self):
        result = validate_intake(mock_data.CLAIM_KWAME_HAPPY_PATH)
        self.assertEqual(result["status"], "ok")

    def test_no_documents_halts_structurally(self):
        result = validate_intake({"claim_id": "X", "policy_id": "POLICY-001", "documents": []})
        self.assertEqual(result["status"], "halted")
        self.assertIsNone(result["reason"])

    def test_missing_tag_halts_structurally(self):
        claim = {
            "claim_id": "X",
            "policy_id": "POLICY-001",
            "documents": [{"type": "flight_notice"}],  # missing 'language'
        }
        result = validate_intake(claim)
        self.assertEqual(result["status"], "halted")
        self.assertIsNone(result["reason"])

    def test_missing_document_reason_reachable(self):
        result = validate_intake(mock_data.CLAIM_MISSING_DOCUMENT)
        self.assertEqual(result["status"], "halted")
        self.assertEqual(result["reason"], "missing_document")


if __name__ == "__main__":
    unittest.main()
