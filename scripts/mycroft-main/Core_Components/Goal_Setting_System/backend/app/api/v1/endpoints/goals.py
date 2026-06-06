"""
Goal extraction endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from app.schemas.goal import GoalExtractionRequest, GoalExtractionResponse
from app.core.processing import goal_parser
from app.api.deps import check_ollama_available

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/extract", response_model=GoalExtractionResponse)
async def extract_goals(
    request: GoalExtractionRequest,
    _: dict = Depends(check_ollama_available)
):
    """
    Extract structured investment goals from natural language
    
    **Example:**
    ```json
    {
      "text": "I want to retire in 20 years with $2M. I have $100k saved and can invest $3k/month.",
      "model": "llama3.1:8b"
    }
    ```
    """
    try:
        logger.info(f"Extracting goals from text: {request.text[:100]}...")
        result = await goal_parser.extract_goals(request)
        logger.info(f"Extracted {len(result.goals)} goals successfully")
        return result
        
    except ValueError as e:
        logger.error(f"Parsing error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"Failed to parse LLM response: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Goal extraction failed: {str(e)}"
        )