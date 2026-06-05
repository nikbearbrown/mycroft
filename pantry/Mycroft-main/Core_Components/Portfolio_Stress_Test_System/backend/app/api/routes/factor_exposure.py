from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
import uuid

from app.models.schemas import FactorExposureRequest, FactorExposureResponse
from app.services.data_fetcher import DataFetcher, DataFetchError
from app.services.returns_calculator import ReturnsCalculator
from app.services.regime_classifier import RegimeClassifier
from app.services.factor_fetcher import FactorFetcher, FactorFetchError
from app.services.factor_regression import FactorRegression
from app.services.factor_analyzer import FactorAnalyzer
from app.services.factor_visualization import FactorVisualization

router = APIRouter()
logger = logging.getLogger("portfolio_analysis.factor_exposure_api")


@router.post("/factor-exposure", response_model=FactorExposureResponse)
async def run_factor_exposure(request: FactorExposureRequest):
    """
    Layer 3 endpoint — Factor Exposure Decomposition.

    Steps:
      1. Fetch portfolio price data + VIX (reuse Layer 1 fetchers)
      2. Calculate portfolio log returns, weight into single series
      3. Fetch/cache Fama-French 5-factor + momentum data
      4. Align factor data to portfolio return window
      5. Static OLS regression (full period)
      6. Rolling OLS regression (252-day window)
      7. Regime-conditional regression (per VIX regime)
      8. Generate risk flags + recommendations
      9. Generate visualizations
    """
    exposure_id = str(uuid.uuid4())
    tickers = [h.ticker for h in request.portfolio]
    weights = {h.ticker: h.weight for h in request.portfolio}
    p = request.params

    logger.info(
        f"[{exposure_id}] Starting factor exposure for "
        f"{len(tickers)} holdings, lookback={p.lookback_days}d"
    )

    try:
        # ── 1. Fetch price data ────────────────────────────────────────────
        logger.info(f"[{exposure_id}] Step 1: Fetching price data")
        price_data = DataFetcher.fetch_price_data(
            tickers=tickers,
            lookback_days=p.lookback_days
        )

        # ── 2. Calculate individual returns ───────────────────────────────
        logger.info(f"[{exposure_id}] Step 2: Calculating log returns")
        returns_df = ReturnsCalculator.calculate_log_returns(price_data)

        # Build weighted portfolio return series
        port_returns = sum(
            returns_df[t] * weights[t]
            for t in tickers if t in returns_df.columns
        )
        port_returns.name = "portfolio"
        port_returns = port_returns.dropna()

        # Normalise index timezone
        port_returns.index = port_returns.index.tz_localize(None) \
            if port_returns.index.tz else port_returns.index

        # ── 3. Fetch factor data ───────────────────────────────────────────
        logger.info(f"[{exposure_id}] Step 3: Fetching factor data")
        start_str = str(port_returns.index.min().date())
        end_str   = str(port_returns.index.max().date())
        factor_data = FactorFetcher.get_factors_for_period(start_str, end_str)

        # Clip portfolio returns to factor data availability
        # (French library typically lags 4-6 weeks behind today)
        factor_end = factor_data.index.max()
        if port_returns.index.max() > factor_end:
            original_end = port_returns.index.max().date()
            port_returns = port_returns[port_returns.index <= factor_end]
            logger.info(
                f"[{exposure_id}] Portfolio returns clipped to factor data availability: "
                f"{original_end} → {factor_end.date()} "
                f"({len(port_returns)} rows remaining)"
            )

        # ── 4. Fetch VIX + classify regimes ───────────────────────────────
        logger.info(f"[{exposure_id}] Step 4: Classifying VIX regimes")
        vix_data = DataFetcher.fetch_vix_data(
            lookback_days=p.lookback_days,
            use_5day_avg=p.use_5day_vix
        )
        regimes = RegimeClassifier.classify_regimes(
            vix_data=vix_data,
            low_threshold=p.vix_low_threshold,
            high_threshold=p.vix_high_threshold,
            min_regime_days=p.min_regime_days
        )

        # ── 5. Static regression ───────────────────────────────────────────
        logger.info(f"[{exposure_id}] Step 5: Static regression")
        static_result = FactorRegression.static_regression(
            port_returns=port_returns,
            factor_data=factor_data,
            significance_level=p.significance_level
        )

        # ── 6. Rolling regression ──────────────────────────────────────────
        logger.info(f"[{exposure_id}] Step 6: Rolling regression")
        rolling_results = FactorRegression.rolling_regression(
            port_returns=port_returns,
            factor_data=factor_data,
            window=p.rolling_window,
            significance_level=p.significance_level
        )

        # ── 7. Regime regression ───────────────────────────────────────────
        logger.info(f"[{exposure_id}] Step 7: Regime-conditional regression")
        regime_results = FactorRegression.regime_regression(
            port_returns=port_returns,
            factor_data=factor_data,
            regimes=regimes,
            significance_level=p.significance_level
        )

        # ── 8. Flags + recommendations ─────────────────────────────────────
        logger.info(f"[{exposure_id}] Step 8: Generating flags")
        risk_flags = FactorAnalyzer.generate_flags(
            static=static_result,
            rolling=rolling_results,
            regime_results=regime_results
        )
        recommendations = FactorAnalyzer.generate_recommendations(
            flags=risk_flags,
            static=static_result
        )

        # ── 9. Visualizations ──────────────────────────────────────────────
        logger.info(f"[{exposure_id}] Step 9: Generating visualizations")
        visualizations = FactorVisualization.generate_all(
            static=static_result,
            rolling=rolling_results,
            regime_results=regime_results
        )

        logger.info(
            f"[{exposure_id}] Complete — R²={static_result.r_squared:.3f}, "
            f"α={static_result.alpha*100:+.2f}%/yr, "
            f"{len(risk_flags)} flags"
        )

        return FactorExposureResponse(
            exposure_id=exposure_id,
            timestamp=datetime.now(),
            portfolio_summary={
                "num_holdings":  len(request.portfolio),
                "tickers":       tickers,
                "total_weight":  sum(weights.values()),
                "lookback_days": p.lookback_days,
                "date_range":    f"{start_str} → {end_str}",
            },
            static_regression=static_result,
            rolling_regressions=rolling_results,
            regime_regressions=regime_results,
            risk_flags=risk_flags,
            recommendations=recommendations,
            visualizations=visualizations
        )

    except (DataFetchError, FactorFetchError) as e:
        logger.error(f"[{exposure_id}] Data error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except ValueError as e:
        logger.error(f"[{exposure_id}] Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error(f"[{exposure_id}] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Factor analysis failed: {e}")