# Allianz Australia — Project Nemo: Agentic Claims Workflow (Reference Implementation)

A buildable, illustrative reference implementation of a seven-agent claims-processing
pipeline for low-value, weather-triggered food-spoilage insurance claims — modeled on
publicly disclosed information about Allianz Australia's "Project Nemo" system.

**This is not Allianz Australia's actual system.** No technical architecture for the real
Project Nemo has been publicly disclosed at any level of detail — not the model, not the
orchestration framework, not the decision thresholds. What *is* publicly confirmed: seven
agent roles, a human-only payout decision, and an AUD$500 claim ceiling. Everything else in
this repository — the execution order, the data-dependency reasoning, the payout-enforcement
mechanism, every system prompt, and all the code — is this project's own construction of
*one plausible way* to build a system matching that public description. Read this repo as a
learning tool and a starting point, not as a disclosure of anyone's proprietary system.

---

## Who this is for

This repo is written for two kinds of readers, deliberately:

- **A developer with no insurance background.** You don't need to know anything about
  claims processing going in — the glossary below and the walkthrough in this README
  should get you oriented in under an hour.
- **An insurance or claims professional with no coding background.** You don't need to read
  the code to understand what this system does and why it's built this way — this README
  is written to stand on its own.

Everyone should be able to clone this, understand it, and extend it — that's the design
goal, not runtime performance or production-readiness.

---

## Domain glossary

| Term | Meaning in this repo |
|---|---|
| **Food-spoilage claim** | An insurance claim for food that spoiled because a power outage stopped a fridge/freezer from working. |
| **NatCat event** | "Natural Catastrophe" — industry shorthand for a severe-weather event (storm, flood, etc.) that triggers many claims at once. |
| **Coverage** | Whether a specific loss is included under a policyholder's insurance contract. |
| **Claims-audit log** | An append-only record of every decision made in a claim's processing, kept for compliance and dispute resolution. |
| **Settlement / payout** | The amount of money actually paid to the policyholder for a claim. |
| **Structured output** | An LLM response constrained to a specific, machine-parseable shape (e.g. `{"determination": "covered", ...}`) instead of free-form text. |
| **Fail-fast** | Checking the cheapest/fastest disqualifying condition first, so a claim that's going to be rejected exits early without wasting effort on later, more expensive checks. |

---

## What the pipeline does, in plain language

A homeowner's power goes out during a storm. Their fridge contents spoil. They file a claim.
Seven specialized steps then run automatically to prepare a recommendation — but a human
claims professional makes the actual payout decision. No step in this pipeline can execute a
payment on its own.

1. **Planner** — reads the raw claim and turns it into structured data (claim ID, amount,
   location, timestamp).
2. **Coverage** — checks whether the policyholder's policy actually covers food spoilage
   from a severe-weather outage.
3. **Weather** — checks external weather data to confirm a matching severe-weather event
   actually happened at that location and time.
4. **Fraud** — screens for signs of fraud, specifically weighing whether Weather found a
   match (an unmatched weather event is itself a red flag) alongside the policyholder's
   claim history.
5. **Payout** — calculates a *recommended* settlement amount. It cannot execute a payment.
6. **Audit** — writes a structured summary of everything the previous steps found, for a
   human to read.
7. **Human review** — a claims professional reads the Audit summary and makes the binding
   decision. Only this step can actually authorize money to move.

Running throughout all of this (not as a numbered step, but wrapped around every other
step) is **Cyber** — a guardrail layer that checks each agent only touches the data it's
supposed to, and halts the whole pipeline if one doesn't.

---

## Why this execution order, specifically

This is the part of the design that's easiest to get wrong, so it's spelled out explicitly
rather than left to be inferred from the code.

- **Coverage runs before Weather.** Not because Coverage needs Weather's answer — it
  doesn't. It's a **fail-fast choice**: if a claim isn't covered at all, there's no reason to
  spend a weather-API call or a fraud check on it. An uncovered claim exits the pipeline
  immediately. (See `data/stub_scenarios.py`'s `UNCOVERED_CLAIM` scenario, and
  `tests/test_workflow.py`'s `test_uncovered_claim_exits_at_coverage` — this behavior is
  actually tested, not just asserted in a comment.)
- **Fraud genuinely requires Weather's result — this is a real dependency, not a
  preference.** Whether a matching weather event was found is itself one of the signals the
  Fraud agent weighs: an unmatched event is a fraud indicator. Fraud's judgment is
  materially different depending on what Weather concluded. (See the `NO_WEATHER_MATCH`
  scenario and its corresponding test — this dependency is exercised, not just described.)
- **Payout requires both Coverage's and Fraud's conclusions.** This is a genuine
  convergence point — a recommendation can't be produced for a claim that hasn't cleared
  both checks.
- **Audit requires everything that ran before it**, for the same reason — it's summarizing
  a process, and can't summarize what hasn't happened yet.
- **Cyber is a wrapper, not a step**, because nothing about its role ("oversee the whole
  process for security and guardrails") is actually sequential — it needs to see every
  agent's call, not just one position in a line.

**`[DEV]` extension point:** Coverage and Weather have no real dependency on each other and
could run in parallel for a latency improvement. This repo ships them sequential, on
purpose — the latency budget doesn't need it, and sequential logic is easier for a reader to
follow. If your use case genuinely needs the latency, `workflow/orchestrator.py` is where to
make that change; nothing else needs to change to support it.

---

## The payout gate: what "a human always decides" means as actual code

A stated principle ("payout decisions are never automated") isn't worth much if it's just a
sentence in a system prompt — a model can ignore an instruction, and a prompt-injection
attack can try to talk it out of following one. This repo enforces the principle in code
instead:

- The Payout agent's output is labeled a **recommendation only**. It has no write access to
  any payout system (see `agents/payout.py`'s data-access notes).
- `workflow/payout_gate.py`'s `PayoutExecutionAPI` will not execute anything without a
  `ClaimDecisionToken` — a signed, claim-scoped, single-use token.
- **Only `HumanReviewSystem` can create that token.** No agent, anywhere in this codebase,
  imports or calls `HumanReviewSystem`.

This is this repo's own construction of how to satisfy that stated principle — it is not a
claim about how any real insurer's system actually enforces it.

---

## Multi-provider support — and what "supported" honestly means here

This workflow works with **Claude, OpenAI, and Gemini**, selected via the `NEMO_PROVIDER`
environment variable (see `.env.example`). Every agent is written once, against the
`LLMProvider` interface (`providers/base.py`) — agents never import a provider SDK
directly, so switching providers is a config change, not a code change.

### Provider Verification Status — read this before you pick a provider

There are three distinct levels of "verified" here, and conflating them is exactly the
kind of error this project's source case study is built to catch:

1. **Syntax-verified** — all three adapters parse and import cleanly. True for all three.
2. **Adapter-logic verified** — `tests/test_provider_adapters.py` mocks each provider's SDK
   client entirely and confirms each adapter correctly builds a request and parses a
   response shaped the way that SDK's own documentation says it will be. **This is true for
   all three, and it's actually been run** — 9 tests, all passing. This catches wrong
   method/attribute names, broken JSON parsing, and incorrect error handling.
3. **Live-API verified** — actually confirmed against a real Claude/OpenAI/Gemini API call.
   **This is not true for any of the three.** The build environment this repo was assembled
   in had no network access, so nothing here has watched a real model actually return a
   real structured response through these adapters.

**What this means for you:** level 2 gives real confidence the adapter code itself isn't
obviously broken — it's a meaningfully stronger claim than "it compiles." It does **not**
tell you whether the schema translation actually satisfies each provider's real
structured-output mechanism in practice, whether the SDK version you install matches what
these mocks assumed, or whether a real model's response ever comes back shaped slightly
differently than documented. **The first thing you should do after cloning this repo is add
your own API key and runtime-verify at least one provider (level 3)** — that's still the
genuine next step, not busywork, and it's the one thing in this repo that cannot be checked
without your own environment and your own judgment about what counts as a good result.

---

## Repository structure

```
allianz-australia-nemo-claims-workflow/
├── README.md                  # this file
├── requirements.txt
├── .env.example                # copy to .env and fill in your keys
├── config.py                  # reads NEMO_PROVIDER / NEMO_THRESHOLD_AUD from env
├── models/claim.py            # Claim, PolicyRecord, AgentOutput shared shapes
├── providers/
│   ├── base.py                 # the LLMProvider contract every adapter implements
│   ├── claude_provider.py
│   ├── openai_provider.py
│   └── gemini_provider.py
├── agents/                    # one file per agent — see each file's own docstring
│   ├── planner.py
│   ├── coverage.py
│   ├── weather.py
│   ├── fraud.py                # includes the [DEV] flagged-claim extension point
│   ├── payout.py
│   ├── audit.py
│   └── cyber.py                # cross-cutting wrapper, not an LLM agent
├── workflow/
│   ├── orchestrator.py         # wires all seven agents together in order
│   └── payout_gate.py          # the token-gated enforcement mechanism
├── data/stub_scenarios.py     # 3 fixtures: happy path, uncovered claim, no-weather-match
├── api/main.py                 # FastAPI wrapper
├── cli/demo.py                 # command-line demo runner
└── tests/
    ├── fake_provider.py         # scripted test double — no API keys needed to run tests
    ├── test_workflow.py         # tests the orchestration logic against all 3 scenarios
    └── test_provider_adapters.py  # tests each adapter's logic against mocked SDK clients
```

---

## Running this repo

### 1. Install dependencies
```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env: set NEMO_PROVIDER and the matching API key
```

### 2. Run the tests (no API key needed — uses FakeProvider and mocked SDK clients)
```bash
python -m pytest tests/test_workflow.py -v            # orchestration logic, all 3 scenarios
python -m pytest tests/test_provider_adapters.py -v   # adapter logic, mocked SDK clients
```
Neither of these calls any real LLM API. See "Provider Verification Status" above for
exactly what each level of testing does and doesn't prove.

### 3. Run the CLI demo (needs a real API key for your chosen provider)
```bash
python -m cli.demo --provider claude --scenario happy_path
python -m cli.demo --provider claude --scenario uncovered_claim
python -m cli.demo --provider claude --scenario no_weather_match
```

### 4. Run the API
```bash
uvicorn api.main:app --reload
# POST /claims/happy_path/run
# POST /claims/{claim_id}/review   {"approved": true}
```

---

## Extension points — the human decisions this repo deliberately left for you

Every `[DEV]` comment in the code marks a specific place where a design choice was made and
could reasonably go a different way. The most significant ones, gathered here:

- **Fraud-flagged claims halt the pipeline; no investigation workflow is built.** There's no
  public description of what a real fraud-investigation queue actually does beyond "a human
  reviews it" — building that out further would be invented process dressed up as reference
  design. If you need one, `agents/fraud.py` and `workflow/orchestrator.py` both mark exactly
  where to add it.
- **Coverage/Weather parallelization** — currently sequential; see "Why this execution
  order" above for the reasoning, and `workflow/orchestrator.py` for where to change it.
- **The AUD threshold is configurable** (`config.py` / `.env`), not hardcoded — it's a policy
  fact, not a code constant.
- **Provider runtime verification** — see "Provider Verification Status" above. This is the
  single most important thing to do next.
- **Human-reviewer authentication** — `workflow/payout_gate.py`'s `HumanReviewSystem` takes
  a plain `reviewer_id` string with no authentication behind it. A real deployment needs
  SSO/session-based auth in front of this; it's out of scope for this reference build.
- **Cyber's guardrail scope** — currently checks data-access boundaries only. Rate limiting,
  PII redaction, and cross-call anomaly detection are all named as future additions in
  `agents/cyber.py` but not built.

---

## What's confirmed vs. constructed, one more time

**Publicly confirmed:** the seven agent roles and their high-level functions; that payout
decisions are made by a human, by design; the AUD$500 claim ceiling; that the whole AI phase
completes in under five minutes for the confirmed example claim.

**This repo's own construction, not a disclosure:** the execution order, every dependency
argument above, all system prompts, the token-gated payout mechanism, the multi-provider
interface, and all code. Build on it, question it, and change anything that doesn't hold up
once you dig in — that's the point of a reference implementation, not a limitation of one.
