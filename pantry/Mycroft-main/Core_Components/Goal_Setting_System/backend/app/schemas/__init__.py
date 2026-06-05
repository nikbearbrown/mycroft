"""
Pydantic schemas package
"""
from app.schemas.goal import (
    GoalExtractionRequest,
    GoalExtractionResponse,
    InvestmentGoal,
    EnrichedGoal,
    ExtractedEntity
)
from app.schemas.simulation import (
    SimulationRequest,
    SimulationResponse,
    SimulationResult,
    SimulationGoalInput,
    SimulationConfig,
    PortfolioAllocation
)

__all__ = [
    "GoalExtractionRequest",
    "GoalExtractionResponse",
    "InvestmentGoal",
    "EnrichedGoal",
    "ExtractedEntity",
    "SimulationRequest",
    "SimulationResponse",
    "SimulationResult",
    "SimulationGoalInput",
    "SimulationConfig",
    "PortfolioAllocation"
]