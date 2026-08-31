"""
main.py
=======
Agentic Credit Memo Pipeline — FastAPI Entry Point

JPMorgan-style commercial credit underwriting workflow.

On startup, the orchestrator is built from:
  - LLM config (model + API key from environment)
  - Three data source adapters (stubs by default)
  - Audit log (dev: in-memory; production: replace with PostgreSQL)
  - Approval queue (dev: logs to console; production: replace with your
    loan origination system's workflow engine)

[DEV] POINTS IN THIS FILE:
  1. Data source adapters — replace Stub* classes in the lifespan function
     with your real adapters. See data_sources.py for the interfaces.
  2. DevAuditLog — replace with PostgreSQL append-only storage in production.
     See AuditLog interface in orchestrator.py for the contract.
  3. DevApprovalQueue — replace with a real submission to your loan origination
     system. See ApprovalQueue interface in approval_routing.py for the contract.
  4. ENVIRONMENT env var — set to "production" in .env or docker-compose.yml to disable auto-reload.

To run:
    uvicorn main:app --reload
    docker compose up

API docs: http://localhost:8000/docs
"""

from __future__ import annotations

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

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("credit_pipeline")


# ─────────────────────────────────────────────────────────────
# DEV IMPLEMENTATIONS
# ─────────────────────────────────────────────────────────────

class DevAuditLog:
    """
    Development audit log — writes to console and in-memory list.

    [DEV] Replace with a PostgreSQL append-only implementation for production.
    The audit trail must be immutable: once a record is written, it cannot
    be edited or deleted. It is the authoritative record of what the pipeline
    did and who approved what — regulators and examiners may request it.
    See AuditLog interface in orchestrator.py for the contract.
    """
    def __init__(self):
        self.entries: list[dict] = []

    def write(self, application_id: UUID, event_type: str, content: Any) -> None:
        entry = {
            "application_id": str(application_id),
            "event_type": event_type,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.entries.append(entry)
        logger.info(f"[AUDIT] [{application_id}] {event_type}")

    def seal(self, application_id: UUID, routing: Any) -> None:
        logger.info(f"[AUDIT] [{application_id}] pipeline_sealed  tier={getattr(routing, 'approval_tier', '?')}")
        self.entries.append({
            "application_id": str(application_id),
            "event_type": "pipeline_sealed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def record_decision(self, application_id: UUID, decision: Any) -> None:
        """
        Appends the human reviewer's credit decision to the audit trail.
        This is the Step 9 record — officer name, credentials, decision, rationale.

        [DEV] In production, this write must be atomic and append-only.
        A decision record must never be editable after it is written.
        """
        entry = {
            "application_id": str(application_id),
            "event_type": "credit_decision_recorded",
            "reviewing_officer": getattr(decision, "reviewing_officer_name", str(decision)),
            "decision": getattr(decision, "decision", str(decision)),
            "rationale": getattr(decision, "decision_rationale", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.entries.append(entry)
        logger.info(
            f"[AUDIT] [{application_id}] credit_decision_recorded  "
            f"officer={entry['reviewing_officer']}  decision={entry['decision']}"
        )


class ApplicationStore:
    """
    Development in-memory store keyed by application_id.
    Holds the WorkflowResult (memo + routing) after /applications/submit
    so the /applications/{id}/decision endpoint can look it up.

    [DEV] Replace with a persistent store (PostgreSQL or your loan
    origination system's application record) for production. The store
    must survive process restarts — an in-memory dict does not.
    """
    def __init__(self):
        self._store: dict[str, Any] = {}

    def save(self, application_id: UUID, result: Any) -> None:
        self._store[str(application_id)] = result

    def get(self, application_id: UUID) -> Any | None:
        return self._store.get(str(application_id))


class DevApprovalQueue:
    """
    Development approval queue — logs the routing decision and memo to console.
    Does not submit to any real system.

    [DEV] Replace with a real implementation that posts the memo to your loan
    origination system's approval workflow. The approval queue is where the
    human analyst or credit committee receives the draft and submits their
    decision. Connect to: nCino, Salesforce Financial Services Cloud, or an
    internal PostgreSQL-backed queue.
    See ApprovalQueue interface in approval_routing.py for the contract.
    """
    def submit(self, routing: Any, memo: Any) -> None:
        logger.info(
            f"\n{'='*60}\n"
            f"[DEV] MEMO ROUTED — Application {routing.application_id}\n"
            f"  Approval tier: {routing.approval_tier}\n"
            f"  Reason: {routing.routing_reason}\n"
            f"{'='*60}\n"
            f"{memo.to_review_string()}\n"
            f"[DEV] No real submission in dev mode. Replace DevApprovalQueue for production.\n"
        )


# ─────────────────────────────────────────────────────────────
# APPLICATION LIFECYCLE
# ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    from orchestrator import CreditMemoOrchestrator
    from data_sources import StubKYCRepository, StubOSINTProvider, StubFinancialDataStore
    from policy_loader import get_loader

    env = os.environ.get("ENVIRONMENT", "development")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    model = os.environ.get("LLM_MODEL", "claude-sonnet-4-6")

    # [DEV] Validate the credit policy file loads on startup.
    # A missing or malformed credit_policy.json should hard-fail here,
    # not silently fall back to defaults that a compliance team hasn't approved.
    try:
        loader = get_loader()
        logger.info(f"Credit policy loaded. Industries: {list(loader._policy.get('ratio_thresholds', {}).keys())}")
    except FileNotFoundError as e:
        logger.error(f"Credit policy file not found: {e}")
        raise

    audit_log = DevAuditLog()
    approval_queue = DevApprovalQueue()
    application_store = ApplicationStore()

    orchestrator = CreditMemoOrchestrator(
        model=model,
        api_key=api_key,
        audit_log=audit_log,
        approval_queue=approval_queue,
    )

    # [DEV] Replace Stub* with real adapters here when they are ready.
    # Keep use_stub flags or environment variable gates so you can flip
    # one adapter at a time during rollout without redeploying everything.
    app.state.orchestrator = orchestrator
    app.state.audit_log = audit_log
    app.state.application_store = application_store
    app.state.kyc_repo = StubKYCRepository()          # [DEV] Replace
    app.state.osint_provider = StubOSINTProvider()    # [DEV] Replace
    app.state.financial_store = StubFinancialDataStore()  # [DEV] Replace

    logger.info(f"Credit memo pipeline ready [environment={env}, model={model}]")
    yield
    logger.info("Shutting down credit memo pipeline.")


# ─────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agentic Credit Memo Pipeline",
    description=(
        "JPMorgan-style multi-agent commercial credit underwriting pipeline. "
        "Three specialized agents (KYC/Data, OSINT, Quantitative) assemble the "
        "evidence; a Reasoning/Report Agent drafts the memo; approval_routing.py "
        "determines the correct approval tier. No credit decision is recorded "
        "without human analyst or committee sign-off."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/applications/submit", tags=["Pipeline"])
def submit_application(application_event: dict, request: Request):
    """
    Main pipeline endpoint.

    Required fields:
      applicant_legal_name, applicant_ein (XX-XXXXXXX),
      applicant_industry, loan_type, requested_amount,
      proposed_collateral_description, relationship_manager_id

    Returns pipeline status, all agent outputs, the routed approval tier,
    and the memo draft (in dev mode).
    """
    from schemas import LoanApplication, CreditContext

    try:
        application = LoanApplication(**application_event)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"error": "Validation failed.", "detail": e.errors()})

    # Pre-fetch all data before any agent runs
    kyc = request.app.state.kyc_repo.query(application.applicant_ein)
    osint = request.app.state.osint_provider.query(
        application.applicant_legal_name, application.applicant_ein
    )
    financials = request.app.state.financial_store.query(application.applicant_ein)

    context = CreditContext(application=application, kyc=kyc, osint=osint, financials=financials)

    try:
        result = request.app.state.orchestrator.run(application, context)
    except Exception as e:
        logger.exception(f"Pipeline error for {application.application_id}: {e}")
        raise HTTPException(status_code=500, detail={"error": "Pipeline failed.", "message": str(e)})

    request.app.state.application_store.save(application.application_id, result)

    return {
        "application_id": str(result.application_id),
        "status": result.status,
        "agent_outputs": result.agent_outputs,
        "escalation_reason": result.escalation_reason,
        "routing_tier": result.routing_tier,
        "routing_reason": result.routing_reason,
        "agent_recommendation": result.memo.agent_recommendation if result.memo else None,
    }


@app.post("/applications/{application_id}/decision", tags=["Pipeline"])
def record_decision(application_id: str, decision_event: dict, request: Request):
    """
    Submit the human reviewer's credit decision for a completed application.

    The reviewing officer's name, credentials, decision, and rationale are
    written permanently to the audit trail. This is the Step 9 record from
    the case study — the accountability is human, and this endpoint captures it.

    Required fields: reviewing_officer_name, reviewing_officer_credentials,
                     decision (APPROVE / DECLINE / APPROVE_WITH_MODIFIED_TERMS),
                     decision_rationale

    Returns the recorded decision so the caller can confirm it was saved.
    """
    from schemas import CreditDecision
    from uuid import UUID as _UUID

    try:
        app_uuid = _UUID(application_id)
    except ValueError:
        raise HTTPException(status_code=422, detail={"error": "Invalid application_id format."})

    stored = request.app.state.application_store.get(app_uuid)
    if stored is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Application not found.",
                "message": (
                    f"No completed pipeline found for application_id={application_id}. "
                    "Submit the application first via POST /applications/submit."
                ),
            },
        )

    try:
        decision = CreditDecision(application_id=app_uuid, **decision_event)
    except Exception as e:
        raise HTTPException(status_code=422, detail={"error": "Validation failed.", "detail": str(e)})

    request.app.state.audit_log.record_decision(app_uuid, decision)

    return {
        "application_id": application_id,
        "status": "decision_recorded",
        "reviewing_officer": decision.reviewing_officer_name,
        "decision": decision.decision,
        "decided_at": decision.decided_at.isoformat(),
    }


@app.get("/workflows/recent", tags=["Pipeline"])
def recent_workflows(request: Request, limit: int = 10):
    audit_log = getattr(request.app.state, "audit_log", None)
    if not isinstance(audit_log, DevAuditLog):
        raise HTTPException(status_code=501, detail="Only available in dev mode.")
    return {"entries": audit_log.entries[-limit:], "total": len(audit_log.entries)}


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error.", "message": str(exc)})


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        reload=os.environ.get("ENVIRONMENT", "development") == "development",
        log_level="info",
    )
