from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class Oracle(Base):
    __tablename__ = "oracles"

    id = Column(Integer, primary_key=True)
    rule_id = Column(String, unique=True, nullable=False)
    rule_text = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # --- freeze gate: the answer key is locked before code-gen may run ---
    frozen = Column(Boolean, nullable=False, server_default="false", default=False)
    frozen_at = Column(DateTime, nullable=True)
    oracle_hash = Column(String, nullable=True)  # tamper-evident hash of frozen content
