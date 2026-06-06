import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import base64
from io import BytesIO
from typing import List, Dict
import logging

from app.models.schemas import (
    RegimeStats, TransitionSummary, CumulativePoint
)

logger = logging.getLogger("portfolio_analysis.regime_performance_viz")

REGIME_COLORS = {
    "low":    "#2ca02c",   # green
    "medium": "#1f77b4",   # blue
    "high":   "#d62728",   # red
}
REGIME_LABELS = {
    "low": "Low VIX", "medium": "Med VIX", "high": "High VIX"
}
BG = "#f8f9fa"
GRID = "#e0e0e0"


def _to_b64(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


class RegimePerformanceViz:

    @staticmethod
    def regime_stats_bar(regime_stats: List[RegimeStats]) -> str:
        """
        Side-by-side grouped bar chart: annualised return, volatility,
        Sharpe ratio, and max drawdown — one group per metric, three bars per group.
        """
        regimes  = [s.regime for s in regime_stats if s.observations >= 5]
        colors   = [REGIME_COLORS[r] for r in regimes]
        labels   = [REGIME_LABELS[r] for r in regimes]

        metrics = {
            "Ann. Return (%)":    [s.ann_return * 100      for s in regime_stats if s.observations >= 5],
            "Ann. Volatility (%)": [s.ann_volatility * 100 for s in regime_stats if s.observations >= 5],
            "Sharpe Ratio":       [s.sharpe_ratio          for s in regime_stats if s.observations >= 5],
            "Max Drawdown (%)":   [s.max_drawdown * 100    for s in regime_stats if s.observations >= 5],
        }

        fig, axes = plt.subplots(1, 4, figsize=(14, 4))
        fig.patch.set_facecolor(BG)

        for ax, (metric_name, values) in zip(axes, metrics.items()):
            ax.set_facecolor(BG)
            bars = ax.bar(labels, values, color=colors, edgecolor="white", width=0.55)
            ax.axhline(0, color="#aaaaaa", linewidth=0.7, linestyle=":")

            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    val + (0.3 if val >= 0 else -0.8),
                    f"{val:.1f}" if "Sharpe" not in metric_name else f"{val:.2f}",
                    ha="center", va="bottom" if val >= 0 else "top",
                    fontsize=7.5, fontweight="bold"
                )

            ax.set_title(metric_name, fontsize=8.5, pad=5)
            ax.set_xticklabels(labels, fontsize=7.5)
            ax.tick_params(axis="y", labelsize=7)
            ax.grid(axis="y", color=GRID, linewidth=0.5)
            ax.spines[["top", "right"]].set_visible(False)

        fig.suptitle("Performance Statistics by VIX Regime",
                     fontsize=11, fontweight="bold", y=1.02)
        plt.tight_layout()
        return _to_b64(fig)

    @staticmethod
    def win_rate_chart(regime_stats: List[RegimeStats]) -> str:
        """
        Horizontal bar chart showing win rate and best/worst day per regime.
        """
        stats = [s for s in regime_stats if s.observations >= 5]
        fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
        fig.patch.set_facecolor(BG)

        datasets = [
            ("Win Rate (%)",  [s.win_rate * 100 for s in stats], False),
            ("Best Day (%)",  [s.best_day * 100  for s in stats], False),
            ("Worst Day (%)", [s.worst_day * 100 for s in stats], True),
        ]

        for ax, (title, values, is_negative) in zip(axes, datasets):
            ax.set_facecolor(BG)
            labels = [REGIME_LABELS[s.regime] for s in stats]
            colors = [REGIME_COLORS[s.regime] for s in stats]
            bars = ax.barh(labels, values, color=colors, edgecolor="white", height=0.5)
            ax.axvline(0, color="#aaaaaa", linewidth=0.7)

            for bar, val in zip(bars, values):
                ax.text(
                    val + (0.2 if val >= 0 else -0.2),
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:+.2f}%",
                    va="center", ha="left" if val >= 0 else "right",
                    fontsize=7.5
                )

            ax.set_title(title, fontsize=8.5, pad=5)
            ax.tick_params(labelsize=7.5)
            ax.grid(axis="x", color=GRID, linewidth=0.5)
            ax.spines[["top", "right"]].set_visible(False)

        fig.suptitle("Daily Return Distribution by Regime",
                     fontsize=11, fontweight="bold", y=1.02)
        plt.tight_layout()
        return _to_b64(fig)

    @staticmethod
    def transition_heatmap(transition_summaries: List[TransitionSummary]) -> str:
        """
        Two heatmaps side by side: avg 5-day and avg 20-day forward return
        after each type of regime transition.
        """
        all_from = ["low", "medium", "high"]
        all_to   = ["low", "medium", "high"]

        def build_matrix(use_5d: bool):
            mat = np.full((3, 3), np.nan)
            for ts in transition_summaries:
                i = all_from.index(ts.from_regime)
                j = all_to.index(ts.to_regime)
                val = ts.avg_fwd_5d if use_5d else ts.avg_fwd_20d
                if val is not None:
                    mat[i, j] = val * 100
            return mat

        m5  = build_matrix(True)
        m20 = build_matrix(False)

        vmax = max(
            np.nanmax(np.abs(m5))  if not np.all(np.isnan(m5))  else 1,
            np.nanmax(np.abs(m20)) if not np.all(np.isnan(m20)) else 1
        )

        tick_labels = ["Low VIX", "Med VIX", "High VIX"]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5))
        fig.patch.set_facecolor(BG)

        for ax, mat, title in [
            (ax1, m5,  "Avg 5-Day Forward Return After Transition"),
            (ax2, m20, "Avg 20-Day Forward Return After Transition")
        ]:
            ax.set_facecolor(BG)
            masked = np.ma.masked_invalid(mat)
            cmap = plt.cm.RdYlGn
            cmap.set_bad("#d0d0d0")
            im = ax.imshow(masked, cmap=cmap, aspect="auto",
                           vmin=-vmax, vmax=vmax)

            ax.set_xticks(range(3))
            ax.set_xticklabels([f"→ {l}" for l in tick_labels], fontsize=7.5)
            ax.set_yticks(range(3))
            ax.set_yticklabels([f"{l} →" for l in tick_labels], fontsize=7.5)
            ax.set_title(title, fontsize=8.5, pad=5)

            for i in range(3):
                for j in range(3):
                    val = mat[i, j]
                    if i == j:
                        ax.text(j, i, "—", ha="center", va="center",
                                fontsize=8, color="#888")
                    elif np.isnan(val):
                        ax.text(j, i, "N/A", ha="center", va="center",
                                fontsize=7.5, color="#888")
                    else:
                        ax.text(j, i, f"{val:+.1f}%",
                                ha="center", va="center", fontsize=8,
                                color="white" if abs(val) > vmax * 0.6 else "black")

            plt.colorbar(im, ax=ax, shrink=0.85).ax.tick_params(labelsize=7)
            ax.spines[["top","right","left","bottom"]].set_visible(False)

        fig.suptitle("Regime Transition Forward Returns",
                     fontsize=11, fontweight="bold", y=1.02)
        plt.tight_layout()
        return _to_b64(fig)

    @staticmethod
    def cumulative_return_chart(cumulative_series: List[CumulativePoint]) -> str:
        """
        Equity curve coloured by regime — each segment coloured by the VIX
        regime active on that day.
        """
        dates   = [p.date for p in cumulative_series]
        returns = [p.cumulative_return * 100 for p in cumulative_series]
        regimes = [p.regime for p in cumulative_series]

        fig, ax = plt.subplots(figsize=(13, 4))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)

        # Draw segments coloured by regime
        for i in range(1, len(dates)):
            color = REGIME_COLORS.get(regimes[i], REGIME_COLORS["medium"])
            ax.plot(
                [dates[i-1], dates[i]],
                [returns[i-1], returns[i]],
                color=color, linewidth=1.5
            )

        ax.axhline(0, color="#aaaaaa", linewidth=0.7, linestyle=":")
        ax.fill_between(dates, returns, 0,
                        where=[r >= 0 for r in returns],
                        alpha=0.07, color="#2ca02c")
        ax.fill_between(dates, returns, 0,
                        where=[r < 0 for r in returns],
                        alpha=0.07, color="#d62728")

        # Legend
        patches = [
            mpatches.Patch(color=REGIME_COLORS[r], label=REGIME_LABELS[r])
            for r in ["low", "medium", "high"]
        ]
        ax.legend(handles=patches, fontsize=8, loc="upper left", frameon=False)

        # Sparse x ticks
        step = max(1, len(dates) // 8)
        ax.set_xticks([dates[i] for i in range(0, len(dates), step)])
        ax.set_xticklabels(
            [dates[i] for i in range(0, len(dates), step)],
            rotation=25, ha="right", fontsize=7
        )
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
        ax.tick_params(axis="y", labelsize=7)
        ax.set_ylabel("Cumulative Return (%)", fontsize=8)
        ax.set_title("Portfolio Equity Curve — Coloured by VIX Regime",
                     fontsize=10, fontweight="bold", pad=6)
        ax.grid(axis="y", color=GRID, linewidth=0.5)
        ax.spines[["top", "right"]].set_visible(False)

        plt.tight_layout()
        return _to_b64(fig)

    @staticmethod
    def generate_all(
        regime_stats: List[RegimeStats],
        transition_summaries: List[TransitionSummary],
        cumulative_series: List[CumulativePoint]
    ) -> Dict[str, str]:
        logger.info("Generating regime performance visualizations")
        return {
            "regime_stats_bar":     RegimePerformanceViz.regime_stats_bar(regime_stats),
            "win_rate_chart":       RegimePerformanceViz.win_rate_chart(regime_stats),
            "transition_heatmap":   RegimePerformanceViz.transition_heatmap(transition_summaries),
            "cumulative_chart":     RegimePerformanceViz.cumulative_return_chart(cumulative_series),
        }