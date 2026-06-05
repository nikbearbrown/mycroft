import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

from app.services.returns_calculator import ReturnsCalculator

logger = logging.getLogger("portfolio_analysis.crash_simulator")


class CrashSimulator:
    """
    Core engine for Layer 2.

    Given a price data dict (covering one crash window + buffer),
    computes:
      - Portfolio cumulative return over the period
      - Benchmark cumulative return
      - Daily drawdown series for both
      - Max drawdown
      - Per-holding returns (for loss driver decomposition)
    """

    @staticmethod
    def _align_to_window(
        price_data: Dict[str, pd.DataFrame],
        start: str,
        end: str
    ) -> Dict[str, pd.DataFrame]:
        """Trim price data to the exact crash window (inclusive)."""
        aligned = {}
        for ticker, df in price_data.items():
            # Normalise tz-aware index to date strings for safe slicing
            idx = df.index
            if hasattr(idx, 'tz') and idx.tz is not None:
                idx = idx.tz_localize(None)
                df = df.copy()
                df.index = idx
            mask = (df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end))
            sliced = df.loc[mask]
            if not sliced.empty:
                aligned[ticker] = sliced
        return aligned

    @staticmethod
    def compute_period_returns(
        price_data: Dict[str, pd.DataFrame],
        start: str,
        end: str
    ) -> Dict[str, pd.Series]:
        """
        Return a dict of ticker -> daily log-return Series
        clipped to [start, end].

        We include the row just before start (from the buffer) to
        compute day-1 return; then slice to window.
        """
        returns = {}
        for ticker, df in price_data.items():
            idx = df.index
            if hasattr(idx, 'tz') and idx.tz is not None:
                idx = idx.tz_localize(None)
                df = df.copy()
                df.index = idx

            prices = df['Close']
            log_ret = np.log(prices / prices.shift(1)).dropna()
            # Clip to crash window
            mask = (log_ret.index >= pd.Timestamp(start)) & (log_ret.index <= pd.Timestamp(end))
            clipped = log_ret.loc[mask]
            if not clipped.empty:
                returns[ticker] = clipped

        return returns

    @staticmethod
    def compute_portfolio_cumulative(
        returns: Dict[str, pd.Series],
        weights: Dict[str, float]
    ) -> pd.Series:
        """
        Weighted portfolio daily return series → cumulative return.
        Tickers missing from returns get zero contribution.
        """
        all_dates = sorted(
            set().union(*[r.index for r in returns.values()])
        )
        port_daily = pd.Series(0.0, index=all_dates)
        for ticker, ret in returns.items():
            w = weights.get(ticker, 0.0)
            aligned = ret.reindex(all_dates, fill_value=0.0)
            port_daily += w * aligned

        # Cumulative return: (1 + r1)(1 + r2)... - 1
        # For log returns: exp(sum) - 1
        cumulative = np.exp(port_daily.cumsum()) - 1
        return cumulative

    @staticmethod
    def compute_drawdown_series(cumulative: pd.Series) -> pd.Series:
        """
        Drawdown at each point = (current - running_max) / (1 + running_max).
        Returns series of negative values (0 = at high-water mark).
        """
        wealth = 1 + cumulative          # index starting at 1
        running_max = wealth.cummax()
        drawdown = (wealth - running_max) / running_max
        return drawdown

    @staticmethod
    def compute_max_drawdown(drawdown_series: pd.Series) -> float:
        return float(drawdown_series.min())

    @staticmethod
    def compute_total_return(returns_series: pd.Series) -> float:
        """Cumulative return of a single asset over the period."""
        return float(np.exp(returns_series.sum()) - 1)

    @staticmethod
    def simulate(
        price_data: Dict[str, pd.DataFrame],
        start: str,
        end: str,
        weights: Dict[str, float],
        benchmark_ticker: str
    ) -> Dict:
        """
        Full simulation for one crash window.

        Returns a dict with everything needed by LossAnalyzer and
        CrashVisualization:
          - port_cumulative   pd.Series
          - bench_cumulative  pd.Series
          - port_drawdown     pd.Series
          - bench_drawdown    pd.Series
          - port_total_return float
          - bench_total_return float
          - port_max_dd       float
          - bench_max_dd      float
          - ticker_returns    Dict[str, float]   (total return per holding)
          - trading_days      int
        """
        logger.info(f"Simulating crash window {start} → {end}")

        # Per-asset daily return series
        all_returns = CrashSimulator.compute_period_returns(price_data, start, end)

        if not all_returns:
            raise ValueError(f"No returns computed for window {start}–{end}")

        # Split portfolio vs benchmark
        portfolio_tickers = [t for t in weights if t in all_returns]
        bench_returns = all_returns.get(benchmark_ticker)

        if len(portfolio_tickers) < 1:
            raise ValueError("No portfolio tickers found in crash price data")

        port_returns_dict = {t: all_returns[t] for t in portfolio_tickers}

        # Portfolio cumulative + drawdown
        port_cum  = CrashSimulator.compute_portfolio_cumulative(port_returns_dict, weights)
        port_dd   = CrashSimulator.compute_drawdown_series(port_cum)

        # Benchmark cumulative + drawdown
        if bench_returns is not None:
            bench_cum = np.exp(bench_returns.cumsum()) - 1
            bench_dd  = CrashSimulator.compute_drawdown_series(bench_cum)
        else:
            logger.warning(f"Benchmark {benchmark_ticker} not available — using zeros")
            bench_cum = pd.Series(0.0, index=port_cum.index)
            bench_dd  = pd.Series(0.0, index=port_cum.index)

        # Per-ticker total returns
        ticker_returns = {
            t: CrashSimulator.compute_total_return(all_returns[t])
            for t in portfolio_tickers
        }

        trading_days = len(port_cum)

        return {
            "port_cumulative":    port_cum,
            "bench_cumulative":   bench_cum,
            "port_drawdown":      port_dd,
            "bench_drawdown":     bench_dd,
            "port_total_return":  float(port_cum.iloc[-1]) if len(port_cum) else 0.0,
            "bench_total_return": float(bench_cum.iloc[-1]) if len(bench_cum) else 0.0,
            "port_max_dd":        CrashSimulator.compute_max_drawdown(port_dd),
            "bench_max_dd":       CrashSimulator.compute_max_drawdown(bench_dd),
            "ticker_returns":     ticker_returns,
            "trading_days":       trading_days,
        }

    @staticmethod
    def compute_recovery_days(
        recovery_price_data: Optional[Dict[str, pd.DataFrame]],
        weights: Dict[str, float],
        crash_end: str,
        trough_value: float     # cumulative return at crash end (negative)
    ) -> Optional[int]:
        """
        How many trading days after crash_end until portfolio recovers to 0%
        (i.e. back to pre-crash level)?

        Returns None if not yet recovered within the recovery window.
        """
        if recovery_price_data is None or not recovery_price_data:
            return None

        try:
            recovery_returns = CrashSimulator.compute_period_returns(
                recovery_price_data,
                crash_end,
                "2099-12-31"    # no upper bound — already clipped by fetch
            )
            if not recovery_returns:
                return None

            port_tickers = [t for t in weights if t in recovery_returns]
            if not port_tickers:
                return None

            port_dict = {t: recovery_returns[t] for t in port_tickers}
            port_cum  = CrashSimulator.compute_portfolio_cumulative(port_dict, weights)

            # Starting from trough, compound with recovery returns
            # Full recovery = cumulative from crash start back to 0
            # We need: (1 + trough_value) * (1 + recovery_gain) = 1
            # → recovery_gain_needed = 1/(1+trough_value) - 1
            needed = (1.0 / (1.0 + trough_value)) - 1.0

            for i, val in enumerate(port_cum.values):
                if val >= needed:
                    return int(i + 1)

            return None  # not recovered in window

        except Exception as e:
            logger.warning(f"Recovery calculation failed (non-fatal): {e}")
            return None