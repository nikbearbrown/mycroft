"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

from app.core.llm import ollama_client
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    Returns service status and Ollama availability
    """
    ollama_status = await ollama_client.check_health()
    
    return {
        "status": "healthy" if ollama_status["available"] else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "ollama": {
            "available": ollama_status["available"],
            "url": settings.OLLAMA_BASE_URL,
            "default_model": settings.DEFAULT_MODEL,
            "available_models": ollama_status.get("models", [])
        }
    }

@router.get("/ping")
async def ping() -> Dict[str, str]:
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}