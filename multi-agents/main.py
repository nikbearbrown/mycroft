from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.oracle import Oracle
from app.models.test_case import TestCase
from app.run_pipeline import run_for_rule
from app.models.generated_code import GeneratedCode
from app.models.check_result import CheckResult
from app.integrity import compute_oracle_hash
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174",
                   "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "alive"}

class RuleInput(BaseModel):
    rule_id: str
    rule_text: str

@app.post("/rules")
def submit_rule(rule: RuleInput, db: Session = Depends(get_db)):
    if db.query(Oracle).filter(Oracle.rule_id == rule.rule_id).first():
        raise HTTPException(status_code=409, detail=f"rule_id '{rule.rule_id}' already exists")
    # keep rules unique by TEXT too (different auto-ids for the same wording = a duplicate)
    text_norm = (rule.rule_text or "").strip().lower()
    if any((o.rule_text or "").strip().lower() == text_norm for o in db.query(Oracle).all()):
        raise HTTPException(status_code=409, detail="a rule with this text already exists")
    new_oracle = Oracle(rule_id=rule.rule_id, rule_text=rule.rule_text)
    db.add(new_oracle)
    db.commit()
    db.refresh(new_oracle)
    return {"id": new_oracle.id, "rule_id": new_oracle.rule_id, "rule_text": new_oracle.rule_text}
@app.get("/rules")
def list_rules(db: Session = Depends(get_db)):
    rules = db.query(Oracle).all()
    output = []
    for r in rules:
        latest_code = (
            db.query(GeneratedCode)
            .filter(GeneratedCode.oracle_id == r.id)
            .order_by(GeneratedCode.id.desc())
            .first()
        )
        output.append({
            "id": r.id,
            "rule_id": r.rule_id,
            "rule_text": r.rule_text,
            "status": latest_code.status if latest_code else "draft",
            "frozen": r.frozen,
            "frozen_at": str(r.frozen_at) if r.frozen_at else None,
        })
    return output


@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    """Delete a rule and everything under it (test cases, generated code, results)."""
    oracle = db.query(Oracle).filter(Oracle.rule_id == rule_id).first()
    if not oracle:
        raise HTTPException(status_code=404, detail="rule not found")

    codes = db.query(GeneratedCode).filter(GeneratedCode.oracle_id == oracle.id).all()
    for gc in codes:
        db.query(CheckResult).filter(CheckResult.generated_code_id == gc.id).delete()
    db.query(GeneratedCode).filter(GeneratedCode.oracle_id == oracle.id).delete()
    db.query(TestCase).filter(TestCase.oracle_id == oracle.id).delete()
    db.delete(oracle)
    db.commit()
    return {"deleted": rule_id}


@app.post("/rules/{rule_id}/freeze")
def freeze_oracle(rule_id: str, db: Session = Depends(get_db)):
    """Lock the answer key. After this, no test case can be added or edited for
    this oracle, and only now may code-gen run against it. We store a hash of the
    exact frozen content so any later tampering is detectable."""
    oracle = db.query(Oracle).filter(Oracle.rule_id == rule_id).first()
    if not oracle:
        raise HTTPException(status_code=404, detail="rule not found")
    if oracle.frozen:
        raise HTTPException(status_code=409, detail="oracle is already frozen")

    test_cases = db.query(TestCase).filter(TestCase.oracle_id == oracle.id).all()
    if not test_cases:
        raise HTTPException(status_code=400, detail="cannot freeze an oracle with no test cases")

    # Any generation that predates this freeze is invalid — clear it so the user
    # starts Step 2 fresh against the locked answer key (no stale results).
    codes = db.query(GeneratedCode).filter(GeneratedCode.oracle_id == oracle.id).all()
    for gc in codes:
        db.query(CheckResult).filter(CheckResult.generated_code_id == gc.id).delete()
    db.query(GeneratedCode).filter(GeneratedCode.oracle_id == oracle.id).delete()

    oracle.oracle_hash = compute_oracle_hash(oracle.rule_text, test_cases)
    oracle.frozen = True
    oracle.frozen_at = datetime.utcnow()
    db.commit()
    return {
        "rule_id": rule_id,
        "frozen": True,
        "frozen_at": str(oracle.frozen_at),
        "oracle_hash": oracle.oracle_hash,
        "test_case_count": len(test_cases),
    }


@app.post("/rules/{rule_id}/unfreeze")
def unfreeze_oracle(rule_id: str, db: Session = Depends(get_db)):
    """Unlock so the rule/examples can be edited again. This discards the current
    AI results (they were tested against the now-old answer key), so the next
    round is still an honest 'answers committed before code' experiment."""
    oracle = db.query(Oracle).filter(Oracle.rule_id == rule_id).first()
    if not oracle:
        raise HTTPException(status_code=404, detail="rule not found")
    if not oracle.frozen:
        raise HTTPException(status_code=409, detail="oracle is not frozen")

    codes = db.query(GeneratedCode).filter(GeneratedCode.oracle_id == oracle.id).all()
    for gc in codes:
        db.query(CheckResult).filter(CheckResult.generated_code_id == gc.id).delete()
    db.query(GeneratedCode).filter(GeneratedCode.oracle_id == oracle.id).delete()

    oracle.frozen = False
    oracle.frozen_at = None
    oracle.oracle_hash = None
    db.commit()
    return {"rule_id": rule_id, "frozen": False}


class RuleTextInput(BaseModel):
    rule_text: str


@app.patch("/rules/{rule_id}")
def edit_rule_text(rule_id: str, payload: RuleTextInput, db: Session = Depends(get_db)):
    """Edit a rule's wording. Only allowed while unfrozen (a locked answer key
    can't be changed). Keeps text unique."""
    oracle = db.query(Oracle).filter(Oracle.rule_id == rule_id).first()
    if not oracle:
        raise HTTPException(status_code=404, detail="rule not found")
    if oracle.frozen:
        raise HTTPException(status_code=409, detail="oracle is frozen — unlock it before editing the rule")

    text_norm = (payload.rule_text or "").strip().lower()
    if not text_norm:
        raise HTTPException(status_code=400, detail="rule text cannot be empty")
    clash = [o for o in db.query(Oracle).all()
             if o.id != oracle.id and (o.rule_text or "").strip().lower() == text_norm]
    if clash:
        raise HTTPException(status_code=409, detail="a rule with this text already exists")

    oracle.rule_text = payload.rule_text.strip()
    db.commit()
    return {"rule_id": rule_id, "rule_text": oracle.rule_text}


@app.post("/run/{rule_id}")
def trigger_run(rule_id: str, db: Session = Depends(get_db)):
    oracle = db.query(Oracle).filter(Oracle.rule_id == rule_id).first()
    if not oracle:
        raise HTTPException(status_code=404, detail="rule not found")
    if not oracle.frozen:
        raise HTTPException(
            status_code=409,
            detail="oracle is not frozen — freeze the answer key before generating code",
        )
    run_for_rule(rule_id)
    return {"status": "completed", "rule_id": rule_id}

@app.get("/results/{rule_id}")
def get_results(rule_id: str, db: Session = Depends(get_db)):
    oracle = db.query(Oracle).filter(Oracle.rule_id == rule_id).first()
    if not oracle:
        return {"error": "rule not found"}

    latest_code = (
        db.query(GeneratedCode)
        .filter(GeneratedCode.oracle_id == oracle.id)
        .order_by(GeneratedCode.id.desc())
        .first()
    )
    if not latest_code:
        return {"rule_id": rule_id, "generated_code": None, "results": []}

    results = db.query(CheckResult).filter(CheckResult.generated_code_id == latest_code.id).all()

    return {
        "rule_id": rule_id,
        "status": latest_code.status,
        "generated_code": latest_code.source_code,
        "code_valid": latest_code.code_valid,
        "code_error": latest_code.code_error,
        "model": latest_code.model,
        "binding_proof": latest_code.binding_proof,
        "results": [
            {
                "check_type": r.check_type,
                "applicant_id": r.applicant_id,
                "oracle_expected": r.oracle_expected,
                "agent_observed": r.agent_observed,
                "match": r.match,
                "rationale": r.rationale,
            }
            for r in results
        ],
    }
class TestCaseInput(BaseModel):
    oracle_id: int
    applicant_id: str
    applicant_data: dict
    expected_outcome: str
    author_rationale: str = ""

@app.post("/test-cases")
def submit_test_case(test_case: TestCaseInput, db: Session = Depends(get_db)):
    oracle = db.query(Oracle).filter(Oracle.id == test_case.oracle_id).first()
    if not oracle:
        raise HTTPException(status_code=404, detail="oracle not found")
    if oracle.frozen:
        raise HTTPException(
            status_code=409,
            detail="oracle is frozen — its answer key is locked and cannot be changed",
        )

    new_test_case = TestCase(
        oracle_id=test_case.oracle_id,
        applicant_id=test_case.applicant_id,
        applicant_data=test_case.applicant_data,
        expected_outcome=test_case.expected_outcome,
        author_rationale=test_case.author_rationale,
    )
    db.add(new_test_case)
    db.commit()
    db.refresh(new_test_case)
    return {
        "id": new_test_case.id,
        "oracle_id": new_test_case.oracle_id,
        "applicant_id": new_test_case.applicant_id,
    }


@app.get("/test-cases/{rule_id}")
def list_test_cases(rule_id: str, db: Session = Depends(get_db)):
    oracle = db.query(Oracle).filter(Oracle.rule_id == rule_id).first()
    if not oracle:
        return {"error": "rule not found"}
    cases = db.query(TestCase).filter(TestCase.oracle_id == oracle.id).all()
    return [
        {
            "id": c.id,
            "applicant_id": c.applicant_id,
            "applicant_data": c.applicant_data,
            "expected_outcome": c.expected_outcome,
            "author_rationale": c.author_rationale,
        }
        for c in cases
    ]


@app.delete("/test-cases/{test_case_id}")
def delete_test_case(test_case_id: int, db: Session = Depends(get_db)):
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not tc:
        raise HTTPException(status_code=404, detail="test case not found")
    oracle = db.query(Oracle).filter(Oracle.id == tc.oracle_id).first()
    if oracle and oracle.frozen:
        raise HTTPException(status_code=409, detail="oracle is frozen — the answer key is locked")
    db.delete(tc)
    db.commit()
    return {"deleted": test_case_id}



class DecisionInput(BaseModel):
    decision: str  # "approved", "rejected", or "in_review"

@app.post("/decision/{rule_id}")
def record_decision(rule_id: str, payload: DecisionInput, db: Session = Depends(get_db)):
    oracle = db.query(Oracle).filter(Oracle.rule_id == rule_id).first()
    if not oracle:
        return {"error": "rule not found"}

    latest_code = (
        db.query(GeneratedCode)
        .filter(GeneratedCode.oracle_id == oracle.id)
        .order_by(GeneratedCode.id.desc())
        .first()
    )
    if not latest_code:
        return {"error": "no generated code to decide on"}

    if payload.decision not in ("approved", "rejected", "in_review"):
        return {"error": "invalid decision"}

    latest_code.status = payload.decision
    latest_code.decided_at = datetime.utcnow()
    db.commit()

    return {"rule_id": rule_id, "status": latest_code.status, "decided_at": str(latest_code.decided_at)}
