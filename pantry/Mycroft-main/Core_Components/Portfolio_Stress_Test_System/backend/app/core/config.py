from pydantic_settings import BaseSettings
from typing import Optional, Dict, List
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "Portfolio Stress Testing - Layers 1–4"
    VERSION: str = "4.0.0"

    # ── Layer 1 ──────────────────────────────────────────────
    DEFAULT_LOOKBACK_DAYS: int = 756
    DEFAULT_ROLLING_WINDOW: int = 252
    VIX_LOW_THRESHOLD: float = 15.0
    VIX_HIGH_THRESHOLD: float = 25.0
    MIN_REGIME_DAYS: int = 20

    # ── Shared ───────────────────────────────────────────────
    YFINANCE_MAX_RETRIES: int = 3
    YFINANCE_TIMEOUT: int = 30
    DATABASE_URL: Optional[str] = None

    # ── Layer 2 ──────────────────────────────────────────────
    PREDEFINED_CRASHES: Dict[str, Dict] = {
        "covid_2020": {
            "key": "covid_2020",
            "name": "COVID Crash",
            "start": "2020-02-19",
            "end": "2020-03-23",
            "benchmark_ticker": "SPY",
            "description": "Fastest bear market in history — S&P fell ~34% in 33 days"
        },
        "tech_selloff_2022": {
            "key": "tech_selloff_2022",
            "name": "Tech Selloff 2022",
            "start": "2022-01-03",
            "end": "2022-10-12",
            "benchmark_ticker": "QQQ",
            "description": "Rate-hike driven bear market — NASDAQ dropped ~33% over 9 months"
        },
        "q4_selloff_2018": {
            "key": "q4_selloff_2018",
            "name": "Q4 Selloff 2018",
            "start": "2018-09-20",
            "end": "2018-12-24",
            "benchmark_ticker": "SPY",
            "description": "Fed tightening + trade war fears — S&P fell ~19% in 3 months"
        },
        "flash_crash_2015": {
            "key": "flash_crash_2015",
            "name": "Flash Crash 2015",
            "start": "2015-08-01",
            "end": "2015-08-24",
            "benchmark_ticker": "SPY",
            "description": "China slowdown fears triggered rapid global selloff — S&P fell ~12%"
        }
    }

    SEVERE_DRAWDOWN_THRESHOLD: float = -0.20
    UNDERPERFORM_THRESHOLD: float = -0.05
    SLOW_RECOVERY_DAYS: int = 120
    CONCENTRATION_DRIVER_PCT: float = 0.15

    # ── Layer 3 ──────────────────────────────────────────────
    FF5_URL: str = (
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
    )
    MOMENTUM_URL: str = (
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "F-F_Momentum_Factor_daily_CSV.zip"
    )
    FACTOR_CACHE_DIR: Path = Path(__file__).parent.parent / "data" / "factor_cache"
    FF5_CACHE_FILE: str = "ff5_daily.parquet"
    MOM_CACHE_FILE: str = "momentum_daily.parquet"
    FACTOR_CACHE_MAX_AGE_DAYS: int = 7

    HIGH_BETA_THRESHOLD: float = 1.3
    SIGNIFICANT_TILT_THRESHOLD: float = 0.3
    LOW_R2_THRESHOLD: float = 0.60
    HIGH_ALPHA_THRESHOLD: float = 0.05
    DRIFT_THRESHOLD: float = 0.4
    CONCENTRATED_FACTOR_PCT: float = 0.50

    # ── Layer 4 ──────────────────────────────────────────────
    # Sharpe ratio thresholds
    LOW_SHARPE_THRESHOLD: float = 0.5       # flag if Sharpe < 0.5 in any regime
    NEGATIVE_SHARPE_THRESHOLD: float = 0.0  # flag if Sharpe < 0 in any regime

    # Return dispersion — flag if high-VIX return is this much worse than low-VIX
    REGIME_RETURN_GAP_THRESHOLD: float = 0.10   # 10 percentage points annualised

    # Volatility spike — flag if high-VIX vol is this multiple of low-VIX vol
    VOL_SPIKE_THRESHOLD: float = 1.5

    # Win rate — flag if win rate drops below this in high-VIX
    LOW_WIN_RATE_THRESHOLD: float = 0.45

    # Transition — flag if avg forward return after Low→High is below this
    TRANSITION_NEGATIVE_THRESHOLD: float = -0.02   # -2% over 5 or 20 days

    class Config:
        env_file = ".env"

settings = Settings()