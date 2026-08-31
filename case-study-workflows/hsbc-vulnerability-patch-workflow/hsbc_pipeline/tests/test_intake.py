import unittest
from hsbc_pipeline.models import VulnerabilityReport
from hsbc_pipeline.intake import validate_vulnerability_report


class TestIntake(unittest.TestCase):
    def test_valid_report_passes(self):
        r = VulnerabilityReport(id="V1", file_path="a.py", description="SQL injection risk")
        validated = validate_vulnerability_report(r)
        self.assertEqual(validated.id, "V1")

    def test_missing_file_path_raises(self):
        r = VulnerabilityReport(id="V1", file_path="", description="desc")
        with self.assertRaises(ValueError):
            validate_vulnerability_report(r)

    def test_missing_description_raises(self):
        r = VulnerabilityReport(id="V1", file_path="a.py", description="")
        with self.assertRaises(ValueError):
            validate_vulnerability_report(r)

    def test_missing_id_raises(self):
        r = VulnerabilityReport(id="", file_path="a.py", description="desc")
        with self.assertRaises(ValueError):
            validate_vulnerability_report(r)


if __name__ == "__main__":
    unittest.main()
