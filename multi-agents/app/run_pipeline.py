from app.db.database import SessionLocal
from app.models.oracle import Oracle
from app.models.test_case import TestCase
from app.models.generated_code import GeneratedCode
from app.models.check_result import CheckResult
from app.agents.graph import build_graph
from app.integrity import compute_binding_proof


def run_for_rule(rule_id: str):
    db = SessionLocal()
    try:
        # 1. Fetch the rule + its test cases from Postgres
        oracle = db.query(Oracle).filter(Oracle.rule_id == rule_id).first()
        if not oracle:
            print(f"No oracle found for rule_id={rule_id}")
            return

        # Freeze gate: code-gen may only run against a locked answer key.
        # Hard halt, no retry (missing precondition).
        if not oracle.frozen:
            print(f"HALT: oracle for rule_id={rule_id} is not frozen. "
                  f"Freeze the answer key before generating code.")
            return

        test_cases = db.query(TestCase).filter(TestCase.oracle_id == oracle.id).all()
        if not test_cases:
            print(f"No test cases found for oracle_id={oracle.id}")
            return

        # Convert DB rows into plain dicts the graph expects
        test_case_dicts = [
            {
                "applicant_id": tc.applicant_id,
                "applicant_data": tc.applicant_data,
                "expected_outcome": tc.expected_outcome,
            }
            for tc in test_cases
        ]

        # 2. Run the LangGraph pipeline
        compiled = build_graph()
        result = compiled.invoke({
            "rule_id": oracle.rule_id,
            "rule_text": oracle.rule_text,
            "test_cases": test_case_dicts,
            "generated_code": "",
            "code_valid": True,
            "code_error": "",
            "gen_model": "",
            "gen_temperature": 0.0,
            "prompt_hash": "",
            "code_hash": "",
            "validation_results": [],
            "simulation_results": [],
        })

        # 3. Save generated code (with provenance + guardrail verdict) back to Postgres
        new_code = GeneratedCode(
            oracle_id=oracle.id,
            source_code=result["generated_code"],
            generation_rationale=f"Generated from rule_text: {oracle.rule_text}",
            model=result.get("gen_model"),
            temperature=result.get("gen_temperature"),
            prompt_hash=result.get("prompt_hash"),
            code_hash=result.get("code_hash"),
            code_valid=result.get("code_valid"),
            code_error=result.get("code_error") or None,
            binding_proof=compute_binding_proof(
                result.get("code_hash"),
                result["validation_results"],
                result["simulation_results"],
            ),
        )
        db.add(new_code)
        db.commit()
        db.refresh(new_code)

        # 4. Save validation + simulation results back to Postgres
        for r in result["validation_results"]:
            db.add(CheckResult(
                generated_code_id=new_code.id,
                check_type="validation",
                applicant_id=r["applicant_id"],
                oracle_expected=r["oracle_expected"],
                agent_observed=r["agent_observed"],
                match=r["match"],
                rationale=r["rationale"],
            ))

        for r in result["simulation_results"]:
            db.add(CheckResult(
                generated_code_id=new_code.id,
                check_type="simulation",
                applicant_id=r["applicant_id"],
                oracle_expected=r["oracle_expected"],
                agent_observed=r["agent_observed"],
                match=r["match"],
                rationale=r["rationale"],
            ))

        db.commit()

        print(f"Done. generated_code id={new_code.id}, "
              f"{len(result['validation_results'])} validation results, "
              f"{len(result['simulation_results'])} simulation results saved.")

    finally:
        db.close()


if __name__ == "__main__":
    rule_ids = [
        "dti_43",
        "loan_over_50k",
        "credit_score_750",
        "recent_late_payment",
        "compound_income_credit_debt",
    ]
    for rule_id in rule_ids:
        print(f"\n=== Running rule: {rule_id} ===")
        run_for_rule(rule_id)
