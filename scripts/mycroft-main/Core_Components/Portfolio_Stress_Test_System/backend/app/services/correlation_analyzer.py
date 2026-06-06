import pandas as pd
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger("portfolio_analysis.correlation_analyzer")


def _strip_tz(index: pd.Index) -> pd.Index:
    """Normalize a DatetimeIndex to tz-naive UTC dates for safe alignment."""
    if isinstance(index, pd.DatetimeIndex) and index.tz is not None:
        return index.tz_localize(None)
    return index


class CorrelationAnalyzer:
    """Service for calculating correlation matrices and diversification metrics"""

    @staticmethod
    def calculate_regime_correlations(
        returns: pd.DataFrame,
        regimes: pd.Series,
        rolling_window: int = 252
    ) -> Dict[str, pd.DataFrame]:
        """
        Calculate correlation matrices for each regime.

        Returns:
            Dict mapping regime name -> correlation matrix DataFrame
        """
        logger.info(f"Calculating regime-specific correlation matrices (window={rolling_window})")

        # ── Fix: strip tz from both indexes before aligning ──────────────────
        returns = returns.copy()
        returns.index = _strip_tz(returns.index)

        regimes = regimes.copy()
        regimes.index = _strip_tz(regimes.index)

        # Align to common dates so boolean indexing is safe
        common_dates = returns.index.intersection(regimes.index)
        returns = returns.loc[common_dates]
        regimes = regimes.loc[common_dates]
        # ─────────────────────────────────────────────────────────────────────

        regime_correlations = {}

        for regime_name in ['low', 'medium', 'high']:
            regime_mask    = regimes == regime_name
            regime_returns = returns.loc[regime_mask]

            if len(regime_returns) < 2:
                logger.warning(
                    f"Insufficient data for {regime_name} regime "
                    f"({len(regime_returns)} days) — using identity matrix"
                )
                tickers     = returns.columns.tolist()
                corr_matrix = pd.DataFrame(
                    np.eye(len(tickers)), index=tickers, columns=tickers
                )
            else:
                corr_matrix = regime_returns.corr()
                if len(regime_returns) < rolling_window:
                    logger.warning(
                        f"{regime_name} regime has only {len(regime_returns)} days "
                        f"(< window {rolling_window}) — correlations may be noisy"
                    )

            regime_correlations[regime_name] = corr_matrix
            logger.info(
                f"  {regime_name.capitalize()} regime: {len(regime_returns)} days, "
                f"avg corr = {CorrelationAnalyzer._avg_correlation(corr_matrix):.3f}"
            )

        return regime_correlations

    @staticmethod
    def calculate_diversification_metrics(
        correlation_matrix: pd.DataFrame,
        weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate diversification metrics from correlation matrix.
        """
        tickers      = correlation_matrix.columns.tolist()
        weight_array = np.array([weights.get(t, 0) for t in tickers])

        avg_corr = CorrelationAnalyzer._weighted_avg_correlation(
            correlation_matrix.values, weight_array
        )

        upper_tri = np.triu(correlation_matrix.values, k=1)
        max_corr  = float(upper_tri.max())
        nonzero   = upper_tri[upper_tri != 0]
        min_corr  = float(nonzero.min()) if nonzero.size > 0 else 0.0

        weighted_corr_sum = 0.0
        for i in range(len(weight_array)):
            for j in range(len(weight_array)):
                weighted_corr_sum += (
                    weight_array[i] * weight_array[j] * correlation_matrix.iloc[i, j]
                )

        effective_n = 1 / weighted_corr_sum if weighted_corr_sum > 0 else float(len(tickers))

        return {
            'avg_pairwise_correlation': float(avg_corr),
            'max_correlation':          max_corr,
            'min_correlation':          min_corr,
            'effective_n_assets':       float(effective_n)
        }

    @staticmethod
    def _avg_correlation(corr_matrix: pd.DataFrame) -> float:
        upper_tri = np.triu(corr_matrix.values, k=1)
        n_pairs   = len(corr_matrix) * (len(corr_matrix) - 1) / 2
        return float(upper_tri.sum() / n_pairs) if n_pairs > 0 else 0.0

    @staticmethod
    def _weighted_avg_correlation(corr_matrix: np.ndarray, weights: np.ndarray) -> float:
        n = len(weights)
        weighted_sum = weight_sum = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                wp = weights[i] * weights[j]
                weighted_sum += wp * corr_matrix[i, j]
                weight_sum   += wp
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0