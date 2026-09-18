from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
import openai # or anthropic, depending on your evaluation LLM
import os

app = FastAPI(title="Provenance Gatekeeper")

# 1. Initialize Week 2 Infrastructure (Embeddings & DB)
model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="financial_ledger")

# 2. Define n8n Payload Schemas
class ClaimRequest(BaseModel):
    claim_id: str
    generated_claim: str

class VerificationVerdict(BaseModel):
    claim_id: str
    verdict: str
    variance_type: str
    ground_truth: str
    explanation: str

# 3. Evaluation Logic (Week 3 core)
def evaluate_variance(claim: str, ledger_truth: str) -> dict:
    """
    Compares the AI claim against the ground truth using a strict grading prompt.
    Categorizes errors into Magnitude, Directional, or Supported.
    """
    prompt = f"""
    You are a strict financial auditor. Compare the AI-generated claim against the Ground Truth Ledger.
    
    AI Claim: "{claim}"
    Ground Truth: "{ledger_truth}"
    
    Categorize the variance as one of the following:
    - SUPPORTED: The claim perfectly matches the truth.
    - MAGNITUDE ERROR: The direction is right, but the numbers are wrong.
    - DIRECTIONAL ERROR: The numbers might match, but the trend (increase/decrease) is inverted.
    
    Respond in JSON format: {{"verdict": "PASS/FAIL", "variance_type": "...", "explanation": "..."}}
    """
    
    # Example using a lightweight LLM call for the evaluation reasoning
    # response = openai.ChatCompletion.create(
    #     model="gpt-4o-mini", # or local LLM
    #     messages=[{"role": "system", "content": prompt}]
    # )
    # return parse_json(response)
    
    # Mocked logic for structural demonstration
    if "decreased" in claim.lower() and "grew" in ledger_truth.lower():
        return {"verdict": "FAIL", "variance_type": "Directional Error", "explanation": "Claim states decrease, ledger states growth."}
    return {"verdict": "FAIL", "variance_type": "Magnitude Error", "explanation": "Numerical mismatch detected."}

# 4. The n8n Intercept Endpoint
@app.post("/verify", response_model=VerificationVerdict)
async def verify_claim(request: ClaimRequest):
    try:
        # Step 1: Retrieve context from ChromaDB (Week 2 logic)
        claim_embedding = model.encode(request.generated_claim).tolist()
        results = collection.query(
            query_embeddings=[claim_embedding],
            n_results=1
        )
        
        if not results['documents'][0]:
            raise HTTPException(status_code=404, detail="No relevant ground truth found in ledger.")
            
        ground_truth = results['documents'][0][0]
        
        # Step 2: Generate the Verdict (Week 3 logic)
        evaluation = evaluate_variance(request.generated_claim, ground_truth)
        
        # Step 3: Return the structured loop back to n8n
        return VerificationVerdict(
            claim_id=request.claim_id,
            verdict=evaluation["verdict"],
            variance_type=evaluation["variance_type"],
            ground_truth=ground_truth,
            explanation=evaluation["explanation"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))