import os
from dotenv import load_dotenv
from anthropic import Anthropic
import re

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

import re

def generate_code(rule_text: str) -> str:
    prompt = f"""You are translating an underwriting rule into Python code.

Rule: {rule_text}

Write a single Python function called `check_applicant(applicant_data: dict) -> str` 
that implements this rule exactly as stated. It should return either "approve", "deny", 
or "manual_review" based on the rule. Return ONLY the Python code, no explanation."""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    print(f"[tokens used] input: {response.usage.input_tokens}, output: {response.usage.output_tokens}")
    
    raw_code = response.content[0].text
    
    # Extract just what's between ``` fences, regardless of whitespace quirks
    match = re.search(r"```(?:python)?\s*\n(.*?)```", raw_code, re.DOTALL)
    if match:
        code = match.group(1).strip()
    else:
        code = raw_code.strip()  # fallback: no fences found, use as-is
    
    return code

if __name__ == "__main__":
    prompt_text = "If debt is more than 43 percent of income, deny the loan."
    code = generate_code(prompt_text)
    print(code)