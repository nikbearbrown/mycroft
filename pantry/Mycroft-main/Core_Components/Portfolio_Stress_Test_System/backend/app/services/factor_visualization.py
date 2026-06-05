import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import base64
from io import BytesIO
from typing import List, Dict
import logging

from app.models.schemas import (
    StaticRegressionResult, RollingFactorSeries, RegimeFactorLoadings
)

logger = logging.getLogger("portfolio_analysis.factor_visualization")

COLORS = {
    "MKT": "#1f77b4",
    "SMB": "#ff7f0e",
    "HML": "#2ca02c",
    "RMW": "#9467bd",
    "CMA": "#8c564b",
    "UMD": "#e377c2",
    "pos": "#2ca02c",
    "neg": "#d62728",
    "neutral": "#7f7f7f",
    "bg": "#f8f9fa",
    "grid": "#e0e0e0",
}

FACTOR_LABELS = {
    "MKT": "Market β",
    "SMB": "Size",
    "HML": "Value",
    "RMW": "Profitability",
    "CMA": "Investment",
    "UMD": "Momentum",
}


def _to_b64(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


class FactorVisualization:

    @staticmethod
    def factor_beta_bar(static: StaticRegressionResult) -> str:
        """
        Horizontal bar chart of factor betas with error-bar style t-stat annotation.
        Significant loadings in solid colour, insignificant greyed out.
        """
        loadings = static.factor_loadings
        factors  = [FACTOR_LABELS[l.factor] for l in loadings]
        betas    = [l.beta for l in loadings]
        colors   = [
            (COLORS[l.factor] if l.significant else "#cccccc")
            for l in loadings
        ]

        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor(COLORS["bg"])
        ax.set_facecolor(COLORS["bg"])

        bars = ax.barh(factors, betas, color=colors, edgecolor="white", height=0.55)
        ax.axvline(0, color=COLORS["neutral"], linewidth=0.9)

        for bar, loading in zip(bars, loadings):
            x   = loading.beta
            sig = "**" if loading.p_value < 0.01 else ("*" if loading.p_value < 0.05 else "")
            ax.text(
                x + (0.02 if x >= 0 else -0.02),
                bar.get_y() + bar.get_height() / 2,
                f"{x:+.3f}{sig}",
                va="center", ha="left" if x >= 0 else "right",
                fontsize=8
            )

        ax.set_xlabel("Factor Beta (β)", fontsize=8)
        ax.set_title(
            f"Factor Loadings  ·  R²={static.r_squared:.3f}  ·  "
            f"α={static.alpha*100:+.2f}%/yr  ·  n={static.observations}",
            fontsize=9, pad=6
        )
        ax.text(
            0.99, 0.02, "* p<0.05  ** p<0.01  grey=insignificant",
            transform=ax.transAxes, ha="right", fontsize=6.5, color="#666"
        )
        ax.grid(axis="x", color=COLORS["grid"], linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
        plt.tight_layout()
        return _to_b64(fig)

    @staticmethod
    def variance_decomposition_pie(static: StaticRegressionResult) -> str:
        """
        Pie chart: factor contributions to explained variance + unexplained slice.
        """
        loadings   = [l for l in static.factor_loadings if l.contribution_to_variance > 0]
        labels     = [FACTOR_LABELS[l.factor] for l in loadings] + ["Unexplained"]
        sizes      = [l.contribution_to_variance for l in loadings]
        unexplained = max(0.0, 1.0 - sum(sizes))
        sizes.append(unexplained)
        colors     = [COLORS[l.factor] for l in loadings] + ["#cccccc"]

        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor(COLORS["bg"])
        ax.set_facecolor(COLORS["bg"])

        wedges, texts, autotexts = ax.pie(
            sizes, labels=None, colors=colors,
            autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
            startangle=140, pctdistance=0.75,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5}
        )
        for at in autotexts:
            at.set_fontsize(7.5)

        ax.legend(
            wedges, labels,
            loc="lower center", bbox_to_anchor=(0.5, -0.12),
            ncol=3, fontsize=7.5, frameon=False
        )
        ax.set_title("Variance Decomposition by Factor", fontsize=9, pad=10)
        plt.tight_layout()
        return _to_b64(fig)

    @staticmethod
    def rolling_beta_chart(rolling: List[RollingFactorSeries]) -> str:
        """
        One subplot per factor showing rolling beta over time.
        Drift-flagged factors get a shaded range band.
        """
        n    = len(rolling)
        cols = 2
        rows = (n + 1) // 2

        fig, axes = plt.subplots(rows, cols, figsize=(13, 2.8 * rows), sharey=False)
        fig.patch.set_facecolor(COLORS["bg"])

        if n == 1:
            axes = [axes]
        elif rows == 1:
            axes = list(axes)
        else:
            axes = [ax for row in axes for ax in row]

        for idx, series in enumerate(rolling):
            ax    = axes[idx]
            ax.set_facecolor(COLORS["bg"])
            color = COLORS[series.factor]

            if not series.series:
                ax.set_title(f"{FACTOR_LABELS[series.factor]} — no data", fontsize=8)
                continue

            dates = [p.date for p in series.series]
            betas = [p.beta  for p in series.series]

            ax.plot(dates, betas, color=color, linewidth=1.4, label=series.factor)
            ax.axhline(0, color=COLORS["neutral"], linewidth=0.6, linestyle=":")

            if series.drift_flag:
                ax.fill_between(dates, betas,
                                alpha=0.12, color=color)
                ax.set_title(
                    f"{FACTOR_LABELS[series.factor]}  ⚠ drift={series.drift_magnitude:.2f}",
                    fontsize=8, color="#c62828", pad=3
                )
            else:
                ax.set_title(f"{FACTOR_LABELS[series.factor]}", fontsize=8, pad=3)

            # Sparse x ticks
            step = max(1, len(dates) // 4)
            ax.set_xticks([dates[i] for i in range(0, len(dates), step)])
            ax.set_xticklabels(
                [dates[i] for i in range(0, len(dates), step)],
                rotation=25, ha="right", fontsize=6
            )
            ax.tick_params(axis="y", labelsize=6.5)
            ax.grid(axis="y", color=COLORS["grid"], linewidth=0.5)
            ax.spines[["top", "right"]].set_visible(False)

        for j in range(n, len(axes)):
            axes[j].set_visible(False)

        fig.suptitle("Rolling Factor Loadings (252-day window)",
                     fontsize=11, fontweight="bold", y=1.01)
        plt.tight_layout()
        return _to_b64(fig)

    @staticmethod
    def regime_beta_heatmap(regime_results: List[RegimeFactorLoadings]) -> str:
        """
        Heatmap: rows = factors, columns = regimes.
        Cell = beta value. Annotated with significance stars.
        """
        factors = ["MKT", "SMB", "HML", "RMW", "CMA", "UMD"]
        regimes = ["low", "medium", "high"]
        labels  = ["Low VIX", "Med VIX", "High VIX"]

        matrix   = np.full((len(factors), len(regimes)), np.nan)
        sig_mask = np.zeros((len(factors), len(regimes)), dtype=bool)

        for j, regime_name in enumerate(regimes):
            res = next((r for r in regime_results if r.regime == regime_name), None)
            if res is None or not res.factor_loadings:
                continue
            for i, factor in enumerate(factors):
                loading = next((l for l in res.factor_loadings if l.factor == factor), None)
                if loading:
                    matrix[i, j]   = loading.beta
                    sig_mask[i, j] = loading.significant

        vmax = np.nanmax(np.abs(matrix)) if not np.all(np.isnan(matrix)) else 1.0

        fig, ax = plt.subplots(figsize=(6, 4.5))
        fig.patch.set_facecolor(COLORS["bg"])
        ax.set_facecolor(COLORS["bg"])

        # Use masked array so NaN cells render as grey
        masked = np.ma.masked_invalid(matrix)
        cmap = plt.cm.RdYlGn
        cmap.set_bad(color="#d0d0d0")

        im = ax.imshow(masked, cmap=cmap, aspect="auto",
                       vmin=-vmax, vmax=vmax)

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_yticks(range(len(factors)))
        ax.set_yticklabels([FACTOR_LABELS[f] for f in factors], fontsize=8)

        for i in range(len(factors)):
            for j in range(len(regimes)):
                val = matrix[i, j]
                if np.isnan(val):
                    ax.text(j, i, "N/A", ha="center", va="center",
                            fontsize=7.5, color="#888888")
                else:
                    star = "*" if sig_mask[i, j] else ""
                    ax.text(j, i, f"{val:+.2f}{star}",
                            ha="center", va="center", fontsize=7.5,
                            color="white" if abs(val) > vmax * 0.6 else "black")

        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("Beta (β)", fontsize=7.5)
        cbar.ax.tick_params(labelsize=7)

        ax.set_title("Factor Loadings by VIX Regime  (* = p<0.05)",
                     fontsize=9, pad=8)
        ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
        plt.tight_layout()
        return _to_b64(fig)

    @staticmethod
    def generate_all(
        static: StaticRegressionResult,
        rolling: List[RollingFactorSeries],
        regime_results: List[RegimeFactorLoadings]
    ) -> Dict[str, str]:
        logger.info("Generating factor exposure visualizations")
        return {
            "factor_betas":          FactorVisualization.factor_beta_bar(static),
            "variance_decomposition": FactorVisualization.variance_decomposition_pie(static),
            "rolling_betas":         FactorVisualization.rolling_beta_chart(rolling),
            "regime_heatmap":        FactorVisualization.regime_beta_heatmap(regime_results),
        }