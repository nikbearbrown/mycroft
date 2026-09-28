---
title: Configuration
slug: config
section: Reference
order: 20
summary: Every environment variable the code reads, with its default, and the runtime settings the server holds in memory.
---

## Environment variables

Read from the process environment; `web/server.py` loads a `.env` file first (searching upward
from the working directory). `.env` is gitignored: never commit it, and never paste its contents
anywhere. [[.env.example]] is the template.

{{env}}

A variable read with no default in code is required only on the path that uses it (for example,
`GEMINI_API_KEY` only for a Gemini-family model).

## Runtime settings

The server also holds a small config in memory, shared by every request until the process
restarts. It is read with `GET /api/config` and changed with `POST /api/config` (unauthenticated;
see [audit-criticals](ledger.html#audit-criticals)), or from the review app's Settings page.

| Setting | Default | Meaning |
|---|---|---|
| `model` | `LANGCHAIN_MODEL`, else `llama3.2` | the model agents run on; the family is inferred from the name |
| `temperature` | `0.0` | sampling temperature |
| `seed` | `42` | Ollama seed, stored with each run for replay (Gemini has none) |
| `agent_id` | `external` | the chat run's agent identity |
| `confidence_score` | `0.75` | the chat run's starting confidence |
| `consistency_probe` | `false` | opt-in, but the probe runs anyway for any non-Gemini model |
| `provider` | `langchain` | fixed; read by the registry |

A compare request can also override the model for one agent (`agent_a_model`, `agent_b_model`),
the pairing, and the contradiction rule. See [HTTP API](api.html).

## Files the server writes

| Path | What | In git |
|---|---|---|
| `web/data/accountability.db` | the record store | no |
| `web/data/filing_cache/` | cached filing documents | no |
| `web/frontend/dist/` | the built review app | no |
