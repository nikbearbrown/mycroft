from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from db.models import EventType


class EventCreate(BaseModel):
    event_type: EventType
    asset_class: str
    ticker: Optional[str] = None
    amount: float
    timestamp: datetime
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class EventOut(EventCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class StateSnapshotOut(BaseModel):
    id: str
    timestamp: datetime
    portfolio_state: Dict[str, float]
    total_value: float

    class Config:
        from_attributes = True


class BehaviorFeatureOut(BaseModel):
    id: str
    window_start: datetime
    window_end: datetime
    hhi: Optional[float]
    entropy: Optional[float]
    turnover_rate: Optional[float]
    idle_capital_ratio: Optional[float]
    dominant_action: Optional[str]
    asset_class_weights: Dict[str, float]

    class Config:
        from_attributes = True


class StrategyOut(BaseModel):
    id: str
    version: int
    computed_at: datetime
    profile_text: str
    risk_posture: Optional[str]
    liquidity_preference: Optional[str]
    concentration_tendency: Optional[str]
    baseline_weights: Dict[str, float]
    metrics_snapshot: Dict[str, Any]

    class Config:
        from_attributes = True


class DriftOut(BaseModel):
    has_baseline: bool
    drift_score: float                        # 0-1, higher = more drift
    current_weights: Dict[str, float]
    baseline_weights: Dict[str, float]
    weight_deltas: Dict[str, float]
    dominant_shift: Optional[str]
    drift_narrative: str


class CapitalFlowOut(BaseModel):
    nodes: List[Dict[str, Any]]               # [{id, name, group}]
    links: List[Dict[str, Any]]               # [{source, target, value}]


class SimulateRequest(BaseModel):
    proposed_events: List[EventCreate]
    horizon_days: int = 30


class SimulateOut(BaseModel):
    projected_weights: Dict[str, float]
    projected_hhi: float
    projected_entropy: float
    projected_risk_posture: str
    narrative: str
