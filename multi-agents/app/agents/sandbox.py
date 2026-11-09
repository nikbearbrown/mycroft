import subprocess
import tempfile
import os
import json

def run_in_sandbox(generated_code: str, applicant_data: dict, timeout: int = 5) -> str:
    """
    Runs AI-generated code in an isolated subprocess against one applicant's data.
    Returns the outcome string (e.g. "approve", "deny", "manual_review"),
    or "ERROR: <message>" if something went wrong.
    """
    # Build a self-contained script: the generated function + a call to it + a print
    script = f"""
{generated_code}

import json
applicant_data = {repr(applicant_data)}
result = check_applicant(applicant_data)
print(result)
"""

    # Write it to a real temporary file on disk
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        temp_path = f.name

    try:
        result = subprocess.run(
    [
        "docker", "run",
        "--rm",                                    # auto-delete container after it exits
        "--network", "none",                       # no internet access at all
        "--memory", "128m",                         # cap RAM usage
        "--cpus", "0.5",                            # cap CPU usage
        "-v", f"{temp_path}:/sandbox/script.py:ro", # mount the file in, READ-ONLY
        "sandbox-runner",                           # the image we built
        "python3", "/sandbox/script.py"
    ],
    capture_output=True,
    text=True,
    timeout=timeout
)
        if result.returncode != 0:
            return f"ERROR: {result.stderr.strip()}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "ERROR: timed out"
    finally:
        os.remove(temp_path)  # always clean up the temp file, success or failure


if __name__ == "__main__":
    fake_generated_code = """
def check_applicant(applicant_data: dict) -> str:
    income = applicant_data.get('income', 0)
    debt = applicant_data.get('debt', 0)
    if income == 0:
        return "manual_review"
    if debt / income > 0.43:
        return "deny"
    return "approve"
"""
    raj_data = {"income": 100000, "debt": 50000}
    outcome = run_in_sandbox(fake_generated_code, raj_data)
    print("SANDBOX RESULT:", outcome)