from datetime import datetime
from sqlalchemy import (
    Column, String, Float, DateTime, Integer, JSON, Text, ForeignKey, Enum
)
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class EventType(str, enum.Enum):
    INVESTMENT = "INVESTMENT"
    DIVESTMENT = "DIVESTMENT"
    CASH_ALLOCATION = "CASH_ALLOCATION"
    HOLD_DECISION = "HOLD_DECISION"
    INACTION_MARKER = "INACTION_MARKER"


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    event_type = Column(Enum(EventType), nullable=False)
    asset_class = Column(String, nullable=False)          # equities, bonds, cash, crypto, etc.
    ticker = Column(String, nullable=True)
    amount = Column(Float, nullable=False)                # USD amount
    timestamp = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


class StateSnapshot(Base):
    __tablename__ = "state_snapshots"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    portfolio_state = Column(JSON, nullable=False)        # {asset_class: amount}
    total_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class BehaviorFeature(Base):
    __tablename__ = "behavior_features"

    id = Column(String, primary_key=True)
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    hhi = Column(Float, nullable=True)                   # Herfindahl-Hirschman Index
    entropy = Column(Float, nullable=True)               # Shannon entropy
    turnover_rate = Column(Float, nullable=True)
    idle_capital_ratio = Column(Float, nullable=True)
    dominant_action = Column(String, nullable=True)
    asset_class_weights = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


class StrategyModel(Base):
    __tablename__ = "strategy_models"

    id = Column(String, primary_key=True)
    version = Column(Integer, nullable=False, default=1)
    computed_at = Column(DateTime, nullable=False)
    profile_text = Column(Text, nullable=False)          # LLM-generated narrative
    risk_posture = Column(String, nullable=True)         # conservative/moderate/aggressive
    liquidity_preference = Column(String, nullable=True) # low/medium/high
    concentration_tendency = Column(String, nullable=True)
    baseline_weights = Column(JSON, default={})          # baseline asset class distribution
    metrics_snapshot = Column(JSON, default={})
    is_current = Column(Integer, default=1)              # 1 = current, 0 = historical
    created_at = Column(DateTime, default=datetime.utcnow)
