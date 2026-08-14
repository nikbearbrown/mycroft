"""
Accountability Layer — Phase 1: Core Schemas
C-02 ReasoningObject + RunSession

Pure Python stdlib — no external dependencies.
For production: swap dataclasses for Pydantic v2 (field names and validators
are kept compatible so the migration is a drop-in replace).

All models are frozen (immutable) after construction — mirrors the
append-only RunRecord store. ADR-03, SEC-03.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────

class AgentID(str, Enum):
    FINANCIAL   = "financial"
    PATENT      = "patent"
    EARNINGS    = "earnings"
    COMPETITIVE = "competitive"
    AAN         = "AAN"
    EXTERNAL    = "external"   # any third-party or provider-agnostic agent (e.g. OpenClaw)


class ParseStatus(str, Enum):
    SUCCESS       = "SUCCESS"
    PARSE_FAILURE = "PARSE_FAILURE"
    HALT          = "HALT"


class DataSourceStatus(str, Enum):
    LIVE      = "live"
    SIMULATED = "simulated"
    FAILED    = "failed"
    CACHED    = "cached"


class RunStatus(str, Enum):
    OPEN     = "OPEN"
    COMPLETE = "COMPLETE"
    HALTED   = "HALTED"


class ConfidenceClassification(str, Enum):
    STANDARD         = "STANDARD"
    HIGH_UNCERTAINTY = "HIGH_UNCERTAINTY_SPECULATIVE"


# ─────────────────────────────────────────────
# Validation error
# ─────────────────────────────────────────────

class ValidationError(Exception):
    """Raised when a schema constraint is violated."""
    pass


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


# ─────────────────────────────────────────────
# Sub-models
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class DataSource:
    """
    One data source consulted by an agent during a run.
    BN-03: data provenance per agent invocation.
    """
    source: str                        # e.g. "SEC EDGAR"
    status: DataSourceStatus
    url: str | None = None             # exact URL fetched
    fetched_at: datetime | None = None
    provenance_note: str | None = None # e.g. "Q3 unavailable — used Q2"

    def __post_init__(self):
        if not self.source or not self.source.strip():
            raise ValidationError("DataSource.source cannot be empty")
        if not isinstance(self.status, DataSourceStatus):
            raise ValidationError(
                f"DataSource.status must be a DataSourceStatus, got {type(self.status)}"
            )


@dataclass(frozen=True)
class Citation:
    """A source cited in the agent's conclusion."""
    label: str              # e.g. "10-K 2024 p.12"
    url: str | None = None
    excerpt: str | None = None  # ≤500 chars

    def __post_init__(self):
        if not self.label or not self.label.strip():
            raise ValidationError("Citation.label cannot be empty")
        if self.excerpt and len(self.excerpt) > 500:
            raise ValidationError("Citation.excerpt must be ≤500 characters")


# ─────────────────────────────────────────────
# C-02 ReasoningObject
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class ReasoningObject:
    """
    Atomic unit of the audit log. One per agent per run, plus one per failed
    validation attempt. Never mutated after write (frozen=True).

    ADR-06: thought_log is LLM-generated evidence, not verified reasoning.
    SEC-01: thought_log, raw_output, llm_tokens never exposed to investor scope.

    SDD ref: C-02
    """

    # ── Required ──
    run_id: uuid.UUID
    agent_id: AgentID
    attempt_number: int         # 1 = first attempt, 2 = retry
    parse_status: ParseStatus
    confidence_score: float     # ADR-04: computed, not self-reported. 0.0–1.0

    # ── Optional ──
    reasoning_id: uuid.UUID = field(default_factory=uuid.uuid4)
    data_sources: tuple[DataSource, ...] = field(default_factory=tuple)
    confidence_degradation_reason: str | None = None
    thought_log: str | None = None          # INTERNAL TIER ONLY — SEC-01
    reasoning_steps: tuple[str, ...] = field(default_factory=tuple)
    conclusion: str | None = None
    citations: tuple[Citation, ...] = field(default_factory=tuple)
    raw_output: dict[str, Any] | None = None    # INTERNAL TIER ONLY — SEC-01
    llm_tokens: dict[str, Any] | None = None    # INTERNAL TIER ONLY — SEC-01
    data_quality_warnings: tuple[str, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=_now_utc)

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValidationError(
                f"confidence_score must be 0.0–1.0, got {self.confidence_score}"
            )
        if self.attempt_number not in (1, 2):
            raise ValidationError(
                f"attempt_number must be 1 or 2, got {self.attempt_number}"
            )
        # ADR-07: attempt 2 result is SUCCESS or HALT — never PARSE_FAILURE
        if self.attempt_number == 2 and self.parse_status == ParseStatus.PARSE_FAILURE:
            raise ValidationError(
                "attempt_number=2 cannot have parse_status=PARSE_FAILURE. "
                "Use SUCCESS (retry worked) or HALT (retry also failed)."
            )
        # F-01: no grade without a conclusion when parse succeeded
        if self.parse_status == ParseStatus.SUCCESS and not self.conclusion:
            raise ValidationError(
                "conclusion is required when parse_status is SUCCESS"
            )
        # ADR-04: warnings must be explained
        if self.data_quality_warnings and not self.confidence_degradation_reason:
            raise ValidationError(
                "confidence_degradation_reason must be set when data_quality_warnings are present"
            )
        if self.created_at.tzinfo is None:
            raise ValidationError("created_at must be timezone-aware (UTC)")

    @property
    def confidence_score_rounded(self) -> float:
        return round(self.confidence_score, 4)

    def to_dict(self, *, investor_scope: bool = False) -> dict[str, Any]:
        """
        Serialise to dict.
        SEC-01: investor_scope=True structurally excludes
        thought_log, raw_output, llm_tokens from the output dict.
        """
        d: dict[str, Any] = {
            "reasoning_id": str(self.reasoning_id),
            "run_id": str(self.run_id),
            "agent_id": self.agent_id.value,
            "attempt_number": self.attempt_number,
            "parse_status": self.parse_status.value,
            "confidence_score": self.confidence_score_rounded,
            "confidence_degradation_reason": self.confidence_degradation_reason,
            "reasoning_steps": list(self.reasoning_steps),
            "conclusion": self.conclusion,
            "citations": [
                {"label": c.label, "url": c.url, "excerpt": c.excerpt}
                for c in self.citations
            ],
            "data_sources": [
                {
                    "source": ds.source,
                    "url": ds.url,
                    "fetched_at": ds.fetched_at.isoformat() if ds.fetched_at else None,
                    "status": ds.status.value,
                    "provenance_note": ds.provenance_note,
                }
                for ds in self.data_sources
            ],
            "data_quality_warnings": list(self.data_quality_warnings),
            "created_at": self.created_at.isoformat(),
        }
        # Auditor scope only
        if not investor_scope:
            d["thought_log"] = self.thought_log
            d["raw_output"] = self.raw_output
            d["llm_tokens"] = self.llm_tokens
        return d

    def to_json(self, *, investor_scope: bool = False) -> str:
        return json.dumps(self.to_dict(investor_scope=investor_scope))


# ─────────────────────────────────────────────
# RunSession
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class RunSession:
    """
    One RunSession per analysis run per ticker.
    Opened by C-01 Audit Middleware. Append-only in the RunRecord store.

    SDD ref: C-01, C-03
    """

    # ── Required ──
    ticker: str
    directive_version: str   # e.g. "v1.0.0"
    directive_text: str      # ADR-05: stored verbatim, not referenced by pointer

    # ── Optional ──
    run_id: uuid.UUID = field(default_factory=uuid.uuid4)
    initiated_at: datetime = field(default_factory=_now_utc)
    status: RunStatus = RunStatus.OPEN
    reasoning_objects: tuple[ReasoningObject, ...] = field(default_factory=tuple)
    run_confidence_score: float | None = None
    confidence_classification: ConfidenceClassification | None = None
    completed_at: datetime | None = None
    aan_triggered: bool = False
    aan_affidavit: str | None = None

    def __post_init__(self):
        # Normalise ticker
        object.__setattr__(self, "ticker", self.ticker.upper().strip())
        self._validate()

    def _validate(self):
        if not self.ticker:
            raise ValidationError("ticker cannot be empty")
        if len(self.ticker) > 10:
            raise ValidationError(
                f"ticker must be ≤10 characters, got {len(self.ticker)!r}"
            )
        if not self.directive_version or not self.directive_version.strip():
            raise ValidationError("directive_version cannot be empty")
        if not self.directive_text or not self.directive_text.strip():
            raise ValidationError("directive_text cannot be empty")
        if self.completed_at and self.status == RunStatus.OPEN:
            raise ValidationError(
                "completed_at cannot be set while status is still OPEN"
            )
        # ADR-08: classification must match score threshold
        if (
            self.run_confidence_score is not None
            and self.confidence_classification is not None
        ):
            expected = (
                ConfidenceClassification.HIGH_UNCERTAINTY
                if self.run_confidence_score < 0.4
                else ConfidenceClassification.STANDARD
            )
            if self.confidence_classification != expected:
                raise ValidationError(
                    f"confidence_classification={self.confidence_classification.value} is "
                    f"inconsistent with run_confidence_score={self.run_confidence_score}. "
                    f"Expected {expected.value} per ADR-08 threshold (0.4)."
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": str(self.run_id),
            "ticker": self.ticker,
            "initiated_at": self.initiated_at.isoformat(),
            "status": self.status.value,
            "directive_version": self.directive_version,
            "directive_text": self.directive_text,
            "run_confidence_score": self.run_confidence_score,
            "confidence_classification": (
                self.confidence_classification.value
                if self.confidence_classification else None
            ),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "aan_triggered": self.aan_triggered,
            "aan_affidavit": self.aan_affidavit,
            "reasoning_objects": [
                ro.to_dict(investor_scope=False) for ro in self.reasoning_objects
            ],
        }
