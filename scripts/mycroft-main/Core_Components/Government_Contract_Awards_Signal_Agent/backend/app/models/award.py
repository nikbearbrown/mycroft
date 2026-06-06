from pydantic import BaseModel
from typing import Optional


class Award(BaseModel):
    award_id: str
    recipient_name: str
    awarding_agency: str
    award_amount: Optional[float] = None
    award_date: Optional[str] = None
    description: Optional[str] = None
    naics_code: Optional[str] = None
    place_of_performance: Optional[str] = None

    # Enriched fields set by classifier and scorer
    agency_type: Optional[str] = None
    signal_score: Optional[float] = None

    # AI-generated analyst brief (only populated for HIGH-signal awards)
    ai_brief: Optional[str] = None
