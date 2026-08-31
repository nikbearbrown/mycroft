# Design Specs

Technical reference for each component in this pipeline: purpose, interface,
inputs/outputs, and explicit scope boundaries. For *why* certain choices were
made, see `DESIGN_DECISIONS.md`. For a narrative walkthrough, see `README.md`.

---

## Pipeline Shape

```
raw claim text ──► Intake ──► Verification ──► Authorization Gate ──► SETTLED
                      │             │                    │
                      ▼             ▼                    ▼
                  ESCALATED     ESCALATED            ESCALATED
```

Strict, linear, fail-fast. A claim that fails at any stage never reaches a
later one. Every escalation carries a specific, named reason — never a
generic "needs review."

---

## Configuration (`config.py`)

Collects the settings an implementer actually needs to change in one place.

| Field | Category | Default | Notes |
|---|---|---|---|
| `llm_provider` | infrastructure | `"fake"` | `[DEV]` — one of `fake`/`claude`/`gpt`/`gemini` |
| `llm_api_key` | secret | none | env var only, required for real providers |
| `confidence_threshold` | tunable | `0.75` | `[DEV]` — illustrative, not a disclosed figure |
| `matching_tolerance` | tunable | `0.05` | `[DEV]` — illustrative, not a disclosed figure |

Raises `UnknownProviderError` for an unrecognized provider, `MissingAPIKeyError`
if a real provider is selected without a key — both at load time.

---

## LLM Provider Layer (`llm_provider/`)

One shared interface, four adapters.

**Interface:** `call(instruction: str, input_text: str) -> str`

| Adapter | Provider | Notes |
|---|---|---|
| `FakeAdapter` | none (default) | Scenario-keyed canned responses, see `fixtures.py` |
| `ClaudeAdapter` | Anthropic | Real HTTP call, untested against live API |
| `GPTAdapter` | OpenAI | Real HTTP call, untested against live API |
| `GeminiAdapter` | Google | Real HTTP call, untested against live API |

`factory.build_llm_client(config)` maps an already-validated provider name to
the corresponding adapter. Only `Intake` calls this layer — no other
component talks to it directly.

---

## Intake (`intake.py`)

Classifies a claim and extracts the fields Verification needs.

**Constructor:** `Intake(llm_client, confidence_threshold)`
**Method:** `process(raw_claim_text: str) -> ExtractedFields | IntakeEscalation`

| Outcome | Condition |
|---|---|
| `ExtractedFields` | Model classifies with confidence ≥ `confidence_threshold` |
| `IntakeEscalation("unclassified")` | Model can't classify, or its output is unparseable |
| `IntakeEscalation("low_confidence")` | Model classifies, confidence < threshold |

Out of scope: comparing extracted fields to any record, retry/timeout
handling for the LLM call.

---

## Verification (`verification.py`)

Checks a claim against the insurer's record and fraud signal, in a fixed
order — each step gates the next.

**Constructor:** `Verification(policy_visit_lookup, fraud_signal_lookup, matching_tolerance)`
**Method:** `process(extracted, customer_id, policy_id) -> VerifiedClaim | VerificationEscalation`

| Step | Check | Escalation reason if failed |
|---|---|---|
| 1 | Diagnosis/amount/date all present | `incomplete_extraction` |
| 2 | Record exists for customer/policy | `no_record_found` |
| 3 | No fraud signal (checked independently of step 2) | `fraud_flag` |
| 4 | Diagnosis, amount (within tolerance), date all match record | `mismatch` |

Out of scope: policy-coverage checking (deliberately not wired into the
default path — see `DESIGN_DECISIONS.md`), calling the LLM layer directly.

---

## Authorization Gate (`authorization_gate.py`)

The final decision point. Ships with zero settlement criteria — see
`DESIGN_DECISIONS.md`, Decision 1.

**Method:** `decide(verified_claim, policy_fn) -> GateOutcome`

| Outcome | Condition |
|---|---|
| `GateOutcome("SETTLED")` | `policy_fn(verified_claim)` returns `True` |
| `GateOutcome("ESCALATED", "not_authorized")` | `policy_fn(verified_claim)` returns `False` |

Does not validate that `policy_fn` exists or is callable — that's the
Orchestrator's job, at construction, not this component's job, per claim.

---

## Orchestrator (`orchestrator.py`)

Sequences the three stages, owns stop-conditions, and validates wiring once
at construction.

**Constructor:** `Orchestrator(intake, verification, gate, policy_fn)` — raises
`MissingPolicyError` if `policy_fn` is missing or not callable.
**Method:** `process_claim(raw_claim_text, customer_id, policy_id) -> ClaimResult`

Contains no classification, comparison, or authorization logic of its own —
purely a router. Does not construct its own dependencies; see
`demo/run_sample_claims.py` for the reference wiring pattern.

---

## Mock Policy/Visit Records (`mock_policy_visit_records.py`)

**Function:** `lookup(customer_id, policy_id) -> dict | None`

Returns `{diagnosis, amount, date}` or `None`. Contains no fraud-related
field — fraud signals live entirely in the next component. `[DEV]` — replace
with a real data-access layer.

---

## Mock Fraud Signal (`mock_fraud_signal.py`)

**Function:** `check(customer_id, policy_id, claim_details) -> bool`

Deliberately separate from Mock Policy/Visit Records — no shared import, no
shared data structure. `[DEV]` — replace with a call to a real fraud system.

---

## Demo Harness (`demo/run_sample_claims.py`)

Two jobs: (1) end-to-end proof that all eight scenarios below produce their
expected outcome, and (2) the reference wiring example for building your own
deployment.

| Scenario | Expected Outcome |
|---|---|
| Sofia — valid claim, low amount | `SETTLED` |
| Unclassifiable text | `ESCALATED`, `unclassified` |
| Low-confidence classification | `ESCALATED`, `low_confidence` |
| Missing diagnosis/amount/date | `ESCALATED`, `incomplete_extraction` |
| Unknown customer/policy | `ESCALATED`, `no_record_found` |
| Fraud signal present, record otherwise matches | `ESCALATED`, `fraud_flag` |
| Record found, amount mismatch | `ESCALATED`, `mismatch` |
| Verified claim, over demo policy's $500 line | `ESCALATED`, `not_authorized` |

---

## Exception Hierarchy (`exceptions.py`)

```
PipelineConfigurationError
  ├── MissingPolicyError    — Orchestrator construction, no/invalid policy_fn
  ├── UnknownProviderError  — Configuration load, unrecognized provider
  └── MissingAPIKeyError    — Configuration load, real provider without a key
```

Categorically separate from claim-level `ESCALATED` outcomes — these
represent caller/wiring mistakes, always fail once and loudly, never per-claim.

---

## Escalation Reason Reference

| Reason | Raised By |
|---|---|
| `unclassified` | Intake |
| `low_confidence` | Intake |
| `incomplete_extraction` | Verification |
| `no_record_found` | Verification |
| `fraud_flag` | Verification |
| `mismatch` | Verification |
| `not_authorized` | Authorization Gate |

All seven, exactly, and no others. If you add or rename a reason, update
this table and the corresponding tests.
