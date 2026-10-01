# How Mycroft picks models today

Findings for the Adaptive Model Routing & Inference Gateway.
Written 2026-09-02; updated 2026-09-10 (live calls), 2026-09-17 (fixture set
and first full run). Based on a read of scripts/, recipes/,
case-study-workflows/, projects/, data/, and logs/RUN_LOG.md. No PM or billing
access was available; every claim below cites a file or a logged call.

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

### Tier models changed twice

**2026-09-02.** Groq publishes no per-token rate for `llama-3.1-8b-instant` or
`llama-3.3-70b-versatile` — both show "Contact Sales". `prices.json` refuses
unpriced models by design, so the gateway could not call the models the repo
evidenced. All three tiers moved to publicly priced models on the same key.

**2026-09-17.** `qwen/qwen3.6-27b` began returning 404 "does not exist or you
do not have access", after two successful calls on 2026-09-10. It is gone from
Groq's model list. Groq's own deprecation page still recommends it as a
migration target, so their docs contradict their API. Replaced with
`qwen/qwen3.8-27b`.

| Tier | Model | Input /1M | Output /1M |
|---|---|---|---|
| cheap | `openai/gpt-oss-20b` | $0.075 | $0.30 |
| mid | `openai/gpt-oss-120b` | $0.15 | $0.60 |
| strong | `qwen/qwen3.8-27b` | $0.80 | $4.00 |

A pinned model can disappear between runs. That is an argument for checking
model availability at the start of a sweep rather than discovering it mid-run.

### Open question for whoever holds the budget

Groq's free-tier limit already blocked a production batch once (RUN_LOG
2026-07-09), and the strong tier's output cap of 1000 tokens per minute now
limits a full benchmark sweep to roughly one strong call per minute. Sprints
7–8 run at volume. Either a paid tier or a second provider is needed — a
spending decision, not an engineering one.

All three tiers share one provider and one key, so a rate limit or an auth
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

Every successful call's cost was recomputed from the price table and matched
the log exactly. These are single observations on one trivial prompt.

**The price table does not give the cost.** Reasoning tokens are billed, and
each model reasons a different amount:

| | Sticker (output price) | Observed on this prompt |
|---|---|---|
| cheap → mid | 2× | 1.4× — the bigger model reasoned less (47 vs 77 tokens) |
| cheap → strong (3.6) | 10× | 19–26× — qwen reasoned 181–245 tokens at the top price |

**Models expose reasoning differently.** `gpt-oss` keeps reasoning out of the
response text. `qwen3.6-27b` returned it inline, in `<think>...</think>` tags,
ahead of the answer. That response passed every check the gate had at the
time — it was well-formed and wrong. Fixed by `strip_reasoning()` in the Groq
adapter, plus an answer check in the gate script.

**Reasoning length varies run to run.** Calls 5 and 6: identical prompt,
181 vs 245 output tokens, +35% cost. One call is not a cost measurement.

**Input tokens depend on the model.** 78 for `gpt-oss`, 19 for `qwen`, same
prompt. The overhead is `gpt-oss`'s prompt format, not a general cost.

**Cold start.** Call 1 took 1,126 ms, call 2 382 ms, same model. Latency
across single calls is not comparable.

**Auth errors must not escalate.** A 401 is `provider_error`, correctly — but
every tier shares the key, so a retry fails identically.

**`outcome: "ok"` means the provider returned, not that the answer is usable.**
Calls 1 and 5 were both `ok`.

## 6. What the first fixture set showed

24 synthetic fixtures, 4 per task type, labeled and frozen
(`scripts/gateway/bench/manifest.json`). Findings about the router and the
checks, before any model had been run.

**The simple router cannot reach strong on a short input.** Its only paths to
strong are a long input or escalation. Every seed input is under 200
characters, so the router sent 8 fixtures to cheap, 16 to mid and 0 to strong.
The labeler put 7 on strong — all short inputs with a trap. Router and labels
agree on 10 of 24.

**Deterministic checks catch malformed answers, not wrong ones.** A misread
sarcastic post still returns a valid label, so `label_in_set` passes and
nothing escalates. The benchmark sees the error because it has an answer key;
production has none.

**Some fixtures test the checks, not the models.** `summ-004`: a correct unit
conversion fails `numbers_grounded`. `summ-003`: the superseded figure passes
it. `extract-004`: an invented value passes `required_keys`.

**Why the fixtures are synthetic.** No real request corpus exists in the repo:
203 of 217 script sample payloads are generic placeholders;
`data/raw/market-sentiment-analysis-part-1/sample/` declares itself synthetic;
the Klarna mock transactions file holds 0 records. Fictional companies are
used so no fixture can be mistaken for market data. Results support claims
about how models handle these task types — not about Mycroft's traffic mix.

## 7. What the first full run showed

Three sweeps on 2026-09-17; the final one is `logs/gateway/runs/2026-09-17T015116-sprint4-run.jsonl`.

| | Value |
|---|---|
| Requests / attempts | 24 / 26 |
| Escalation | 8% (`rag-001`, `rag-004`) |
| Failure | 0% |
| Cost | $0.00250 total · $0.000104 per request |
| Latency | p50 393 ms · p95 734 ms |
| Graded | 16 of 24 · 14 correct |

**No wrong-but-valid answers appeared.** The count this sprint exists to
measure — an answer that passes every free check and is still wrong — came out
at **zero real cases** across 24 fixtures, including every deliberate trap:
sarcasm, a headline whose negative words belong to a rival company, two
statements in tension that do not contradict, and two distractor passages that
share the question's keywords. The two entries the run printed under that
heading are answer-key errors: `sent-001` and `sent-004` are keyed `negative`,
the models answered `positive`, and the models are right.

**The cheap tier handled the wrong-entity trap.** `sent-004` attributes
sentiment to the named company while the negative words belong to a rival —
the failure class that reached a finished brief per RUN_LOG. The 20b model got
it right.

**The first check failure was the check's fault, not a model's.** In the 01:44
sweep, all three escalations came from `verdict_with_quote` rejecting a quote
that spanned both statements — a sensible answer to "quote the conflicting
span". After the prompt was narrowed to one continuous span from a single
statement, all four contradiction fixtures passed and graded correct, and
escalation fell from 11% to 8%. The one remaining escalation pair was genuine:
the mid model answered without citing a passage.

**Escalated requests cost 3.2× a single-attempt one.** 8% of requests consumed
23% of the spend: $0.000282 each against $0.000088. Retrying is cheap in
absolute terms and expensive in relative terms, which is exactly why the
trigger has to be right.

**The cost ladder is not monotonic on trivial prompts.** On the gate prompt
the strong tier cost $0.0000232 (19 in / 2 out) against cheap's $0.00002895
(78 in / 77 out) — strong was 20% *cheaper* while its sticker output price is
13× higher. The crossover is near five output tokens: any real answer puts
strong far above cheap. What this establishes is narrow and still useful — the
sticker ratio and the observed ratio can point in opposite directions, and
which model is cheaper depends on how much each one says.

**A model can vanish between runs, and a cap can make a tier unusable.**
`qwen/qwen3.6-27b` 404'd a week after working. Its replacement was then
refused on every call because the configured 1024-token budget exceeded the
account's 1000 output-tokens-per-minute cap — a failure of configuration, not
of the model, which answered fine at 896.

## 8. Consequences

- Policy refers to tier names, never models; `prices.json` stays versioned and
  keeps retired models so old rows stay traceable.
- `max_tokens` is set per tier in `policy.json`, and must stay under the
  account's per-minute output cap or every call is refused before it runs.
- The router measures input in characters, because token counts depend on the model.
- A 429 about pacing is worth one retry; a 429 about request size is not.
- Sprint 5's judge is needed for the 8 extraction and summarization fixtures
  that no deterministic check can grade.
- Sprint 6 should ask whether `numbers_grounded` earns its place, given that it
  fails a correct unit conversion by design.
- Sprint 7 should run every fixture on all three tiers, several times each,
  discarding a warmup call — so the cheapest correct tier is measured rather
  than predicted, and cost is reported as a spread. At the strong tier's
  current cap that is roughly one call per minute.
- Sprint 8 must compare cost per *useful answer*, not per token.

## 9. What the first judged run showed

Three runs on 2026-09-24 -- a 2-fixture smoke (13:29), the full 8 (13:43), and
a 4-fixture re-run after the validator fix (14:00). 14 comparisons, 28 judging
calls, on `summarization` and `rag_answer` only: the tasks where no answer key
can exist. cheap wrote answer A, mid wrote answer B, strong judged, each pair
both ways round.

| result | count |
|---|---|
| tie | 10 |
| mid won | 1 |
| cheap won | 0 |
| inconsistent (verdict flipped when the answers swapped) | 3 |
| unparsed | 0 |

**Judging costs more than answering.** An answer cost $0.000086 on average; a
comparison cost $0.000420 in judging -- 2.4x the cost of producing the two
answers it compares, plus two strong-tier calls of latency. That ratio is the
argument for keeping the judge offline, and it is why a "route by judged
quality" design would be more expensive than always using the strong model.

**Three of 28 answers failed their check over a bracket glyph.** The mid tier
wrote its citation as 【0】 rather than [0], and `cites_context` saw no
citation at all. The answers were correct and cited the right passage. In the
request path each one is an escalation to a dearer tier bought by punctuation
-- the same class of defect as the `verdict_with_quote` false alarms in
section 7, found the same way: by reading what the models actually wrote.
`cites_context` now translates fullwidth brackets before matching, and the
out-of-range check is unchanged, so widening what counts as a bracket did not
widen what counts as a valid passage.

**The judge's disagreements are about degree, not direction.** All three
inconsistent results were `tie` one way round and a winner the other. Not once
did it pick A in one order and B in the other. And all 28 replies were a bare
FIRST / SECOND / TIE at a 256-token budget -- nothing unparseable, no
reasoning leaking into the verdict.

**The same pair judged twice does not give the same verdict.** rag-001 came
back `tie` at 13:29 and `inconsistent` at 13:43 and 14:00. rag-003 came back
`b` at 13:43 and `tie` at 14:00. The models rewrite their answers each run, so
a single sweep is one sample, not a measurement.

**On open prose, mid bought nothing measurable over cheap.** Ten ties, one mid
win, no cheap win. Read this as a hypothesis with evidence behind it, not a
result: the verdicts are model judgments no human has checked yet, the sample
is 8 fixtures, and the answers are one or two sentences long. Sprint 6 is what
decides whether these verdicts can be quoted at all.

### Consequences

- The judge never runs in the request path, and no routing decision reads a
  verdict. It costs more than the work it grades.
- Sprint 6 must hand-score these same pairs blind and measure agreement. Until
  then, no quality number from the judge belongs in a report.
- Sprint 7 needs several runs per fixture, not one: the answers, and therefore
  the verdicts, change between runs.
- A check that rejects a correct answer over formatting is a cost bug, not a
  cosmetic one. Both found so far (quote spans, citation brackets) were
  invisible until someone read the raw answers.

## 10. What the scorer check showed

Sprint 6. 32 pairs — 8 open-ended fixtures, 4 independently generated answer
pairs each — scored twice: once by the strong-model judge from section 9, once
by a human who could not see which tier wrote which answer, could not see the
judge's verdict, and was shown the two answers in a seeded random order so that
the human's own position bias could be measured the same way the judge's was.

|  | picked cheap | picked mid | tie |
|---|---|---|---|
| human | 11 | 16 | 5 |
| judge | 0 | 0 | 28 |

Four further pairs got no verdict at all: the judge contradicted itself when the
answers were swapped.

**Cohen's kappa is 0.00.** Raw agreement was 18%, which is exactly what chance
predicts given the two distributions. Per task type: `rag_answer` 27% raw, kappa
0.00; `summarization` 8% raw, kappa 0.00. Not weak agreement -- none.

**The judge never once picked a winner; the human picked one on 27 of 32.** A
rater that uses a single category has no discrimination to measure, so there is
nothing here to calibrate or tune toward. The judge is not a weak instrument for
these tasks, it is not an instrument.

**Section 9's main conclusion is withdrawn.** "On open-ended work, mid bought
nothing measurable over cheap -- 10 ties, 1 mid win, 0 cheap wins" was a
property of the instrument, not of the models. A human reading the same kind of
pairs saw a difference in 27 of 32 and favoured mid 16 to 11. Section 9 stays as
written, because the record is append-only; this section supersedes its
conclusion.

**The human showed no detectable order bias**: 13 picks for the first answer
shown, 14 for the second. The judge flipped its verdict on 4 pairs when the
order changed. Of the two raters, the one that cannot scale is the one whose
judgments are stable.

**Caveat, from the human's own notes.** Three notes read "more detailed", "well
detailed", "more clearer". The mid tier writes longer answers, so some of the
16-11 split may be a preference for thoroughness rather than for correctness.
This is a confound to watch in Sprint 7, not a reason to discount a kappa of
zero.

**Scope.** 32 pairs over 8 distinct fixtures. Four samples of one fixture are
four observations of the same task, not four tasks, so the effective coverage
is 8.

### Consequences

- The pairwise judge is retired as a quality measure for `summarization` and
  `rag_answer`. No number it produced may be quoted as a quality figure.
- Sprint 7's baseline reports judged quality for no prose task. Those two task
  types carry cost, latency and check-pass rate only, with quality recorded as
  unmeasured.
- Sprint 8's ship / don't-ship decision rests on the four task types that have
  an answer key, plus cost and latency everywhere. If that is not enough to
  decide, the honest outcome is "undecidable on the available evidence".
- The next cheap experiment is to remove TIE from the judge's options and force
  a choice, then re-measure. It separates two diagnoses that look identical from
  the outside: a judge that cannot tell these answers apart, and a judge that
  can but takes the safe option. One prompt change, 32 pairs, about two cents.
- Blind, independent scoring found this one week after the number was produced.
  The same discipline applied to section 9 at the time would have caught it
  immediately; the lesson is to run the check in the same sprint as the claim.
