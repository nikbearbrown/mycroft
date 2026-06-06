import pandas as pd
import numpy as np
from typing import Dict, List
import logging

from app.core.config import settings
from app.models.schemas import LossDriver, DrawdownPoint, CrashResult

logger = logging.getLogger("portfolio_analysis.loss_analyzer")


class LossAnalyzer:
    """
    Converts raw simulation output into structured CrashResult objects.
    Handles loss driver decomposition, risk flag generation, and
    building the drawdown time-series for the frontend chart.
    """

    @staticmethod
    def build_loss_drivers(
        ticker_returns: Dict[str, float],
        weights: Dict[str, float]
    ) -> List[LossDriver]:
        """
        Attribute portfolio loss to individual holdings.

        contribution_to_loss = weight_i * return_i
        contribution_pct     = contribution_i / total_portfolio_loss   (as a fraction)
        """
        total_loss = sum(
            weights.get(t, 0.0) * r
            for t, r in ticker_returns.items()
        )

        drivers = []
        for ticker, ret in ticker_returns.items():
            w = weights.get(ticker, 0.0)
            contrib = w * ret
            contrib_pct = (contrib / total_loss) if total_loss != 0 else 0.0
            drivers.append(LossDriver(
                ticker=ticker,
                weight=round(w, 4),
                period_return=round(ret, 4),
                contribution_to_loss=round(contrib, 4),
                contribution_pct=round(contrib_pct, 4)
            ))

        # Sort by magnitude of contribution (worst contributors first)
        drivers.sort(key=lambda d: d.contribution_to_loss)
        return drivers

    @staticmethod
    def build_drawdown_series(
        port_dd: pd.Series,
        bench_dd: pd.Series
    ) -> List[DrawdownPoint]:
        """Merge portfolio and benchmark drawdown series into response-ready list."""
        # Align on common index
        combined = pd.DataFrame({
            "port":  port_dd,
            "bench": bench_dd
        }).fillna(method="ffill").fillna(0.0)

        points = []
        for dt, row in combined.iterrows():
            points.append(DrawdownPoint(
                date=str(dt.date()),
                portfolio_dd=round(float(row["port"]),  4),
                benchmark_dd=round(float(row["bench"]), 4)
            ))
        return points

    @staticmethod
    def generate_crash_risk_flags(
        port_total_return: float,
        bench_total_return: float,
        max_drawdown: float,
        recovery_days: int | None,
        loss_drivers: List[LossDriver]
    ) -> List[str]:
        flags = []

        if max_drawdown < settings.SEVERE_DRAWDOWN_THRESHOLD:
            flags.append("SEVERE_DRAWDOWN")

        rel_perf = port_total_return - bench_total_return
        if rel_perf < settings.UNDERPERFORM_THRESHOLD:
            flags.append("SIGNIFICANT_UNDERPERFORMANCE")

        if recovery_days is not None and recovery_days > settings.SLOW_RECOVERY_DAYS:
            flags.append("SLOW_RECOVERY")
        elif recovery_days is None:
            flags.append("NOT_YET_RECOVERED")

        # Check if a single stock drove > threshold % of the loss
        for d in loss_drivers:
            if d.contribution_pct > settings.CONCENTRATION_DRIVER_PCT:
                flags.append(f"CONCENTRATED_LOSS_DRIVER:{d.ticker}")

        return flags

    @staticmethod
    def build_crash_result(
        key: str,
        name: str,
        description: str,
        start: str,
        end: str,
        benchmark_ticker: str,
        sim: Dict,
        weights: Dict[str, float],
        recovery_days: int | None
    ) -> CrashResult:
        """Assemble a full CrashResult from simulation output."""

        loss_drivers = LossAnalyzer.build_loss_drivers(sim["ticker_returns"], weights)
        drawdown_series = LossAnalyzer.build_drawdown_series(
            sim["port_drawdown"], sim["bench_drawdown"]
        )

        rel_perf = sim["port_total_return"] - sim["bench_total_return"]
        risk_flags = LossAnalyzer.generate_crash_risk_flags(
            port_total_return=sim["port_total_return"],
            bench_total_return=sim["bench_total_return"],
            max_drawdown=sim["port_max_dd"],
            recovery_days=recovery_days,
            loss_drivers=loss_drivers
        )

        return CrashResult(
            key=key,
            name=name,
            description=description,
            start=start,
            end=end,
            trading_days=sim["trading_days"],
            benchmark_ticker=benchmark_ticker,
            portfolio_total_return=round(sim["port_total_return"],  4),
            benchmark_total_return=round(sim["bench_total_return"], 4),
            relative_performance=round(rel_perf, 4),
            max_drawdown=round(sim["port_max_dd"],   4),
            benchmark_max_drawdown=round(sim["bench_max_dd"], 4),
            recovery_days=recovery_days,
            loss_drivers=loss_drivers,
            risk_flags=risk_flags,
            drawdown_series=drawdown_series
        )

    @staticmethod
    def generate_overall_flags_and_recommendations(
        crash_results: List[CrashResult]
    ) -> tuple[List[str], List[str]]:
        """Roll up flags across all crash windows into portfolio-level insights."""
        all_flags = []
        recommendations = []

        # How many crashes triggered severe drawdown?
        severe_count = sum(1 for r in crash_results if "SEVERE_DRAWDOWN" in r.risk_flags)
        underperf_count = sum(1 for r in crash_results if "SIGNIFICANT_UNDERPERFORMANCE" in r.risk_flags)
        not_recovered = [r.name for r in crash_results if "NOT_YET_RECOVERED" in r.risk_flags]

        avg_dd = np.mean([r.max_drawdown for r in crash_results]) if crash_results else 0.0
        avg_rel = np.mean([r.relative_performance for r in crash_results]) if crash_results else 0.0

        if severe_count >= 2:
            all_flags.append("CONSISTENTLY_SEVERE_DRAWDOWNS")
            recommendations.append(
                f"Portfolio suffered severe drawdowns (>{abs(settings.SEVERE_DRAWDOWN_THRESHOLD)*100:.0f}%) "
                f"in {severe_count} of {len(crash_results)} crashes. "
                "Consider adding defensive assets (bonds, gold, low-beta stocks) to reduce peak losses."
            )

        if underperf_count >= 2:
            all_flags.append("CONSISTENT_UNDERPERFORMANCE_VS_BENCHMARK")
            recommendations.append(
                f"Portfolio underperformed its benchmark in {underperf_count} of {len(crash_results)} crashes. "
                "Holdings may carry idiosyncratic risk that diversification doesn't protect against. "
                "Review factor exposures in Layer 3."
            )

        if not_recovered:
            all_flags.append("UNRESOLVED_RECOVERY")
            recommendations.append(
                f"Portfolio had not fully recovered within the observation window after: "
                f"{', '.join(not_recovered)}. Long recovery periods increase sequence-of-returns risk."
            )

        # Concentrated loss drivers across crashes
        driver_counts: Dict[str, int] = {}
        for r in crash_results:
            for f in r.risk_flags:
                if f.startswith("CONCENTRATED_LOSS_DRIVER:"):
                    ticker = f.split(":")[1]
                    driver_counts[ticker] = driver_counts.get(ticker, 0) + 1

        repeat_drivers = [t for t, c in driver_counts.items() if c >= 2]
        if repeat_drivers:
            all_flags.append("REPEAT_LOSS_CONCENTRATION")
            recommendations.append(
                f"{', '.join(repeat_drivers)} drove outsized losses in multiple crashes. "
                "Consider trimming these positions or hedging with uncorrelated assets."
            )

        if not all_flags:
            recommendations.append(
                "Portfolio held up relatively well across historical crashes. "
                "Continue monitoring via Layer 1 regime analysis for correlation drift."
            )

        return all_flags, recommendations