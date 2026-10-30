from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from mycroft_finance_investigator.freshness import (
    FreshnessError,
    assess,
    period_end,
    read_provenance,
)


class FreshnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.verified = Path(self.temporary.name)
        self._write_provenance()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_provenance(self, **overrides: object) -> None:
        payload = {
            "classification": "synthetic_sample",
            "origin": "Created locally for tests",
            "created_on": "2026-03-10",
            "entity": "Northstar Software Sample",
            "period": "2026-02",
        }
        payload.update(overrides)
        (self.verified / "provenance.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    # --- period arithmetic ----------------------------------------------

    def test_period_end_handles_month_lengths(self) -> None:
        self.assertEqual(period_end("2026-02"), date(2026, 2, 28))
        self.assertEqual(period_end("2024-02"), date(2024, 2, 29))  # leap year
        self.assertEqual(period_end("2026-12"), date(2026, 12, 31))

    def test_period_end_refuses_a_bad_period(self) -> None:
        for bad in ("2026-13", "2026", "February"):
            with self.subTest(period=bad):
                with self.assertRaises(FreshnessError):
                    period_end(bad)

    # --- provenance is required ------------------------------------------

    def test_missing_provenance_is_refused_not_assumed_fresh(self) -> None:
        (self.verified / "provenance.json").unlink()
        with self.assertRaises(FreshnessError):
            read_provenance(self.verified)

    def test_incomplete_provenance_is_refused(self) -> None:
        self._write_provenance(created_on="")
        with self.assertRaises(FreshnessError):
            read_provenance(self.verified)

    # --- the impossibility check -----------------------------------------

    def test_data_created_before_the_period_closed_is_refused(self) -> None:
        self._write_provenance(created_on="2026-02-10")  # period ends 02-28
        with self.assertRaises(FreshnessError) as caught:
            assess(self.verified, date(2026, 3, 1), 30, 365)
        self.assertIn("cannot describe a period that had not finished",
                      str(caught.exception))

    def test_created_on_exactly_at_period_end_is_allowed(self) -> None:
        self._write_provenance(created_on="2026-02-28")
        result = assess(self.verified, date(2026, 3, 1), 30, 365)
        self.assertEqual(result["lag_days"], 0)

    def test_as_of_before_creation_is_refused(self) -> None:
        with self.assertRaises(FreshnessError):
            assess(self.verified, date(2026, 1, 1), 30, 365)

    # --- the two gaps -----------------------------------------------------

    def test_fresh_inside_both_limits(self) -> None:
        result = assess(self.verified, date(2026, 3, 20), 30, 365)
        self.assertEqual(result["verdict"], "FRESH")
        self.assertEqual(result["lag_days"], 10)   # 02-28 -> 03-10
        self.assertEqual(result["age_days"], 10)   # 03-10 -> 03-20
        self.assertEqual(result["reasons"], [])

    def test_stale_when_the_data_took_too_long_to_arrive(self) -> None:
        self._write_provenance(created_on="2026-07-26")
        result = assess(self.verified, date(2026, 8, 1), 30, 365)
        self.assertEqual(result["verdict"], "STALE")
        self.assertEqual(result["lag_days"], 148)
        self.assertTrue(any("after the period closed" in r for r in result["reasons"]))

    def test_expired_when_the_data_has_sat_too_long(self) -> None:
        result = assess(self.verified, date(2027, 6, 1), 30, 60)
        self.assertEqual(result["verdict"], "EXPIRED")
        self.assertTrue(any("old at time of use" in r for r in result["reasons"]))

    def test_both_gaps_report_both_reasons(self) -> None:
        self._write_provenance(created_on="2026-07-26")
        result = assess(self.verified, date(2027, 6, 1), 30, 60)
        self.assertEqual(result["verdict"], "EXPIRED")
        self.assertEqual(len(result["reasons"]), 2)

    def test_limits_are_boundaries_not_approximations(self) -> None:
        # lag is exactly 10 days; a limit of 10 passes, 9 does not.
        self.assertEqual(assess(self.verified, date(2026, 3, 20), 10, 365)["verdict"],
                         "FRESH")
        self.assertEqual(assess(self.verified, date(2026, 3, 20), 9, 365)["verdict"],
                         "STALE")

    def test_negative_limits_are_refused(self) -> None:
        with self.assertRaises(FreshnessError):
            assess(self.verified, date(2026, 3, 20), -1, 365)

    def test_classification_is_carried_through(self) -> None:
        result = assess(self.verified, date(2026, 3, 20), 30, 365)
        self.assertEqual(result["classification"], "synthetic_sample")


if __name__ == "__main__":
    unittest.main()
