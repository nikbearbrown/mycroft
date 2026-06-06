import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
import base64
from io import BytesIO
from typing import List, Dict
import logging

from app.models.schemas import CrashResult

logger = logging.getLogger("portfolio_analysis.crash_visualization")

# ── shared style ──────────────────────────────────────────────────────────────
COLORS = {
    "portfolio":  "#1f77b4",
    "benchmark":  "#d62728",
    "positive":   "#2ca02c",
    "negative":   "#d62728",
    "neutral":    "#7f7f7f",
    "bg":         "#f8f9fa",
    "grid":       "#e0e0e0",
}

def _to_b64(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


class CrashVisualization:

    @staticmethod
    def generate_drawdown_chart(crash_results: List[CrashResult]) -> str:
        """
        One subplot per crash, showing portfolio vs benchmark drawdown paths.
        """
        n = len(crash_results)
        ncols = min(2, n)
        nrows = (n + 1) // 2

        fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4.5 * nrows))
        fig.patch.set_facecolor(COLORS["bg"])

        # Flatten axes for uniform indexing
        if n == 1:
            axes = [axes]
        elif nrows == 1:
            axes = list(axes)
        else:
            axes = [ax for row in axes for ax in row]

        for idx, result in enumerate(crash_results):
            ax = axes[idx]
            ax.set_facecolor(COLORS["bg"])

            if result.drawdown_series:
                dates  = [p.date for p in result.drawdown_series]
                p_dd   = [p.portfolio_dd * 100 for p in result.drawdown_series]
                b_dd   = [p.benchmark_dd * 100 for p in result.drawdown_series]

                ax.plot(dates, p_dd, color=COLORS["portfolio"],
                        linewidth=2.0, label="Portfolio")
                ax.fill_between(dates, p_dd, 0, alpha=0.15, color=COLORS["portfolio"])
                ax.plot(dates, b_dd, color=COLORS["benchmark"],
                        linewidth=1.5, linestyle="--", label=result.benchmark_ticker)

            ax.axhline(0, color=COLORS["neutral"], linewidth=0.8, linestyle=":")
            ax.set_title(
                f"{result.name}\n"
                f"Port: {result.portfolio_total_return*100:+.1f}%  |  "
                f"Bench: {result.benchmark_total_return*100:+.1f}%  |  "
                f"Max DD: {result.max_drawdown*100:.1f}%",
                fontsize=9, pad=6
            )
            ax.set_ylabel("Drawdown (%)", fontsize=8)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))

            # Sparse x-tick labels
            if result.drawdown_series:
                step = max(1, len(dates) // 5)
                tick_positions = list(range(0, len(dates), step))
                ax.set_xticks([dates[i] for i in tick_positions])
                ax.set_xticklabels(
                    [dates[i] for i in tick_positions],
                    rotation=30, ha="right", fontsize=7
                )

            ax.grid(axis="y", color=COLORS["grid"], linewidth=0.7)
            ax.legend(fontsize=8, loc="lower left")
            ax.spines[["top", "right"]].set_visible(False)

        # Hide unused subplots
        for j in range(n, len(axes)):
            axes[j].set_visible(False)

        fig.suptitle("Portfolio vs Benchmark Drawdown — Historical Crashes",
                     fontsize=13, fontweight="bold", y=1.01)
        plt.tight_layout()
        return _to_b64(fig)

    @staticmethod
    def generate_loss_driver_chart(crash_results: List[CrashResult]) -> str:
        """
        Horizontal bar chart of per-holding contribution to loss for each crash.
        """
        n = len(crash_results)
        ncols = min(2, n)
        nrows = (n + 1) // 2

        fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4.5 * nrows))
        fig.patch.set_facecolor(COLORS["bg"])

        if n == 1:
            axes = [axes]
        elif nrows == 1:
            axes = list(axes)
        else:
            axes = [ax for row in axes for ax in row]

        for idx, result in enumerate(crash_results):
            ax = axes[idx]
            ax.set_facecolor(COLORS["bg"])

            drivers = result.loss_drivers
            tickers  = [d.ticker for d in drivers]
            contribs = [d.contribution_to_loss * 100 for d in drivers]
            colors   = [COLORS["negative"] if c < 0 else COLORS["positive"] for c in contribs]

            bars = ax.barh(tickers, contribs, color=colors, edgecolor="white", height=0.6)
            ax.axvline(0, color=COLORS["neutral"], linewidth=0.8)

            for bar, val in zip(bars, contribs):
                ax.text(
                    val + (0.1 if val >= 0 else -0.1),
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:+.2f}%", va="center",
                    ha="left" if val >= 0 else "right",
                    fontsize=8
                )

            ax.set_title(f"{result.name} — Loss Attribution", fontsize=9, pad=6)
            ax.set_xlabel("Contribution to Portfolio Return (%)", fontsize=8)
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}%"))
            ax.grid(axis="x", color=COLORS["grid"], linewidth=0.7)
            ax.spines[["top", "right"]].set_visible(False)

        for j in range(n, len(axes)):
            axes[j].set_visible(False)

        fig.suptitle("Loss Attribution by Holding", fontsize=13, fontweight="bold", y=1.01)
        plt.tight_layout()
        return _to_b64(fig)

    @staticmethod
    def generate_summary_heatmap(crash_results: List[CrashResult]) -> str:
        """
        Heatmap: rows = holdings, columns = crashes.
        Cell = holding's total return (%) during that crash.
        """
        tickers = sorted({d.ticker for r in crash_results for d in r.loss_drivers})
        crash_names = [r.name for r in crash_results]

        matrix = np.zeros((len(tickers), len(crash_results)))
        for j, result in enumerate(crash_results):
            for d in result.loss_drivers:
                if d.ticker in tickers:
                    i = tickers.index(d.ticker)
                    matrix[i, j] = d.period_return * 100

        fig, ax = plt.subplots(figsize=(max(8, len(crash_results) * 2.5), max(4, len(tickers) * 0.7)))
        fig.patch.set_facecolor(COLORS["bg"])
        ax.set_facecolor(COLORS["bg"])

        vmax = max(abs(matrix.max()), abs(matrix.min()), 1)
        im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto",
                       vmin=-vmax, vmax=vmax)

        ax.set_xticks(range(len(crash_names)))
        ax.set_xticklabels(crash_names, rotation=20, ha="right", fontsize=9)
        ax.set_yticks(range(len(tickers)))
        ax.set_yticklabels(tickers, fontsize=9)

        for i in range(len(tickers)):
            for j in range(len(crash_results)):
                val = matrix[i, j]
                ax.text(j, i, f"{val:+.1f}%", ha="center", va="center",
                        fontsize=8,
                        color="white" if abs(val) > vmax * 0.6 else "black")

        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("Return (%)", fontsize=8)
        ax.set_title("Holding Returns Across Crash Periods", fontsize=12, fontweight="bold", pad=10)
        ax.spines[["top", "right", "left", "bottom"]].set_visible(False)

        plt.tight_layout()
        return _to_b64(fig)

    @staticmethod
    def generate_all(crash_results: List[CrashResult]) -> Dict[str, str]:
        logger.info("Generating crash simulation visualizations")
        return {
            "drawdown_chart":    CrashVisualization.generate_drawdown_chart(crash_results),
            "loss_driver_chart": CrashVisualization.generate_loss_driver_chart(crash_results),
            "summary_heatmap":   CrashVisualization.generate_summary_heatmap(crash_results),
        }