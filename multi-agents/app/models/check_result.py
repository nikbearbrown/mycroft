from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from app.db.database import Base

class CheckResult(Base):
    __tablename__ = "check_results"

    id = Column(Integer, primary_key=True)
    generated_code_id = Column(Integer, ForeignKey("generated_code.id"), nullable=False)
    check_type = Column(String, nullable=False)
    applicant_id = Column(String, nullable=False)
    oracle_expected = Column(String, nullable=False)
    agent_observed = Column(String, nullable=False)
    match = Column(Boolean, nullable=False)
    rationale = Column(String, nullable=False)