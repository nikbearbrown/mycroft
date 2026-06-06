from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional
from app.services.parser import parse_awards
from app.services.classifier import classify_award
from app.services.scorer import score_award
from app.services.summarizer import summarize_awards
from app.services.fetcher import fetch_recent_awards
from app.services.llm_briefer import enrich_with_briefs
from app.models.award import Award

router = APIRouter()

_MOCK_AWARDS = [
    Award(award_id="MOCK-001", recipient_name="Palantir Technologies Inc",
          awarding_agency="DEPT OF DEFENSE.DEFENSE INTELLIGENCE AGENCY",
          award_amount=52_000_000, award_date="2026-04-01",
          description="Artificial intelligence and machine learning data analytics platform for intelligence analysis and threat detection.",
          naics_code="541512", place_of_performance="McLean, VA"),
    Award(award_id="MOCK-002", recipient_name="Anduril Industries Inc",
          awarding_agency="DEPT OF DEFENSE.DEPT OF THE AIR FORCE",
          award_amount=150_000_000, award_date="2026-04-02",
          description="Autonomous systems integration and AI-powered surveillance for border and perimeter security operations.",
          naics_code="541511", place_of_performance="Costa Mesa, CA"),
    Award(award_id="MOCK-003", recipient_name="Booz Allen Hamilton Inc",
          awarding_agency="DEPT OF DEFENSE.DEPT OF THE NAVY.NAVSEA",
          award_amount=38_000_000, award_date="2026-03-28",
          description="Cybersecurity and software engineering services supporting naval command and control systems.",
          naics_code="541519", place_of_performance="Washington, DC"),
    Award(award_id="MOCK-004", recipient_name="L3 Technologies Inc",
          awarding_agency="DEPT OF DEFENSE.DEPT OF THE NAVY",
          award_amount=147_498_082, award_date="2026-03-15",
          description="Systems integration services for shipboard communication and electronic warfare systems.",
          naics_code="334511", place_of_performance="Camden, NJ"),
    Award(award_id="MOCK-005", recipient_name="Scale AI Inc",
          awarding_agency="DEPT OF DEFENSE.US ARMY",
          award_amount=22_500_000, award_date="2026-04-03",
          description="Data labeling and AI training data pipeline for computer vision and autonomous vehicle recognition programs.",
          naics_code="541511", place_of_performance="San Francisco, CA"),
    Award(award_id="MOCK-006", recipient_name="GOV San Antonio LLC",
          awarding_agency="GENERAL SERVICES ADMINISTRATION.GSA PUBLIC BUILDINGS SERVICE",
          award_amount=20_075_389, award_date="2026-03-20",
          description="Facilities management and building operations services for federal office complex.",
          naics_code="531110", place_of_performance="San Antonio, TX"),
]


@router.get("/mock", response_model=List[Award])
async def fetch_mock_awards():
    """Return mock award data with Claude briefs — use when SAM.gov quota is exceeded."""
    awards = list(_MOCK_AWARDS)
    for award in awards:
        award.agency_type = classify_award(award)
        award.signal_score = score_award(award)
    awards = await enrich_with_briefs(awards)
    return awards


@router.post("/upload", response_model=List[Award])
async def upload_awards(file: UploadFile = File(...)):
    """Parse and process a SAM.gov contract awards CSV or JSON file."""
    content = await file.read()
    try:
        awards = parse_awards(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")

    results = []
    for award in awards:
        award.agency_type = classify_award(award)
        award.signal_score = score_award(award)
        results.append(award)

    return results


@router.get("/summary")
async def get_summary(awards: List[Award]):
    """Generate a signal summary report from a list of processed awards."""
    return summarize_awards(awards)


@router.get("/flagged", response_model=List[Award])
async def get_flagged(awards: List[Award], min_score: float = 0.7):
    """Return awards whose signal score meets the minimum threshold."""
    return [a for a in awards if (a.signal_score or 0) >= min_score]


@router.get("/fetch", response_model=List[Award])
async def fetch_live_awards(
    limit: int = Query(100, ge=1, le=1000),
    keyword: Optional[str] = Query(None),
):
    """Fetch recent award notices live from SAM.gov, enrich, and return signals."""
    try:
        awards = await fetch_recent_awards(limit=limit, keyword=keyword or "")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SAM.gov fetch failed: {e}")

    for award in awards:
        award.agency_type = classify_award(award)
        award.signal_score = score_award(award)

    awards = await enrich_with_briefs(awards)

    return awards
