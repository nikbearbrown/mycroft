# Lemonade Pet Insurance Claims Pipeline — Reference Scaffold

A working, tested reference implementation of a pet-insurance claims
automation pipeline, modeled on the publicly confirmed functions of
Lemonade, Inc.'s claims bot ("AI Jim"). This is **not** Lemonade's actual
system, and it does not claim to be — it's a design-ready starting point
built to be honest about exactly where public disclosure stops and
illustration begins.

If you're new to this repo, read this file top to bottom once before
touching any code. It's written so you leave it understanding not just
*what* each file does, but *why it's shaped the way it is*.

---

## What This Actually Is

This repository is a **case study companion artifact**, not a production
system and not a Lemonade product. It exists to make one thing concrete: a
plausible, working architecture for the kind of claims-processing pipeline
Lemonade's own disclosures describe in outcome (96% of first-notice-of-loss
handled without a human, ~55% of claims resolved end-to-end) but not in
mechanism (Lemonade has never disclosed *what specifically* makes a claim
eligible for automatic settlement).

Every design choice in this repo falls into one of three categories, and the
code is written to make it obvious which:

- **Confirmed** — a function this pipeline performs is something Lemonade
  has actually stated AI Jim does (classify a claim, check it against a
  record, triage unresolved claims to a human specialist by
  qualifications/workload/schedule).
- **Constructed, and labeled `[DEV]`** — a specific mechanism or default
  value this pipeline needs to actually run, which nothing in the public
  record discloses, so this repo invents a clearly-marked illustrative
  placeholder (a confidence threshold, a matching tolerance).
- **Deliberately absent** — one specific mechanism (the Authorization Gate's
  settlement criteria) where this repo does **not** invent a placeholder at
  all, because doing so would misrepresent how thin Lemonade's actual public
  disclosure is on that exact point. This is the single most important
  thing to understand before you start reading code — see
  [The Authorization Gate](#the-authorization-gate-the-one-component-with-no-default)
  below.

If you want the full reasoning behind every decision here, `DESIGN_DECISIONS.md`
logs each one with its rationale. `DESIGN_SPECS.md` is the dry technical
reference (interfaces, inputs/outputs) if you just need to look something up.
This README is the narrative version — read it first.

---

## The 30-Second Mental Model

A claim moves through three stages, in a fixed order, and stops the instant
any stage rejects it:

```
raw claim text ──► Intake ──► Verification ──► Authorization Gate ──► SETTLED
                      │             │                    │
                      ▼             ▼                    ▼
                  ESCALATED     ESCALATED            ESCALATED
             (unclassified /  (incomplete_extraction /  (not_authorized)
              low_confidence)  no_record_found /
                                fraud_flag /
                                mismatch)
```

Every escalation carries a specific, named reason — never a generic "needs
review." A claim that fails at Intake never reaches Verification. A claim
that fails at Verification never reaches the Gate. Nothing downstream ever
runs on a claim that already failed upstream.

---

## Quickstart

No API key required. No signup. This runs entirely on canned, deterministic
responses out of the box.

```bash
# From the repo root:
python3 -m unittest discover -s tests -p "test_*.py" -v   # run the full test suite (43 tests)
python3 demo/run_sample_claims.py                          # watch the pipeline run end to end
```

The demo script prints eight sample claims and their outcomes — one
automatic settlement, and one example of every escalation reason this
pipeline can produce. Read its output before reading its code; it's the
fastest way to build intuition for how the pieces fit together.

To use a real language model instead of the built-in deterministic fake:

```bash
export LLM_PROVIDER=claude      # or "gpt" or "gemini"
export LLM_API_KEY=your-key-here
python3 demo/run_sample_claims.py
```

Nothing else changes — not the demo script, not the pipeline logic. See
[Configuring a Real LLM Provider](#configuring-a-real-llm-provider) below
for why that swap requires zero code changes.

---

## Repository Structure — What Each File Is and Why It Exists

```
lemonade-claims-workflow/
├── config.py                       # All tunable settings, in one place
├── exceptions.py                   # Shared error types for wiring/config mistakes
├── fixtures.py                     # One canonical set of demo/test scenario data
├── intake.py                       # Stage 1: classify + extract from free text
├── verification.py                 # Stage 2: check claim against record + fraud signal
├── authorization_gate.py           # Stage 3: the final decision — see the callout below
├── orchestrator.py                 # Sequences the three stages, validates wiring
├── mock_policy_visit_records.py    # Fake insurer database, standing in for a real one
├── mock_fraud_signal.py            # Fake fraud-detection source, kept separate on purpose
├── llm_provider/
│   ├── base.py                     # The shared interface every adapter implements
│   ├── fake_adapter.py             # Default, zero-cost, deterministic responses
│   ├── claude_adapter.py           # Real adapter for Anthropic's API
│   ├── gpt_adapter.py              # Real adapter for OpenAI's API
│   ├── gemini_adapter.py           # Real adapter for Google's API
│   └── factory.py                  # Picks the right adapter based on Configuration
├── demo/
│   └── run_sample_claims.py        # Runnable proof + the reference wiring example
├── tests/                          # 43 tests, one file per component above
├── DESIGN_DECISIONS.md             # Why each non-obvious choice was made
├── DESIGN_SPECS.md                 # Dry technical reference: interfaces, I/O tables
└── README.md                       # This file
```

### Why there's a separate file for almost everything

Each stage of the pipeline, each mock data source, and each LLM provider
lives in its own file, on purpose. The goal is that you can replace any one
piece — swap in a real database for `mock_policy_visit_records.py`, plug in
your own fraud system for `mock_fraud_signal.py`, point `config.py` at a
different model — without touching anything else. If you find yourself
needing to edit `intake.py` to change which LLM provider is used, or editing
`verification.py` to change a threshold, something has gone wrong with that
separation — those values live in `config.py` and get **injected**, not
hardcoded. `DESIGN_DECISIONS.md` §9 spells out exactly which kinds of value
are read directly from Configuration versus which are always
constructor-injected, and why.

### `fixtures.py` — why one file, not scattered test data

Every sample claim, every mock customer, every canned LLM response used
anywhere in this repo — in the test suite, in the demo script, in
`FakeAdapter` — is defined exactly once, in `fixtures.py`. This was a
deliberate choice to avoid two drifting copies of "what does Sofia's claim
look like" existing in different files and slowly disagreeing with each
other. If you add a new test scenario, add it here first.

---

## Walking Through a Claim: Sofia's Story

The clearest way to understand this pipeline is to trace one claim through
it — this is the exact scenario the demo script runs first.

1. **A customer files a claim.** Sofia describes a vet visit for her dog's
   kennel cough, costing $120, on May 1st, 2026. This raw text (plus her
   customer/policy ID, already known from her logged-in session) is handed
   to the `Orchestrator`.

2. **Intake classifies it.** `Intake.process()` sends Sofia's text, along
   with an extraction instruction, to whichever LLM provider is configured
   (by default, `FakeAdapter`, which recognizes this exact demo scenario and
   returns a pre-written response). The response is parsed into
   `{diagnosis: "kennel cough", amount: 120.0, date: "2026-05-01", confidence: 0.95}`.
   Confidence is well above the configured threshold, so the claim proceeds.

3. **Verification checks it.** `Verification.process()` runs four checks in
   order: are diagnosis/amount/date all present (yes) → does a record exist
   for Sofia's customer/policy ID (yes, in `mock_policy_visit_records.py`)
   → is there a fraud signal for Sofia (no, checked independently in
   `mock_fraud_signal.py`) → does the claimed diagnosis/amount/date match
   the record within tolerance (yes). The claim becomes a `VerifiedClaim`
   and proceeds.

4. **The Authorization Gate decides.** `AuthorizationGate.decide()` calls
   whatever `policy_fn` was supplied when the pipeline was built. In the
   demo, that's `demo_only_policy`, which just checks `amount < 500` — and
   $120 qualifies. The claim is `SETTLED`.

Now trace what happens if any one of those steps had gone differently: an
unrecognized claim never gets past Intake; a claim with no matching customer
ID never gets past Verification's second check; a claim your fraud system
flags never gets past Verification's third check, *even if the record
otherwise matches perfectly* — that independence is deliberate, see the next
section. And a $700 surgery claim, verified in every other respect, still
gets escalated at the Gate, with reason `not_authorized`, because it exceeds
the demo policy's arbitrary $500 line.

---

## The Authorization Gate: The One Component With No Default

This is the single most important design decision in this repository, and
it's worth understanding before you read `authorization_gate.py` itself,
because the file will look unusually empty compared to everything around it
— that emptiness is the point, not a bug.

**Every other undisclosed mechanism in this pipeline got an illustrative,
clearly-labeled default.** The confidence threshold in `config.py` is
`0.75` — invented, but labeled `[DEV]` and functional out of the box. The
matching tolerance is `0.05` — same story. These are placeholders you're
expected to look at and probably replace, but the pipeline runs correctly
with them left alone.

**The Authorization Gate got no such default, on purpose.** Lemonade has
publicly confirmed that its claims bot triages claims it is "not authorized
to settle" to a human expert — but nowhere in any 10-K, shareholder letter,
investor presentation, or executive interview has Lemonade stated what makes
a claim fall inside or outside that authority. No dollar threshold. No
claim-type list. No confidence score. This case study's whole point is that
this is a real, documented gap in Lemonade's disclosure — not something
this project could fill in with a "reasonable-sounding" number without
misrepresenting how thin the actual public record is.

So `authorization_gate.py` contains genuinely nothing — no threshold, no
`[DEV]` marker, no commented-out placeholder. It requires a real, callable
`policy_fn` to do anything at all:

```python
gate = AuthorizationGate()
outcome = gate.decide(verified_claim, policy_fn=your_policy_function)
```

**You must supply your own `policy_fn`** — a function that takes a verified
claim and returns `True` (settle it) or `False` (escalate it, reason
`not_authorized`). This pipeline has no opinion about what that function
should contain. That's not a limitation to work around; it's the honest
reflection of a real gap in what's publicly known.

To make the pipeline demonstrably runnable anyway, `demo/run_sample_claims.py`
supplies a trivial, explicitly-labeled `demo_only_policy` (`amount < 500`) —
but it's commented in the code as exactly what it is: a test prop, not a
serious default, and it deliberately carries no `[DEV]` marker so it's never
mistaken for one. See `DESIGN_DECISIONS.md`, Decisions 1 and 2, for the full
reasoning.

**If you're building on this repo for anything real:** this is the one
place you cannot skip customizing. Everything else in this pipeline runs
correctly with its illustrative defaults left alone. The Authorization Gate
does not run at all — meaningfully — without your own real policy.

---

## Configuring a Real LLM Provider

By default, `config.py` sets `LLM_PROVIDER=fake`, which means `Intake` talks
to `FakeAdapter` — a deterministic, zero-cost stand-in that recognizes a
fixed set of demo/test scenarios (see `fixtures.py`) and returns pre-written
responses for them, degrading to a generic low-confidence response for
anything it doesn't recognize.

To use a real model, set two environment variables:

```bash
export LLM_PROVIDER=claude   # or "gpt", or "gemini"
export LLM_API_KEY=your-actual-api-key
```

That's the entire change required. `Intake` never references a provider by
name — it only ever calls `llm_client.call(instruction, input_text)`, the
one shared interface every adapter (fake or real) implements. Swapping which
adapter sits behind that interface is `config.py`'s and `factory.py`'s job
alone. If you ever find yourself needing to edit `intake.py` to add support
for a new provider, something has broken this isolation — a fourth provider
should only ever require one new file in `llm_provider/` implementing the
same `call()` interface.

**Costs and correctness with a real provider:** the extraction instruction
in `intake.py` (`EXTRACTION_INSTRUCTION`) is a `[DEV]`-marked illustrative
placeholder, not tuned against any real model. Expect to rewrite it for your
own claim types and to validate its output format against whichever model
you actually use — the JSON-parsing logic in `Intake.process()` expects a
specific shape (`claim_type`, `diagnosis`, `amount`, `date`, `confidence`),
and a real model's raw output will need to reliably match that shape or be
adapted to it.

---

## Testing

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

**43 tests, organized one file per component**, matching the file
structure above exactly (`tests/test_intake.py` tests `intake.py`, and so
on). A few things worth knowing before you dig into the test files:

- **Mock/spy assertions are used deliberately**, not just to check
  outcomes but to prove *sequencing*. Several tests assert not just that a
  claim was escalated with the right reason, but that later stages were
  never called at all — this is the actual proof of the "nothing downstream
  runs on a rejected claim" guarantee, not just an assumption baked into the
  design docs.
- **No test calls a real external API.** The three real LLM adapters
  (`claude_adapter.py`, `gpt_adapter.py`, `gemini_adapter.py`) are tested
  with the HTTP layer mocked. "43 tests passing" should not be read as "this
  has been validated against live model output" — it hasn't, and can't be,
  without a real API key and real cost.
- **The Authorization Gate's tests verify a contract, not a business
  rule.** `tests/test_authorization_gate.py` proves the Gate settles when
  its policy returns `True` and escalates with `not_authorized` when it
  returns `False` — it does not, and cannot, test *what should* authorize a
  claim, because nothing in this pipeline claims to know. Don't read the
  Gate's test coverage as validating any settlement logic; there isn't any
  to validate.
- **Two tests assert an absence** — `tests/test_mock_policy_visit_records.py`
  and `tests/test_mock_fraud_signal.py` each confirm the other module is
  never imported. This protects a specific, deliberate design decision (see
  `DESIGN_DECISIONS.md` §7) from silently eroding as the codebase changes.
- **This suite uses the Python standard library's `unittest` module, not
  `pytest`** — an environment constraint from how this repo was built and
  validated, not a preference. See `DESIGN_DECISIONS.md` §11 if you want to
  port it to `pytest`.

---

## Extending This for Real Use — A Checklist

If you're taking this scaffold beyond illustration, here's everything that
needs your own real input, roughly in order of how load-bearing it is:

1. **Write your own `policy_fn` for the Authorization Gate.** Non-optional
   — see the callout above. This pipeline has no default here.
2. **Replace `mock_policy_visit_records.py`** with a real data-access layer
   against your actual policy/visit database. Keep the same `lookup(customer_id, policy_id) -> dict | None`
   interface so `Verification` doesn't need to change.
3. **Replace `mock_fraud_signal.py`** with a call to your real fraud-detection
   system. Keep the same `check(customer_id, policy_id, claim_details) -> bool`
   interface, and keep it genuinely independent of your record lookup — don't
   fold it back into the same data source, for the reasons in
   `DESIGN_DECISIONS.md` §7.
4. **Rewrite `EXTRACTION_INSTRUCTION` in `intake.py`** for your own claim
   types and your own chosen model's response tendencies.
5. **Re-tune `CONFIDENCE_THRESHOLD_DEFAULT` and `MATCHING_TOLERANCE_DEFAULT`
   in `config.py`** — these are illustrative starting points, not validated
   against any real claim distribution.
6. **Consider whether you need the policy-coverage check** described but
   deliberately not built into `verification.py`'s default comparison logic
   — see `DESIGN_SPECS.md`'s Verification section and the blueprint
   reasoning it references.
7. **Revisit the Configuration file-split decision** (`DESIGN_DECISIONS.md`
   §5) if you're moving from a reference scaffold to something handling real
   credentials at real stakes.

Search the codebase for `[DEV]` to find every marker — each one names
exactly what it's flagging and why.

---

## A Note on What This Repo Is Not

This is not Lemonade's actual claims-processing system, does not claim to
replicate it, and should not be presented as though it does. It's a
reference scaffold built from what Lemonade has publicly confirmed (a claims
bot that classifies, verifies, and triages) plus explicitly-labeled
illustrative construction everywhere the public record stops. Where this
repo diverges most sharply from a real production system is the
Authorization Gate — and that divergence is the entire point of the exercise,
not an oversight. See the case study this pipeline accompanies for the full
sourcing behind every confirmed claim referenced above.
