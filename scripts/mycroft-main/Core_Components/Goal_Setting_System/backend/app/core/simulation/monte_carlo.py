"""
Monte Carlo Simulation Engine
"""
import numpy as np
import logging
from typing import Dict, List

from app.schemas.simulation import (
    SimulationGoalInput,
    SimulationConfig,
    SimulationResult
)
from app.core.data.market_data import market_data_fetcher

logger = logging.getLogger(__name__)

class MonteCarloSimulator:
    """Run Monte Carlo simulations for investment goals"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
    
    def simulate_goal(self, goal: SimulationGoalInput) -> SimulationResult:
        """Run Monte Carlo simulation for a single goal"""
        logger.info(f"Simulating goal: {goal.goal_name}")
        
        # Validate allocation
        goal.allocation.validate_total()
        
        # Get portfolio statistics
        portfolio_stats = market_data_fetcher.get_portfolio_statistics(
            goal.allocation,
            self.config.historical_years
        )
        
        # Run simulations
        final_values = []
        
        for _ in range(self.config.num_simulations):
            final_value = self._run_single_simulation(goal, portfolio_stats)
            final_values.append(final_value)
        
        final_values = np.array(final_values)
        
        # Calculate outcomes
        success_count = np.sum(final_values >= goal.target_amount)
        success_prob = success_count / self.config.num_simulations
        
        median = np.median(final_values)
        percentile_10 = np.percentile(final_values, 10)
        percentile_90 = np.percentile(final_values, 90)
        
        # Calculate expected shortfall
        shortfalls = goal.target_amount - final_values[final_values < goal.target_amount]
        expected_shortfall = np.mean(shortfalls) if len(shortfalls) > 0 else 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            goal,
            success_prob,
            expected_shortfall,
            portfolio_stats
        )
        
        # Calculate percentile outcomes
        percentiles = {}
        for p in [5, 10, 25, 50, 75, 90, 95]:
            percentiles[f"p{p}"] = round(np.percentile(final_values, p), 2)
        
        return SimulationResult(
            goal_id=goal.goal_id,
            goal_name=goal.goal_name,
            success_probability=round(success_prob, 4),
            median_outcome=round(median, 2),
            worst_case_10th=round(percentile_10, 2),
            best_case_90th=round(percentile_90, 2),
            expected_shortfall=round(expected_shortfall, 2),
            recommended_adjustments=recommendations,
            percentile_outcomes=percentiles
        )
    
    def _run_single_simulation(
        self,
        goal: SimulationGoalInput,
        portfolio_stats: Dict[str, float]
    ) -> float:
        """Run a single simulation path"""
        monthly_return = portfolio_stats["monthly_mean"]
        monthly_vol = portfolio_stats["monthly_std"]
        months = int(goal.timeline_years * 12)
        inflation_adjusted_monthly = (1 + self.config.inflation_rate) ** (1/12) - 1
        
        # Initialize
        value = goal.current_savings
        
        # Simulate each month
        for month in range(months):
            # Generate random return
            random_return = np.random.normal(monthly_return, monthly_vol)
            
            # Apply return to current value
            value = value * (1 + random_return)
            
            # Add contribution (inflation-adjusted)
            inflation_factor = (1 + inflation_adjusted_monthly) ** month
            adjusted_contribution = goal.monthly_contribution * inflation_factor
            value += adjusted_contribution
        
        return value
    
    def _generate_recommendations(
        self,
        goal: SimulationGoalInput,
        success_prob: float,
        expected_shortfall: float,
        portfolio_stats: Dict[str, float]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Success probability recommendations
        if success_prob < 0.5:
            monthly_increase = expected_shortfall / (goal.timeline_years * 12)
            recommendations.append(
                f"⚠️ Low success probability ({success_prob:.1%}). "
                f"Consider increasing monthly contribution by ${monthly_increase:.2f}"
            )
        elif success_prob < 0.75:
            recommendations.append(
                f"⚠️ Moderate success probability ({success_prob:.1%}). "
                "Consider slight adjustments to timeline or contributions."
            )
        else:
            recommendations.append(
                f"✅ High success probability ({success_prob:.1%}). Goal is on track!"
            )
        
        # Allocation recommendations
        allocation = goal.allocation
        if goal.timeline_years > 10 and allocation.stocks < 60:
            recommendations.append(
                "💡 Long timeline allows for more aggressive allocation. "
                "Consider increasing stock allocation for higher returns."
            )
        elif goal.timeline_years < 5 and allocation.stocks > 60:
            recommendations.append(
                "⚠️ Short timeline with aggressive allocation increases risk. "
                "Consider more conservative allocation."
            )
        
        # Risk-adjusted return recommendations
        sharpe = portfolio_stats["sharpe_ratio"]
        if sharpe < 0.5:
            recommendations.append(
                "📊 Low risk-adjusted returns. Consider optimizing allocation."
            )
        
        return recommendations