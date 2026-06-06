"""
Goal parsing and extraction logic
"""
import json
import re
import logging
from typing import Dict, Any
from datetime import datetime

from app.core.llm import ollama_client, build_extraction_prompt
from app.schemas.goal import GoalExtractionRequest, GoalExtractionResponse, InvestmentGoal

logger = logging.getLogger(__name__)

    
def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract JSON from LLM response"""
    # Try to find JSON block
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
    
    # Try parsing entire text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Could not extract valid JSON from LLM response")

async def extract_goals(request: GoalExtractionRequest) -> GoalExtractionResponse:
    """Extract goals from natural language using LLM"""
    start_time = datetime.utcnow()
    
    try:
        # Build prompt
        prompt = build_extraction_prompt(request.text)
        
        # Call LLM
        model = request.model or "llama3:latest"
        llm_response = await ollama_client.generate(
            prompt=prompt,
            model=model,
            temperature=request.temperature
        )
        
        # Parse JSON response
        extracted_data = extract_json_from_text(llm_response)
        
        # Validate structure
        if "goals" not in extracted_data:
            raise ValueError("Response missing 'goals' field")
        
        # Parse goals into Pydantic models
        goals = [InvestmentGoal(**goal) for goal in extracted_data["goals"]]
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        return GoalExtractionResponse(
            success=True,
            goals=goals,
            summary=extracted_data.get("summary", "Goals extracted successfully"),
            processed_at=end_time.isoformat(),
            model_used=model,
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Goal extraction failed: {str(e)}")
        raise
