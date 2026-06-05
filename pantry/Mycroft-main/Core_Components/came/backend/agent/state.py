from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime


class AgentState(TypedDict):
    # Input
    events: List[Dict[str, Any]]
    snapshots: List[Dict[str, Any]]

    # Intermediate
    normalized_events: List[Dict[str, Any]]
    current_portfolio: Dict[str, float]
    total_value: float
    patterns: Dict[str, Any]

    # Behavior features
    hhi: float
    entropy: float
    turnover_rate: float
    idle_capital_ratio: float
    dominant_action: str
    asset_class_weights: Dict[str, float]

    # Drift
    baseline_weights: Dict[str, float]
    drift_score: float
    weight_deltas: Dict[str, float]

    # Output
    risk_posture: str
    liquidity_preference: str
    concentration_tendency: str
    profile_text: str
    error: Optional[str]
