"""Small, focused tests for the thesis-critical logic:
the guardrail, the tamper-evident hashes, and the freeze gate.
Run with:  python -m pytest tests/ -q
"""
from app.agents.guardrail import check_generated_code
from app.integrity import compute_oracle_hash, compute_binding_proof


class _TC:
    def __init__(self, a, d, e, r=""):
        self.applicant_id = a
        self.applicant_data = d
        self.expected_outcome = e
        self.author_rationale = r


# --- guardrail: reject, never repair ---

def test_guardrail_accepts_valid():
    assert check_generated_code("def check_applicant(applicant_data):\n    return 'approve'")["valid"]

def test_guardrail_rejects_fenced_text():
    assert not check_generated_code("```python\ndef check_applicant(d):\n    return 'approve'\n```")["valid"]

def test_guardrail_rejects_missing_function():
    assert not check_generated_code("x = 1")["valid"]

def test_guardrail_rejects_wrong_arity():
    assert not check_generated_code("def check_applicant():\n    return 'x'")["valid"]


# --- integrity hashes ---

def test_oracle_hash_is_order_independent():
    cases = [_TC("raj", {"x": 1}, "deny"), _TC("mae", {"x": 2}, "approve")]
    assert compute_oracle_hash("rule", cases) == compute_oracle_hash("rule", list(reversed(cases)))

def test_oracle_hash_changes_on_edit():
    cases = [_TC("raj", {"x": 1}, "deny")]
    assert compute_oracle_hash("rule", cases) != compute_oracle_hash("rule-edited", cases)

def test_binding_proof_changes_with_results():
    b1 = compute_binding_proof("hash", [{"match": True}], [{"match": True}])
    b2 = compute_binding_proof("hash", [{"match": False}], [{"match": True}])
    assert b1 != b2


# --- freeze gate (uses the app + DB; creates and cleans up a temp rule) ---

def test_freeze_gate_end_to_end():
    from fastapi.testclient import TestClient
    import main
    from app.db.database import SessionLocal
    from app.models.oracle import Oracle
    from app.models.test_case import TestCase

    c = TestClient(main.app)
    rid = "_pytest_freeze_gate"

    def _cleanup():
        db = SessionLocal()
        o = db.query(Oracle).filter(Oracle.rule_id == rid).first()
        if o:
            db.query(TestCase).filter(TestCase.oracle_id == o.id).delete()
            db.delete(o); db.commit()
        db.close()

    _cleanup()
    try:
        oid = c.post("/rules", json={"rule_id": rid, "rule_text": "t"}).json()["id"]
        assert c.post(f"/run/{rid}").status_code == 409          # cannot run unfrozen
        assert c.post("/test-cases", json={"oracle_id": oid, "applicant_id": "a1",
                      "applicant_data": {"x": 1}, "expected_outcome": "approve"}).status_code == 200
        assert c.post(f"/rules/{rid}/freeze").status_code == 200  # freeze OK
        assert c.post("/test-cases", json={"oracle_id": oid, "applicant_id": "a2",
                      "applicant_data": {"x": 2}, "expected_outcome": "deny"}).status_code == 409  # locked
    finally:
        _cleanup()
