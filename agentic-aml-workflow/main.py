"""
main.py
=======
Agentic AML Compliance Workflow — FastAPI Entry Point

Starts the pipeline API. On first run with default settings:
  - All four agents execute against real LLM calls
  - GLEIF LEI database is queried (free public API)
  - KYC, OFAC, TX history use stubs (no real data)
  - Human review auto-approves when DEV_AUTO_APPROVE=true

To run:
    uvicorn main:app --reload
    docker compose up

API docs available at: http://localhost:8000/docs
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Load .env file before any config imports
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("aml_pipeline")


# ─────────────────────────────────────────────────────────────
# DEV IMPLEMENTATIONS
# Used when DEV_AUTO_APPROVE=true (default in .env.example).
# Replace with real implementations for production.
# ─────────────────────────────────────────────────────────────

class DevAuditLog:
    """
    Development audit log. Writes to console and an in-memory list.
    Replace with PostgreSQL implementation for production.
    See orchestrator.py AuditLog interface for the contract.
    """
    def __init__(self):
        self.entries: list[dict] = []

    def write(self, trade_id: UUID, event_type: str, content: Any) -> None:
        entry = {
            "trade_id": str(trade_id),
            "event_type": event_type,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.entries.append(entry)
        logger.info(f"[AUDIT] [{trade_id}] {event_type}")

    def seal(self, trade_id: UUID, decision: Any) -> None:
        logger.info(f"[AUDIT] [{trade_id}] audit_sealed  decision={getattr(decision, 'approved', '?')}")
        self.entries.append({
            "trade_id": str(trade_id),
            "event_type": "audit_sealed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


class _DevApprovalToken:
    """Dev-only approval token that is valid for any trade."""
    def __init__(self, trade_id: UUID):
        self.token_id = UUID("00000000-0000-0000-0000-000000000001")
        self._trade_id = trade_id

    def is_valid_for(self, trade_id: UUID) -> bool:
        return True


class DevHumanReviewQueue:
    """
    Development human review queue.
    When DEV_AUTO_APPROVE=true, immediately approves every exception report.
    The full exception report is logged so you can read what the compliance
    officer would have received.

    Replace with a real queue + UI for production.
    See orchestrator.py HumanReviewQueue interface for the contract.
    """

    def request_approval(self, trade_id: UUID, report: str):
        from orchestrator import ApprovalDecision

        logger.info(
            f"\n{'='*60}\n"
            f"[DEV] EXCEPTION REPORT for trade {trade_id}\n"
            f"{'='*60}\n"
            f"{report}\n"
            f"{'='*60}\n"
            f"[DEV] Auto-approving (DEV_AUTO_APPROVE=true)\n"
        )

        return ApprovalDecision(
            approved=True,
            officer_id="DEV-AUTO-APPROVE",
            timestamp=datetime.now(timezone.utc),
            rationale="Auto-approved in development mode (DEV_AUTO_APPROVE=true). "
                      "Replace DevHumanReviewQueue with a real implementation for production.",
            token=_DevApprovalToken(trade_id),
        )


class DevSettlementAPI:
    """
    Development settlement API. Logs the settlement instruction but does
    not execute it. Replace with your real settlement system for production.
    See orchestrator.py SettlementAPI interface for the contract.
    """

    def execute(self, trade_id: UUID, token: Any) -> None:
        if not token.is_valid_for(trade_id):
            raise PermissionError(f"ApprovalToken is not valid for trade {trade_id}.")
        logger.info(
            f"[DEV] Settlement instruction logged for trade {trade_id}. "
            "No real settlement executed in dev mode."
        )


class DevEscalationQueue:
    """
    Development escalation queue. Logs escalation packages but does not
    route them. Replace with a real queue for production.
    See escalation.py EscalationQueue interface for the contract.
    """

    def enqueue(self, package: Any) -> None:
        logger.warning(
            f"[DEV] Escalation queued for trade {package.trade_id}. "
            f"Team: {package.assigned_team}. Reason: {package.escalation_reason}"
        )


# ─────────────────────────────────────────────────────────────
# APPLICATION LIFECYCLE
# ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Build the orchestrator on startup. Store it in app.state
    so request handlers can access it without rebuilding per request.
    """
    from config import PipelineConfig, build_orchestrator
    from taxonomy_loader import get_loader

    env = os.environ.get("ENVIRONMENT", "development")
    dev_auto_approve = os.environ.get("DEV_AUTO_APPROVE", "true").lower() == "true"

    logger.info(f"Starting AML pipeline API  [environment={env}]")

    # Load taxonomy
    try:
        loader = get_loader()
        logger.info(f"Taxonomy loaded: {loader.list_flag_types()}")
    except FileNotFoundError as e:
        logger.error(f"Taxonomy file not found: {e}")
        raise

    # Build config
    if env == "production":
        config = PipelineConfig.from_env()
        logger.info("Using production config (PipelineConfig.from_env())")
    else:
        config = PipelineConfig.development()
        logger.info(
            "Using development config (PipelineConfig.development())\n"
            "  GLEIF LEI API:    REAL (free public API)\n"
            "  KYC records:      STUB\n"
            "  OFAC sanctions:   STUB\n"
            "  TX history:       STUB\n"
            f"  Human review:     {'DEV AUTO-APPROVE' if dev_auto_approve else 'REAL (will block waiting for approval)'}\n"
            "  Audit log:        DEV (console + in-memory)\n"
            "  Settlement API:   DEV (logged only)\n"
        )

    # Build dev dependencies if applicable
    audit_log = DevAuditLog()
    deps: dict = {"audit_log": audit_log}

    if dev_auto_approve or env != "production":
        deps["review_queue"] = DevHumanReviewQueue()
        deps["settlement_api"] = DevSettlementAPI()
        deps["escalation_queue"] = DevEscalationQueue()
        if dev_auto_approve:
            logger.warning(
                "DEV_AUTO_APPROVE=true — human review gate is bypassed. "
                "Set DEV_AUTO_APPROVE=false to test the blocking review path."
            )

    # Build orchestrator
    orchestrator = build_orchestrator(config, deps=deps)
    app.state.orchestrator = orchestrator
    app.state.audit_log = audit_log  # Expose for the /workflows endpoint
    logger.info("Orchestrator ready.")

    yield  # App runs

    logger.info("Shutting down AML pipeline API.")


# ─────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agentic AML Compliance Workflow",
    description=(
        "Multi-agent AML compliance pipeline for US institutional equities. "
        "Processes AML-flagged trades through a four-agent pipeline "
        "(triage → investigation → reasoning → report) with a mandatory "
        "human compliance officer checkpoint before settlement execution."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    """Basic health check. Returns 200 when the API is ready."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/trades/flagged", tags=["Pipeline"])
def handle_flagged_trade(trade_event: dict, request: Request):
    """
    Main pipeline endpoint. Accepts a raw trade event dict and runs the
    full AML compliance pipeline.

    The request body must be a valid Trade event. Required fields:
      trade_id, security_isin, security_description,
      counterparty_name, counterparty_lei (20-char), counterparty_country,
      trade_side (BUY/SELL), quantity, execution_price, trade_value,
      settlement_date, execution_timestamp (UTC), trader_id, desk_id, aml_flag

    Returns a WorkflowResult with pipeline status and all agent outputs.

    Example request body: see tests/conftest.py SANCTIONS_NAME_MATCH_EVENT
    """
    from schemas import Trade

    # Validate schema at the boundary
    try:
        trade = Trade.from_event(trade_event)
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Trade event failed schema validation.",
                "validation_errors": e.errors(),
                "hint": "Check counterparty_lei is exactly 20 alphanumeric characters "
                        "and confidence_score is between 0.30 and 0.85.",
            },
        )

    # Confidence score routing check
    from taxonomy_loader import get_loader
    thresholds = get_loader().get_confidence_thresholds()

    if trade.aml_flag:
        score = trade.aml_flag.confidence_score
        if score > thresholds["auto_escalate_above"]:
            # [DEV] In production, this should route to the escalation queue directly.
            # For now, return a clear error so developers know what to build.
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Trade confidence score exceeds auto-escalation threshold.",
                    "confidence_score": score,
                    "threshold": thresholds["auto_escalate_above"],
                    "action": "Route this trade directly to the escalation queue "
                              "before calling this endpoint. See handle_aml_flag() in orchestrator.py.",
                },
            )

    # Run pipeline
    try:
        result = request.app.state.orchestrator.run(trade)
    except NotImplementedError as e:
        raise HTTPException(
            status_code=501,
            detail={
                "error": "A required component is not yet implemented.",
                "message": str(e),
                "hint": "Check the [DEV] markers in orchestrator.py and config.py. "
                        "In development mode, set DEV_AUTO_APPROVE=true in .env to bypass "
                        "the human review gate.",
            },
        )
    except Exception as e:
        logger.exception(f"Pipeline error for trade {trade.trade_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Pipeline execution failed.",
                "message": str(e),
            },
        )

    return {
        "trade_id": str(result.trade_id),
        "status": result.status,
        "agent_outputs": result.outputs,
        "escalation_reason": result.escalation_reason,
        "decision": result.decision.to_dict() if result.decision else None,
    }


@app.get("/workflows/recent", tags=["Pipeline"])
def recent_workflows(request: Request, limit: int = 10):
    """
    Returns the most recent audit log entries (dev mode only).
    In production, query your audit log database directly.
    """
    audit_log = getattr(request.app.state, "audit_log", None)
    if not isinstance(audit_log, DevAuditLog):
        raise HTTPException(
            status_code=501,
            detail="This endpoint is only available in development mode (DevAuditLog). "
                   "In production, query your audit log database directly."
        )
    recent = audit_log.entries[-limit:]
    return {"entries": recent, "total": len(audit_log.entries)}


@app.get("/taxonomy/flags", tags=["Reference"])
def list_flag_types():
    """Returns all AML flag types defined in the taxonomy."""
    from taxonomy_loader import get_loader
    loader = get_loader()
    return {
        "flag_types": loader.list_flag_types(),
        "confidence_thresholds": loader.get_confidence_thresholds(),
    }


# ─────────────────────────────────────────────────────────────
# EXCEPTION HANDLERS
# ─────────────────────────────────────────────────────────────

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": str(exc)},
    )


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        reload=os.environ.get("ENVIRONMENT", "development") == "development",
        log_level="info",
    )
