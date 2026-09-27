"""
api/main.py

FastAPI wrapper around the workflow, for readers who want to call this as
a service rather than through the CLI. Run with:

    uvicorn api.main:app --reload

Two endpoints, matching the two-phase design (autonomous pipeline, then
human checkpoint):
  POST /claims/{scenario_name}/run     -> runs the pipeline, returns Audit summary
  POST /claims/{claim_id}/review       -> submits a human decision, executes payout if approved

[DEV] EXTENSION POINT: this API only exposes the 3 stub scenarios by name,
not arbitrary claim submission — wire a real intake endpoint here if
you're adapting this beyond the reference scenarios.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import WorkflowConfig, ConfigError
from providers import get_provider
from workflow.orchestrator import NemoOrchestrator, WorkflowHaltedError, WorkflowResult
from workflow.payout_gate import HumanReviewSystem, PayoutExecutionAPI
from data.stub_scenarios import ALL_SCENARIOS

app = FastAPI(title="Project Nemo Reference Workflow")

# [DEV] In-memory state for demo purposes only — a real service would
# persist pending results and issued tokens, not hold them in process memory.
_pending_results: dict = {}
_review_system = HumanReviewSystem()
_payout_api = PayoutExecutionAPI()


class ReviewRequest(BaseModel):
    approved: bool
    reviewer_id: str = "api-reviewer"


def _get_orchestrator() -> NemoOrchestrator:
    try:
        config = WorkflowConfig.from_env()
        provider = get_provider(config)
    except ConfigError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return NemoOrchestrator(provider, threshold_aud=config.threshold_aud)


@app.post("/claims/{scenario_name}/run")
def run_claim(scenario_name: str):
    if scenario_name not in ALL_SCENARIOS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown scenario '{scenario_name}'. Options: {list(ALL_SCENARIOS.keys())}",
        )

    scenario = ALL_SCENARIOS[scenario_name]
    orchestrator = _get_orchestrator()

    try:
        result = orchestrator.run(
            scenario.raw_claim_event,
            scenario.policy_record,
            scenario.meteorological_data,
            scenario.claim_history_summary,
        )
    except WorkflowHaltedError as e:
        return {"status": "halted", "stage": e.stage, "reason": e.reason}

    _pending_results[result.claim_id] = result
    return {
        "status": result.status,
        "claim_id": result.claim_id,
        "audit_summary": result.audit_summary,
        "recommended_amount_aud": result.recommended_amount_aud,
    }


@app.post("/claims/{claim_id}/review")
def review_claim(claim_id: str, review: ReviewRequest):
    result = _pending_results.get(claim_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No pending result for claim_id='{claim_id}'.")

    token = _review_system.submit_decision(claim_id, review.approved, review.reviewer_id)

    if not review.approved:
        return {"status": "declined", "claim_id": claim_id}

    confirmation = _payout_api.execute_payout(claim_id, result.recommended_amount_aud, token)
    return {"status": "executed", "claim_id": claim_id, "confirmation": confirmation}
