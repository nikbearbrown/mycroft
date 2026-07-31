"""Tests for enricher.py window math and cluster_analyzer.py detection rules.
Run from insider-cluster-signals/: python -m unittest discover tests
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, MODULE_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


enricher = _load("enricher")
cluster_analyzer = _load("cluster_analyzer")


def _trade(owner="0001", ticker="FIXT", date="2026-03-04", code="P", shares=100.0,
           price=10.0, alpha=None, officer=False, director=True, ten_pct=False):
    return {
        "accession": f"acc-{owner}-{date}", "ticker": ticker, "issuer_name": "FIXTURE CORP",
        "owner_cik": owner, "owner_name": f"OWNER {owner}", "officer_title": "",
        "is_officer": officer, "is_director": director, "is_ten_percent_owner": ten_pct,
        "transaction_code": code, "transaction_date": date,
        "shares": shares, "price_per_share": price, "alpha_30d": alpha,
    }


class TestWindowReturn(unittest.TestCase):
    # Hand-computed: buy at 100 on 03-01; +30d lands on 03-31, nearest prior close = 110
    # -> raw return exactly +10%.
    SERIES = [("2026-03-01", 100.0), ("2026-03-15", 105.0), ("2026-03-30", 110.0), ("2026-04-15", 120.0)]

    def test_hand_computed_ten_percent_return(self):
        value, reason = enricher.window_return(self.SERIES, "2026-03-01")
        self.assertIsNone(reason)
        self.assertEqual(value, 10.0)

    def test_immature_window_returns_reason_not_shorter_window(self):
        value, reason = enricher.window_return(self.SERIES, "2026-04-10")
        self.assertIsNone(value)
        self.assertIn("window not matured", reason)

    def test_nearest_prior_trading_day_lookup(self):
        # 2026-03-20 is not in the series; nearest prior close is 105 on 03-15.
        self.assertEqual(enricher.close_on_or_before(self.SERIES, "2026-03-20"), 105.0)


class TestClusterDetection(unittest.TestCase):
    def _clusters(self, trades):
        windows = cluster_analyzer.windows_by_ticker(trades)
        return [
            cluster_analyzer.build_cluster(w)
            for w in windows
            if len({t["owner_cik"] for t in w}) >= cluster_analyzer.MIN_INSIDERS
        ]

    def test_two_insiders_within_window_is_a_cluster(self):
        clusters = self._clusters([_trade("0001", date="2026-03-04"), _trade("0002", date="2026-03-20")])
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]["n_insiders"], 2)

    def test_two_insiders_31_days_apart_is_not_a_cluster(self):
        clusters = self._clusters([_trade("0001", date="2026-03-01"), _trade("0002", date="2026-04-01")])
        self.assertEqual(clusters, [])

    def test_one_insider_many_trades_is_not_a_cluster(self):
        clusters = self._clusters([_trade("0001", date="2026-03-01"), _trade("0001", date="2026-03-10")])
        self.assertEqual(clusters, [])

    def test_different_tickers_never_cluster_together(self):
        clusters = self._clusters([_trade("0001", ticker="AAA"), _trade("0002", ticker="BBB")])
        self.assertEqual(clusters, [])

    def test_role_weighted_conviction(self):
        # officer 1.5 + director 1.0 = 2.5
        clusters = self._clusters([
            _trade("0001", officer=True, director=False),
            _trade("0002", officer=False, director=True),
        ])
        self.assertEqual(clusters[0]["weighted_conviction"], 2.5)
        self.assertEqual(clusters[0]["members"][0]["role"], "officer")

    def test_mean_alpha_ignores_immature_trades(self):
        clusters = self._clusters([
            _trade("0001", alpha=4.0), _trade("0002", alpha=None), _trade("0003", alpha=6.0),
        ])
        self.assertEqual(clusters[0]["mean_alpha_30d"], 5.0)
        self.assertEqual(clusters[0]["trades_with_alpha"], 2)

    def test_cluster_traces_to_all_member_accessions(self):
        clusters = self._clusters([_trade("0001", date="2026-03-04"), _trade("0002", date="2026-03-05")])
        self.assertEqual(len(clusters[0]["accessions"]), 2)


if __name__ == "__main__":
    unittest.main()
