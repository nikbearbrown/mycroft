"""
Goal-related Pydantic schemas
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime

class ExtractedEntity(BaseModel):
    """Entities extracted from text"""
    amounts: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

class GoalExtractionRequest(BaseModel):
    """Request to extract goals from natural language"""
    text: str = Field(
        ..., 
        description="Natural language investment goal description",
        min_length=10
    )
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    model: Optional[str] = Field(None, description="Ollama model to use")
    temperature: Optional[float] = Field(0.1, ge=0.0, le=1.0)
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        if len(v.strip()) < 10:
            raise ValueError('Text too short for meaningful extraction')
        return v.strip()

class InvestmentGoal(BaseModel):
    """Structured investment goal"""
    goal_type: Literal[
        "retirement", "house_purchase", "education", "wealth_building",
        "emergency_fund", "debt_payoff", "vacation", "business", "other"
    ]
    description: str
    target_amount: Optional[float] = None
    timeline_years: Optional[float] = None
    timeline_months: Optional[int] = None
    risk_tolerance: Literal["conservative", "moderate", "aggressive", "unknown"]
    priority: Literal["high", "medium", "low"]
    current_savings: Optional[float] = None
    monthly_contribution: Optional[float] = None
    annual_return_assumption: Optional[float] = None
    constraints: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    extracted_entities: ExtractedEntity

class GoalExtractionResponse(BaseModel):
    """Response from goal extraction"""
    success: bool
    goals: List[InvestmentGoal]
    summary: str
    processed_at: str
    model_used: str
    processing_time_ms: float

class EnrichedGoal(InvestmentGoal):
    """Goal with additional calculated fields"""
    required_monthly_contribution: Optional[float] = None
    total_investment_needed: Optional[float] = None
    gap_to_goal: Optional[float] = None
    projected_final_value: Optional[float] = None
    feasibility_score: Optional[float] = None