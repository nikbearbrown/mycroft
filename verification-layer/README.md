# Verification Layer

_A runnable implementation of the Snickerdoodle contract — the part of Mycroft where
the principles stop being prose and start being code that halts._

Mycroft's chapters argue that AI made execution cheap but not judgment cheap. This
subsystem is the argument in executable form: an agent wrapper that refuses to pass
along output it cannot structurally verify, writes an append-only record of every
attempt, and renders that record differently to different readers.

**Renamed from `accountability-layer` on 2026-08-21**, when a second component, Cross-Agent
Validation, was built on top of the same evidence store. This folder now holds both: the
accountability mechanism (which records what one agent did) and Cross-Agent Validation
(which compares two agents against each other). See `logs/RUN_LOG.md` for both changes.

## What the accountability component enforces

| Snickerdoodle principle | How this code implements it |
|---|---|
| **P3 — Provenance or it isn't evidence** | Every agent attempt produces a `ReasoningObject` (`schemas.py`) carrying run_id, agent_id, attempt number, directive version, raw output, and outcome. Runs persist to an append-only SQLite store with `RAISE(ABORT)` triggers against `UPDATE`/`DELETE` (`web/db.py`). |
| **P4 — Gates are hard stops** | `run_validation_loop` (`middleware.py`) parses the agent's response structurally; on failure it retries **once** with a corrective directive, and on second failure raises `HaltError`. It does not degrade, summarize, or pass through. |
| **P5 — Two customers, twice** | `to_dict(investor_scope=True)` structurally *omits* `thought_log` / `raw_output` / `llm_tokens` rather than nulling them — the auditor reads the reasoning, the investor reads the conclusion. |
| **P8 — Trust is earned** | Confidence is recorded and classified against a threshold; determinism claims are hedged in the adapters rather than asserted (`gemini_adapter.py`, `ollama_adapter.py` both state that seed reproducibility holds only within a fixed model version and quantization). |

## Status — honest

**Research prototype. Localhost only. Do not expose to a network.**

The core engine (parser, validation loop, schemas, cross-agent comparison) is well-built and
well-tested: **129 tests, all passing**, stdlib `unittest` only. The web/auth layer is not.
[`accountability-layer-audit.md`](accountability-layer-audit.md) is a full technical
audit of commit `fe45eb4` and records **four CRITICAL findings**, all reachable over
HTTP with no credentials:

1. Investor redaction is bypassed at storage time by `RunSession.to_dict()`.
2. Fourteen of sixteen API routes have no authentication at all.
3. `DELETE /api/runs` drops and recreates the audit tables, unauthenticated.
4. `POST /api/auth/token` mints an `auditor` token for anyone who asks.

Per the verification stack, that audit is layer 2 — *a report for human judgment*, not
a verdict. Nothing here is attested, and no recipe in `recipes/` should claim
`RUNNABLE-LIVE` on top of this layer until §7 of the audit is addressed.

## Layout

| Path | What it is |
|---|---|
| `parser.py` | Structural parsing of `<thought_log>` / `<conclusion>`; raises `StructuralParseError`. The best-tested module here. |
| `middleware.py` | The retry-then-halt validation loop (ADR-07). |
| `schemas.py` | `ReasoningObject` / `RunSession` + their validation rules and tiered serialization. |
| `directive.py` | Versioned system directives; the corrective directive used on retry. |
| `claims.py`, `verification.py`, `consistency.py` | Claim extraction, claim verification, and consistency probing across repeated runs. |
| `cross_validation.py` | **Cross-Agent Validation** — runs two agents on one subject, flags numeric contradictions between their conclusions, and persists both agents' records under one shared `run_id`. Reuses `consistency.py`'s scoring unmodified. |
| `adapters/fixture_adapter.py` | Deterministic stand-in agent with a caller-chosen conclusion, for testing logic that consumes a conclusion. |
| `financial_grader.py`, `observability.py` | EDGAR-backed financial grader **skeleton** + LangFuse tracing. Not wired into the web app. |
| `adapters/` | `gemini_adapter.py`, `ollama_adapter.py`, `mock_adapter.py` — one contract: `(subject, context, directive) -> AgentResponse`. |
| `web/` | FastAPI server, JWT auth, SQLite store, and the browser UI (`web/static/`). |
| `tests/` | 129 stdlib `unittest` tests. |
| `index.html` | Index for the Week 1–3 walkthrough artifacts in `docs/` (gitignored, present on disk only). |

## Install

**Requires Python ≥ 3.10** (tested on 3.12.6). Dependencies are **not** installed by
Mycroft's `npm install` — this is the only Python service in the repo and it carries
its own [`requirements.txt`](requirements.txt).

The core engine is stdlib-only, so if you just want to run the tests you can skip
straight to step 3 on a bare interpreter. The install is only needed for the web app
and the live LLM providers.

**1.** Create a virtualenv:

```bash
cd verification-layer && python -m venv env
```

**2.** Activate it, then install. Activation differs by platform —
`env\Scripts\activate` on Windows, `source env/bin/activate` on macOS/Linux:

```bash
python -m pip install -r requirements.txt
```

**3.** Run the test suite — 129 tests, no credentials or network needed, since the
mock and fixture adapters cover every path:

```bash
cd verification-layer && python -m unittest discover -s tests
```

**4.** Start the local server on http://localhost:8000:

```bash
cd verification-layer && python -m uvicorn web.server:app --reload --port 8000
```

`start-server.sh` does the same thing but is POSIX-only — it hardcodes
`source env/bin/activate` under `#!/bin/bash`, so it does not run on Windows. Use the
`uvicorn` command above on any OS.

Copy `.env.example` to `.env` for real Gemini calls or LangFuse tracing; both degrade
gracefully when unset. `.env` is gitignored here and at the Mycroft root — never commit it.

## Self-contained by design

Every file this subsystem needs lives in this directory. It has its own
[`.gitignore`](.gitignore), [`DATA_CONTRACT.md`](DATA_CONTRACT.md), and
[`logs/RUN_LOG.md`](logs/RUN_LOG.md), and it modifies **no file outside this folder** —
not the repo-root manifests, not `scripts/`, not the shared run log. That keeps the merge
surface at zero against the other contributors' branches (the shared `logs/RUN_LOG.md`
has been touched by seven authors and is the repo's most contended file).

The cost is explicit: **CI does not conformance-check this code**, because the repo gate
(`scripts/conformance.mjs`) only walks its `DEFAULT_PATHS` and this directory is not in
them. Run it yourself from the repo root before committing:

```bash
node scripts/conformance.mjs verification-layer
```

One wart, measured: that command has no exclusion list for this directory, so if a local
`env/` virtualenv exists here, `node scripts/conformance.mjs verification-layer` walks into
it and shells out to `py_compile` once **per file** in site-packages. Measured on this
machine: **6,241 files, 10m45s** — it looks hung, but it is only extremely slow (and it does
pass). Either run conformance before creating the venv, or point it at specific files:

```bash
node scripts/conformance.mjs verification-layer/cross_validation.py
```
