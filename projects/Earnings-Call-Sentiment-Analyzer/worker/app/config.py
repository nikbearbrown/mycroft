from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "earnings_sentiment")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")
    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user: str = os.getenv("RABBITMQ_USERNAME", "guest")
    rabbitmq_password: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    model_name: str = os.getenv("MODEL_NAME", "ProsusAI/finbert")
    model_batch_size: int = int(os.getenv("MODEL_BATCH_SIZE", "16"))

    def resolve_upload_path(self, message_path: str) -> Path:
        upload_root = Path(self.upload_dir).expanduser().resolve()
        candidate = Path(message_path)
        if not candidate.is_absolute():
            candidate = upload_root / candidate
        candidate = candidate.resolve()
        if not candidate.is_relative_to(upload_root):
            raise ValueError("Analysis job file path is outside the configured upload directory")
        return candidate
