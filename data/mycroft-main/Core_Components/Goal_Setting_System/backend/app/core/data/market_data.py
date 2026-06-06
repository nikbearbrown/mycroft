"""
Market Data Fetcher using yfinance with robust fallback
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict
import logging

from app.core.config import settings
from app.schemas.simulation import PortfolioAllocation

logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """Fetch and process market data from free sources"""
    
    TICKERS = {
        "stocks": settings.STOCK_TICKER,
        "bonds": settings.BOND_TICKER,
        "cash": settings.CASH_TICKER
    }
    
    # Historical parameters based on long-term market data
    HISTORICAL_PARAMS = {
        "stocks": {"annual_return": 0.10, "annual_vol": 0.16},   # 10% return, 16% vol
        "bonds": {"annual_return": 0.045, "annual_vol": 0.06},   # 4.5% return, 6% vol
        "cash": {"annual_return": 0.03, "annual_vol": 0.01}      # 3% return, 1% vol
    }
    
    @classmethod
    def fetch_historical_returns(
        cls,
        asset_class: str,
        years: int = None
    ) -> pd.Series:
        """Fetch historical returns for an asset class"""
        years = years or settings.MARKET_DATA_YEARS
        ticker = cls.TICKERS.get(asset_class, cls.TICKERS["stocks"])
        
        logger.info(f"Attempting to fetch {asset_class} data for {ticker}")
        
        try:
            # Try multiple methods to fetch data
            data = None
            
            # Method 1: Ticker object with history
            try:
                ticker_obj = yf.Ticker(ticker)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=years*365 + 30)
                
                data = ticker_obj.history(
                    start=start_date,
                    end=end_date,
                    auto_adjust=True,
                    actions=False
                )
            except Exception as e:
                logger.warning(f"Method 1 failed for {ticker}: {str(e)}")
            
            # Method 2: Direct download
            if data is None or data.empty:
                try:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=years*365 + 30)
                    
                    data = yf.download(
                        ticker,
                        start=start_date,
                        end=end_date,
                        progress=False,
                        auto_adjust=True
                    )
                except Exception as e:
                    logger.warning(f"Method 2 failed for {ticker}: {str(e)}")
            
            # Method 3: Use shorter period
            if data is None or data.empty:
                try:
                    ticker_obj = yf.Ticker(ticker)
                    data = ticker_obj.history(period="5y", auto_adjust=True)
                except Exception as e:
                    logger.warning(f"Method 3 failed for {ticker}: {str(e)}")
            
            # Check if we got valid data
            if data is None or data.empty:
                logger.warning(f"All fetch methods failed for {ticker}, using synthetic data")
                return cls._generate_synthetic_returns(asset_class, years)
            
            # Handle MultiIndex columns from yf.download
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Extract close prices
            if 'Close' in data.columns:
                prices = data['Close']
            elif 'Adj Close' in data.columns:
                prices = data['Adj Close']
            else:
                logger.warning(f"No price column found for {ticker}, using synthetic data")
                return cls._generate_synthetic_returns(asset_class, years)
            
            # Ensure it's a Series
            if isinstance(prices, pd.DataFrame):
                prices = prices.squeeze()  # Convert single-column DataFrame to Series
            
            # Remove NaN values
            prices = prices.dropna()
            
            if len(prices) < 30:  # Need at least 30 days
                logger.warning(f"Insufficient price data for {ticker}, using synthetic data")
                return cls._generate_synthetic_returns(asset_class, years)
            
            # Resample to monthly
            try:
                monthly_prices = prices.resample('ME').last()
            except (ValueError, AttributeError):
                try:
                    monthly_prices = prices.resample('M').last()
                except:
                    # Manual monthly sampling
                    monthly_prices = prices.groupby(pd.Grouper(freq='M')).last()
            
            monthly_prices = monthly_prices.dropna()
            
            if len(monthly_prices) < 12:
                logger.warning(f"Insufficient monthly data for {ticker}, using synthetic data")
                return cls._generate_synthetic_returns(asset_class, years)
            
            # Calculate returns
            returns = monthly_prices.pct_change().dropna()
            
            # Ensure returns is a Series
            if isinstance(returns, pd.DataFrame):
                returns = returns.squeeze()
            
            logger.info(f"Successfully fetched {len(returns)} months of real data for {asset_class}")
            return returns
            
        except Exception as e:
            logger.error(f"Unexpected error fetching {ticker}: {str(e)}")
            return cls._generate_synthetic_returns(asset_class, years)
    
    @classmethod
    def _generate_synthetic_returns(cls, asset_class: str, years: int) -> pd.Series:
        """Generate synthetic returns based on historical market statistics"""
        params = cls.HISTORICAL_PARAMS.get(asset_class, cls.HISTORICAL_PARAMS["stocks"])
        
        # Convert annual to monthly
        monthly_mean = (1 + params["annual_return"]) ** (1/12) - 1
        monthly_std = params["annual_vol"] / np.sqrt(12)
        
        num_months = years * 12
        
        # Generate dates
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=num_months, freq='ME')
        
        # Generate returns with some autocorrelation for realism
        np.random.seed(hash(asset_class) % (2**32))  # Consistent seed per asset class
        
        returns = np.zeros(num_months)
        returns[0] = np.random.normal(monthly_mean, monthly_std)
        
        # Add some autocorrelation (momentum)
        for i in range(1, num_months):
            shock = np.random.normal(0, monthly_std)
            returns[i] = 0.1 * returns[i-1] + monthly_mean + shock
        
        logger.info(f"Generated {num_months} months of synthetic data for {asset_class}")
        
        return pd.Series(returns, index=dates)
    
    @classmethod
    def get_portfolio_statistics(
        cls,
        allocation: PortfolioAllocation,
        years: int = None
    ) -> Dict[str, float]:
        """Calculate historical portfolio statistics"""
        years = years or settings.MARKET_DATA_YEARS
        
        logger.info(f"Calculating portfolio statistics for allocation: {allocation.dict()}")
        
        try:
            # Fetch returns for each asset class
            stocks_returns = cls.fetch_historical_returns("stocks", years)
            bonds_returns = cls.fetch_historical_returns("bonds", years)
            cash_returns = cls.fetch_historical_returns("cash", years)
            
            # Ensure all are Series
            if not isinstance(stocks_returns, pd.Series):
                stocks_returns = pd.Series(stocks_returns)
            if not isinstance(bonds_returns, pd.Series):
                bonds_returns = pd.Series(bonds_returns)
            if not isinstance(cash_returns, pd.Series):
                cash_returns = pd.Series(cash_returns)
            
            logger.info(f"Data shapes - Stocks: {stocks_returns.shape}, Bonds: {bonds_returns.shape}, Cash: {cash_returns.shape}")
            
            # Align all series to common dates
            all_returns = pd.DataFrame({
                'stocks': stocks_returns,
                'bonds': bonds_returns,
                'cash': cash_returns
            })
            
            # Drop any NaN rows
            all_returns = all_returns.dropna()
            
            if len(all_returns) < 12:
                logger.warning("Insufficient aligned data, using theoretical statistics")
                return cls._calculate_theoretical_statistics(allocation)
            
            logger.info(f"Using {len(all_returns)} months of aligned data")
            
            # Calculate weighted portfolio returns
            portfolio_returns = (
                all_returns['stocks'].astype(float) * (allocation.stocks / 100) +
                all_returns['bonds'].astype(float) * (allocation.bonds / 100) +
                all_returns['cash'].astype(float) * (allocation.cash / 100)
            )
            
            # Calculate statistics
            mean_return = float(portfolio_returns.mean())
            std_return = float(portfolio_returns.std())
            
            annual_return = (1 + mean_return) ** 12 - 1
            annual_vol = std_return * np.sqrt(12)
            sharpe = (annual_return - 0.03) / annual_vol if annual_vol > 0 else 0
            
            max_dd = cls._calculate_max_drawdown(portfolio_returns)
            
            stats = {
                "annual_return": round(float(annual_return), 4),
                "annual_volatility": round(float(annual_vol), 4),
                "sharpe_ratio": round(float(sharpe), 4),
                "monthly_mean": round(float(mean_return), 6),
                "monthly_std": round(float(std_return), 6),
                "max_drawdown": round(float(max_dd), 4)
            }
            
            logger.info(f"Portfolio statistics calculated successfully: Annual Return={stats['annual_return']}, Vol={stats['annual_volatility']}")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}", exc_info=True)
            logger.info("Using theoretical statistics as fallback")
            return cls._calculate_theoretical_statistics(allocation)
    
    @classmethod
    def _calculate_theoretical_statistics(cls, allocation: PortfolioAllocation) -> Dict[str, float]:
        """Calculate theoretical statistics based on historical averages"""
        # Weighted average of returns
        annual_return = (
            cls.HISTORICAL_PARAMS["stocks"]["annual_return"] * (allocation.stocks / 100) +
            cls.HISTORICAL_PARAMS["bonds"]["annual_return"] * (allocation.bonds / 100) +
            cls.HISTORICAL_PARAMS["cash"]["annual_return"] * (allocation.cash / 100)
        )
        
        # Weighted volatility (simplified, assumes no correlation)
        annual_vol = np.sqrt(
            (cls.HISTORICAL_PARAMS["stocks"]["annual_vol"] ** 2) * ((allocation.stocks / 100) ** 2) +
            (cls.HISTORICAL_PARAMS["bonds"]["annual_vol"] ** 2) * ((allocation.bonds / 100) ** 2) +
            (cls.HISTORICAL_PARAMS["cash"]["annual_vol"] ** 2) * ((allocation.cash / 100) ** 2)
        )
        
        monthly_mean = (1 + annual_return) ** (1/12) - 1
        monthly_std = annual_vol / np.sqrt(12)
        sharpe = (annual_return - 0.03) / annual_vol if annual_vol > 0 else 0
        
        logger.info(f"Theoretical stats: Annual Return={round(annual_return, 4)}, Vol={round(annual_vol, 4)}")
        
        return {
            "annual_return": round(annual_return, 4),
            "annual_volatility": round(annual_vol, 4),
            "sharpe_ratio": round(sharpe, 4),
            "monthly_mean": round(monthly_mean, 6),
            "monthly_std": round(monthly_std, 6),
            "max_drawdown": -0.20  # Conservative estimate
        }
    
    @staticmethod
    def _calculate_max_drawdown(returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return float(drawdown.min())
        except Exception as e:
            logger.warning(f"Error calculating max drawdown: {str(e)}")
            return -0.20

# Global instance
market_data_fetcher = MarketDataFetcher()