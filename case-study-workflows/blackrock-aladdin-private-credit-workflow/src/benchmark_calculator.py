"""
Benchmark Calculation Module.

Input: retrieved fund and asset data.
Output: computed ratios, each tagged with the source record it was derived
from — money multiple, leverage ratio, valuation trend, equity cushion, and
debt service coverage.

================================================================================
ILLUSTRATIVE — NOT RISK-REVIEWED. DO NOT USE FOR REAL CREDIT DECISIONS.
================================================================================
§3.4's own [DEV] marker says: "do not ship default thresholds without a risk
owner signing off on them." That's correct guidance for a production
deployment, and incompatible with a fork-and-learn repo, where no risk owner
exists. This repo's resolution — an explicit, documented authorial choice,
not BlackRock's — is to ship illustrative thresholds with correct formulas,
disclaimed in three places: this docstring, a runtime log line every time
this module runs, and the README.

The five ratios themselves are standard, correct private-credit math — not a
judgment call. The FLAG THRESHOLDS are common industry rule-of-thumb
reference points (leverage above 6.0x, DSCR below 1.25x, equity cushion
below 20%) included for teaching purposes — not BlackRock's actual risk
policy, and not reviewed by any risk or analytics function.

The money multiple threshold (below 1.0x) is different in kind from the
other three: it's closer to a definitional fact than a debatable cutoff —
below 1.0x means the position is worth less than what was invested, by
definition, not by house policy.
================================================================================
"""
import logging
from .models import BenchmarkResult

logger = logging.getLogger(__name__)


class BenchmarkCalculator:
    THRESHOLDS = {
        "money_multiple": 1.0,           # flag below this — capital impairment, by definition
        "leverage_ratio": 6.0,           # flag above this — illustrative rule-of-thumb
        "debt_service_coverage": 1.25,   # flag below this — illustrative rule-of-thumb
        "equity_cushion": 0.20,          # flag below this — illustrative rule-of-thumb
    }

    def run(self, fund_data: list[dict]) -> list[BenchmarkResult]:
        logger.warning(
            "BenchmarkCalculator: illustrative, non-risk-reviewed thresholds in use. "
            "Not for production credit decisions — see README."
        )
        results = []
        for record in fund_data:
            results.extend(self._compute_for_record(record))
        return results

    def _compute_for_record(self, r: dict) -> list[BenchmarkResult]:
        money_multiple = r["current_value"] / r["invested_capital"]
        leverage_ratio = r["debt_outstanding"] / r["ebitda"]
        valuation_trend = (r["current_value"] - r["prior_period_value"]) / r["prior_period_value"]
        equity_cushion = (r["current_value"] - r["debt_outstanding"]) / r["current_value"]
        dscr = r["ebitda"] / r["interest_expense"]

        t = self.THRESHOLDS
        return [
            BenchmarkResult("money_multiple", money_multiple, r["asset_id"],
                "capital impairment \u2014 below 1.0x invested capital"
                if money_multiple < t["money_multiple"] else None),
            BenchmarkResult("leverage_ratio", leverage_ratio, r["asset_id"],
                "elevated leverage" if leverage_ratio > t["leverage_ratio"] else None),
            BenchmarkResult("valuation_trend", valuation_trend, r["asset_id"],
                "declining valuation" if valuation_trend < 0 else None),
            BenchmarkResult("equity_cushion", equity_cushion, r["asset_id"],
                "thin cushion" if equity_cushion < t["equity_cushion"] else None),
            BenchmarkResult("debt_service_coverage", dscr, r["asset_id"],
                "coverage concern" if dscr < t["debt_service_coverage"] else None),
        ]
