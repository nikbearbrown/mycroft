"""
API Dependencies
"""
from fastapi import HTTPException
from app.core.llm import ollama_client

async def check_ollama_available():
    """Dependency to check if Ollama is available"""
    health = await ollama_client.check_health()
    if not health["available"]:
        raise HTTPException(
            status_code=503,
            detail="Ollama service is not available. Please ensure Ollama is running."
        )
    return health