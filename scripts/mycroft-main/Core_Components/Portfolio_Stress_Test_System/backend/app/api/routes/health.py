from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Portfolio Stress Testing - Layer 1",
        "timestamp": datetime.now().isoformat()
    }
