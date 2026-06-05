import numpy as np
from typing import List, Tuple
import logging

from app.core.config import settings
from app.models.schemas import (
    StaticRegressionResult, RollingFactorSeries, RegimeFactorLoadings
)

logger = logging.getLogger("portfolio_analysis.factor_analyzer")

FACTOR_LABELS = {
    "MKT": "Market Beta",
    "SMB": "Size (Small-Cap Tilt)",
    "HML": "Value Tilt",
    "RMW": "Profitability (Quality)",
    "CMA": "Investment (Conservative)",
    "UMD": "Momentum",
}


class FactorAnalyzer:
    """
    Generates risk flags and natural-language recommendations
    from static + rolling + regime regression results.
    """

    @staticmethod
    def generate_flags(
        static: StaticRegressionResult,
        rolling: List[RollingFactorSeries],
        regime_results: List[RegimeFactorLoadings]
    ) -> List[str]:
        flags = []

        # ── Static regression flags ───────────────────────────────────────
        mkt = next((l for l in static.factor_loadings if l.factor == "MKT"), None)
        if mkt and mkt.beta > settings.HIGH_BETA_THRESHOLD:
            flags.append(f"HIGH_MARKET_BETA:{mkt.beta:.2f}")

        for loading in static.factor_loadings:
            if loading.factor == "MKT":
                continue
            if abs(loading.beta) > settings.SIGNIFICANT_TILT_THRESHOLD and loading.significant:
                direction = "LONG" if loading.beta > 0 else "SHORT"
                flags.append(f"SIGNIFICANT_{direction}_{loading.factor}_TILT")

        if static.r_squared < settings.LOW_R2_THRESHOLD:
            flags.append(f"HIGH_UNEXPLAINED_VARIANCE:{static.unexplained_variance_pct:.1f}%")

        if abs(static.alpha) > settings.HIGH_ALPHA_THRESHOLD and \
                static.alpha_p_value < 0.05:
            direction = "POSITIVE" if static.alpha > 0 else "NEGATIVE"
            flags.append(f"SIGNIFICANT_{direction}_ALPHA:{static.alpha*100:+.1f}%ann")

        # Check if one factor dominates variance
        total_ctv = sum(l.contribution_to_variance for l in static.factor_loadings)
        if total_ctv > 0:
            for loading in static.factor_loadings:
                share = loading.contribution_to_variance / total_ctv
                if share > settings.CONCENTRATED_FACTOR_PCT:
                    flags.append(
                        f"CONCENTRATED_{loading.factor}_EXPOSURE:{share*100:.0f}%_OF_VARIANCE"
                    )

        # ── Rolling drift flags ───────────────────────────────────────────
        for series in rolling:
            if series.drift_flag:
                flags.append(
                    f"FACTOR_DRIFT:{series.factor}:"
                    f"range={series.drift_magnitude:.2f}"
                )

        # ── Regime instability flags ──────────────────────────────────────
        low_reg  = next((r for r in regime_results if r.regime == "low"),  None)
        high_reg = next((r for r in regime_results if r.regime == "high"), None)

        if low_reg and high_reg and \
                low_reg.factor_loadings and high_reg.factor_loadings:
            for factor in ["MKT", "UMD", "SMB"]:
                b_low  = next((l.beta for l in low_reg.factor_loadings  if l.factor == factor), None)
                b_high = next((l.beta for l in high_reg.factor_loadings if l.factor == factor), None)
                if b_low is not None and b_high is not None:
                    shift = abs(b_high - b_low)
                    if shift > settings.DRIFT_THRESHOLD:
                        flags.append(
                            f"REGIME_BETA_SHIFT:{factor}:"
                            f"low={b_low:.2f}→high={b_high:.2f}"
                        )

        logger.info(f"Generated {len(flags)} factor risk flags")
        return flags

    @staticmethod
    def generate_recommendations(
        flags: List[str],
        static: StaticRegressionResult
    ) -> List[str]:
        recs = []

        for flag in flags:
            if flag.startswith("HIGH_MARKET_BETA"):
                beta = flag.split(":")[1]
                recs.append(
                    f"Market beta of {beta} means the portfolio amplifies market moves. "
                    "Consider low-beta defensive stocks, bonds, or covered calls to reduce "
                    "directional market exposure."
                )

            elif "LONG_UMD_TILT" in flag:
                recs.append(
                    "Strong momentum tilt detected. Momentum strategies historically "
                    "suffer sharp reversals during rate-hike regimes and volatility spikes. "
                    "Layer 2 crash results may show elevated losses in 2022."
                )

            elif "SHORT_HML_TILT" in flag:
                recs.append(
                    "Significant growth tilt (short value) detected. Growth portfolios "
                    "carry duration risk — rising rates compress valuations. "
                    "Consider adding value-oriented or dividend-paying positions."
                )

            elif "LONG_HML_TILT" in flag:
                recs.append(
                    "Value tilt detected. Value portfolios can lag in prolonged growth "
                    "rallies. Monitor momentum exposure relative to benchmark."
                )

            elif "HIGH_UNEXPLAINED_VARIANCE" in flag:
                pct = flag.split(":")[1]
                recs.append(
                    f"{pct} of portfolio variance is unexplained by the six-factor model. "
                    "This suggests significant idiosyncratic or sector-specific risk not "
                    "captured by standard factors. Review individual position concentration."
                )

            elif flag.startswith("SIGNIFICANT_POSITIVE_ALPHA"):
                recs.append(
                    "Statistically significant positive alpha detected — the portfolio "
                    "generates returns beyond what factor exposures explain. "
                    "Validate this persists out-of-sample before attributing it to skill."
                )

            elif flag.startswith("SIGNIFICANT_NEGATIVE_ALPHA"):
                val = flag.split(":")[1]
                recs.append(
                    f"Statistically significant negative alpha of {val} — the portfolio "
                    "underperforms its factor exposures. Review fee drag, trading costs, "
                    "and whether factor tilts are efficiently implemented."
                )

            elif flag.startswith("CONCENTRATED_") and "EXPOSURE" in flag:
                parts = flag.split("_")
                factor = parts[1]
                recs.append(
                    f"Over 50% of portfolio variance is driven by the {FACTOR_LABELS.get(factor, factor)} "
                    f"factor. This is a concentrated single-factor bet. "
                    "Consider diversifying across uncorrelated factor exposures."
                )

            elif flag.startswith("FACTOR_DRIFT"):
                _, factor, rng = flag.split(":")
                recs.append(
                    f"{FACTOR_LABELS.get(factor, factor)} exposure has drifted significantly "
                    f"(range: {rng}) over the rolling window. Factor drift can indicate "
                    "portfolio composition changes or regime-driven shifts — review recent "
                    "position changes."
                )

            elif flag.startswith("REGIME_BETA_SHIFT"):
                _, factor, vals = flag.split(":")
                recs.append(
                    f"{FACTOR_LABELS.get(factor, factor)} loading shifts from {vals} across "
                    "VIX regimes. This regime-dependent factor behavior explains why "
                    "correlation analysis (Layer 1) and crash performance (Layer 2) "
                    "diverge from calm-market expectations."
                )

        if not recs:
            recs.append(
                "Factor exposures appear balanced with no dominant single-factor concentration. "
                "Continue monitoring factor drift via rolling regression as market regimes evolve."
            )

        return recs