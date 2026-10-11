# Changelog

The four improvements that turned this from "AI writes code, human eyeballs it" into an
honest verification harness. Each entry: **what changed** and **why it matters**.

## 1. Lock the answer key before code generation (+ tamper-evident hash)
**What changed.** A rule's example answers can now be **frozen**. Once frozen, the test
cases can't be edited, and only then may code generation run — the pipeline hard-halts
(`409`) on any attempt to run against an unfrozen rule. Freezing also stores a SHA-256
**hash** of the exact committed content (rule text + all test cases).
**Why.** Without a commit-first step, "the checks passed" proves nothing — you could quietly
adjust answers to match whatever the AI produced. Locking first is what makes the whole test
honest; the hash makes any later tampering detectable. *(Files: `models/oracle.py`,
`integrity.py`, `main.py`, `run_pipeline.py`.)*

## 2. Pre-execution guardrail — reject, never repair
**What changed.** Before the validator runs AI code, a static guardrail checks it parses,
defines `check_applicant`, takes one argument, and has a return. If it fails, the run records
`"unrunnable"` for that code — it does **not** fix it.
**Why.** It separates two very different failures: *"the AI wrote wrong logic"* vs *"the AI
wrote text that isn't even runnable Python."* Both are honest outcomes reported distinctly.
Repairing the code would mean testing ourselves instead of the AI. This also killed a real
bug where malformed output made every check falsely "fail." *(File: `agents/guardrail.py`,
wired in `agents/graph.py`.)*

## 3. Independent reasoner on a different model
**What changed.** The second checker (the reasoner) now runs on **Claude Opus 4.8**, while the
code generator runs on **Claude Sonnet 4.5**. The reasoner reads only the rule + applicant data
and never sees the generated code.
**Why.** If the same model both wrote and judged the code, a shared blind spot could make it
bless its own mistake. A different model, blind to the code, is a genuinely independent second
opinion — so agreement means more than "the same model twice." *(File: `agents/reasoner.py`.)*

## 4. Give the generator the data schema
**What changed.** The generator is now told the exact **field names and types** the applicant
data will contain (e.g. `days_since_late_payment (number)`), derived automatically from the
test cases.
**Why.** Previously the AI had to *guess* field names, so code failed for schema reasons
("it couldn't guess my database columns") rather than logic reasons — noise that drowned out
the real signal. A real developer always knows the schema; withholding it was an unfair test.
Providing it isolates genuine **logic** mistranslations, which is the actual thesis. It does
not reveal the correct answers. *(Files: `agents/code_gen.py`, `agents/graph.py`.)*
