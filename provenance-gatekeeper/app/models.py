from pydantic import BaseModel
from typing import Optional

class ClaimPayload(BaseModel):
    claim_text: str
    company_id: str
    agent_source: str
    recipe_id: str

class VerificationResponse(BaseModel):
    original_claim: str
    verification_status: str  # 'Supported', 'Contradicted', or 'Quarantined'
    source_citation_url: Optional[str] = None
    confidence_score: Optional[float] = None