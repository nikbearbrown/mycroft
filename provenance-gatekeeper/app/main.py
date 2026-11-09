from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
import sqlite3
import requests
import os
import re
from datetime import timedelta

# Auth imports
from .auth import Token, User, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, FAKE_USERS_DB, verify_password
from . import dashboard

app = FastAPI(title="Provenance Gatekeeper")

app.include_router(dashboard.router)

# --- WEEK 1 & 2: Infrastructure & Data ---
model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="financial_ledger")

# --- WEEK 4: Tracking Log Initialization ---
def init_db():
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

# --- WEEK 6: Regex & Semantic Normalization ---
def parse_financial_number(text: str) -> float | None:
    """Extracts and normalizes numbers from messy string outputs (e.g. $4.5M -> 4500000.0)"""
    if not text or text.lower() in ["null", "n/a", "none"]:
        return None
        
    # Standardize phrasing
    text = text.lower().replace(',', '')
    text = text.replace('million', 'm').replace('billion', 'b').replace('thousand', 'k')
    
    # Extract the core number and optional suffix
    match = re.search(r'[-+]?\d*\.?\d+\s*[kmb]?', text)
    if not match:
        return None
        
    val_str = match.group(0).strip()
    
    multiplier = 1
    if val_str.endswith('m'):
        multiplier = 1_000_000
        val_str = val_str[:-1]
    elif val_str.endswith('k'):
        multiplier = 1_000
        val_str = val_str[:-1]
    elif val_str.endswith('b'):
        multiplier = 1_000_000_000
        val_str = val_str[:-1]
        
    try:
        return float(val_str) * multiplier
    except ValueError:
        return None

def evaluate_variance(claim: str, ledger_truth: str) -> dict:
    """Upgraded evaluation using deterministic float normalization."""
    # 1. Parse both sides
    claim_val = parse_financial_number(claim)
    truth_val = parse_financial_number(ledger_truth)
    
    # 2. Trap malformed text hallucinations and SQL injections
    if claim_val is None:
        return {"verdict": "FAIL", "variance_type": "Data Type Error", "explanation": "Payload contains no valid financial data."}
    if truth_val is None:
        return {"verdict": "ERROR", "variance_type": "Ledger Error", "explanation": "Ground truth is not a valid number."}
        
    # 3. Directional check (e.g., model claims decrease when truth is growth)
    if "decreased" in claim.lower() and "grew" in ledger_truth.lower():
        return {"verdict": "FAIL", "variance_type": "Directional Error", "explanation": "Claim states decrease, ledger states growth."}
        
    # 4. Magnitude validation
    if claim_val != truth_val:
         return {"verdict": "FAIL", "variance_type": "Magnitude Error", "explanation": f"Numerical mismatch: Extracted {claim_val} vs Truth {truth_val}"}
         
    return {"verdict": "PASS", "variance_type": "Supported", "explanation": "Claim matches ground truth magnitude."}

# --- WEEK 4: Logging & Alerting Functions ---
def log_evaluation(claim_id: str, generated_claim: str, verdict: str, variance_type: str):
    conn = sqlite3.connect("gatekeeper_logs.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO evaluation_logs (claim_id, generated_claim, verdict, variance_type) VALUES (?, ?, ?, ?)",
        (claim_id, generated_claim, verdict, variance_type)
    )
    conn.commit()
    conn.close()

def trigger_alert(claim_id: str, variance_type: str, explanation: str):
    webhook_url = os.getenv("ALERT_WEBHOOK_URL", "http://n8n:5678/webhook/hallucination-alert")
    
    # Send the exact JSON keys that n8n is waiting for
    payload = {
        "claim_id": claim_id,
        "variance_type": variance_type,
        "explanation": explanation
    }
    
    try:
        # Actually fire the HTTP POST request to the n8n container
        requests.post(webhook_url, json=payload, timeout=5)
        print(f"REAL ALERT SENT to {webhook_url}: {payload}")
    except Exception as e:
        print(f"Failed to trigger external alert: {e}")

# --- WEEK 8: AUTHENTICATION ENDPOINT ---
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = FAKE_USERS_DB.get(form_data.username)
    if not user_dict or not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_dict["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- THE N8N WEBHOOK (PROTECTED) ---
@app.post("/verify", response_model=VerificationVerdict)
def verify_claim(request: ClaimRequest, current_user: User = Depends(get_current_user)):
    try:
        claim_embedding = model.encode(request.generated_claim).tolist()
        results = collection.query(query_embeddings=[claim_embedding], n_results=1)
        
        if not results['documents'][0]:
            raise HTTPException(status_code=404, detail="No relevant ground truth found in ledger.")
            
        ground_truth = results['documents'][0][0]
        evaluation = evaluate_variance(request.generated_claim, ground_truth)
        
        log_evaluation(
            claim_id=request.claim_id, 
            generated_claim=request.generated_claim, 
            verdict=evaluation["verdict"], 
            variance_type=evaluation["variance_type"]
        )
        
        if evaluation["verdict"] == "FAIL":
            trigger_alert(request.claim_id, evaluation["variance_type"], evaluation["explanation"])
        
        return VerificationVerdict(
            claim_id=request.claim_id,
            verdict=evaluation["verdict"],
            variance_type=evaluation["variance_type"],
            ground_truth=ground_truth,
            explanation=evaluation["explanation"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))