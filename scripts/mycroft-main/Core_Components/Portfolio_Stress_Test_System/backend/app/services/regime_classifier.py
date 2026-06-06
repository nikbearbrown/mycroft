import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger("portfolio_analysis.regime_classifier")

class RegimeClassifier:
    """Service for classifying market regimes based on VIX"""
    
    @staticmethod
    def classify_regimes(
        vix_data: pd.Series,
        low_threshold: float,
        high_threshold: float,
        min_regime_days: int = 20
    ) -> pd.Series:
        """
        Classify trading days into VIX regimes
        
        Args:
            vix_data: Series with VIX levels
            low_threshold: VIX level below which is 'low' regime
            high_threshold: VIX level above which is 'high' regime
            min_regime_days: Minimum consecutive days to qualify as regime
            
        Returns:
            Series with regime labels ('low', 'medium', 'high')
        """
        logger.info(f"Classifying regimes with thresholds: low<{low_threshold}, high>{high_threshold}")
        
        # Initial classification
        regimes = pd.Series(index=vix_data.index, dtype=str)
        regimes[vix_data < low_threshold] = 'low'
        regimes[(vix_data >= low_threshold) & (vix_data < high_threshold)] = 'medium'
        regimes[vix_data >= high_threshold] = 'high'
        
        # Apply minimum regime duration filter
        regimes = RegimeClassifier._filter_short_regimes(regimes, min_regime_days)
        
        # Log regime statistics
        regime_counts = regimes.value_counts()
        total_days = len(regimes)
        
        logger.info(f"Regime distribution:")
        logger.info(f"  Low VIX: {regime_counts.get('low', 0)} days ({regime_counts.get('low', 0)/total_days*100:.1f}%)")
        logger.info(f"  Medium VIX: {regime_counts.get('medium', 0)} days ({regime_counts.get('medium', 0)/total_days*100:.1f}%)")
        logger.info(f"  High VIX: {regime_counts.get('high', 0)} days ({regime_counts.get('high', 0)/total_days*100:.1f}%)")
        
        return regimes
    
    @staticmethod
    def _filter_short_regimes(regimes: pd.Series, min_days: int) -> pd.Series:
        """Remove regime periods shorter than min_days"""
        if min_days <= 1:
            return regimes
        
        filtered = regimes.copy()
        current_regime = filtered.iloc[0]
        regime_start = 0
        
        for i in range(1, len(filtered)):
            if filtered.iloc[i] != current_regime:
                # Regime changed - check if previous regime was too short
                regime_length = i - regime_start
                if regime_length < min_days:
                    # Mark as the surrounding regime (simple forward fill)
                    if i < len(filtered):
                        filtered.iloc[regime_start:i] = filtered.iloc[i]
                
                current_regime = filtered.iloc[i]
                regime_start = i
        
        return filtered
