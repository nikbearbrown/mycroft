## What Mycroft actually pays for

Determined by reading the repo; no PM or billing access was available.

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

### The strong tier is unresolved

Cheap and mid are both Groq on one key. No third provider has evidenced paid
use, so the strong tier is set to **Ollama (local, free)** on a provisional
basis. This is a deliberate trade: a working third tier today, at no cost and
with no budget approval, unblocks Sprints 3–8, which need *a* third tier more
than they need the *best* one.

Swap condition is recorded in `tiers.json` under `strong.replace_when`. Because
`prices.json` is versioned and cost is frozen per row at log time, that swap will
appear in the record as a dated change rather than a silent one.

### Open question for whoever holds the budget

Groq's free-tier limit already blocked a production batch once (RUN_LOG 2026-08-22).
Sprint 7's baseline run and Sprint 8's comparison both need to complete without
hitting it. Either a paid Groq tier or a second provider will be needed before
those sprints, and that is a spending decision, not an engineering one.