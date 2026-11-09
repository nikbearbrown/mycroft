from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

from app.agents.code_gen import generate_code
from app.agents.guardrail import check_generated_code
from app.agents.sandbox import run_in_sandbox
from app.agents.reasoner import reason_about_applicant


class PipelineState(TypedDict):
    rule_id: str
    rule_text: str
    test_cases: List[Dict[str, Any]]
    generated_code: str
    code_valid: bool
    code_error: str
    gen_model: str
    gen_temperature: float
    prompt_hash: str
    code_hash: str
    validation_results: List[Dict[str, Any]]
    simulation_results: List[Dict[str, Any]]


def _infer_fields(test_cases) -> dict:
    """Union of field names -> type across the rule's test cases. Given to the
    generator so it uses the real schema instead of guessing field names."""
    fields = {}
    for tc in test_cases:
        for k, v in (tc.get("applicant_data") or {}).items():
            if k in fields:
                continue
            if isinstance(v, bool):
                fields[k] = "boolean"
            elif isinstance(v, (int, float)):
                fields[k] = "number"
            else:
                fields[k] = "text"
    return fields


def code_gen_node(state: PipelineState) -> dict:
    """Generate the code, then run it through the guardrail. The guardrail only
    accepts or rejects — it never repairs — so a rejection becomes an honest
    'unrunnable code' outcome instead of being silently patched. Provenance
    (model, temperature, hashes) is carried forward so the run is reproducible."""
    gen = generate_code(state["rule_text"], _infer_fields(state["test_cases"]))
    code = gen["code"]
    verdict = check_generated_code(code)
    if not verdict["valid"]:
        print(f"GUARDRAIL rejected generated code: {verdict['error']}")
    return {
        "generated_code": code,
        "code_valid": verdict["valid"],
        "code_error": verdict["error"] or "",
        "gen_model": gen["model"],
        "gen_temperature": gen["temperature"],
        "prompt_hash": gen["prompt_hash"],
        "code_hash": gen["code_hash"],
    }


def validator_node(state: PipelineState) -> dict:
    """Dynamic check: runs the AI-generated code in the sandbox against each
    applicant and compares the output to the human answer key. If the guardrail
    rejected the code, execution is skipped and every case is recorded as
    'unrunnable' — a distinct, honest outcome, not a false 'no match'."""
    results = []

    if not state.get("code_valid", True):
        for tc in state["test_cases"]:
            results.append({
                "applicant_id": tc["applicant_id"],
                "oracle_expected": tc["expected_outcome"],
                "agent_observed": "unrunnable",
                "match": False,
                "rationale": f"Generated code was rejected before execution: {state.get('code_error')}",
            })
        return {"validation_results": results}

    for tc in state["test_cases"]:
        observed = run_in_sandbox(state["generated_code"], tc["applicant_data"])
        match = (observed.strip().lower() == tc["expected_outcome"].strip().lower())
        results.append({
            "applicant_id": tc["applicant_id"],
            "oracle_expected": tc["expected_outcome"],
            "agent_observed": observed,
            "match": match,
            "rationale": f"Ran generated code against {tc['applicant_id']}'s data; "
                         f"expected '{tc['expected_outcome']}', got '{observed}'."
        })
    return {"validation_results": results}


def simulator_node(state: PipelineState) -> dict:
    """Semantic check: independently reasons about each applicant from the plain-English
    rule text — it never sees the generated code. When this disagrees with the
    Validator, the code and the rule's intent have diverged."""
    results = []
    for tc in state["test_cases"]:
        prediction = reason_about_applicant(state["rule_text"], tc["applicant_data"])
        observed = prediction["outcome"]
        match = (observed.strip().lower() == tc["expected_outcome"].strip().lower())
        results.append({
            "applicant_id": tc["applicant_id"],
            "oracle_expected": tc["expected_outcome"],
            "agent_observed": observed,
            "match": match,
            "rationale": f"Reasoned from the rule (not the code) for {tc['applicant_id']}: "
                         f"{prediction['rationale']}"
        })
    return {"simulation_results": results}


def build_graph():
    """Single source of truth for the pipeline wiring: code_gen fans out to the
    validator and simulator in parallel, then both join at END."""
    graph = StateGraph(PipelineState)
    graph.add_node("code_gen", code_gen_node)
    graph.add_node("validator", validator_node)
    graph.add_node("simulator", simulator_node)

    graph.set_entry_point("code_gen")
    graph.add_edge("code_gen", "validator")
    graph.add_edge("code_gen", "simulator")
    graph.add_edge("validator", END)
    graph.add_edge("simulator", END)

    return graph.compile()
