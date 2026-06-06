from typing import Dict, List, Tuple
import logging

logger = logging.getLogger("portfolio_analysis.risk_analyzer")

class RiskAnalyzer:
    """Service for analyzing portfolio risk and generating flags"""
    
    @staticmethod
    def analyze_degradation(
        low_vix_metrics: Dict,
        high_vix_metrics: Dict
    ) -> Dict[str, float]:
        """
        Calculate diversification degradation metrics
        
        Returns:
            Dict with degradation statistics
        """
        logger.info("Analyzing diversification degradation")
        
        avg_corr_increase = high_vix_metrics['avg_pairwise_correlation'] - low_vix_metrics['avg_pairwise_correlation']
        avg_corr_pct_increase = (avg_corr_increase / low_vix_metrics['avg_pairwise_correlation']) * 100
        
        max_corr_increase = high_vix_metrics['max_correlation'] - low_vix_metrics['max_correlation']
        
        eff_assets_decrease = low_vix_metrics['effective_n_assets'] - high_vix_metrics['effective_n_assets']
        eff_assets_pct_decrease = (eff_assets_decrease / low_vix_metrics['effective_n_assets']) * 100
        
        degradation = {
            'avg_corr_increase': avg_corr_increase,
            'avg_corr_pct_increase': avg_corr_pct_increase,
            'max_corr_increase': max_corr_increase,
            'eff_assets_decrease': eff_assets_decrease,
            'eff_assets_pct_decrease': eff_assets_pct_decrease
        }
        
        logger.info(f"Degradation analysis:")
        logger.info(f"  Avg correlation increase: {avg_corr_pct_increase:.1f}%")
        logger.info(f"  Effective assets decrease: {eff_assets_pct_decrease:.1f}%")
        
        return degradation
    
    @staticmethod
    def generate_risk_flags(
        degradation: Dict,
        high_vix_metrics: Dict,
        portfolio_size: int
    ) -> List[str]:
        """
        Generate risk flags based on degradation metrics
        
        Returns:
            List of risk flag strings
        """
        flags = []
        
        if degradation['avg_corr_pct_increase'] > 50:
            flags.append('SEVERE_CORRELATION_SPIKE')
            logger.warning("Risk flag: SEVERE_CORRELATION_SPIKE")
        
        if degradation['eff_assets_pct_decrease'] > 40:
            flags.append('MAJOR_DIVERSIFICATION_LOSS')
            logger.warning("Risk flag: MAJOR_DIVERSIFICATION_LOSS")
        
        if high_vix_metrics['max_correlation'] > 0.85:
            flags.append('EXTREME_STRESS_CORRELATION')
            logger.warning("Risk flag: EXTREME_STRESS_CORRELATION")
        
        if high_vix_metrics['effective_n_assets'] < 3 and portfolio_size > 5:
            flags.append('ILLUSION_OF_DIVERSIFICATION')
            logger.warning("Risk flag: ILLUSION_OF_DIVERSIFICATION")
        
        if high_vix_metrics['avg_pairwise_correlation'] > 0.70:
            flags.append('HIGH_STRESS_CORRELATION')
            logger.warning("Risk flag: HIGH_STRESS_CORRELATION")
        
        if len(flags) == 0:
            logger.info("No risk flags triggered - portfolio shows resilient diversification")
        
        return flags
    
    @staticmethod
    def generate_recommendations(risk_flags: List[str], degradation: Dict) -> List[str]:
        """Generate actionable recommendations based on risk flags"""
        recommendations = []
        
        if 'SEVERE_CORRELATION_SPIKE' in risk_flags:
            recommendations.append(
                f"Portfolio correlation increases by {degradation['avg_corr_pct_increase']:.1f}% during stress. "
                "Consider adding assets with negative or low correlation to market factors (e.g., bonds, commodities, defensive sectors)."
            )
        
        if 'MAJOR_DIVERSIFICATION_LOSS' in risk_flags:
            recommendations.append(
                f"Effective diversification drops by {degradation['eff_assets_pct_decrease']:.1f}% under stress. "
                "Review sector and factor exposures - holdings may be more concentrated than they appear."
            )
        
        if 'EXTREME_STRESS_CORRELATION' in risk_flags:
            recommendations.append(
                "Some holdings become highly correlated (>0.85) during high volatility. "
                "Consider tail-risk hedging strategies or defensive positions."
            )
        
        if 'ILLUSION_OF_DIVERSIFICATION' in risk_flags:
            recommendations.append(
                "Despite multiple holdings, portfolio behaves like 2-3 assets under stress. "
                "True diversification requires uncorrelated return drivers, not just different tickers."
            )
        
        if 'HIGH_STRESS_CORRELATION' in risk_flags:
            recommendations.append(
                "Average correlation exceeds 0.70 during stress periods. "
                "Portfolio may experience severe drawdowns during market dislocations."
            )
        
        if len(recommendations) == 0:
            recommendations.append(
                "Portfolio maintains reasonable diversification across volatility regimes. "
                "Continue monitoring correlation structure and consider periodic rebalancing."
            )
        
        return recommendations

