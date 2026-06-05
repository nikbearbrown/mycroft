"""
Simulation-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class PortfolioAllocation(BaseModel):
    """Asset allocation for portfolio"""
    stocks: float = Field(ge=0, le=100, description="% in stocks/equities")
    bonds: float = Field(ge=0, le=100, description="% in bonds")
    cash: float = Field(ge=0, le=100, description="% in cash/money market")
    
    def validate_total(self):
        """Validate allocation sums to 100%"""
        total = self.stocks + self.bonds + self.cash
        if not (99 <= total <= 101):  # Allow 1% rounding error
            raise ValueError(f"Allocation must sum to 100%, got {total}%")
        return self

class SimulationGoalInput(BaseModel):
    """Goal input for simulation"""
    goal_id: str
    goal_name: str
    target_amount: float = Field(gt=0)
    timeline_years: float = Field(gt=0)
    current_savings: float = Field(ge=0, default=0)
    monthly_contribution: float = Field(ge=0)
    allocation: PortfolioAllocation

class SimulationConfig(BaseModel):
    """Configuration for Monte Carlo simulation"""
    num_simulations: int = Field(1000, ge=100, le=10000)
    confidence_level: float = Field(0.95, ge=0.8, le=0.99)
    inflation_rate: float = Field(0.03, ge=0, le=0.10)
    rebalancing_frequency: Literal["monthly", "quarterly", "annually"] = "annually"
    use_historical_data: bool = True
    historical_years: int = Field(20, ge=5, le=30)

class SimulationRequest(BaseModel):
    """Request to run portfolio simulation"""
    goals: List[SimulationGoalInput]
    config: SimulationConfig = SimulationConfig()

class SimulationResult(BaseModel):
    """Results from Monte Carlo simulation for single goal"""
    goal_id: str
    goal_name: str
    success_probability: float = Field(ge=0.0, le=1.0)
    median_outcome: float
    worst_case_10th: float
    best_case_90th: float
    expected_shortfall: float
    recommended_adjustments: List[str]
    percentile_outcomes: Dict[str, float]

class SimulationResponse(BaseModel):
    """Complete simulation response"""
    success: bool
    total_success_probability: float
    goals: List[SimulationResult]
    portfolio_statistics: Dict[str, Any]
    recommendations: List[str]
    simulation_timestamp: str
    processing_time_ms: float