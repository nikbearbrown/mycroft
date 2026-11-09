from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class GeneratedCode(Base):
    __tablename__ = "generated_code"

    id = Column(Integer, primary_key=True)
    oracle_id = Column(Integer, ForeignKey("oracles.id"), nullable=False)
    source_code = Column(String, nullable=False)
    generation_rationale = Column(String)
    generated_at = Column(DateTime, server_default=func.now())
    status = Column(String, default="needs_review")
    decided_at = Column(DateTime, nullable=True)

    # --- provenance: enough to reproduce and audit this specific run ---
    model = Column(String, nullable=True)
    temperature = Column(Float, nullable=True)
    prompt_hash = Column(String, nullable=True)
    code_hash = Column(String, nullable=True)
    # --- guardrail verdict on this generated code ---
    code_valid = Column(Boolean, nullable=True)
    code_error = Column(String, nullable=True)
    # --- sealed bundle: hash of code + both checkers' results ---
    binding_proof = Column(String, nullable=True)
