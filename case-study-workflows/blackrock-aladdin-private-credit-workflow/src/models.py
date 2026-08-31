"""
Shared data contracts used across pipeline components.

Traceability: these types are the handoff shape between components, per the
/v4 traceability matrix and /v3 component specs in this repo's design docs.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedIntent:
    """Structured output of the Orchestrator / Query Parser (§3.1).

    Originally specced against pydantic's BaseModel; switched to a plain
    dataclass since no validation features were actually being used (the
    Orchestrator builds this directly from parsed JSON, not via pydantic's
    model_validate_json) — one less dependency required to run the demo."""
    borrower_or_entity: str
    requested_metrics: list[str]
    fund_scope: Optional[list[str]] = None
    raw_query: str = ""


@dataclass
class BenchmarkResult:
    """Output of the Benchmark Calculation module (§3.4)."""
    metric: str
    value: float
    source_record_id: str
    flag: Optional[str] = None


@dataclass
class GuardrailResult:
    """Output of the Guardrail / Hallucination Check (§3.5)."""
    passed: bool
    verified_draft: str
    unverified_figures: list
    escalated: bool
