# CommBank Disputes Workflow — Illustrative Reference Implementation

A single-tool, linear workflow (Intake → Verification → Gate) modeling the
three publicly confirmed functions of Commonwealth Bank of Australia's
unnamed agentic payment-disputes tool, as documented in the companion case
study ("Commonwealth Bank: Agentic AI in Retail Banking").

This is a **design-ready starting scaffold**, not a finished product and not
a disclosure of CBA's actual system. Every design decision below is labeled
CONFIRMED or CONSTRUCTED. Nothing is left unlabeled.

---

## What's Confirmed

Sourced to Dan Jermyn (CBA Chief Decision Scientist), quoted in Evident
Insights, "167 ways banks use AI," 20 Feb 2025, and to Evident's own
description of the tool's behavior:

- The tool understands customer intent in an AI-assisted channel.
- The tool verifies transaction details against CBA's internal records.
- The tool lodges a dispute automatically once unspecified "criteria" are met.
- This is a single tool with three functions, not a documented multi-agent
  pipeline — no source describes a multi-step internal architecture, a
  merchant-history lookup, a regulatory-evaluation engine, or an autonomous
  chargeback-execution step.

Nothing else about this tool is publicly confirmed. No model, no
orchestration framework, no specific dollar thresholds, no error/override
rate. CBA's own flagship AI disclosure (December 2025, "Our Approach to
Adopting AI") does not mention this use case at all.

---

## What's Constructed

Everything else in this repository is this project's own authorial
decision, made explicit rather than left implicit:

- **That extraction (amount/merchant/date) lives inside Intake**, rather
  than being a separate unnamed function — see `docs/DESIGN_DECISIONS.md`,
  entry 001. This resolves an open question the case study itself flags and
  does not answer.
- **The exact matching logic in Verification** (case-insensitive merchant
  name, exact date match) — no source describes CBA's actual matching
  tolerance.
- **The risk-tiered auto-lodge thresholds in Gate** ($750 duplicate_charge /
  $500 unrecognized_charge / $250 unauthorized_transaction) — entirely
  invented, marked `[DEV]` in `src/components/gate.py`. CBA has never
  disclosed a figure, tiered or otherwise. This specific design — tiering by
  dispute type rather than one flat number — was decided against this
  project's own recommendation for a flat threshold; see
  `docs/DESIGN_DECISIONS.md`, entry 005, for the reasoning and the recorded
  disagreement.
- **Escalating on an unclassified dispute type** rather than defaulting it
  through Gate's tiering — see `docs/DESIGN_DECISIONS.md`, entry 006.
- **The distinction between a fail-fast "no record found" and a
  Gate-evaluated "record found but mismatched"** — see
  `docs/DESIGN_DECISIONS.md`, entry 002.
- **All code, mock data, and the orchestrator's call sequence.**
- **The extraction-confidence escalation threshold (0.6)** in Intake.

Every `[DEV]`-marked line in the code is a customization point: a value, a
matching rule, or an integration seam meant to be replaced when adapting
this scaffold to a real use case, not a claim about how CBA's system works.

---

## Setup / How to Run

No external services, credentials, or CBA systems are involved anywhere in
this repository — it runs entirely against fabricated mock data.

```bash
pip install -r requirements.txt   # pytest, if available in your environment

# Either:
pytest tests/ -v

# Or, if pytest isn't available (no external dependency required):
python3 run_tests.py
```

No environment variables are required. No API keys. No network access.

---

## What the Tests Actually Verify

This suite was executed in full before this repository was called finished
— every claim below is a reported result, not a description of intended
behavior.

| Test file | What it proves |
|---|---|
| `test_intake_verification_dependency.py` | Verification cannot succeed without Intake's output; called with a missing merchant, it escalates gracefully (`incomplete_claim_details`) rather than failing silently or crashing. Called with correct Intake-shaped input, it matches correctly. |
| `test_verification_gate_dependency.py` | Gate refuses to auto-lodge when Verification's output is withheld (`record_found=False`) or negative (`match_result=False`) — the dependency is real, not assumed. |
| `test_fail_fast_pipeline.py` | The orchestrator actually stops at Intake on ambiguous input and at Verification when no record exists — Gate is never called with unusable data in either case (confirmed via `gate_result is None`). |
| `test_escalation_paths.py` | All three named escalation triggers (ambiguous input, unmet criteria, high-value threshold) are each independently confirmed reachable, with the correct `escalation_reason`. |
| `test_negative_and_positive_cases.py` | A case engineered to fail every gate criterion is confirmed to escalate. A clean case is confirmed to actually reach `auto_lodge_decision=True`. Two further cases confirm the risk-tiered thresholds (entry 005) actually change the outcome for the same dollar amount depending on `dispute_type` — not just described as tiered, but shown producing a different decision at $600 and at $12.99. A final case confirms an unclassified `dispute_type` escalates at Intake (entry 006) rather than silently defaulting through Gate's tiering. |

**Two findings from actually running this suite, not from prose review:**
1. The first version of `run_verification` raised an unhandled
`AttributeError` when called with a missing merchant, instead of escalating
gracefully. Caught by the dependency test designed to feed it malformed
input, and fixed before this repository was finalized — see
`docs/DESIGN_DECISIONS.md`, entry 003.
2. Making Gate's threshold depend on `dispute_type` (entry 005) surfaced a
second-order gap during design review: Intake's original escalation logic
never checked whether `dispute_type` itself was classifiable, so a claim
with a clean amount/merchant/date but no matching dispute-type phrase would
have silently defaulted to a middle risk tier it was never evaluated
against. Closed by entry 006 and covered by
`test_unclassified_dispute_type_escalates_before_gate`.

Both are recorded here rather than quietly corrected, because they're a
concrete demonstration of why this suite is run and not just described.

**Result:** 14 tests, 14 passing, 0 failing, as of the version in this
repository.

---

## Known Limitations

- **Extraction is rule-based (regex/keyword), not ML-based.** It's built
  only to demonstrate the Intake → Verification data contract, not to model
  what CBA's actual natural-language understanding does — no source
  discloses that either.
- **Mock data is six hardcoded transactions.** A real integration point is
  marked `[DEV]` in `src/mock_data/transactions.py` and
  `src/components/verification.py`.
- **No concurrency, retry, or timeout handling.** This is a synchronous,
  single-request pipeline; production use would need these and they are
  out of scope here.
- **No test exercises multiple disputes arriving concurrently** — the case
  study's operational-scale problem (roughly 15,000 disputes/day) is not
  modeled at all here; this repo models one dispute's path through the
  pipeline, not throughput.
- **The auto-lodge thresholds (tiered by dispute type), matching tolerance,
  and confidence cutoff are all single invented values**, not the product
  of any tuning or real data.

---

## Explicit Non-Claims

This repository is **not** a disclosure of Commonwealth Bank of Australia's
actual proprietary disputes-handling system. It does not claim CBA's system
works this way, uses this matching logic, or applies this threshold. It
should not be cited as evidence of CBA's technical architecture. It is an
illustrative scaffold, built to be consistent with the three functions
publicly confirmed about CBA's tool and no richer than what they support —
intended as a tested starting point for someone building a structurally
similar workflow, not as a description of what CommBank has actually built.
