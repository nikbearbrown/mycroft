from fastapi import FastAPI, HTTPException
from app.models import ClaimPayload, VerificationResponse
from app.retrieval import retrieve_candidates

app = FastAPI(title="Mycroft Provenance Gatekeeper", version="0.1.0")

@app.post("/verify", response_model=VerificationResponse)
async def verify_claim(payload: ClaimPayload):
    """
    Intercepts an AI claim from the n8n Orchestrator, runs candidate retrieval, 
    and adjudicates the entailment.
    """
    try:
        # Stage 1: Retrieve candidate text chunks
        candidates = retrieve_candidates(payload.claim_text)
        
        # TODO for Week 2/3: Stage 2 NLI & Numeric Adjudication goes here.
        # For now, we simulate the strict threshold. If it's not a perfect match, we quarantine.
        
        # Simulating a failure closed state for safety
        return VerificationResponse(
            original_claim=payload.claim_text,
            verification_status="Quarantined",
            source_citation_url=None
        )
        
    except Exception as e:
        # Non-2xx response tells n8n there was an infrastructure failure
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "active", "stage": "retrieval_configured"}