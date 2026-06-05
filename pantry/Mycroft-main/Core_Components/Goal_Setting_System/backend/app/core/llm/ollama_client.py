"""
Ollama LLM Client
"""
import httpx
import logging
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.DEFAULT_MODEL
        self.timeout = settings.LLM_TIMEOUT
    
    async def check_health(self) -> Dict[str, Any]:
        """Check if Ollama is running and get available models"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/tags",
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    return {
                        "available": True,
                        "models": models,
                        "default_model": self.default_model
                    }
                return {"available": False, "models": []}
        except Exception as e:
            logger.error(f"Ollama health check failed: {str(e)}")
            return {
                "available": False,
                "models": [],
                "error": str(e)
            }
    
    async def generate(
        self,
        prompt: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate response from Ollama"""
        try:
            model = model or self.default_model
            temperature = temperature or settings.LLM_TEMPERATURE
            max_tokens = max_tokens or settings.LLM_MAX_TOKENS
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": 0.9,
                        "num_predict": max_tokens
                    }
                }
                
                logger.info(f"Calling Ollama with model: {model}")
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama API error: {response.text}")
                
                result = response.json()
                return result.get("response", "")
                
        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise Exception("Ollama request timed out. Try a smaller model or increase timeout.")
        except Exception as e:
            logger.error(f"Ollama generation failed: {str(e)}")
            raise Exception(f"Ollama error: {str(e)}")

# Global client instance
ollama_client = OllamaClient()