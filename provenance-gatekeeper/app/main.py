from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
import sqlite3
import requests
import os

app = FastAPI(title="Provenance Gatekeeper")

# --- WEEK 1 & 2: Infrastructure & Data ---
model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="financial_ledger")

# --- WEEK 4: Tracking Log Initialization ---
def init_db():
    """Creates a local SQLite database to permanently log all claim verifications."""
    conn = sqlite3.connect("gatekeeper_logs.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id TEXT,
            generated_claim TEXT,
            verdict TEXT,
            variance_type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- SCHEMAS ---
class ClaimRequest(BaseModel):
    claim_id: str
    generated_claim: str

class VerificationVerdict(BaseModel):
    claim_id: str
    verdict: str
    variance_type: str
    ground_truth: str
    explanation: str

# --- WEEK 3: Evaluation Logic ---
def evaluate_variance(claim: str, ledger_truth: str) -> dict:
    if "decreased" in claim.lower() and "grew" in ledger_truth.lower():
        return {"verdict": "FAIL", "variance_type": "Directional Error", "explanation": "Claim states decrease, ledger states growth."}
    if claim != ledger_truth:
         return {"verdict": "FAIL", "variance_type": "Magnitude Error", "explanation": "Numerical mismatch detected."}
    return {"verdict": "PASS", "variance_type": "Supported", "explanation": "Claim matches ground truth."}

# --- WEEK 4: Logging & Alerting Functions ---
def log_evaluation(claim_id: str, generated_claim: str, verdict: str, variance_type: str):
    """Saves the outcome to the permanent tracking log."""
    conn = sqlite3.connect("gatekeeper_logs.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO evaluation_logs (claim_id, generated_claim, verdict, variance_type) VALUES (?, ?, ?, ?)",
        (claim_id, generated_claim, verdict, variance_type)
    )
    conn.commit()
    conn.close()

def trigger_alert(claim_id: str, variance_type: str, explanation: str):
    """Sends an immediate external notification when a hallucination is caught."""
    # Example: Slack/Discord/Teams Webhook URL
    webhook_url = os.getenv("ALERT_WEBHOOK_URL", "https://mock-webhook-url.com/alert")
    
    payload = {
        "text": f"🚨 **Gatekeeper Alert: Hallucination Intercepted!**\n*Claim ID:* {claim_id}\n*Type:* {variance_type}\n*Details:* {explanation}"
    }
    
    try:
        # In a real environment, this pushes the alert payload to your messaging platform
        # requests.post(webhook_url, json=payload)
        print(f"ALERT SENT to {webhook_url}: {payload}")
    except Exception as e:
        print(f"Failed to trigger external alert: {e}")

# --- THE N8N WEBHOOK ---
@app.post("/verify", response_model=VerificationVerdict)
async def verify_claim(request: ClaimRequest):
    try:
        # 1. Retrieve
        claim_embedding = model.encode(request.generated_claim).tolist()
        results = collection.query(query_embeddings=[claim_embedding], n_results=1)
        
        if not results['documents'][0]:
            raise HTTPException(status_code=404, detail="No relevant ground truth found in ledger.")
            
        ground_truth = results['documents'][0][0]
        
        # 2. Evaluate
        evaluation = evaluate_variance(request.generated_claim, ground_truth)
        
        # 3. Log (Week 4)
        log_evaluation(
            claim_id=request.claim_id, 
            generated_claim=request.generated_claim, 
            verdict=evaluation["verdict"], 
            variance_type=evaluation["variance_type"]
        )
        
        # 4. Alert (Week 4)
        if evaluation["verdict"] == "FAIL":
            trigger_alert(request.claim_id, evaluation["variance_type"], evaluation["explanation"])
        
        # 5. Respond
        return VerificationVerdict(
            claim_id=request.claim_id,
            verdict=evaluation["verdict"],
            variance_type=evaluation["variance_type"],
            ground_truth=ground_truth,
            explanation=evaluation["explanation"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))