from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True)
    oracle_id = Column(Integer, ForeignKey("oracles.id"), nullable=False)
    applicant_id = Column(String, nullable=False)
    applicant_data = Column(JSONB, nullable=False)
    expected_outcome = Column(String, nullable=False)
    author_rationale = Column(String, nullable=False)
