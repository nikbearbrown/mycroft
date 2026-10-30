from __future__ import annotations

import csv
import shutil
import tempfile
import unittest
from pathlib import Path

from mycroft_finance_investigator.validation import (
    ValidationError,
    validate_finance_pack,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
RAW_SAMPLE = REPO_ROOT / "data/raw/mycroft-finance-investigator"
SCHEMA = PROJECT_ROOT / "schemas/finance-pack.schema.json"


class ValidationTests(unittest.TestCase):
    def test_sample_pack_validates_and_writes_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            verified = Path(temporary) / "verified"
            result = validate_finance_pack(RAW_SAMPLE, verified, SCHEMA)

            self.assertEqual(sum(result.row_counts.values()), 43)
            self.assertEqual(result.row_counts["ledger.csv"], 14)
            self.assertTrue((verified / "validation-result.json").is_file())
            self.assertTrue((verified / "validation-audit.md").is_file())
            self.assertIn("PENDING_HUMAN_REVIEW", (verified / "validation-audit.md").read_text())

    def test_ledger_mismatch_is_a_hard_stop(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            raw = Path(temporary) / "raw"
            verified = Path(temporary) / "verified"
            shutil.copytree(RAW_SAMPLE, raw)
            actuals = raw / "actuals.csv"
            with actuals.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
                fields = list(rows[0])
            rows[0]["amount"] = "719999.00"
            with actuals.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)

            with self.assertRaisesRegex(ValidationError, "do not reconcile"):
                validate_finance_pack(raw, verified, SCHEMA)

    def test_unmapped_account_is_a_hard_stop(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            raw = Path(temporary) / "raw"
            verified = Path(temporary) / "verified"
            shutil.copytree(RAW_SAMPLE, raw)
            mapping = raw / "account_mapping.csv"
            lines = mapping.read_text(encoding="utf-8").splitlines()
            mapping.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(ValidationError, "unmapped accounts"):
                validate_finance_pack(raw, verified, SCHEMA)


if __name__ == "__main__":
    unittest.main()
