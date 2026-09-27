# How Mycroft picks models today

Findings for the Adaptive Model Routing & Inference Gateway.
Written 2026-09-02; updated 2026-09-10 with live-call and fixture results.
Based on a read of scripts/, recipes/, case-study-workflows/, projects/, data/,
and logs/RUN_LOG.md. No PM or billing access was available; every claim below
cites a file or a logged call.

## 1. Model choice is hardcoded four incompatible ways

None is a routing abstraction, and one is not machine-readable at all.

| Where | How the model is chosen | Readable by code? |
|---|---|---|
| 204 stub scripts in `scripts/tools/` | Baked into the filename and a `NODE_NAME` constant, e.g. `'Groq Chat Model'`, `'Anthropic Model 3'` | No — an identity, not a setting |
| `scripts/tools/llm-model-invocation.py` | A `provider` payload field defaulting to `google_gemini`, with a `credential_env` lookup | Yes — but the file cannot be imported |
| `recipes/vendor-intelligence-brief.yaml:107` | Prose inside a description: `LLM (AWS Bedrock Nova Micro)` | No — it is documentation |
| 8 dirs under `case-study-workflows/` | `llm_provider/factory.py`, env-selected among fake/claude/gpt/gemini | Yes — but duplicated per workflow |

## 2. No live call existed in this repository

- 204 files under `scripts/tools/` hardcode `"live_call_performed": False`.
- Zero SDK or HTTP imports (`anthropic`, `openai`, `groq`, `httpx`, `requests`)
  anywhere under `scripts/`, excluding the quarantined `scripts/mycroft-main/`.
- No `requirements.txt` or `pyproject.toml` at the repo root.

The gateway is the first real inference path this repository has had.

## 3. 101 scripts cannot be imported

Every shared module is stored with hyphens and imported with underscores —
e.g. `scripts/gigo/ai-talent-shared.py` imported as `scripts.gigo.ai_talent_shared`.
A hyphen is a minus sign in Python, so these can never resolve. There are also
no `__init__.py` files. All 10 distinct shared-module imports are broken,
affecting 101 of 460 scripts across `tools/`, `gigo/`, and `ingest/`.

Consequence: `scripts/gateway/` imports nothing from those trees.

## 4. What Mycroft actually pays for

**One free-tier Groq account is the only provider with evidence of real use.**

### Evidence for Groq

- `scripts/gigo/ai-talent-shared.py:201` is the only script in the repo naming a
  concrete provider/model/credential triple:
  `{"provider": "groq", "model": "llama-3.1-8b-instant", "credential_env": "GROQ_API_KEY"}`
- `logs/RUN_LOG.md:92` — `[BLOCKER] Groq token limit at company #33 of 50 batch`
- `logs/RUN_LOG.md:99` — `Phase 3: Solve Groq token limit (upgrade tier or
  secondary provider for news classification)`

Hitting a token ceiling partway through a 50-company batch, with "upgrade tier"
named as a candidate fix, indicates a **free tier**. No paid plan is evidenced
anywhere in the repo.

### Everything else is configured, not confirmed

| Provider | What the repo shows | Reading |
|---|---|---|
| Anthropic | 44 `ANTHROPIC_API_KEY` references, all in the 8 case-study reference workflows or `finance-event-signals`, where `LLM_PROVIDER=deterministic` is the default | Configured, not evidenced |
| OpenAI / Gemini | Alternates in `.env.example` files that say "fill in the one provider you're using" | Options, not commitments |
| Ollama | `OLLAMA_BASE_URL` → `localhost:11434` | Local, free, no key |
| HuggingFace | One spec, `ProsusAI/finbert` — an embedding model | Not a chat tier |
| AWS Bedrock Nova Micro | Prose in `recipes/vendor-intelligence-brief.yaml:107`; no credential reference anywhere | Documentation only |

### Tier models changed on 2026-09-02

The evidenced models could not be used. Groq publishes no per-token rate for
`llama-3.1-8b-instant` or `llama-3.3-70b-versatile` — both show "Contact Sales"
(https://console.groq.com/docs/models, read 2026-09-02). `prices.json` refuses
unpriced models by design, so the gateway could not call them.

All three tiers moved to publicly priced models on the same Groq key:

| Tier | Model | Input /1M | Output /1M |
|---|---|---|---|
| cheap | `openai/gpt-oss-20b` | $0.075 | $0.30 |
| mid | `openai/gpt-oss-120b` | $0.15 | $0.60 |
| strong | `qwen/qwen3.6-27b` | $0.60 | $3.00 |

The provisional Ollama strong tier was dropped: its $0 marginal cost made every
cost comparison degenerate, and a priced strong tier removed the reason to keep it.

Cost of the change: no Mycroft project has used these models before. Benefit:
a defensible cost number, without which Sprints 8–9 have no result.

### Open question for whoever holds the budget

Groq's free-tier limit already blocked a production batch once (RUN_LOG
2026-07-09). Sprints 7–8 run at volume. Either a paid tier or a second provider
is needed before then — a spending decision, not an engineering one.

All three tiers now share one provider and one key, so a rate limit or an auth
failure takes out the whole ladder at once. There is no tier to escalate to.

## 5. What the first live calls showed

Six gated calls, 2026-09-02 and 2026-09-10, prompt `"Reply with exactly one
word: ok"`. Source: `logs/gateway/first-live-call.jsonl`.

| # | Tier | max_tokens | In | Out | Cost | Latency | Result |
|---|---|---|---|---|---|---|---|
| 1 | cheap | 16 | 78 | 16 | $0.00001065 | 1,126 ms | empty — budget spent on reasoning |
| 2 | cheap | 256 | 78 | 77 | $0.00002895 | 382 ms | `ok` |
| 3 | cheap | 256 | 0 | 0 | $0.00 | 177 ms | invalid key → `provider_error` |
| 4 | mid | 256 | 78 | 47 | $0.00003990 | 617 ms | `ok` |
| 5 | strong | 256 | 17 | 181 | $0.00055320 | 1,170 ms | `ok` wrapped in a `<think>` block |
| 6 | strong | 256 | 17 | 245 | $0.00074520 | 1,424 ms | `ok`, after the fix |

Total spend $0.00138; the two strong calls are 94% of it. Every successful
call's cost was recomputed from the price table and matched the log exactly.
These are single observations on one trivial prompt — signals to test, not
conclusions.

**The price table does not give the cost.** Reasoning tokens are billed, and
each model reasons a different amount:

| | Sticker (output price) | Observed on this prompt |
|---|---|---|
| cheap → mid | 2× | 1.4× — the bigger model reasoned less (47 vs 77 tokens) |
| cheap → strong | 10× | 19–26× — qwen reasoned 181–245 tokens at the top price |

On this evidence, starting cheap only beats starting mid if cheap is right
more than ~73% of the time.

**Models expose reasoning differently.** `gpt-oss` keeps reasoning out of the
response text. `qwen3.6-27b` returned it inline, in `<think>...</think>` tags,
ahead of the answer. That response passed every check the gate had at the
time — it was well-formed and wrong. Fixed by `strip_reasoning()` in the Groq
adapter, plus an answer check in the gate script. Left unfixed, every
validator would have failed the strong tier.

**Reasoning length varies run to run.** Calls 5 and 6: identical prompt,
181 vs 245 output tokens, +35% cost. One call is not a cost measurement.

**The strong tier was near its budget.** 245 of 256 tokens used — 11 from
truncation, which returns an empty answer. `policy.json` now gives strong 1,024.

**Input tokens depend on the model.** 78 for `gpt-oss`, 17 for `qwen`, same
prompt. The overhead is `gpt-oss`'s prompt format, not a general cost.

**Cold start.** Call 1 took 1,126 ms, call 2 382 ms, same model. Call 4 was the
first call in its session. Latency across these calls is not yet comparable.

**Auth errors must not escalate.** A 401 is `provider_error`, correctly — but
every tier shares the key, so a retry fails identically.

**`outcome: "ok"` means the provider returned, not that the answer is usable.**
Calls 1 and 5 were both `ok`.

## 6. What the first fixture set showed

24 synthetic fixtures, 4 per task type, labeled and frozen 2026-09-10
(`scripts/gateway/bench/manifest.json`). No model has been run on them yet —
these are findings about the router and the checks, not about models.

**The simple router cannot reach strong on a short input.** Its only paths to
strong are a long input or escalation. Every seed input is under 200
characters, so the router sent 8 fixtures to cheap, 16 to mid and 0 to strong.
The labeler put 7 on strong — all short inputs with a trap. Router and labels
agree on 9 of 24. The labels are predictions; this is not yet a measurement.

**Deterministic checks catch malformed answers, not wrong ones.** A misread
sarcastic post still returns a valid label, so `label_in_set` passes and
nothing escalates. The benchmark sees the error because it has an answer key;
production has none. This is the main design risk for Sprints 4–5.

**Some fixtures test the checks, not the models.** `summ-004`: a correct unit
conversion fails `numbers_grounded`. `summ-003`: the superseded figure passes
it. `extract-004`: an invented value passes `required_keys`.

**Why the fixtures are synthetic.** No real request corpus exists in the repo:
203 of 217 script sample payloads are generic placeholders;
`data/raw/market-sentiment-analysis-part-1/sample/` declares itself synthetic;
the Klarna mock transactions file holds 0 records. Fictional companies are
used so no fixture can be mistaken for market data. Results will support claims
about how models handle these task types — not about Mycroft's real traffic mix.

## 7. Consequences

- Policy refers to tier names, never models; `prices.json` stays versioned.
- `max_tokens` is set per tier in `policy.json`; 256 was too tight for strong.
- The router measures input in characters, because token counts depend on the model.
- Sprint 4 must separate transient errors (rate limit, 5xx, timeout) from
  terminal ones (401, unknown model).
- Sprint 4–5: escalation driven only by deterministic validators will miss
  wrong-but-valid answers. Decide what, if anything, triggers escalation for
  label and verdict tasks.
- Sprint 7 should run every fixture on all three tiers, several times each,
  discarding a warmup call — so the cheapest correct tier is measured rather
  than predicted, and cost is reported as a spread.
- Sprint 8 must compare cost per *useful answer*, not per token.
