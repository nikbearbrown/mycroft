import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

from app.core.config import settings
from app.models.schemas import (
    RegimeStats, TransitionEvent, TransitionSummary, CumulativePoint
)

logger = logging.getLogger("portfolio_analysis.regime_performance")

REGIME_ORDER = ["low", "medium", "high"]
REGIME_LABELS = {"low": "Low VIX", "medium": "Med VIX", "high": "High VIX"}


def _safe(val: float, fallback: float = 0.0) -> float:
    """Replace nan/inf with fallback so JSON serialization never fails."""
    import math
    if val is None or math.isnan(val) or math.isinf(val):
        return fallback
    return val


class RegimePerformanceEngine:
    """
    Core engine for Layer 4.

    Given aligned portfolio returns, regime labels, and risk-free rate series,
    computes:
      - Per-regime annualised statistics
      - Regime transition events and forward-return summaries
      - Full cumulative return series colour-coded by regime
    """

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _strip_tz(index: pd.Index) -> pd.Index:
        if isinstance(index, pd.DatetimeIndex) and index.tz is not None:
            return index.tz_localize(None)
        return index

    @staticmethod
    def _align(
        port_returns: pd.Series,
        regimes: pd.Series,
        rf: pd.Series
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Strip tz and intersect all three series to common dates."""
        port_returns = port_returns.copy()
        port_returns.index = RegimePerformanceEngine._strip_tz(port_returns.index)

        regimes = regimes.copy()
        regimes.index = RegimePerformanceEngine._strip_tz(regimes.index)

        rf = rf.copy()
        rf.index = RegimePerformanceEngine._strip_tz(rf.index)

        common = port_returns.index \
            .intersection(regimes.index) \
            .intersection(rf.index)

        return (
            port_returns.loc[common],
            regimes.loc[common],
            rf.loc[common]
        )

    @staticmethod
    def _max_drawdown(returns: pd.Series) -> float:
        """Max drawdown of a return series."""
        if returns.empty:
            return 0.0
        wealth = (1 + returns).cumprod()
        peak   = wealth.cummax()
        dd     = (wealth - peak) / peak
        return float(dd.min())

    @staticmethod
    def _avg_drawdown(returns: pd.Series) -> float:
        if returns.empty:
            return 0.0
        wealth = (1 + returns).cumprod()
        peak   = wealth.cummax()
        dd     = (wealth - peak) / peak
        return float(dd[dd < 0].mean()) if (dd < 0).any() else 0.0

    # ── Per-regime statistics ─────────────────────────────────────────────

    @staticmethod
    def compute_regime_stats(
        port_returns: pd.Series,
        regimes: pd.Series,
        rf: pd.Series
    ) -> List[RegimeStats]:
        """Compute annualised performance stats for each VIX regime."""
        results = []

        for regime in REGIME_ORDER:
            mask    = regimes == regime
            r       = port_returns.loc[mask]
            rf_r    = rf.loc[mask]

            if len(r) < 5:
                logger.warning(f"  {regime}: only {len(r)} obs — skipping stats")
                results.append(RegimeStats(
                    regime=regime, observations=len(r),
                    ann_return=0.0, ann_volatility=0.0, sharpe_ratio=0.0,
                    max_drawdown=0.0, avg_drawdown=0.0,
                    win_rate=0.0, best_day=0.0, worst_day=0.0,
                    cumulative_return=0.0
                ))
                continue

            excess   = r - rf_r
            ann_ret  = float(r.mean() * 252)
            ann_vol  = float(r.std() * np.sqrt(252))
            ann_rf   = float(rf_r.mean() * 252)
            sharpe   = float((ann_ret - ann_rf) / ann_vol) if ann_vol > 0 else 0.0
            cum_ret  = float((1 + r).prod() - 1)
            win_rate = float((r > 0).mean())

            logger.info(
                f"  {regime}: {len(r)} obs | "
                f"ret={ann_ret*100:+.1f}% vol={ann_vol*100:.1f}% "
                f"sharpe={sharpe:.2f} maxdd={RegimePerformanceEngine._max_drawdown(r)*100:.1f}%"
            )

            results.append(RegimeStats(
                regime=regime,
                observations=len(r),
                ann_return=round(_safe(ann_ret), 4),
                ann_volatility=round(_safe(ann_vol), 4),
                sharpe_ratio=round(_safe(sharpe), 3),
                max_drawdown=round(_safe(RegimePerformanceEngine._max_drawdown(r)), 4),
                avg_drawdown=round(_safe(RegimePerformanceEngine._avg_drawdown(r)), 4),
                win_rate=round(_safe(win_rate), 4),
                best_day=round(_safe(float(r.max())), 4),
                worst_day=round(_safe(float(r.min())), 4),
                cumulative_return=round(_safe(cum_ret), 4)
            ))

        return results

    # ── Regime transition analysis ────────────────────────────────────────

    @staticmethod
    def compute_transitions(
        port_returns: pd.Series,
        regimes: pd.Series,
        windows: List[int] = [5, 20]
    ) -> Tuple[List[TransitionEvent], List[TransitionSummary]]:
        """
        Identify every day where regime changes and compute forward returns
        over each window after the transition.
        """
        # Find transition dates: where regime[t] != regime[t-1]
        regime_shifted = regimes.shift(1)
        transition_mask = (regimes != regime_shifted) & regime_shifted.notna()
        transition_dates = regimes.index[transition_mask]

        events: List[TransitionEvent] = []
        for dt in transition_dates:
            from_r = str(regime_shifted.loc[dt])
            to_r   = str(regimes.loc[dt])

            fwd = {}
            for w in windows:
                # Forward return = compound return over next w days
                future_idx = port_returns.index.get_loc(dt)
                future_slice = port_returns.iloc[future_idx + 1: future_idx + 1 + w]
                if len(future_slice) == w:
                    fwd[w] = round(float((1 + future_slice).prod() - 1), 4)
                else:
                    fwd[w] = None

            events.append(TransitionEvent(
                date=str(dt.date()),
                from_regime=from_r,
                to_regime=to_r,
                fwd_5d_return=fwd.get(5),
                fwd_20d_return=fwd.get(20)
            ))

        logger.info(f"Found {len(events)} regime transitions")

        # Summarise by transition type
        transition_types = [
            ("low",    "medium", "Low → Med"),
            ("low",    "high",   "Low → High"),
            ("medium", "low",    "Med → Low"),
            ("medium", "high",   "Med → High"),
            ("high",   "medium", "High → Med"),
            ("high",   "low",    "High → Low"),
        ]

        summaries: List[TransitionSummary] = []
        for from_r, to_r, label in transition_types:
            subset = [e for e in events if e.from_regime == from_r and e.to_regime == to_r]
            if not subset:
                continue

            fwd5  = [e.fwd_5d_return  for e in subset if e.fwd_5d_return  is not None]
            fwd20 = [e.fwd_20d_return for e in subset if e.fwd_20d_return is not None]

            summaries.append(TransitionSummary(
                from_regime=from_r,
                to_regime=to_r,
                label=label,
                n_events=len(subset),
                avg_fwd_5d=round(_safe(float(np.mean(fwd5))),   4) if fwd5  else None,
                avg_fwd_20d=round(_safe(float(np.mean(fwd20))), 4) if fwd20 else None,
                pct_negative_5d=round(_safe(float(np.mean([1 for x in fwd5  if x < 0]) / len(fwd5))),  4) if fwd5  else None,
                pct_negative_20d=round(_safe(float(np.mean([1 for x in fwd20 if x < 0]) / len(fwd20))), 4) if fwd20 else None,
            ))

        return events, summaries

    # ── Cumulative return series ──────────────────────────────────────────

    @staticmethod
    def compute_cumulative_series(
        port_returns: pd.Series,
        regimes: pd.Series
    ) -> List[CumulativePoint]:
        """
        Full cumulative return series with each point tagged by its regime.
        Used for the colour-coded equity curve chart.
        """
        cum = (1 + port_returns).cumprod() - 1
        points = []
        for dt, val in cum.items():
            regime = regimes.get(dt, "medium")
            points.append(CumulativePoint(
                date=str(dt.date()),
                cumulative_return=round(float(val), 4),
                regime=str(regime)
            ))
        return points

    # ── Risk flags ────────────────────────────────────────────────────────

    @staticmethod
    def generate_flags(
        regime_stats: List[RegimeStats],
        transition_summaries: List[TransitionSummary]
    ) -> List[str]:
        flags = []

        low  = next((s for s in regime_stats if s.regime == "low"),    None)
        med  = next((s for s in regime_stats if s.regime == "medium"), None)
        high = next((s for s in regime_stats if s.regime == "high"),   None)

        # Sharpe flags
        for s in regime_stats:
            if s.observations < 5:
                continue
            if s.sharpe_ratio < settings.NEGATIVE_SHARPE_THRESHOLD:
                flags.append(f"NEGATIVE_SHARPE:{s.regime.upper()}_VIX:{s.sharpe_ratio:.2f}")
            elif s.sharpe_ratio < settings.LOW_SHARPE_THRESHOLD:
                flags.append(f"LOW_SHARPE:{s.regime.upper()}_VIX:{s.sharpe_ratio:.2f}")

        # Regime return gap
        if low and high and low.observations >= 5 and high.observations >= 5:
            gap = low.ann_return - high.ann_return
            if gap > settings.REGIME_RETURN_GAP_THRESHOLD:
                flags.append(
                    f"REGIME_RETURN_GAP:{gap*100:.1f}pp "
                    f"(low={low.ann_return*100:+.1f}% vs high={high.ann_return*100:+.1f}%)"
                )

        # Volatility spike
        if low and high and low.ann_volatility > 0 and high.observations >= 5:
            vol_ratio = high.ann_volatility / low.ann_volatility
            if vol_ratio > settings.VOL_SPIKE_THRESHOLD:
                flags.append(
                    f"VOL_SPIKE_IN_STRESS:{vol_ratio:.1f}x "
                    f"(low={low.ann_volatility*100:.1f}% → high={high.ann_volatility*100:.1f}%)"
                )

        # Win rate collapse in high VIX
        if high and high.observations >= 5:
            if high.win_rate < settings.LOW_WIN_RATE_THRESHOLD:
                flags.append(
                    f"LOW_WIN_RATE_HIGH_VIX:{high.win_rate*100:.0f}%"
                )

        # Transition flags — low→high is the most actionable
        for ts in transition_summaries:
            if ts.from_regime == "low" and ts.to_regime == "high":
                if ts.avg_fwd_5d is not None and \
                        ts.avg_fwd_5d < settings.TRANSITION_NEGATIVE_THRESHOLD:
                    flags.append(
                        f"DANGEROUS_TRANSITION:LOW_TO_HIGH:"
                        f"avg_5d={ts.avg_fwd_5d*100:+.1f}%"
                    )
            if ts.from_regime == "medium" and ts.to_regime == "high":
                if ts.avg_fwd_5d is not None and \
                        ts.avg_fwd_5d < settings.TRANSITION_NEGATIVE_THRESHOLD:
                    flags.append(
                        f"DANGEROUS_TRANSITION:MED_TO_HIGH:"
                        f"avg_5d={ts.avg_fwd_5d*100:+.1f}%"
                    )

        return flags

    @staticmethod
    def generate_recommendations(
        flags: List[str],
        regime_stats: List[RegimeStats],
        transition_summaries: List[TransitionSummary]
    ) -> List[str]:
        recs = []

        for flag in flags:
            if flag.startswith("NEGATIVE_SHARPE"):
                parts = flag.split(":")
                regime = parts[1].replace("_VIX", "").capitalize()
                sharpe = parts[2]
                recs.append(
                    f"Portfolio has a negative Sharpe ratio during {regime} VIX periods "
                    f"({sharpe}), meaning it loses money on a risk-adjusted basis in that "
                    f"environment. Review which holdings drive underperformance in this regime "
                    f"using Layer 2 crash attribution and Layer 3 factor loadings."
                )

            elif flag.startswith("LOW_SHARPE"):
                parts = flag.split(":")
                regime = parts[1].replace("_VIX", "").capitalize()
                recs.append(
                    f"Sharpe ratio drops below 0.5 during {regime} VIX periods — "
                    f"compensation per unit of risk is poor in this environment. "
                    f"Consider whether the holdings driving volatility in this regime "
                    f"are justified by their return contribution."
                )

            elif flag.startswith("REGIME_RETURN_GAP"):
                recs.append(
                    "Annualised returns differ by more than 10 percentage points between "
                    "low and high VIX regimes. This portfolio has strong regime dependency — "
                    "it performs materially differently depending on market conditions. "
                    "Consider adding defensive positions (low-beta equities, treasuries, gold) "
                    "to reduce the performance gap across regimes."
                )

            elif flag.startswith("VOL_SPIKE"):
                mult = flag.split(":")[1].split("x")[0]
                recs.append(
                    f"Portfolio volatility is {mult}x higher in high-VIX periods than in "
                    f"calm markets. Volatility expansion of this magnitude under stress "
                    f"significantly increases drawdown risk. The Layer 3 regime heatmap "
                    f"will show which factor loadings are amplifying during stress."
                )

            elif flag.startswith("LOW_WIN_RATE"):
                rate = flag.split(":")[2]
                recs.append(
                    f"Win rate falls to {rate} during high-VIX periods — fewer than half "
                    f"of trading days are positive when markets are stressed. This indicates "
                    f"persistent negative drift under volatility, not just occasional large "
                    f"losses. Consider positions that generate positive carry during stress."
                )

            elif "DANGEROUS_TRANSITION" in flag:
                direction = "low to high" if "LOW_TO_HIGH" in flag else "medium to high"
                ret = flag.split("avg_5d=")[1]
                recs.append(
                    f"The portfolio averages {ret} in the 5 days following a {direction} "
                    f"VIX transition. Regime transitions into stress are the highest-risk "
                    f"window for this portfolio. This is a systematic early-warning signal — "
                    f"rising VIX is historically predictive of near-term losses for this "
                    f"specific allocation."
                )

        if not recs:
            recs.append(
                "Portfolio performance is relatively consistent across VIX regimes with "
                "no major risk-adjusted return deterioration under stress. Continue "
                "monitoring regime transitions as the primary leading indicator of "
                "short-term performance risk."
            )

        return recs