from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
import uuid

from app.models.schemas import RegimePerformanceRequest, RegimePerformanceResponse
from app.services.data_fetcher import DataFetcher, DataFetchError
from app.services.returns_calculator import ReturnsCalculator
from app.services.regime_classifier import RegimeClassifier
from app.services.factor_fetcher import FactorFetcher, FactorFetchError
from app.services.regime_performance import RegimePerformanceEngine
from app.services.regime_performance_viz import RegimePerformanceViz

router = APIRouter()
logger = logging.getLogger("portfolio_analysis.regime_performance_api")


@router.post("/regime-performance", response_model=RegimePerformanceResponse)
async def run_regime_performance(request: RegimePerformanceRequest):
    """
    Layer 4 endpoint — Regime-Specific Performance Analysis.

    Steps:
      1. Fetch portfolio price data + VIX
      2. Calculate weighted portfolio returns
      3. Classify VIX regimes
      4. Fetch risk-free rate from cached factor data (RF column)
      5. Compute per-regime statistics
      6. Detect regime transitions + forward returns
      7. Build cumulative return series
      8. Generate risk flags + recommendations
      9. Generate visualizations
    """
    performance_id = str(uuid.uuid4())
    tickers = [h.ticker for h in request.portfolio]
    weights = {h.ticker: h.weight for h in request.portfolio}
    p = request.params

    logger.info(
        f"[{performance_id}] Starting regime performance for "
        f"{len(tickers)} holdings, lookback={p.lookback_days}d"
    )

    try:
        # ── 1. Fetch price data ────────────────────────────────────────────
        logger.info(f"[{performance_id}] Step 1: Fetching price data")
        price_data = DataFetcher.fetch_price_data(
            tickers=tickers,
            lookback_days=p.lookback_days
        )

        # ── 2. Portfolio returns ───────────────────────────────────────────
        logger.info(f"[{performance_id}] Step 2: Calculating returns")
        returns_df = ReturnsCalculator.calculate_log_returns(price_data)

        port_returns = sum(
            returns_df[t] * weights[t]
            for t in tickers if t in returns_df.columns
        )
        port_returns.name = "portfolio"
        port_returns = port_returns.dropna()
        port_returns.index = port_returns.index.tz_localize(None) \
            if port_returns.index.tz else port_returns.index

        # ── 3. VIX regimes ─────────────────────────────────────────────────
        logger.info(f"[{performance_id}] Step 3: Classifying regimes")
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

        # ── 4. Risk-free rate from French cache ────────────────────────────
        logger.info(f"[{performance_id}] Step 4: Fetching risk-free rate")
        start_str = str(port_returns.index.min().date())
        end_str   = str(port_returns.index.max().date())
        try:
            factor_data = FactorFetcher.get_factors_for_period(start_str, end_str)
            rf = factor_data["RF"]
            rf.index = rf.index.tz_localize(None) if rf.index.tz else rf.index
            logger.info(f"[{performance_id}] RF rate loaded: {len(rf)} rows")
        except FactorFetchError as e:
            logger.warning(f"[{performance_id}] RF fetch failed, using zero: {e}")
            rf = port_returns * 0.0   # fallback: zero RF

        # ── 5. Align + per-regime stats ────────────────────────────────────
        logger.info(f"[{performance_id}] Step 5: Computing regime stats")
        port_aligned, regimes_aligned, rf_aligned = RegimePerformanceEngine._align(
            port_returns, regimes, rf
        )
        logger.info(
            f"[{performance_id}] Aligned: {len(port_aligned)} obs, "
            f"date range {port_aligned.index.min().date()} → "
            f"{port_aligned.index.max().date()}"
        )

        regime_stats = RegimePerformanceEngine.compute_regime_stats(
            port_aligned, regimes_aligned, rf_aligned
        )

        # ── 6. Transition analysis ─────────────────────────────────────────
        logger.info(f"[{performance_id}] Step 6: Transition analysis")
        transition_events, transition_summaries = \
            RegimePerformanceEngine.compute_transitions(
                port_aligned, regimes_aligned,
                windows=p.transition_windows
            )

        # ── 7. Cumulative series ───────────────────────────────────────────
        logger.info(f"[{performance_id}] Step 7: Cumulative return series")
        cumulative_series = RegimePerformanceEngine.compute_cumulative_series(
            port_aligned, regimes_aligned
        )

        # ── 8. Flags + recommendations ─────────────────────────────────────
        logger.info(f"[{performance_id}] Step 8: Generating flags")
        risk_flags = RegimePerformanceEngine.generate_flags(
            regime_stats, transition_summaries
        )
        recommendations = RegimePerformanceEngine.generate_recommendations(
            risk_flags, regime_stats, transition_summaries
        )

        # ── 9. Visualizations ──────────────────────────────────────────────
        logger.info(f"[{performance_id}] Step 9: Generating visualizations")
        visualizations = RegimePerformanceViz.generate_all(
            regime_stats, transition_summaries, cumulative_series
        )

        logger.info(
            f"[{performance_id}] Complete — "
            f"{len(risk_flags)} flags, "
            f"{len(transition_events)} transitions"
        )

        return RegimePerformanceResponse(
            performance_id=performance_id,
            timestamp=datetime.now(),
            portfolio_summary={
                "num_holdings":  len(request.portfolio),
                "tickers":       tickers,
                "total_weight":  sum(weights.values()),
                "lookback_days": p.lookback_days,
                "date_range":    f"{start_str} → {end_str}",
                "total_transitions": len(transition_events),
            },
            regime_stats=regime_stats,
            transition_events=transition_events,
            transition_summaries=transition_summaries,
            cumulative_series=cumulative_series,
            risk_flags=risk_flags,
            recommendations=recommendations,
            visualizations=visualizations
        )

    except DataFetchError as e:
        logger.error(f"[{performance_id}] Data error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        logger.error(f"[{performance_id}] Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"[{performance_id}] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Regime performance analysis failed: {e}")