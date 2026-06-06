from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # N8N - Choose one method
    n8n_webhook_url: str = ""  # For webhook trigger
    n8n_api_url: str = "http://localhost:5678/api/v1"  # For API trigger
    n8n_workflow_id: str = "oqtFi5me5Cypzy06"  # Your workflow ID
    
    # Ollama
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    
    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # RAG
    chroma_persist_directory: str = "./chroma_db"
    max_context_feeds: int = 10
    chunk_size: int = 2000
    chunk_overlap: int = 400
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()