"""Pre-execution guardrail for AI-generated code.

This is a REJECT-NEVER-REPAIR check. It statically inspects the code the model
produced and decides whether it is safe/valid to execute — but it never edits
the code. The moment a guardrail rewrites the model's output we stop testing
the model and start testing ourselves, which would undermine the whole thesis.

A rejection is therefore a legitimate, honest outcome ("the AI produced
unrunnable code"), reported as such rather than silently patched.
"""
import ast

REQUIRED_FUNC = "check_applicant"


def check_generated_code(code: str) -> dict:
    """Return {"valid": bool, "error": str|None}.

    Checks, in order:
      1. non-empty
      2. parses as Python (catches the stray-``` / partial-output case)
      3. defines a top-level function `check_applicant`
      4. that function takes exactly one argument
      5. that function has at least one return statement
    """
    if not code or not code.strip():
        return {"valid": False, "error": "empty code"}

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"valid": False, "error": f"does not parse: {e.msg} (line {e.lineno})"}

    func = next(
        (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == REQUIRED_FUNC),
        None,
    )
    if func is None:
        return {"valid": False, "error": f"no function named {REQUIRED_FUNC}() is defined"}

    if len(func.args.args) != 1:
        return {"valid": False, "error": f"{REQUIRED_FUNC}() must take exactly one argument"}

    if not any(isinstance(n, ast.Return) for n in ast.walk(func)):
        return {"valid": False, "error": f"{REQUIRED_FUNC}() has no return statement"}

    return {"valid": True, "error": None}


if __name__ == "__main__":
    samples = {
        "good": "def check_applicant(applicant_data):\n    return 'approve'",
        "fenced": "```python\ndef check_applicant(applicant_data):\n    return 'approve'\n```",
        "no func": "x = 1",
        "wrong args": "def check_applicant():\n    return 'approve'",
    }
    for name, code in samples.items():
        print(name, "->", check_generated_code(code))
