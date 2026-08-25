"""Pydantic signal schema — the data contract for the entire ECIS system."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class GuidanceDirection(str, Enum):
    RAISED = "raised"
    LOWERED = "lowered"
    MAINTAINED = "maintained"


class SourceMethod(str, Enum):
    KEYWORD = "keyword"
    FINBERT = "finbert"
    NER = "ner"
    LLM = "llm"
    TRIANGULATED = "triangulated"
    FINETUNED_LLM = "finetuned_llm"


class VerificationStatus(str, Enum):
    CONFIRMED = "confirmed"
    REVISED = "revised"
    REJECTED = "rejected"


class SectionLabel(str, Enum):
    PREPARED_REMARKS = "prepared_remarks"
    QA = "qa"


class SignalRecord(BaseModel):
    """A single extracted guidance signal with full provenance."""

    ticker: str = Field(..., min_length=1, max_length=10)
    direction: GuidanceDirection
    confidence_raw: float = Field(..., ge=0.0, le=1.0)
    confidence_calibrated: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    source_method: SourceMethod
    supporting_quote: str = Field(..., min_length=1)
    quote_embedding: Optional[list[float]] = None
    section_label: SectionLabel
    speaker: str = ""
    transcript_date: date
    chunk_index: int = Field(..., ge=0)
    character_offsets: tuple[int, int]
    reasoning_trace: Optional[str] = None
    ner_entities: Optional[dict[str, list[str]]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    self_consistency_votes: Optional[list[dict]] = None
    verification_status: Optional[VerificationStatus] = None
    llm_model: Optional[str] = None
    content_hash: Optional[str] = None
    retry_count: int = 0
    provenance: Optional[str] = None
    raw_llm_output: Optional[str] = None
    low_confidence: bool = False

    @field_validator("character_offsets")
    @classmethod
    def offsets_must_be_valid_range(cls, v: tuple[int, int]) -> tuple[int, int]:
        start, end = v
        if start < 0 or end < 0:
            raise ValueError("Character offsets must be non-negative")
        if end <= start:
            raise ValueError("End offset must be greater than start offset")
        return v

    model_config = {"frozen": False, "extra": "forbid"}


class ChunkMeta(BaseModel):
    """Metadata attached to every transcript chunk."""

    source_file: str
    ticker: str
    transcript_date: date
    section_label: SectionLabel
    speaker: str = ""
    chunk_index: int = Field(..., ge=0)
    char_start: int = Field(..., ge=0)
    char_end: int = Field(..., ge=0)

    @field_validator("char_end")
    @classmethod
    def end_after_start(cls, v: int, info) -> int:
        if "char_start" in info.data and v <= info.data["char_start"]:
            raise ValueError("char_end must be greater than char_start")
        return v


class FastPassResult(BaseModel):
    """Combined output from keyword + FinBERT fast-pass readers."""

    chunk_index: int
    chunk_text: str

    keyword_matched: bool = False
    keyword_direction: Optional[GuidanceDirection] = None
    keyword_phrases: list[str] = Field(default_factory=list)
    keyword_confidence: float = 0.0

    finbert_positive: float = 0.0
    finbert_negative: float = 0.0
    finbert_neutral: float = 0.0
    finbert_dominant: Optional[str] = None
    finbert_confidence: float = 0.0
    finbert_direction: Optional[GuidanceDirection] = None
