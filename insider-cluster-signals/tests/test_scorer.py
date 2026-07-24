"""Tests for signal_scorer.py classification rules (trade-time info only).
Run from insider-cluster-signals/: python -m unittest discover tests
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("signal_scorer", MODULE_DIR / "signal_scorer.py")
signal_scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(signal_scorer)


def _cluster(n_insiders=2, conviction=2.5, value=200_000.0, roles=("officer", "director"),
             alpha=None):
    return {
        "ticker": "FIXT", "n_insiders": n_insiders, "weighted_conviction": conviction,
        "total_value_usd": value, "mean_alpha_30d": alpha,
        "window": {"start": "2026-03-01", "end": "2026-03-10"},
        "members": [{"role": r} for r in roles],
    }


class TestClassify(unittest.TestCase):
    def test_three_insiders_is_strong(self):
        tier, _ = signal_scorer.classify(_cluster(n_insiders=3, conviction=2.0, value=50_000))
        self.assertEqual(tier, "STRONG")

    def test_high_conviction_and_value_is_strong(self):
        tier, _ = signal_scorer.classify(_cluster(n_insiders=2, conviction=2.5, value=150_000))
        self.assertEqual(tier, "STRONG")

    def test_two_insiders_low_value_is_watch(self):
        tier, _ = signal_scorer.classify(_cluster(n_insiders=2, conviction=2.0, value=60_000))
        self.assertEqual(tier, "WATCH")

    def test_below_noise_floor_is_skip(self):
        tier, reason = signal_scorer.classify(_cluster(value=10_000))
        self.assertEqual(tier, "SKIP")
        self.assertIn("noise floor", reason)

    def test_pure_holder_cluster_is_skip_even_when_large(self):
        tier, reason = signal_scorer.classify(
            _cluster(n_insiders=4, conviction=3.0, value=5_000_000, roles=("ten_percent_owner", "other"))
        )
        self.assertEqual(tier, "SKIP")
        self.assertIn("mechanical", reason)

    def test_alpha_never_affects_classification(self):
        # Identical clusters, wildly different outcomes -> identical tier (no look-ahead).
        great = signal_scorer.classify(_cluster(alpha=50.0))
        awful = signal_scorer.classify(_cluster(alpha=-50.0))
        self.assertEqual(great, awful)

    def test_rank_score_monotonic_in_value(self):
        small = signal_scorer.rank_score(_cluster(value=100_000))
        large = signal_scorer.rank_score(_cluster(value=10_000_000))
        self.assertGreater(large, small)


if __name__ == "__main__":
    unittest.main()
