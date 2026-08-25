"""Typed state schemas for all LangGraph agent graphs."""

from __future__ import annotations

from typing import Any, Optional

from typing_extensions import TypedDict

from ecis.schemas.signal import (
    FastPassResult,
    GuidanceDirection,
    SignalRecord,
)


class EscalationCategory:
    A = "A"  # Both readers agree
    B = "B"  # One reader flagged, low confidence
    C = "C"  # Readers disagree on direction
    D = "D"  # Neither reader detected anything


class PipelineState(TypedDict, total=False):
    """State flowing through the top-level extraction pipeline graph."""

    ticker: str
    transcript_path: str
    transcript_text: str

    chunks: list[dict[str, Any]]

    fast_pass_results: list[FastPassResult]

    category_a_indices: list[int]
    category_b_indices: list[int]
    category_c_indices: list[int]
    category_d_indices: list[int]

    keyword_signals: list[dict]
    finbert_signals: list[dict]
    ner_results: list[dict]
    llm_signals: list[dict]

    conflict_resolutions: list[dict]

    triangulated_signals: list[SignalRecord]
    final_signals: list[SignalRecord]

    current_chunk_index: int
    errors: list[str]
    llm_model: str
    chunk_models: dict[int, str]
    rejected_chunks: list[dict[str, Any]]


class ConflictState(TypedDict, total=False):
    """State for the four-node conflict resolution subgraph."""

    chunk_index: int
    chunk_text: str
    ticker: str
    transcript_date: str

    keyword_direction: Optional[GuidanceDirection]
    finbert_direction: Optional[GuidanceDirection]
    keyword_phrases: list[str]
    finbert_scores: dict[str, float]

    preceding_chunk: Optional[str]
    following_chunk: Optional[str]

    resolution_prompt: str
    resolved_direction: Optional[GuidanceDirection]
    resolved_confidence: float
    vindicated_reader: Optional[str]  # "keyword" or "finbert"
    resolution_reasoning: str


class WatchdogState(TypedDict, total=False):
    """State for the calibration watchdog graph."""

    rolling_window_size: int
    reader_name: str

    rolling_brier: float
    rolling_ece: float
    rolling_skill_score: float
    consecutive_negative_skill: int

    ece_threshold: float
    negative_skill_threshold: int
    underperformance_threshold: int
    consecutive_underperformance: int

    action_type: Optional[str]  # "recalibrate", "reduce_weight", "propose_reversion"
    action_details: dict[str, Any]
    requires_human_approval: bool
    human_approved: Optional[bool]


class LearningState(TypedDict, total=False):
    """State for the orchestration learning feedback graph."""

    total_signals_expected: int
    missed_signals: list[dict]
    missed_from_category_d: int
    false_negative_rate: float

    current_thresholds: dict[str, float]
    proposed_thresholds: dict[str, float]
    adjustment_magnitude: float  # Percentage change

    requires_human_approval: bool
    human_approved: Optional[bool]
    adjustment_applied: bool
    d_chunk_count: int
    classified_chunks: int
    skip_reason: Optional[str]
