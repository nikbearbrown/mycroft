from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.oracle import Oracle
from app.models.test_case import TestCase
from app.run_pipeline import run_for_rule
from app.models.generated_code import GeneratedCode
from app.models.check_result import CheckResult
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
        })
    return output

@app.post("/run/{rule_id}")
def trigger_run(rule_id: str):
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
            "applicant_id": c.applicant_id,
            "applicant_data": c.applicant_data,
            "expected_outcome": c.expected_outcome,
            "author_rationale": c.author_rationale,
        }
        for c in cases
    ]



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
