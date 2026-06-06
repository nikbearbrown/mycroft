import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from typing import Dict, List
import logging

logger = logging.getLogger("portfolio_analysis.visualization")

class Visualizer:
    """Service for generating visualization outputs"""
    
    @staticmethod
    def generate_correlation_heatmaps(
        correlations: Dict[str, pd.DataFrame],
        tickers: List[str]
    ) -> Dict[str, str]:
        """
        Generate correlation heatmaps for each regime
        
        Returns:
            Dict mapping regime name -> base64 encoded PNG image
        """
        logger.info("Generating correlation heatmaps")
        
        heatmaps = {}
        
        fig, axes = plt.subplots(1, 3, figsize=(20, 6))
        fig.suptitle('Portfolio Correlation Structure Across Volatility Regimes', fontsize=16, fontweight='bold')
        
        regimes = ['low', 'medium', 'high']
        titles = ['Low VIX (<15)', 'Medium VIX (15-25)', 'High VIX (>25)']
        
        for idx, (regime, title) in enumerate(zip(regimes, titles)):
            corr_matrix = correlations.get(regime)
            
            if corr_matrix is not None:
                sns.heatmap(
                    corr_matrix,
                    annot=True,
                    fmt='.2f',
                    cmap='RdYlGn_r',
                    center=0.5,
                    vmin=-1,
                    vmax=1,
                    square=True,
                    ax=axes[idx],
                    cbar_kws={'label': 'Correlation'}
                )
                axes[idx].set_title(title, fontsize=12, fontweight='bold')
                axes[idx].set_xlabel('')
                axes[idx].set_ylabel('')
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        heatmaps['combined'] = image_base64
        logger.info("Generated combined correlation heatmap")
        
        return heatmaps
    
    @staticmethod
    def generate_degradation_chart(degradation: Dict) -> str:
        """Generate bar chart showing degradation metrics"""
        logger.info("Generating degradation visualization")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        metrics = [
            'Avg Correlation\nIncrease',
            'Effective Assets\nDecrease'
        ]
        values = [
            degradation['avg_corr_pct_increase'],
            degradation['eff_assets_pct_decrease']
        ]
        
        colors = ['#ff6b6b' if v > 40 else '#ffd93d' if v > 20 else '#6bcf7f' for v in values]
        
        bars = ax.bar(metrics, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        
        ax.set_ylabel('Percentage Change (%)', fontsize=12, fontweight='bold')
        ax.set_title('Diversification Degradation: Low VIX → High VIX', fontsize=14, fontweight='bold')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}%',
                   ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return image_base64