import os
import re
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Deliberately a DIFFERENT model than the code generator (code_gen uses
# claude-sonnet-4-5). If the same model both wrote and checked, a shared blind
# spot would make it agree with its own mistake. A different model reduces that
# correlated failure, so agreement means more than "the same model twice."
REASONER_MODEL = "claude-opus-4-8"

VALID_OUTCOMES = {"approve", "deny", "manual_review"}


def reason_about_applicant(rule_text: str, applicant_data: dict) -> dict:
    """
    Independent semantic check. Reads the plain-English rule and reasons about a
    single applicant WITHOUT ever seeing the generated code, then predicts the
    outcome. Returns {"outcome": str, "rationale": str}.

    This is deliberately blind to the code so it can disagree with the Validator:
    a disagreement means the code and the rule's intent have diverged.
    """
    prompt = f"""You are an underwriting officer applying a rule by hand. You have
NOT seen any code — reason only from the rule and the applicant's data.

Rule: {rule_text}

Applicant data: {applicant_data}

Decide the outcome for this applicant. Respond in EXACTLY this format, nothing else:
OUTCOME: <approve|deny|manual_review>
REASON: <one sentence explaining why, referring to the applicant's numbers>"""

    response = client.messages.create(
        model=REASONER_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    print(f"[reasoner tokens] input: {response.usage.input_tokens}, "
          f"output: {response.usage.output_tokens}")

    raw = response.content[0].text

    outcome_match = re.search(r"OUTCOME:\s*(\w+)", raw, re.IGNORECASE)
    reason_match = re.search(r"REASON:\s*(.+)", raw, re.IGNORECASE | re.DOTALL)

    outcome = outcome_match.group(1).strip().lower() if outcome_match else "manual_review"
    if outcome not in VALID_OUTCOMES:
        outcome = "manual_review"

    rationale = reason_match.group(1).strip() if reason_match else raw.strip()

    return {"outcome": outcome, "rationale": rationale}


if __name__ == "__main__":
    rule = "If debt is more than 43 percent of income, deny the loan."
    for data in ({"income": 100000, "debt": 50000}, {"income": 100000, "debt": 30000}):
        print(data, "->", reason_about_applicant(rule, data))
