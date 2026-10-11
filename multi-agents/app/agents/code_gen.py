import os
import re
from dotenv import load_dotenv
from anthropic import Anthropic

from app.integrity import sha256_text

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-5"
TEMPERATURE = 1.0   # explicit + recorded; non-zero keeps each run an independent roll
MAX_TOKENS = 300


def generate_code(rule_text: str, fields: dict | None = None) -> dict:
    """Translate an underwriting rule into a check_applicant() function.

    `fields` is the data schema — the exact field names and types the
    applicant_data dict will contain (e.g. {"days_since_late_payment": "number"}).
    Passing it removes the field-name guessing that otherwise makes code fail for
    schema reasons rather than logic reasons. A real developer always knows the
    schema; withholding it would be an unfair test. It does NOT reveal the answers.

    Returns a dict with the extracted code plus provenance (model, temperature,
    prompt/code hashes, token usage) so a run can be reproduced and audited.
    """
    schema_line = ""
    if fields:
        listed = ", ".join(f"{k} ({t})" for k, t in fields.items())
        schema_line = (
            f"\nThe applicant_data dict contains exactly these fields: {listed}.\n"
            "Use these exact field names — do not invent, rename, or assume other fields.\n"
        )

    prompt = f"""You are translating an underwriting rule into Python code.

Rule: {rule_text}
{schema_line}
Write a single Python function called `check_applicant(applicant_data: dict) -> str`
that implements this rule exactly as stated. It should return either "approve", "deny",
or "manual_review" based on the rule. Return ONLY the Python code, no explanation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    print(f"[code-gen tokens] input: {response.usage.input_tokens}, "
          f"output: {response.usage.output_tokens}")

    raw_code = response.content[0].text

    # Extract just what's between ``` fences, regardless of whitespace quirks.
    # (The guardrail is the real safety net if this misses — it rejects, never repairs.)
    match = re.search(r"```(?:python)?\s*\n(.*?)```", raw_code, re.DOTALL)
    code = match.group(1).strip() if match else raw_code.strip()

    return {
        "code": code,
        "model": MODEL,
        "temperature": TEMPERATURE,
        "prompt_hash": sha256_text(prompt),
        "code_hash": sha256_text(code),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


if __name__ == "__main__":
    result = generate_code("If debt is more than 43 percent of income, deny the loan.")
    print(result["code"])
    print("\n[code_hash]", result["code_hash"][:12])
