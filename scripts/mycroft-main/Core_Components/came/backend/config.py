from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://came:came@localhost:5432/came"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    class Config:
        env_file = ".env"


settings = Settings()
