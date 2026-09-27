# Aladdin Private Credit Query Pipeline — Reference Implementation

> **This is an illustrative reference implementation, not BlackRock's proprietary system.**
> It's a recipe for how to build this class of system, grounded in BlackRock's publicly
> documented architecture patterns for Aladdin Copilot — not a specification of BlackRock's
> actual implementation. Internal identifiers, thresholds, stub data, and exact API
> contracts throughout this repo are invented for teaching purposes.

Fork it, clone it, break it, change it. That's the point.

---

## What this is (and isn't)

A working, runnable pipeline that answers natural-language questions about private credit
positions — parses the question, retrieves relevant data, computes standard credit
benchmarks, checks its own output for unsupported figures, and hands a verified answer to
a human. **It never recommends an action or takes one.** It reports what it found; a person
decides what happens next.

This is a **blueprint**, not a production system. If you're evaluating whether this is safe
to point at real money or real client data: it isn't, not without a lot more work — see
the disclaimers below, which are not boilerplate.

## Who this is for

Two different readers, two different paths through this repo:

- **If you code but don't know finance**: start with `src/pipeline.py` to see the whole
  flow in one place, then read each module in `src/` — every one has a docstring
  explaining what it does and why. The Domain Glossary below will get you through the
  finance vocabulary fast.
- **If you know finance but don't code**: the Domain Glossary, Architecture Overview, and
  Worked Examples sections below are written for you — you shouldn't need to open a
  single `.py` file to understand what the system does and why it's built this way.

Either way, budget 2–3 hours to go from opening this repo to being able to explain what
each part does in your own words. That's the actual goal here — not memorizing the code,
understanding the pattern.

## Quickstart

```bash
git clone <this-repo>
cd blackrock-aladdin-private-credit-workflow
pip install -r requirements.txt
cp .env.example .env   # fill in ONE provider's API key — you don't need all three
```

**Option A — curl, no Python editing required:**
```bash
uvicorn api:app --reload
# in another terminal:
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is our exposure to Example Industrial Holdings, and is leverage elevated?"}'
```

**Option B — CLI:**
```bash
python3 run_demo.py "Are there coverage concerns for Riverside Distribution Partners?"
```

**Option C — no API key at all, see the guardrail in action:**
```bash
python3 tests/test_guardrail_scenarios.py
```
This runs three real scenarios against fake LLM responses — a clean draft, a hallucinated
figure that gets caught and corrected, and one that stays wrong and gets escalated visibly.
Good starting point if you want to understand the guardrail before touching a real LLM call.

---

## Domain Glossary — the five numbers this system computes, in plain language

If you don't have a finance background, read this before anything else. Every formula
below uses the exact field names from `src/benchmark_calculator.py`, so you can match
this explanation directly to the code.

**Money Multiple** — `current_value ÷ invested_capital`
How much a dollar invested has become. A money multiple of 1.45x means every dollar put
in is now worth $1.45. **Below 1.0x means the position is worth less than what was put
in — capital impairment, by definition, not a judgment call.**

**Leverage Ratio** — `debt_outstanding ÷ ebitda`
How many years of the company's core earnings (EBITDA) it would take to pay off all its
debt. Higher means more debt relative to earning power, which means more risk if earnings
decline. This repo flags anything above 6.0x as elevated — a common industry rule of
thumb, not a hard rule.

**Debt Service Coverage Ratio (DSCR)** — `ebitda ÷ interest_expense`
How comfortably earnings cover interest payments. A DSCR of 1.25x means earnings are 25%
more than what's strictly needed to cover interest — a real cushion. **Below 1.0x means
earnings don't even cover the interest bill**, which is a serious warning sign in its own
right, not just a rule-of-thumb flag. This repo flags anything below 1.25x.

**Equity Cushion** — `(current_value − debt_outstanding) ÷ current_value`
What fraction of the asset's value would belong to equity holders if it were sold today,
after paying off debt. A thin or negative cushion means lenders have a claim on most or
all of the value — equity holders absorb the first losses if value keeps dropping. This
repo flags anything below 20%.

**Valuation Trend** — `(current_value − prior_period_value) ÷ prior_period_value`
Simple percentage change in the asset's value since the last measurement. Positive means
appreciating, negative means declining. There's no "threshold" here — any decline gets
flagged, since direction matters more than degree for this one.

**Why these five and not others**: together they answer four different questions — "is
this worth more or less than what went in" (money multiple), "is it becoming more or less
valuable over time" (valuation trend), "how much debt is riding on this" (leverage ratio),
"can earnings actually service that debt" (DSCR), and "who eats the loss first if value
drops further" (equity cushion). A single ratio can look fine while another one is
flashing red — that's why the pipeline reports all five together, not just the ones that
happen to look bad.

---

## Worked Examples — two real queries, traced end to end

These are the actual numbers this repo's stub data produces — pulled from real code
execution, not hypothetical.

### Example 1: a healthy position

**Query**: *"What's our exposure to Example Industrial Holdings, and is leverage elevated?"*

| Metric | Value | Flagged? |
|---|---|---|
| Money multiple | 1.452x | No |
| Leverage ratio | 2.947x | No — well under 6.0x |
| Valuation trend | +5.17% | No — appreciating |
| Equity cushion | 54.1% | No — well above 20% |
| DSCR | 4.524x | No — well above 1.25x |

Nothing here is flagged. The synthesized answer reports a healthy position with no
concerns, the guardrail verifies every figure cleanly, and the human reviewer sees a
clean, unremarkable answer. This is the "everything's fine" path — worth seeing once so
you know what normal looks like before you look at the distressed example.

### Example 2: a distressed position — the stress test

**Query**: *"How is our position in Riverside Distribution Partners performing, and are
there any coverage concerns?"*

| Metric | Value | Flagged? |
|---|---|---|
| Money multiple | 0.704x | **Yes — capital impairment** |
| Leverage ratio | 7.500x | **Yes — elevated leverage** |
| Valuation trend | -17.4% | **Yes — declining valuation** |
| Equity cushion | -26.3% | **Yes — thin/negative cushion** |
| DSCR | 1.143x | **Yes — coverage concern** |

All five metrics flagged — a genuinely distressed asset, invented specifically to exercise
every warning path at once. Notice the equity cushion is *negative*: debt outstanding
(\$24M) actually exceeds the current asset value (\$19M), meaning even a full liquidation
wouldn't cover what's owed. This is the scenario that exercises the guardrail hardest —
`tests/test_guardrail_scenarios.py` uses this exact asset to test what happens when a
synthesized draft misstates a figure (simulating a hallucination) and confirm the system
either catches and corrects it, or escalates visibly rather than failing silently.

---

## Architecture Overview

Four phases, always in this order, triggered only by a human question — nothing in this
pipeline runs on its own:

1. **Query intake and parsing** — a person asks a question in plain English.
2. **Scoped retrieval** — the system figures out which of its two data sources it actually
   needs, and pulls from them at the same time (not one after another).
3. **Calculation, synthesis, and verification** — standard credit ratios get computed, an
   LLM writes a plain-language summary, and a separate, non-LLM check confirms every
   number in that summary is actually grounded in the computed data.
4. **Human review** — a person reads the (verified) answer and decides what, if anything,
   happens next. Nothing here acts on the answer automatically.

There's no execution stage and no approval-gate mechanism, unlike the compliance and
credit-underwriting workflows elsewhere in this case study series — this pipeline has no
authority to act on its own output, so there's nothing downstream to architecturally block.

### Why calculation → synthesis → guardrail, specifically, in that order

It might look more natural to check the numbers *before* an LLM writes prose about them —
catch a bad calculation before anyone talks about it. But the guardrail's actual job is
catching **hallucination**, not catching arithmetic errors. Raw benchmark figures are
deterministic math computed straight from retrieved data — nothing to hallucinate there.
The hallucination risk enters specifically when the LLM-backed Synthesis module writes
natural-language prose *around* those numbers and might state a figure that was never
actually computed. A guardrail that ran before synthesis would have nothing generated yet
to check — this is why the order here is deliberate, not incidental.

### Why the two data adapters aren't fully independent

The private credit adapter and portfolio holdings adapter run concurrently, and for most
queries that's genuinely safe — they don't need each other's output. But a query scoped by
*borrower name* rather than *fund ID* breaks that independence: portfolio records are only
keyed by fund ID, not borrower name, so the pipeline has to first resolve which fund a
named borrower belongs to (from the private credit adapter's result) before it can
correctly narrow the portfolio data to the right fund. This repo handles that with a
post-retrieval join in `pipeline.py`, done right after both adapters return. A system
serving borrowers with positions spread across many funds would need a dedicated
borrower-to-fund lookup performed *before* scoping, not after — this repo's simpler
approach works because each fictional borrower here maps to exactly one fund.

---

## Component Walkthrough

| Component | What it does | Where |
|---|---|---|
| Orchestrator | Turns your question into structured intent (which entity, which metrics) | `src/orchestrator.py` |
| Registry filter | Decides which of the two data sources this question actually needs | `src/registry_filter.py` |
| Adapters | Fetch data — one for private credit fund/asset data, one for portfolio positions | `src/adapters.py` |
| Benchmark calculator | Computes the five ratios from the Domain Glossary above | `src/benchmark_calculator.py` |
| Synthesizer | Writes a plain-language answer — reports findings, never recommends action | `src/synthesizer.py` |
| Guardrail | Checks every number in that answer against what was actually computed | `src/guardrail.py` |
| Audit log | Optional record of what each step did, for a given query | `src/audit_log.py` |
| Pipeline | Wires all of the above together in the right order | `src/pipeline.py` |
| LLM providers | Swappable interface — Claude, OpenAI, or Gemini, your choice | `src/llm_providers.py` |
| Human reviewer | Not code — see below | — |

### Registry filter — why hard-coded rules instead of something smarter

This repo has exactly two data sources. Building an embedding-based retrieval system to
decide between two options is solving a problem this repo doesn't have. Simple keyword
matching against the requested metrics is not a shortcut here, it's the correct-sized
solution — reconsider only if you add more than two or three data sources.

### LLM providers — why all three are fully implemented, not just one

Not every learner forking this repo defaults to the same LLM vendor. Someone with an
OpenAI subscription shouldn't have to reverse-engineer an Anthropic SDK call as their
first task here. All three providers (`ClaudeProvider`, `OpenAIProvider`,
`GeminiProvider`) are real, working implementations — pick yours via the `PROVIDER`
environment variable, no code editing required.

### Guardrail — why it guarantees no silent failure, not that it always self-corrects

When the guardrail can't verify a figure, it tries exactly one silent regeneration. If
that succeeds, the answer is clean. If it doesn't — and LLM behavior here is genuinely
non-deterministic, not a reliable switch — the system escalates visibly, every time, with
no second silent attempt. **What's guaranteed: an unverified number never reaches you
silently. What's not guaranteed: the first retry always fixes it.** Both outcomes are
correct behavior; only one of them looks clean.

**The human reviewer** is the actual final step, worth stating plainly for anyone who
isn't a developer reading this: after the pipeline produces an answer, a person applies
judgment the system doesn't have access to, and decides what — if anything — happens
next. This system never places a trade, flags a covenant breach to a counterparty, or
takes any action. It answers a question. What a person does with that answer is entirely
outside this repo's scope, by design.

---

## Disclaimers that matter — please actually read these

### The benchmark thresholds are illustrative, not risk-reviewed

The five formulas above are standard, correct private-credit math. The thresholds that
decide when something gets *flagged* (leverage above 6.0x, DSCR below 1.25x, equity
cushion below 20%, money multiple below 1.0x) are common industry rule-of-thumb reference
points, included so the numbers mean something pedagogically — **they are not
BlackRock's actual risk policy, and they have not been reviewed by any risk or analytics
function.** This is disclaimed on purpose in three places: `benchmark_calculator.py`'s
docstring, a warning logged every time it runs, and here. **Do not use these thresholds
for a real credit decision.**

### The stub data is invented

"Example Industrial Holdings" and "Riverside Distribution Partners" don't exist. Every
record in `data/*.json` is fictional. See `data/README.md`.

---

## Extension Points

Things this repo deliberately leaves for you to build, not because they're hard, but
because they're outside what this reference implementation is trying to teach:

- **Chart/visual output** — add a rendering step after `ResponseSynthesizer.draft()`;
  it's a presentation-layer addition, not a change to pipeline logic.
- **More data sources** — add a new `Adapter` subclass and register it in
  `build_default_pipeline()`. Once you have more than two or three tools, revisit
  `registry_filter.py`'s hard-coded rules — that's the point where embedding-based
  retrieval over tool descriptions starts earning its complexity.
- **A different audit log backend** — swap `AuditLog`'s file-append for a database or
  structured logging service; the interface (`append(query_id, module, output)`) doesn't
  need to change.
- **Borrower-to-fund resolution as a real lookup step** — instead of the post-retrieval
  join this repo uses, if you're modeling borrowers with positions across multiple funds.

---

## Troubleshooting

**"Set ANTHROPIC_API_KEY..." (or OPENAI_API_KEY / GEMINI_API_KEY) error on startup**
You haven't filled in `.env`. Copy `.env.example` to `.env` and add the one key matching
whichever `PROVIDER` you set — you only need one, not all three.

**`ModuleNotFoundError` for `anthropic`, `openai`, or `google.genai`**
You only need the package matching your chosen `PROVIDER`. If `PROVIDER=claude`, you need
`anthropic` installed, not the other two. Check `requirements.txt`'s comments.

**The guardrail escalates on almost everything, even for what looks like a normal query**
Check that your query actually names one of the two stub borrowers ("Example Industrial
Holdings" or "Riverside Distribution Partners"). A query naming an entity that doesn't
exist in the stub data returns no benchmark results at all — with nothing to verify
figures against, the guardrail has no way to confirm anything, so it escalates by design
rather than guessing. This is a known, disclosed limitation of the two-record stub
dataset, not a bug in the verification logic itself.

**The Orchestrator fails after two attempts to parse your query**
LLMs asked for structured JSON don't always comply, especially with unusual phrasing. Try
rephrasing the question more directly ("What is the leverage ratio for X"), or try a
different provider — compliance with format instructions varies by model.

**`ModuleNotFoundError: fastapi` when running `uvicorn api:app`**
Run `pip install -r requirements.txt` first — `fastapi` and `uvicorn` are required
regardless of which LLM provider you use.

---

## Running the tests

```bash
python3 tests/test_guardrail_scenarios.py
```

No API key required — this uses fake LLM responses to exercise three real scenarios: a
clean draft, a hallucination the guardrail catches and fixes, and one that persists and
gets escalated. If you're learning this codebase, start here before touching a live provider.
