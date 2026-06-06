import os
import httpx
from typing import List
from dotenv import load_dotenv
from app.models.award import Award

load_dotenv()

_API_KEY = os.getenv("SAM_GOV_API_KEY")
_BASE_URL = "https://api.sam.gov/opportunities/v2/search"


async def fetch_recent_awards(limit: int = 100, keyword: str = "") -> List[Award]:
    """
    Fetch recent contract award notices from SAM.gov (async).

    Args:
        limit:   max number of records to return (SAM.gov max per page: 1000)
        keyword: optional search keyword to filter results
    """
    if not _API_KEY:
        raise RuntimeError("SAM_GOV_API_KEY is not set in .env")

    today = _format_date(0)
    from_date = _format_date(30)

    params = {
        "api_key": _API_KEY,
        "limit": limit,
        "offset": 0,
        "postedFrom": from_date,   # SAM.gov requires both postedFrom AND postedTo
        "postedTo": today,
        "ptype": "a",              # 'a' = award notice
    }
    if keyword:
        params["q"] = keyword

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(_BASE_URL, params=params)

    if response.status_code == 429:
        try:
            body = response.json()
            next_access = body.get("nextAccessTime", "tomorrow")
        except Exception:
            next_access = "tomorrow"
        raise RuntimeError(f"RATE_LIMITED:{next_access}")

    if response.status_code != 200:
        raise RuntimeError(
            f"SAM.gov returned {response.status_code}: {response.text[:300]}"
        )

    data = response.json()
    records = data.get("opportunitiesData") or []
    return [_to_award(r) for r in records]


def _to_award(record: dict) -> Award:
    award_data = record.get("award") or {}
    awardee = award_data.get("awardee") or {}
    pop = record.get("placeOfPerformance") or {}
    city = pop.get("city") or {}

    return Award(
        award_id=record.get("noticeId", ""),
        recipient_name=awardee.get("name", ""),
        awarding_agency=record.get("fullParentPathName", ""),
        award_amount=float(award_data.get("amount") or 0),
        award_date=award_data.get("date", ""),
        description=record.get("title", ""),
        naics_code=record.get("naicsCode", ""),
        place_of_performance=city.get("name", ""),
    )


def _format_date(days_ago: int) -> str:
    from datetime import date, timedelta
    return (date.today() - timedelta(days=days_ago)).strftime("%m/%d/%Y")
