import ast
import inspect
import unittest

import mock_policy_visit_records
from fixtures import SOFIA_CUSTOMER_ID, SOFIA_POLICY_ID, MOCK_VISIT_RECORDS


class MockPolicyVisitRecordsTests(unittest.TestCase):
    def test_lookup_on_known_customer_returns_expected_record(self):
        record = mock_policy_visit_records.lookup(SOFIA_CUSTOMER_ID, SOFIA_POLICY_ID)

        self.assertIsNotNone(record)
        self.assertEqual(record["diagnosis"], "kennel cough")
        self.assertEqual(record["amount"], 120.0)

    def test_lookup_on_unknown_identifier_returns_none(self):
        record = mock_policy_visit_records.lookup("nobody", "no_policy")

        self.assertIsNone(record)

    def test_visit_records_have_no_fraud_related_field(self):
        # Asserting an absence - given the specific conflation risk named in
        # /v2 (folding Forensic-Graph-equivalent fraud detection into the
        # same record as policy/visit data), this fails loudly if that
        # boundary ever erodes rather than relying on code review to catch it.
        for record in MOCK_VISIT_RECORDS.values():
            self.assertNotIn("fraud", {key.lower() for key in record.keys()})

    def test_module_has_no_import_of_mock_fraud_signal(self):
        # Mirror of mock_fraud_signal's own independence test - the
        # guarantee is enforced from both sides, per /review Finding 4.
        source = inspect.getsource(mock_policy_visit_records)
        tree = ast.parse(source)
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_names.add(node.module)

        self.assertFalse(any("mock_fraud_signal" in name for name in imported_names))


if __name__ == "__main__":
    unittest.main()
