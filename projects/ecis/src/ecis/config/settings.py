"""Centralised configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(_PROJECT_ROOT / ".env")


class _Settings:
    edgar_user_agent: str = os.getenv("EDGAR_USER_AGENT", "ECIS Research admin@example.com")
    fmp_api_key: str = os.getenv("FMP_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm_llama_model: str = os.getenv("LLM_LLAMA_MODEL", "llama3.1:8b-instruct-q8_0")
    llm_mistral_model: str = os.getenv("LLM_MISTRAL_MODEL", "mistral:7b-instruct")
    llm_qwen_model: str = os.getenv("LLM_QWEN_MODEL", "qwen2.5:14b-instruct-q4_K_M")
    llm_model: str = os.getenv("LLM_MODEL", os.getenv("LLM_LLAMA_MODEL", "llama3.1:8b-instruct-q8_0"))

    project_root: Path = _PROJECT_ROOT
    data_dir: Path = _PROJECT_ROOT / os.getenv("DATA_DIR", "data")
    db_dir: Path = _PROJECT_ROOT / os.getenv("DB_DIR", "data/db")

    raw_edgar_dir: Path = data_dir / "raw" / "edgar"
    raw_fmp_dir: Path = data_dir / "raw" / "fmp"
    cleaned_dir: Path = data_dir / "processed" / "cleaned"
    normalised_dir: Path = data_dir / "processed" / "normalised"
    chunks_dir: Path = data_dir / "processed" / "chunks"

    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "")

    chunk_size_tokens: int = 400
    chunk_overlap_tokens: int = 50

    self_consistency_temps: list[float] = [0.1, 0.3, 0.5]
    confidence_agreement_threshold: float = 0.15
    dedup_similarity_threshold: float = 0.90

    weight_keyword: float = 0.15
    weight_finbert: float = 0.20
    weight_llm: float = 0.50
    weight_llm_llama: float = float(os.getenv("WEIGHT_LLM_LLAMA", "0.50"))
    weight_llm_mistral: float = float(os.getenv("WEIGHT_LLM_MISTRAL", "0.50"))
    weight_llm_qwen: float = float(os.getenv("WEIGHT_LLM_QWEN", "0.52"))
    weight_agreement: float = 0.15

    min_chunk_tokens: int = int(os.getenv("MIN_CHUNK_TOKENS", "20"))
    max_boilerplate_ratio: float = float(os.getenv("MAX_BOILERPLATE_RATIO", "0.8"))
    min_scorecard_confidence: float = float(os.getenv("MIN_SCORECARD_CONFIDENCE", "0.35"))
    speaker_role_weights: dict[str, float] = {
        "cfo": float(os.getenv("SPEAKER_WEIGHT_CFO", "1.0")),
        "ceo": float(os.getenv("SPEAKER_WEIGHT_CEO", "0.8")),
        "coo": float(os.getenv("SPEAKER_WEIGHT_COO", "0.7")),
        "ir": float(os.getenv("SPEAKER_WEIGHT_IR", "0.6")),
        "analyst": float(os.getenv("SPEAKER_WEIGHT_ANALYST", "0.3")),
        "operator": float(os.getenv("SPEAKER_WEIGHT_OPERATOR", "0.0")),
        "unknown": float(os.getenv("SPEAKER_WEIGHT_UNKNOWN", "0.8")),
    }
    chunk_quality_weights: dict[str, float] = {
        "boilerplate": 0.40,
        "token_count": 0.20,
        "completeness": 0.20,
        "speaker_transitions": 0.20,
    }
    llm_json_max_retries: int = int(os.getenv("LLM_JSON_MAX_RETRIES", "3"))
    llm_json_retry_base_delay: float = float(os.getenv("LLM_JSON_RETRY_BASE_DELAY", "0.5"))

    edgar_requests_per_second: int = 10
    fmp_daily_limit: int = 250

    finbert_model_name: str = "ProsusAI/finbert"
    finbert_batch_size: int = 16

    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    def resolve_llm_models(self, spec: str | None = None) -> list[str]:
        raw = (spec or "llama").strip()
        key = raw.lower()
        if key in ("llama", "llama3", "llama3.1"):
            return [self.llm_llama_model]
        if key in ("mistral", "mistral-7b"):
            return [self.llm_mistral_model]
        if key in ("qwen", "qwen2.5", "qwen2.5-14b"):
            return [self.llm_qwen_model]
        if key == "both":
            return [self.llm_llama_model, self.llm_mistral_model]
        if key == "all":
            return [self.llm_llama_model, self.llm_mistral_model, self.llm_qwen_model]
        return [raw]

    def model_alias(self, model_name: str) -> str:
        name = (model_name or "").lower()
        if "qwen" in name:
            return "qwen"
        if "mistral" in name:
            return "mistral"
        if "llama" in name:
            return "llama"
        return model_name or "unknown"

    def llm_weight_for(self, model_name: str | None, weights: dict[str, float] | None = None) -> float:
        table = weights or {}
        alias = self.model_alias(model_name or "")
        keyed = table.get(f"llm_{alias}")
        if keyed is not None:
            return keyed
        defaults = {
            "llama": self.weight_llm_llama,
            "mistral": self.weight_llm_mistral,
            "qwen": self.weight_llm_qwen,
        }
        return table.get("llm", defaults.get(alias, self.weight_llm))

    def ensure_dirs(self) -> None:
        for d in (
            self.raw_edgar_dir,
            self.raw_fmp_dir,
            self.cleaned_dir,
            self.normalised_dir,
            self.chunks_dir,
            self.db_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)


settings = _Settings()
