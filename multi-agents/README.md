# Can you trust AI to turn rules into code?

A proof-of-concept **verification harness for "policy-as-code."** When a plain-English
rule (e.g. *"deny the loan if debt is over 43% of income"*) has to become executable
code, and an AI writes that code, this project checks whether the code **faithfully
implements the rule** — before a human approves it.

It is **not** a training system. The AI is a fixed, pre-trained model we prompt each
time. Nothing here teaches or fine-tunes it. The human's job is to **check and approve**
the code the AI wrote.

---

## The thesis

> **You cannot trust AI-generated code by reading it.** It silently encodes decisions
> you never made — thresholds, boundaries, interpretations — that *look* correct. So you
> need independent checks against answers you committed **in advance**, and where those
> checks disagree tells you *what* went wrong.

The project proves two things at once:

- **The danger** — AI code hides confident, unauthorized decisions you'd never catch by inspection.
- **The defense** — independent verification against a pre-committed human answer key catches
  them, and pinpoints whether the fault is a **code bug**, an **ambiguous rule**, or your **own answer being wrong**.

### A concrete example
Rule: *"deny the loan if the applicant has had a **recent** late payment."*
Given only the rule, the AI writes code that treats "recent" as `days_since_late_payment < 90`.
Nobody told it 90 — it invented that threshold from industry convention, buried it in code,
and it disagrees with a human policy that counts *exactly 90 days* as recent. You would never
see that decision without reading the generated code line by line. This tool surfaces it.

---

## How it works

The flow is deliberately ordered so the test stays honest:

```
1. Write the answer key   →   2. Freeze (lock)   →   3. AI writes code + 2 checks   →   4. Human reviews
   (rule + example                (can't edit;          ┌─ validator: runs the code       (approve /
    applicants + the                only now can        └─ reasoner: re-reads the rule      reject)
    correct outcome)                code-gen run)           (blind to the code)
```

1. **Write the answer key.** A human writes a rule and, for a few example applicants, the
   outcome they say is correct (`approve` / `deny` / `manual_review`).
2. **Freeze.** The answer key is locked and hashed. Only now may code generation run.
   This is what makes the test honest — you can't tweak answers to match the code afterward.
3. **Check.** The AI generates code; a guardrail confirms it's runnable; then **two
   independent checkers** compare it to your locked answers.
4. **Review.** A human sees the per-applicant verdicts and approves, rejects, or flags the code.

### The agents

| Agent | Sees | Uses an LLM? | What it answers |
|-------|------|--------------|-----------------|
| **Code generator** (`code_gen.py`) | the rule + the data field names/types | Yes — `claude-sonnet-4-5` | writes `check_applicant(data) -> outcome` |
| **Validator** (`sandbox.py`) | the generated **code**, executed | No — runs it in Docker | Does the *code's output* match your answer? |
| **Reasoner** (`reasoner.py`) | the **rule** only (**blind to the code**) | Yes — `claude-opus-4-8` | Does an *independent reading of the rule* match your answer? |

The two checkers are deliberately different: one **executes** the code, the other **ignores it**
and re-reasons from the rule. If both looked at the code, both could be fooled by the same
convincing bug. They also use **different models**, so agreement means more than "the same model twice."

A **guardrail** (`guardrail.py`) sits between the generator and the validator. It statically
checks the code is valid, runnable Python (parses, defines `check_applicant`, has a return) —
and **rejects it if not, never repairs it.** A rejection is recorded as an honest "unrunnable
code" outcome. (Repairing would mean testing ourselves instead of the AI.)

### The 2×2 diagnosis

Each applicant gets two independent verdicts against your locked answer. The *combination*
localizes the fault:

| Code matches answer? | Reasoner matches answer? | Verdict | Meaning |
|---|---|---|---|
| ✓ | ✓ | **Trustworthy** | code, rule, and your answer all agree |
| ✗ | ✓ | **Code bug caught** | the rule was clear; the AI's code got it wrong |
| ✓ | ✗ | **Rule may be ambiguous** | code matches you, but a plain reading of the rule differs |
| ✗ | ✗ | **Answer key looks wrong** | both disagree with you — your answer or the rule is off |

---

## Key design decisions

- **Lock the answer key before code generation.** Without this, "the checks passed" proves
  nothing — you could have adjusted answers after seeing the code. Freezing records a hash of
  the exact committed content, so tampering is detectable. Unlocking to edit discards the
  current results, keeping each run an honest "answers committed before code" experiment.
- **Guardrail rejects, never repairs.** Separates "the AI wrote wrong logic" from "the AI wrote
  unrunnable text" — both honest failures, reported distinctly.
- **Two independent checkers, different models.** Executing vs. re-reasoning, Sonnet vs. Opus —
  reduces correlated blind spots.
- **The AI is given the data schema** (field names + types), the way a real developer always
  knows the schema. This removes field-name guessing so a failure means a real *logic* error,
  not "the AI couldn't guess your database columns." It does **not** reveal the answers.
- **Provenance on every run** — model, temperature, prompt hash, code hash — so a run is
  reproducible and auditable. A **binding hash** ties the code to the exact results a human approved.

---

## Real-world use cases

Anywhere written rules become code that decides things about people or money — especially
regulated, high-stakes domains that need an audit trail:

- **Lending / underwriting** (the demo domain) — loan approval rules
- **Insurance** — claims and eligibility rules
- **Tax software** — encoding each year's tax rules
- **Government benefits** — eligibility (SNAP, Medicaid, …)
- **Healthcare** — prior-authorization, clinical-trial eligibility
- **Banking compliance** — KYC / AML thresholds

**Who uses it (roles — all one person in this demo):**
- **Rule author** — writes the policy in plain English.
- **Answer-key author** — writes the correct outcomes for example cases, *first*.
- **Reviewer / approver** — an engineer, risk manager, or compliance officer who reviews the
  AI's code plus the two checks and approves or rejects.

---

## Architecture

- **Backend** — FastAPI (`main.py`) + SQLAlchemy models, PostgreSQL.
- **Pipeline** — LangGraph (`app/agents/graph.py`): `code_gen` fans out to `validator` and
  `simulator` (reasoner) in parallel, then joins.
- **Sandbox** — AI code runs in a Docker container (`--network none`, memory/CPU caps,
  read-only mount, timeout) so untrusted code can't touch anything.
- **Frontend** — React + Vite (`frontend/`): the stepped write → freeze → check → review UI.

### Project structure
```
main.py                     FastAPI app + endpoints
app/
  agents/
    code_gen.py             generator (Claude → Python)
    guardrail.py            reject-not-repair static check
    sandbox.py              runs code in Docker (validator engine)
    reasoner.py             independent rule reader (validator's counterpart)
    graph.py                LangGraph wiring + nodes
  models/                   SQLAlchemy: oracle, test_case, generated_code, check_result
  db/database.py            engine / session
  integrity.py              oracle hash + binding proof
  run_pipeline.py           run one rule end-to-end, persist results
  eval.py                   multi-run reliability eval (read-only)
frontend/                   React + Vite UI
Dockerfile                  the sandbox image (python:3.12-slim)
tests/test_pipeline.py      guardrail / hash / freeze-gate tests
```

---

## Setup & run (local)

**Prerequisites:** Python 3.12, Node.js 22, PostgreSQL, Docker, an Anthropic API key.

**1. Python environment**
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Environment variables** — create `.env` in the project root:
```
DATABASE_URL=postgresql://<user>@localhost:5432/loan_pipeline
ANTHROPIC_API_KEY=sk-ant-...
```

**3. PostgreSQL** — create the database (tables are created automatically on first run):
```bash
createdb loan_pipeline
```

**4. Sandbox image** — build the container the AI code runs in:
```bash
docker build -t sandbox-runner .
```

**5. Backend**
```bash
source venv/bin/activate
PYTHONPATH=$(pwd) uvicorn main:app --reload    # http://127.0.0.1:8000
```

**6. Frontend** (needs Node 22)
```bash
cd frontend
npm install
npm run dev                                     # http://localhost:5173
```
Set `frontend/.env` if your API runs elsewhere: `VITE_API_BASE=http://127.0.0.1:8000`

### Command-line alternatives
```bash
python -m app.run_pipeline          # run the (frozen) rules end-to-end
python -m app.eval <rule_id> 10     # run one rule 10x, report failure rate + variance
python -m pytest tests/ -q          # guardrail / hash / freeze-gate tests
```

---

## API reference (main endpoints)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/rules` | create a rule (unique by id and text) |
| `PATCH` | `/rules/{rule_id}` | edit rule text (only while unfrozen) |
| `DELETE` | `/rules/{rule_id}` | delete a rule and everything under it |
| `POST` | `/test-cases` | add an example applicant + expected outcome (only while unfrozen) |
| `DELETE` | `/test-cases/{id}` | delete an example (only while unfrozen) |
| `POST` | `/rules/{rule_id}/freeze` | lock the answer key + hash it |
| `POST` | `/rules/{rule_id}/unfreeze` | unlock to edit (clears current results) |
| `POST` | `/run/{rule_id}` | generate code + run both checks (requires frozen) |
| `GET` | `/results/{rule_id}` | latest code + per-applicant results + binding hash |
| `POST` | `/decision/{rule_id}` | human approve / reject / needs-review |

---

## Scope & limitations (honest)

This is a **proof-of-concept demonstrating a pattern**, not a production system.

- It checks **translation fidelity** (does the code match the rule?) — **not** whether the rule
  itself is fair, legal, or good. A facially-neutral but discriminatory rule would pass cleanly.
- It only catches bugs your example cases **exercise**. Untested edge cases slip through.
- Both LLM-based checks are **non-deterministic**; a single run is an anecdote — use the
  multi-run eval for a real failure rate.
- No real applicant data, no production deployment path. A real system would add fairness
  review, monitoring, versioning, and legal sign-off on top.

A worked example of "passes cleanly but is still a bad rule" (a ZIP-code redlining rule that
the pipeline approves as *Trustworthy*) is in **[`LIMITATIONS.md`](LIMITATIONS.md)** — read it
before presenting; it's the honest counterweight to the demo.

---

## Outcomes across the rule set (honest)

The pipeline is non-deterministic, so outcomes are reported as *what the checks tend to
surface*, not a fixed score:

- **Clean rules** (e.g. DTI > 43%, loan > $50k) — code, reasoner, and answer key usually all
  agree → **Trustworthy**.
- **Objective edge cases** (e.g. "above 750" → is 750 excluded?) — the AI's code sometimes
  writes `>=` and is silently wrong at the boundary while the reasoner reads the rule
  correctly → **Code bug caught**. (Verify per run — it doesn't fail every time.)
- **Vague rules** (e.g. "recent late payment") — the AI invents a threshold (often 90 days)
  from convention; both checks may disagree with a differently-defined human answer → surfaced
  as **rule ambiguous / answer key looks wrong**, not a clean code bug. This is a real finding
  about ambiguity, reported as such — never edited to force a "catch."

## Related docs
- **[`CHANGELOG.md`](CHANGELOG.md)** — the four improvements (what changed + why).
- **[`DESIGN_DECISIONS.md`](DESIGN_DECISIONS.md)** — load-bearing choices + rejected shortcuts (tripwires).
- **[`LIMITATIONS.md`](LIMITATIONS.md)** — what this does *not* prove, with the redlining example.
