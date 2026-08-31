import ast
import inspect
import unittest

import mock_fraud_signal
from fixtures import FRAUD_CUSTOMER_ID, FRAUD_POLICY_ID, SOFIA_CUSTOMER_ID, SOFIA_POLICY_ID


class MockFraudSignalTests(unittest.TestCase):
    def test_check_on_known_flagged_customer_returns_true(self):
        self.assertTrue(mock_fraud_signal.check(FRAUD_CUSTOMER_ID, FRAUD_POLICY_ID, {}))

    def test_check_on_known_unflagged_customer_returns_false(self):
        self.assertFalse(mock_fraud_signal.check(SOFIA_CUSTOMER_ID, SOFIA_POLICY_ID, {}))

    def test_check_on_unknown_customer_returns_false_not_a_finding_about_records(self):
        # Absence of a fraud flag is not itself a finding about whether a
        # record exists - that distinction belongs entirely to Mock
        # Policy/Visit Records.
        self.assertFalse(mock_fraud_signal.check("nobody", "no_policy", {}))

    def test_module_has_no_import_of_mock_policy_visit_records(self):
        source = inspect.getsource(mock_fraud_signal)
        tree = ast.parse(source)
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_names.add(node.module)

        self.assertFalse(any("mock_policy_visit_records" in name for name in imported_names))


if __name__ == "__main__":
    unittest.main()
