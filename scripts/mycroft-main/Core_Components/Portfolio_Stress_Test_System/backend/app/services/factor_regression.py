import numpy as np
import pandas as pd
import statsmodels.api as sm
from typing import Dict, List, Tuple
import logging

from app.core.config import settings
from app.models.schemas import (
    FactorLoading, StaticRegressionResult,
    RollingFactorSeries, RollingLoadingPoint
)

logger = logging.getLogger("portfolio_analysis.factor_regression")

FACTORS = ["MKT", "SMB", "HML", "RMW", "CMA", "UMD"]


class FactorRegression:
    """
    OLS regression engine for Fama-French 5-factor + momentum model.

    Three modes:
      1. static   — single regression over full lookback period
      2. rolling  — 252-day rolling window, one regression per day
      3. regime   — separate regression per VIX regime label
    """

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _build_excess_returns(
        port_returns: pd.Series,
        factor_data: pd.DataFrame
    ) -> Tuple[pd.Series, pd.DataFrame]:
        """
        Align portfolio returns with factor data on common dates.
        Returns (excess_returns, X) where excess_returns = R_p - RF.
        """
        combined = pd.DataFrame({"R_p": port_returns}).join(
            factor_data, how="inner"
        ).dropna()

        y = combined["R_p"] - combined["RF"]          # excess returns
        X = combined[FACTORS]
        return y, X

    @staticmethod
    def _run_ols(
        y: pd.Series,
        X: pd.DataFrame,
        significance_level: float
    ) -> Dict:
        """
        Run OLS with constant (alpha). Return dict of regression stats.
        """
        X_const = sm.add_constant(X, has_constant="add")
        model   = sm.OLS(y, X_const).fit()

        port_var = float(y.var()) if y.var() > 0 else 1e-10

        loadings = []
        for factor in FACTORS:
            if factor not in model.params:
                continue
            b      = float(model.params[factor])
            t      = float(model.tvalues[factor])
            p      = float(model.pvalues[factor])
            f_var  = float(X[factor].var()) if X[factor].var() > 0 else 0.0
            ctv    = (b ** 2) * f_var / port_var   # contribution to variance

            loadings.append(FactorLoading(
                factor=factor,
                beta=round(b, 4),
                t_stat=round(t, 3),
                p_value=round(p, 4),
                significant=(p < significance_level),
                contribution_to_variance=round(max(ctv, 0.0), 4)
            ))

        alpha_daily     = float(model.params.get("const", 0.0))
        alpha_annual    = alpha_daily * 252
        alpha_t         = float(model.tvalues.get("const", 0.0))
        alpha_p         = float(model.pvalues.get("const", 1.0))
        r2              = float(model.rsquared)
        adj_r2          = float(model.rsquared_adj)
        dominant        = max(loadings, key=lambda l: l.contribution_to_variance).factor \
                          if loadings else "MKT"

        return {
            "alpha":                  round(alpha_annual, 4),
            "alpha_t_stat":           round(alpha_t, 3),
            "alpha_p_value":          round(alpha_p, 4),
            "r_squared":              round(r2, 4),
            "adj_r_squared":          round(adj_r2, 4),
            "unexplained_variance_pct": round((1 - r2) * 100, 2),
            "factor_loadings":        loadings,
            "dominant_factor":        dominant,
            "observations":           int(model.nobs),
        }

    # ── Public methods ────────────────────────────────────────────────────

    @staticmethod
    def static_regression(
        port_returns: pd.Series,
        factor_data: pd.DataFrame,
        significance_level: float = 0.05
    ) -> StaticRegressionResult:
        """Full-period OLS regression."""
        logger.info("Running static factor regression")

        # Force tz-naive on both before join
        pr = port_returns.copy()
        pr.index = pr.index.tz_localize(None) if pr.index.tz else pr.index
        fd = factor_data.copy()
        fd.index = fd.index.tz_localize(None) if fd.index.tz else fd.index

        y, X = FactorRegression._build_excess_returns(pr, fd)

        if len(y) < 60:
            raise ValueError(
                f"Insufficient data for regression: {len(y)} observations (need ≥ 60)"
            )

        stats = FactorRegression._run_ols(y, X, significance_level)
        logger.info(
            f"Static regression: R²={stats['r_squared']:.3f}, "
            f"α={stats['alpha']*100:+.2f}% ann., "
            f"dominant={stats['dominant_factor']}"
        )
        return StaticRegressionResult(**stats)

    @staticmethod
    def rolling_regression(
        port_returns: pd.Series,
        factor_data: pd.DataFrame,
        window: int = 252,
        significance_level: float = 0.05
    ) -> List[RollingFactorSeries]:
        """
        Rolling OLS: one regression per day using the past `window` observations.
        Returns one RollingFactorSeries per factor.
        """
        logger.info(f"Running rolling regression (window={window})")

        # Force tz-naive on both before the inner join
        pr = port_returns.copy()
        pr.index = pr.index.tz_localize(None) if pr.index.tz else pr.index
        fd = factor_data.copy()
        fd.index = fd.index.tz_localize(None) if fd.index.tz else fd.index

        y, X = FactorRegression._build_excess_returns(pr, fd)
        logger.info(f"Rolling regression: {len(y)} common obs, y.index.tz={y.index.tz}, X.shape={X.shape}")

        if len(y) < window + 1:
            raise ValueError(
                f"Need at least {window + 1} observations for rolling regression, "
                f"got {len(y)}"
            )

        dates  = y.index
        n      = len(y)
        y_arr  = y.values
        X_df   = X  # keep as DataFrame to preserve column names in OLS
        n_fac  = len(FACTORS)

        # Pre-allocate: rows = time steps, cols = factors
        betas  = np.full((n, n_fac), np.nan)
        r2s    = np.full(n, np.nan)

        for i in range(window - 1, n):
            y_w  = y_arr[i - window + 1: i + 1]
            X_w  = X_df.iloc[i - window + 1: i + 1]   # DataFrame slice keeps names
            X_c  = sm.add_constant(X_w, has_constant="add")
            try:
                res      = sm.OLS(y_w, X_c).fit()
                for fi, factor in enumerate(FACTORS):
                    betas[i, fi] = res.params.get(factor, np.nan)
                r2s[i]   = res.rsquared
            except Exception:
                pass

        series_list = []
        for fi, factor in enumerate(FACTORS):
            beta_series = betas[:, fi]
            valid_mask  = ~np.isnan(beta_series)

            points = [
                RollingLoadingPoint(
                    date=str(dates[i].date()),
                    beta=round(float(beta_series[i]), 4),
                    r_squared=round(float(r2s[i]), 4) if not np.isnan(r2s[i]) else 0.0
                )
                for i in range(n) if valid_mask[i]
            ]

            valid_betas    = beta_series[valid_mask]
            drift_mag      = float(valid_betas.max() - valid_betas.min()) \
                             if len(valid_betas) > 0 else 0.0
            drift_flag     = drift_mag > settings.DRIFT_THRESHOLD

            series_list.append(RollingFactorSeries(
                factor=factor,
                series=points,
                drift_flag=drift_flag,
                drift_magnitude=round(drift_mag, 4)
            ))
            if drift_flag:
                logger.info(f"  Drift flag: {factor} range={drift_mag:.3f}")

        logger.info(f"Rolling regression complete: {sum(1 for s in series_list if s.drift_flag)} drift flags")
        return series_list

    @staticmethod
    def regime_regression(
        port_returns: pd.Series,
        factor_data: pd.DataFrame,
        regimes: pd.Series,
        significance_level: float = 0.05
    ) -> List["RegimeFactorLoadings"]:
        """
        Run separate OLS regression for each VIX regime (low / medium / high).
        """
        from app.models.schemas import RegimeFactorLoadings

        logger.info("Running regime-conditional factor regressions")

        # Strip tz and align all three series
        port_returns = port_returns.copy()
        port_returns.index = port_returns.index.tz_localize(None) \
            if port_returns.index.tz else port_returns.index

        factor_data = factor_data.copy()
        factor_data.index = factor_data.index.tz_localize(None) \
            if factor_data.index.tz else factor_data.index

        regimes = regimes.copy()
        regimes.index = regimes.index.tz_localize(None) \
            if regimes.index.tz else regimes.index

        results = []
        for regime_name in ["low", "medium", "high"]:
            regime_dates = regimes[regimes == regime_name].index
            r_regime     = port_returns.reindex(regime_dates).dropna()
            f_regime     = factor_data.reindex(regime_dates).dropna()

            common       = r_regime.index.intersection(f_regime.index)
            r_regime     = r_regime.loc[common]
            f_regime     = f_regime.loc[common]

            if len(common) < 15:
                logger.warning(
                    f"  {regime_name}: only {len(common)} obs — skipping regression"
                )
                results.append(RegimeFactorLoadings(
                    regime=regime_name,
                    observations=len(common),
                    factor_loadings=[],
                    r_squared=0.0,
                    alpha=0.0
                ))
                continue

            y, X = FactorRegression._build_excess_returns(r_regime, f_regime)
            stats = FactorRegression._run_ols(y, X, significance_level)

            results.append(RegimeFactorLoadings(
                regime=regime_name,
                observations=stats["observations"],
                factor_loadings=stats["factor_loadings"],
                r_squared=stats["r_squared"],
                alpha=stats["alpha"]
            ))
            logger.info(
                f"  {regime_name}: {stats['observations']} obs, "
                f"R²={stats['r_squared']:.3f}, α={stats['alpha']*100:+.2f}%"
            )

        return results