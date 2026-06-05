"""
Portfolio simulation endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import numpy as np
import logging

from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.core.simulation import MonteCarloSimulator

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/simulate", response_model=SimulationResponse)
async def simulate_portfolio(request: SimulationRequest):
    """
    Run Monte Carlo simulation for investment goals
    
    **Example:**
    ```json
    {
      "goals": [{
        "goal_id": "retirement_1",
        "goal_name": "Retirement",
        "target_amount": 2000000,
        "timeline_years": 20,
        "current_savings": 100000,
        "monthly_contribution": 3000,
        "allocation": {"stocks": 70, "bonds": 25, "cash": 5}
      }],
      "config": {
        "num_simulations": 1000
      }
    }
    ```
    """
    start_time = datetime.utcnow()
    
    try:
        # Validate allocations
        for goal in request.goals:
            goal.allocation.validate_total()
        
        # Initialize simulator
        simulator = MonteCarloSimulator(request.config)
        
        # Run simulations for each goal
        logger.info(f"Running {request.config.num_simulations} simulations for {len(request.goals)} goals")
        results = []
        for goal in request.goals:
            result = simulator.simulate_goal(goal)
            results.append(result)
        
        # Calculate aggregate statistics
        total_success_prob = np.prod([r.success_probability for r in results])
        
        total_target = sum(g.target_amount for g in request.goals)
        total_monthly = sum(g.monthly_contribution for g in request.goals)
        
        portfolio_stats = {
            "total_goals": len(request.goals),
            "total_target_amount": round(total_target, 2),
            "total_monthly_contribution": round(total_monthly, 2),
            "average_success_probability": round(
                np.mean([r.success_probability for r in results]), 4
            ),
            "weakest_goal": min(results, key=lambda x: x.success_probability).goal_name,
            "strongest_goal": max(results, key=lambda x: x.success_probability).goal_name
        }
        
        # Generate recommendations
        recommendations = _generate_recommendations(results, total_success_prob)
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        logger.info(f"Simulation complete. Overall success: {total_success_prob:.1%}")
        
        return SimulationResponse(
            success=True,
            total_success_probability=round(total_success_prob, 4),
            goals=results,
            portfolio_statistics=portfolio_stats,
            recommendations=recommendations,
            simulation_timestamp=end_time.isoformat(),
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Simulation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )

def _generate_recommendations(results, total_success_prob):
    """Generate global recommendations"""
    recommendations = []
    
    if total_success_prob < 0.3:
        recommendations.append(
            "🚨 CRITICAL: Very low probability of achieving all goals. Major adjustments needed."
        )
    elif total_success_prob < 0.6:
        recommendations.append(
            "⚠️ WARNING: Moderate probability of achieving all goals. Consider prioritizing or increasing contributions."
        )
    else:
        recommendations.append(
            f"✅ GOOD: {total_success_prob:.1%} probability of achieving all goals."
        )
    
    weak_goals = [r for r in results if r.success_probability < 0.7]
    if weak_goals:
        goal_names = ", ".join([g.goal_name for g in weak_goals])
        recommendations.append(f"🎯 Focus on improving: {goal_names}")
    
    return recommendations