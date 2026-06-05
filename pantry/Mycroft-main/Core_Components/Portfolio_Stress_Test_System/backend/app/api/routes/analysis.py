from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import logging
import uuid

from app.models.schemas import (
    AnalysisRequest, 
    AnalysisResponse,
    RegimeMetrics,
    CorrelationMetrics,
    DegradationAnalysis
)
from app.services.data_fetcher import DataFetcher, DataFetchError
from app.services.regime_classifier import RegimeClassifier
from app.services.returns_calculator import ReturnsCalculator
from app.services.correlation_analyzer import CorrelationAnalyzer
from app.services.risk_analyzer import RiskAnalyzer
from app.services.visualization import Visualizer

router = APIRouter()
logger = logging.getLogger("portfolio_analysis.api")

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_portfolio(request: AnalysisRequest):
    """
    Main endpoint for Layer 1 regime-dependent diversification analysis
    
    Process:
    1. Fetch price and VIX data
    2. Calculate returns
    3. Classify market regimes
    4. Calculate regime-specific correlations
    5. Compute diversification metrics
    6. Analyze degradation
    7. Generate visualizations
    8. Return comprehensive analysis
    """
    analysis_id = str(uuid.uuid4())
    logger.info(f"Starting analysis {analysis_id} for {len(request.portfolio)} holdings")
    
    try:
        # Extract tickers and weights
        tickers = [h.ticker for h in request.portfolio]
        weights = {h.ticker: h.weight for h in request.portfolio}
        
        # Step 1: Fetch price data
        logger.info("Step 1: Fetching price data")
        price_data = DataFetcher.fetch_price_data(
            tickers=tickers,
            lookback_days=request.params.lookback_days
        )
        
        # Step 2: Fetch VIX data
        logger.info("Step 2: Fetching VIX data")
        vix_data = DataFetcher.fetch_vix_data(
            lookback_days=request.params.lookback_days,
            use_5day_avg=request.params.use_5day_vix
        )
        
        # Step 3: Calculate returns
        logger.info("Step 3: Calculating log returns")
        returns = ReturnsCalculator.calculate_log_returns(price_data)
        
        # Step 4: Classify regimes
        logger.info("Step 4: Classifying market regimes")
        regimes = RegimeClassifier.classify_regimes(
            vix_data=vix_data,
            low_threshold=request.params.vix_low_threshold,
            high_threshold=request.params.vix_high_threshold,
            min_regime_days=request.params.min_regime_days
        )
        
        # Step 5: Calculate regime-specific correlations
        logger.info("Step 5: Calculating regime-specific correlations")
        correlations = CorrelationAnalyzer.calculate_regime_correlations(
            returns=returns,
            regimes=regimes,
            rolling_window=request.params.rolling_window
        )
        
        # Step 6: Calculate diversification metrics for each regime
        logger.info("Step 6: Calculating diversification metrics")
        metrics = {}
        for regime_name, corr_matrix in correlations.items():
            metrics[regime_name] = CorrelationAnalyzer.calculate_diversification_metrics(
                correlation_matrix=corr_matrix,
                weights=weights
            )
        
        # Step 7: Analyze degradation
        logger.info("Step 7: Analyzing diversification degradation")
        degradation = RiskAnalyzer.analyze_degradation(
            low_vix_metrics=metrics['low'],
            high_vix_metrics=metrics['high']
        )
        
        # Step 8: Generate risk flags
        logger.info("Step 8: Generating risk flags")
        risk_flags = RiskAnalyzer.generate_risk_flags(
            degradation=degradation,
            high_vix_metrics=metrics['high'],
            portfolio_size=len(request.portfolio)
        )
        
        # Step 9: Generate recommendations
        recommendations = RiskAnalyzer.generate_recommendations(risk_flags, degradation)
        
        # Step 10: Generate visualizations
        logger.info("Step 10: Generating visualizations")
        heatmaps = Visualizer.generate_correlation_heatmaps(
            correlations=correlations,
            tickers=tickers
        )
        degradation_chart = Visualizer.generate_degradation_chart(degradation)
        
        # Construct response
        response = AnalysisResponse(
            analysis_id=analysis_id,
            timestamp=datetime.now(),
            portfolio_summary={
                "num_holdings": len(request.portfolio),
                "tickers": tickers,
                "total_weight": sum(weights.values()),
                "lookback_days": request.params.lookback_days
            },
            regime_metrics=RegimeMetrics(
                low_vix=CorrelationMetrics(**metrics['low']),
                medium_vix=CorrelationMetrics(**metrics['medium']),
                high_vix=CorrelationMetrics(**metrics['high'])
            ),
            degradation_analysis=DegradationAnalysis(**degradation),
            risk_flags=risk_flags,
            recommendations=recommendations,
            visualizations={
                "correlation_heatmaps": heatmaps['combined'],
                "degradation_chart": degradation_chart
            }
        )
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        return response
        
    except DataFetchError as e:
        logger.error(f"Data fetch error in analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error in analysis {analysis_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
