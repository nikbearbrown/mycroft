from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime
from app.models import FeedListResponse, Feed, FetchTriggerResponse, SourceFeed, ImpactLevel
from app.crud import FeedCRUD
import httpx
from app.config import get_settings

router = APIRouter(prefix="/api/feeds", tags=["feeds"])
settings = get_settings()

@router.post("/fetch", response_model=FetchTriggerResponse)
async def trigger_feed_fetch():
    """Trigger n8n workflow to fetch new RSS feeds"""
    
    # Method 1: Via Webhook (if you added webhook trigger)
    if settings.n8n_webhook_url:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(settings.n8n_webhook_url)
                
                if response.status_code in [200, 201]:
                    return FetchTriggerResponse(
                        status="success",
                        message="Feed fetching workflow triggered via webhook",
                        workflow_triggered=True
                    )
                else:
                    raise HTTPException(
                        status_code=500, 
                        detail=f"n8n webhook returned status {response.status_code}"
                    )
        
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Could not connect to n8n webhook: {str(e)}"
            )
    
    # Method 2: Via n8n API (if you have workflow ID)
    elif settings.n8n_workflow_id:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Trigger workflow execution via API
                response = await client.post(
                    f"{settings.n8n_api_url}/workflows/{settings.n8n_workflow_id}/execute",
                    json={}
                )
                
                if response.status_code in [200, 201]:
                    return FetchTriggerResponse(
                        status="success",
                        message="Feed fetching workflow triggered via API",
                        workflow_triggered=True
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"n8n API returned status {response.status_code}: {response.text}"
                    )
        
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Could not connect to n8n API: {str(e)}"
            )
    
    # No configuration found
    else:
        raise HTTPException(
            status_code=501,
            detail="n8n trigger not configured. Set N8N_WEBHOOK_URL or N8N_WORKFLOW_ID in .env"
        )


@router.get("/stats")  # ← MOVE THIS BEFORE /{feed_id}
async def get_stats():
    """Get dashboard statistics"""
    try:
        return FeedCRUD.get_stats()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )

@router.get("/recent")  # ← MOVE THIS BEFORE /{feed_id} TOO
async def get_recent_feeds(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100)
):
    """Get recent high-priority feeds for dashboard"""
    try:
        return FeedCRUD.get_recent_feeds(days=days, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent feeds: {str(e)}"
        )

@router.get("/list", response_model=FeedListResponse)
async def list_feeds(
    source_feed: Optional[SourceFeed] = None,
    min_urgency: Optional[int] = Query(None, ge=1, le=10),
    max_urgency: Optional[int] = Query(None, ge=1, le=10),
    impact_level: Optional[ImpactLevel] = None,
    categories: Optional[List[str]] = Query(None),
    is_enforcement: Optional[bool] = None,
    has_deadline: Optional[bool] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List feeds with flexible filtering
    
    Example queries:
    - `/api/feeds/list?min_urgency=7` - High priority only
    - `/api/feeds/list?source_feed=SEC Press Releases` - SEC only
    - `/api/feeds/list?categories=crypto&categories=enforcement` - Crypto enforcement
    """
    try:
        result = FeedCRUD.list_feeds(
            source_feed=source_feed.value if source_feed else None,
            min_urgency=min_urgency,
            max_urgency=max_urgency,
            impact_level=impact_level.value if impact_level else None,
            categories=categories,
            is_enforcement=is_enforcement,
            has_deadline=has_deadline,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        return FeedListResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list feeds: {str(e)}"
        )

@router.get("/{feed_id}")  # ← THIS MUST BE LAST
async def get_feed(feed_id: int):
    """Get single feed by ID"""
    try:
        feed = FeedCRUD.get_feed_by_id(feed_id)
        if not feed:
            raise HTTPException(status_code=404, detail="Feed not found")
        return feed
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get feed: {str(e)}"
        )