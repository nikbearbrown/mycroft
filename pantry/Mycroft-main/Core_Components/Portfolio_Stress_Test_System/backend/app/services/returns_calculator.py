import pandas as pd
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger("portfolio_analysis.returns_calculator")

class ReturnsCalculator:
    """Service for calculating returns from price data"""
    
    @staticmethod
    def calculate_log_returns(price_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Calculate log returns for all tickers
        
        Args:
            price_data: Dict mapping ticker -> DataFrame with Close prices
            
        Returns:
            DataFrame with Date index and ticker columns containing log returns
        """
        logger.info(f"Calculating log returns for {len(price_data)} tickers")
        
        returns_dict = {}
        
        for ticker, prices_df in price_data.items():
            prices = prices_df['Close']
            
            # Calculate log returns: ln(P_t / P_{t-1})
            log_returns = np.log(prices / prices.shift(1))
            
            returns_dict[ticker] = log_returns
        
        # Combine into single DataFrame
        returns_df = pd.DataFrame(returns_dict)
        
        # Drop first row (NaN values)
        returns_df = returns_df.dropna(how='all')
        
        logger.info(f"Calculated returns for {len(returns_df)} trading days")
        logger.info(f"Return statistics:")
        for ticker in returns_df.columns:
            mean_return = returns_df[ticker].mean() * 252  # Annualized
            volatility = returns_df[ticker].std() * np.sqrt(252)  # Annualized
            logger.info(f"  {ticker}: {mean_return*100:.2f}% return, {volatility*100:.2f}% vol")
        
        return returns_df
