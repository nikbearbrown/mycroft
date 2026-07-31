"""Tests for fetcher.py index parsing and accession dedupe (no network calls).
Run from insider-cluster-signals/: python -m unittest discover tests
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("fetcher", MODULE_DIR / "fetcher.py")
fetcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetcher)


def _entry(accession: str, cik: str = "0000001") -> dict:
    return {
        "cik": cik,
        "company": "FIXTURE CORP",
        "date_filed": "2026-03-02",
        "file_name": f"edgar/data/{cik}/{accession}.txt",
    }


class TestDedupeByAccession(unittest.TestCase):
    def test_joint_filer_duplicates_collapse_to_one_entry(self):
        # Same filing listed once per joint filer (different CIK, same accession).
        entries = [
            _entry("0001-26-000001", cik="0000001"),
            _entry("0001-26-000001", cik="0000002"),
            _entry("0001-26-000002", cik="0000003"),
        ]
        unique = fetcher.dedupe_by_accession(entries)
        self.assertEqual(len(unique), 2)
        self.assertEqual(
            [e["file_name"].rsplit("/", 1)[-1] for e in unique],
            ["0001-26-000001.txt", "0001-26-000002.txt"],
        )

    def test_first_seen_entry_wins(self):
        entries = [_entry("0001-26-000001", cik="0000001"), _entry("0001-26-000001", cik="0000002")]
        self.assertEqual(fetcher.dedupe_by_accession(entries)[0]["cik"], "0000001")

    def test_no_duplicates_is_identity(self):
        entries = [_entry("0001-26-000001"), _entry("0001-26-000002")]
        self.assertEqual(fetcher.dedupe_by_accession(entries), entries)

    def test_empty_input(self):
        self.assertEqual(fetcher.dedupe_by_accession([]), [])


if __name__ == "__main__":
    unittest.main()
