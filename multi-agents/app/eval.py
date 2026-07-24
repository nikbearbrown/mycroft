"""Simple multi-run reliability eval.

Runs one frozen rule through the pipeline N times. Each run regenerates the code
fresh (an independent roll, since the model is non-deterministic) and we report
how often the AI's code matched the human answer key. One run is an anecdote;
N runs is a measurement — e.g. "the compound rule passed 6/10 runs."

Read-only: this does NOT write to the database.

Usage:  python -m app.eval <rule_id> [N]
"""
import sys
from statistics import pstdev

from app.db.database import SessionLocal
from app.models.oracle import Oracle
from app.models.test_case import TestCase
from app.agents.graph import build_graph


def _initial_state(oracle, tcs):
    return {
        "rule_id": oracle.rule_id,
        "rule_text": oracle.rule_text,
        "test_cases": tcs,
        "generated_code": "",
        "code_valid": True,
        "code_error": "",
        "gen_model": "",
        "gen_temperature": 0.0,
        "prompt_hash": "",
        "code_hash": "",
        "validation_results": [],
        "simulation_results": [],
    }


def run_eval(rule_id: str, n: int = 10):
    db = SessionLocal()
    oracle = db.query(Oracle).filter(Oracle.rule_id == rule_id).first()
    if not oracle:
        print(f"No oracle for rule_id={rule_id}"); db.close(); return
    if not oracle.frozen:
        print(f"HALT: '{rule_id}' is not frozen. Freeze it before evaluating."); db.close(); return

    test_cases = db.query(TestCase).filter(TestCase.oracle_id == oracle.id).all()
    tcs = [{"applicant_id": t.applicant_id, "applicant_data": t.applicant_data,
            "expected_outcome": t.expected_outcome} for t in test_cases]
    db.close()

    total = len(tcs)
    graph = build_graph()
    case_rates = []      # fraction of cases the code got right, per run
    unrunnable = 0
    full_pass = 0        # runs where code matched EVERY case

    print(f"\nEvaluating '{rule_id}'  ({total} cases x {n} runs)\n")
    for i in range(1, n + 1):
        r = graph.invoke(_initial_state(oracle, tcs))
        if not r.get("code_valid", True):
            unrunnable += 1
            case_rates.append(0.0)
            print(f"  run {i:>2}: code UNRUNNABLE ({r.get('code_error')})")
            continue
        matches = sum(1 for x in r["validation_results"] if x["match"])
        case_rates.append(matches / total)
        if matches == total:
            full_pass += 1
        print(f"  run {i:>2}: code matched {matches}/{total}")

    avg = sum(case_rates) / len(case_rates)
    print("\n--- summary ---")
    print(f"  full-pass runs  : {full_pass}/{n}  (code matched every case)")
    print(f"  avg case match  : {avg:.0%}")
    print(f"  variance (stdev): {pstdev(case_rates):.2f}")
    print(f"  unrunnable runs : {unrunnable}/{n}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python -m app.eval <rule_id> [N]")
    else:
        run_eval(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10)
