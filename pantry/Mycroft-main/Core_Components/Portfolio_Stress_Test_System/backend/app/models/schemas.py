from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime, date

# ============================================================
# LAYER 1 — unchanged
# ============================================================

class PortfolioHolding(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    shares: float = Field(..., gt=0)
    weight: float = Field(..., ge=0, le=1)

    @validator('ticker')
    def ticker_uppercase(cls, v):
        return v.upper().strip()

class AnalysisParameters(BaseModel):
    lookback_days: int = Field(default=756, ge=252, le=2520)
    rolling_window: int = Field(default=252, ge=20, le=504)
    vix_low_threshold: float = Field(default=15.0, ge=10, le=20)
    vix_high_threshold: float = Field(default=25.0, ge=20, le=40)
    min_regime_days: int = Field(default=20, ge=5, le=60)
    use_5day_vix: bool = Field(default=True)

class AnalysisRequest(BaseModel):
    portfolio: List[PortfolioHolding] = Field(..., min_items=2, max_items=50)
    params: Optional[AnalysisParameters] = Field(default_factory=AnalysisParameters)

    @validator('portfolio')
    def validate_weights(cls, holdings):
        total = sum(h.weight for h in holdings)
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        return holdings

class CorrelationMetrics(BaseModel):
    avg_pairwise_correlation: float
    max_correlation: float
    min_correlation: float
    effective_n_assets: float

class RegimeMetrics(BaseModel):
    low_vix: CorrelationMetrics
    medium_vix: CorrelationMetrics
    high_vix: CorrelationMetrics

class DegradationAnalysis(BaseModel):
    avg_corr_increase: float
    avg_corr_pct_increase: float
    max_corr_increase: float
    eff_assets_decrease: float
    eff_assets_pct_decrease: float

class AnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: datetime
    portfolio_summary: Dict
    regime_metrics: RegimeMetrics
    degradation_analysis: DegradationAnalysis
    risk_flags: List[str]
    recommendations: List[str]
    visualizations: Dict


# ============================================================
# LAYER 2 — unchanged
# ============================================================

class CrashPeriod(BaseModel):
    key: str
    name: str
    start: str
    end: str
    benchmark_ticker: str = Field(default="SPY")
    description: Optional[str] = None

    @validator('start', 'end')
    def valid_date(cls, v):
        datetime.strptime(v, "%Y-%m-%d")
        return v

class CrashSimulationRequest(BaseModel):
    portfolio: List[PortfolioHolding] = Field(..., min_items=2, max_items=50)
    selected_crashes: Optional[List[str]] = None
    custom_crash: Optional[CrashPeriod] = None

    @validator('portfolio')
    def validate_weights(cls, holdings):
        total = sum(h.weight for h in holdings)
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total:.3f}")
        return holdings

class LossDriver(BaseModel):
    ticker: str
    weight: float
    period_return: float
    contribution_to_loss: float
    contribution_pct: float

class DrawdownPoint(BaseModel):
    date: str
    portfolio_dd: float
    benchmark_dd: float

class CrashResult(BaseModel):
    key: str
    name: str
    description: str
    start: str
    end: str
    trading_days: int
    benchmark_ticker: str
    portfolio_total_return: float
    benchmark_total_return: float
    relative_performance: float
    max_drawdown: float
    benchmark_max_drawdown: float
    recovery_days: Optional[int]
    loss_drivers: List[LossDriver]
    risk_flags: List[str]
    drawdown_series: List[DrawdownPoint]

class CrashSimulationResponse(BaseModel):
    simulation_id: str
    timestamp: datetime
    portfolio_summary: Dict
    crash_results: List[CrashResult]
    worst_crash: str
    avg_max_drawdown: float
    avg_relative_performance: float
    overall_risk_flags: List[str]
    recommendations: List[str]
    visualizations: Dict


# ============================================================
# LAYER 3 — unchanged
# ============================================================

class FactorExposureParameters(BaseModel):
    lookback_days: int = Field(default=756, ge=252, le=2520)
    rolling_window: int = Field(default=252, ge=60, le=504)
    vix_low_threshold: float = Field(default=15.0, ge=10, le=20)
    vix_high_threshold: float = Field(default=25.0, ge=20, le=40)
    min_regime_days: int = Field(default=20, ge=5, le=60)
    use_5day_vix: bool = Field(default=True)
    significance_level: float = Field(default=0.05, ge=0.01, le=0.10)

class FactorExposureRequest(BaseModel):
    portfolio: List[PortfolioHolding] = Field(..., min_items=2, max_items=50)
    params: Optional[FactorExposureParameters] = Field(
        default_factory=FactorExposureParameters
    )

    @validator('portfolio')
    def validate_weights(cls, holdings):
        total = sum(h.weight for h in holdings)
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total:.3f}")
        return holdings

class FactorLoading(BaseModel):
    factor: str
    beta: float
    t_stat: float
    p_value: float
    significant: bool
    contribution_to_variance: float

class StaticRegressionResult(BaseModel):
    alpha: float
    alpha_t_stat: float
    alpha_p_value: float
    r_squared: float
    adj_r_squared: float
    unexplained_variance_pct: float
    factor_loadings: List[FactorLoading]
    dominant_factor: str
    observations: int

class RollingLoadingPoint(BaseModel):
    date: str
    beta: float
    r_squared: float

class RollingFactorSeries(BaseModel):
    factor: str
    series: List[RollingLoadingPoint]
    drift_flag: bool
    drift_magnitude: float

class RegimeFactorLoadings(BaseModel):
    regime: str
    observations: int
    factor_loadings: List[FactorLoading]
    r_squared: float
    alpha: float

class FactorExposureResponse(BaseModel):
    exposure_id: str
    timestamp: datetime
    portfolio_summary: Dict
    static_regression: StaticRegressionResult
    rolling_regressions: List[RollingFactorSeries]
    regime_regressions: List[RegimeFactorLoadings]
    risk_flags: List[str]
    recommendations: List[str]
    visualizations: Dict


# ============================================================
# LAYER 4 — Regime-Specific Performance Analysis
# ============================================================

class RegimePerformanceParameters(BaseModel):
    lookback_days: int = Field(default=756, ge=252, le=2520)
    vix_low_threshold: float = Field(default=15.0, ge=10, le=20)
    vix_high_threshold: float = Field(default=25.0, ge=20, le=40)
    min_regime_days: int = Field(default=20, ge=5, le=60)
    use_5day_vix: bool = Field(default=True)
    transition_windows: List[int] = Field(
        default=[5, 20],
        description="Days forward to measure post-transition performance"
    )

class RegimePerformanceRequest(BaseModel):
    portfolio: List[PortfolioHolding] = Field(..., min_items=2, max_items=50)
    params: Optional[RegimePerformanceParameters] = Field(
        default_factory=RegimePerformanceParameters
    )

    @validator('portfolio')
    def validate_weights(cls, holdings):
        total = sum(h.weight for h in holdings)
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total:.3f}")
        return holdings


# ── Per-regime statistics ─────────────────────────────────────

class RegimeStats(BaseModel):
    regime: str                        # low / medium / high
    observations: int
    # Annualised return and risk
    ann_return: float
    ann_volatility: float
    sharpe_ratio: float
    # Drawdown
    max_drawdown: float
    avg_drawdown: float
    # Daily return distribution
    win_rate: float                    # fraction of positive-return days
    best_day: float
    worst_day: float
    # Cumulative return over all regime days (not annualised)
    cumulative_return: float


# ── Regime transition analysis ────────────────────────────────

class TransitionEvent(BaseModel):
    date: str                          # date of transition
    from_regime: str
    to_regime: str
    fwd_5d_return: Optional[float]
    fwd_20d_return: Optional[float]


class TransitionSummary(BaseModel):
    from_regime: str
    to_regime: str
    label: str                         # e.g. "Low → High"
    n_events: int
    avg_fwd_5d: Optional[float]
    avg_fwd_20d: Optional[float]
    pct_negative_5d: Optional[float]   # fraction of transitions with negative 5d return
    pct_negative_20d: Optional[float]


# ── Cumulative return series for chart ────────────────────────

class CumulativePoint(BaseModel):
    date: str
    cumulative_return: float
    regime: str                        # colour-coding by regime


# ── Top-level response ────────────────────────────────────────

class RegimePerformanceResponse(BaseModel):
    performance_id: str
    timestamp: datetime
    portfolio_summary: Dict
    # Core per-regime stats
    regime_stats: List[RegimeStats]
    # Transition analysis
    transition_events: List[TransitionEvent]
    transition_summaries: List[TransitionSummary]
    # Full cumulative return series coloured by regime
    cumulative_series: List[CumulativePoint]
    # Flags + recommendations
    risk_flags: List[str]
    recommendations: List[str]
    visualizations: Dict