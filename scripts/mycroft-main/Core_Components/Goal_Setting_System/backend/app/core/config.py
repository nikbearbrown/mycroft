"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Project Info
    PROJECT_NAME: str = "Mycroft Goal Simulator"
    DESCRIPTION: str = "Investment goal extraction and Monte Carlo simulation engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "llama3:latest"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT: int = 120
    
    # Simulation Configuration
    DEFAULT_NUM_SIMULATIONS: int = 1000
    MIN_SIMULATIONS: int = 100
    MAX_SIMULATIONS: int = 10000
    DEFAULT_CONFIDENCE_LEVEL: float = 0.95
    DEFAULT_INFLATION_RATE: float = 0.03
    
    # Market Data Configuration
    MARKET_DATA_YEARS: int = 20
    CACHE_TTL_SECONDS: int = 3600
    USE_FALLBACK_DATA: bool = True
    
    # Tickers for market data
    STOCK_TICKER: str = "SPY"
    BOND_TICKER: str = "AGG"
    CASH_TICKER: str = "^IRX"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()