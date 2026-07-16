from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Oracle(Base):
    __tablename__ = "oracles"

    id = Column(Integer, primary_key=True)
    rule_id = Column(String, unique=True, nullable=False)
    rule_text = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
