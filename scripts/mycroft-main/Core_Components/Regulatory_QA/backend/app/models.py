from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ImpactLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class SourceFeed(str, Enum):
    SEC = "SEC Press Releases"
    FEDERAL_REGISTER = "Federal Register - Securities"
    FINRA = "FINRA Enforcement News"
    CFTC = "CFTC Regulations"
    INVESTMENT_ADVISOR = "Investment Advisor Rules"

class Feed(BaseModel):
    id: int
    source_feed: str
    source: str
    title: str
    link: str
    published: datetime
    content: Optional[str] = None
    urgency_score: Optional[int] = None
    impact_level: Optional[str] = None
    keyword_matches: Optional[Dict[str, bool]] = None
    categories: Optional[List[str]] = None
    word_count: Optional[int] = None
    has_deadline: bool = False
    is_enforcement: bool = False
    email_sent: bool = False
    scraped_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    # Remove email_sent_at and updated_at - they don't exist in your DB
    
    class Config:
        from_attributes = True

class FeedListResponse(BaseModel):
    total: int
    feeds: List[Feed]
    filters_applied: Dict[str, Any]

class FeedQuery(BaseModel):
    question: str
    feed_ids: List[int] = Field(min_items=1, max_items=10)
    
class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    context_count: int

class FetchTriggerResponse(BaseModel):
    status: str
    message: str
    workflow_triggered: bool