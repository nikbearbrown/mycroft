"""
Data models for the HSBC coding-assistant vulnerability-patch reference pipeline.
No field here is asserted to match any real HSBC schema — HSBC discloses no
vulnerability-report or patch-record structure (see README, "What's Constructed").
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class VulnerabilityReport:
    id: str
    file_path: str
    description: str


@dataclass
class DraftPatch:
    vulnerability_id: str
    diff: str
    assistant_notes: str


@dataclass
class ReviewDecision:
    approved: bool
    reason: Optional[str] = None


@dataclass
class PipelineResult:
    status: str  # "escalated", "rejected", "applied"
    reason: Optional[str] = None
    patch: Optional[DraftPatch] = None
