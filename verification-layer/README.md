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

## Documentation

**[The reference site](docs/reference/index.html)** documents every file, feature, layer,
component and design decision in this folder: how a run flows end to end, the HTTP API,
configuration, record shapes, the Honest Ledger, and a list of places where older documents
(including parts of this README) no longer match the code.

- **Open it locally.** It's static HTML: open `docs/reference/index.html` in a browser, no
  server needed. (GitHub shows `.html` files as source, not as pages.) Light by default; the
  header has a dark-theme toggle.
- **Rebuild it** after changing the code or the docs: `python scripts/build_docs.py`. Its
  sources are in `docs/reference/src/` (see `AUTHORING.md` there), and parts of it (file
  inventories, routes, environment variables, the ledger) are generated from the code.
- **It can't silently fall behind.** `tests/test_docs_coverage.py` fails if a file has no
  entry or a link breaks.

## What the accountability component enforces

| Snickerdoodle principle | How this code implements it |
|---|---|
| **P3 — Provenance or it isn't evidence** | Every agent attempt produces a `ReasoningObject` (`core/schemas.py`) carrying run_id, agent_id, attempt number, directive version, raw output, and outcome. Runs persist to an append-only SQLite store with `RAISE(ABORT)` triggers against `UPDATE`/`DELETE` (`web/db.py`). |
| **P4 — Gates are hard stops** | `run_validation_loop` (`pipeline/middleware.py`) parses the agent's response structurally; on failure it retries **once** with a corrective directive, and on second failure raises `HaltError`. It does not degrade, summarize, or pass through. |
| **P5 — Two customers, twice** | `to_dict(investor_scope=True)` structurally *omits* `thought_log` / `raw_output` / `llm_tokens` rather than nulling them — the auditor reads the reasoning, the investor reads the conclusion. |
| **P8 — Trust is earned** | Confidence is recorded and classified against a threshold; determinism claims are hedged in the adapters rather than asserted (`gemini_adapter.py`, `ollama_adapter.py` both state that seed reproducibility holds only within a fixed model version and quantization). |

## Status — honest

**Research prototype. Localhost only. Do not expose to a network.**

The core engine (parser, validation loop, schemas, cross-agent comparison) is well-built and
well-tested: **242 tests, all passing** (as of 2026-09-11), stdlib `unittest` only. The
web/auth layer is not — `GET /api/self-report` discovers the live count rather than
restating this number, so trust that over this paragraph.
A full technical audit of commit `fe45eb4` records **four CRITICAL findings**, all
reachable over HTTP with no credentials. That audit now lives in the author's
gitignored working folder and is not distributed with the repo, so its findings are
restated here rather than linked:

1. Investor redaction is bypassed at storage time by `RunSession.to_dict()`.
2. Fourteen of sixteen API routes have no authentication at all.
3. `DELETE /api/runs` drops and recreates the audit tables, unauthenticated.
4. `POST /api/auth/token` mints an `auditor` token for anyone who asks.

Per the verification stack, that audit is layer 2 — *a report for human judgment*, not
a verdict. Nothing here is attested, and no recipe in `recipes/` should claim
`RUNNABLE-LIVE` on top of this layer until §7 of the audit is addressed.

## Layout

Organised as inward-pointing layers: each one may import from the layers above it in
this table and never from the layers below. `core/` imports nothing internal at all,
which is what makes it safe for every other layer to depend on.

### `core/` — abstractions and domain types (no internal dependencies)

| Path | What it is |
|---|---|
| `core/contracts.py` | The two contracts everything else is written against, as `Protocol`s: `AgentAdapter` (`(subject, context, directive) -> AgentResponse`) and `JsonFetcher` (`url -> dict`). Both used to exist only as prose in a comment. |
| `core/parsing.py` | Structural parsing of `<thought_log>` / `<conclusion>`; raises `StructuralParseError`. The best-tested module here. (Was `parser.py`, which shadowed a stdlib module name.) |
| `core/schemas.py` | `ReasoningObject` / `RunSession` + their validation rules and tiered serialization. |
| `core/directive.py` | Versioned system directives; the corrective directive used on retry. |
| `core/numeric.py` | The one definition of "a number": the quantitative-token regex and magnitude suffixes. Previously three verbatim copies across `claims`/`consistency`/`verification`, each carrying a comment asking the reader to keep it in sync by hand. |

### `adapters/` — one provider each, all satisfying `AgentAdapter`

| Path | What it is |
|---|---|
| `adapters/registry.py` | Provider name to factory, label and model-key. Adding a provider is one entry here; nothing in `web/` or `scripts/` branches on the provider set. |
| `adapters/gemini_adapter.py`, `ollama_adapter.py` | Live Gemini and local Ollama, each over their native SDK/protocol. |
| `adapters/langchain_adapter.py` | Live Ollama via LangChain's `ChatOllama`, or — when `failure_mode` is set — a scripted, network-free double (LangChain's own `GenericFakeChatModel`) whose `FAILURE_MODES` drive ADR-07's retry/halt paths in tests. Replaced `mock_adapter.py` (archived at `archive/adapters/mock_adapter.py`, not deleted, per this repo's never-delete rule). Deliberate exception to stdlib-only: adds `langchain-core` and `langchain-ollama`. |
| `adapters/fixture_adapter.py` | Deterministic stand-in with a caller-chosen conclusion, for testing logic that consumes a conclusion. Not the only Producer B path anymore; see `producers/earnings.py`. |

### `pipeline/` — execution machinery

| Path | What it is |
|---|---|
| `pipeline/middleware.py` | The retry-then-halt validation loop (ADR-07). |
| `pipeline/observability.py` | LangFuse tracing wrapper around adapters, used by every producer. |

### `datasources/` — the only network egress (P2)

| Path | What it is |
|---|---|
| `datasources/edgar.py` | SEC EDGAR read client: `lookup_cik`, `fetch_company_facts`, `latest_value`. Every fetch is injectable, which is why the suite is network-free without patching module globals. |

### `producers/` — the agents whose disagreement is measured

| Path | What it is |
|---|---|
| `producers/lens.py` | `ConceptLens` (a producer's whole identity: concepts, `AgentID`, header, trace name) and `run_lens`, the single runner all producers share. A third producer is a `ConceptLens` value, not a new module. |
| `producers/financial.py` | Producer A — balance-sheet and top-line concepts. |
| `producers/earnings.py` | Producer B — a *different* slice of the same companyfacts payload (per-share/operating-income), giving Cross-Agent Validation a second real, independently-reasoned agent instead of only the fixture. |

### `validation/` — the verification stack

| Path | What it is |
|---|---|
| `validation/claims.py`, `validation/verification.py`, `validation/consistency.py` | Claim extraction, claim verification against source, and consistency probing across repeated runs of one agent. Used by both `/api/chat` (since Week 7) and, as of 2026-09-11, `/api/compare` — per-producer, independently. |
| `validation/cross_validation.py` | **Cross-Agent Validation** — runs two agents on one subject, flags numeric contradictions between their conclusions, and persists both agents' records under one shared `run_id`. Reuses `validation/consistency.py`'s scoring unmodified. `contradiction_rule` picks between the legacy `"symmetric_difference"` rule (default, every existing test unchanged) and `"concept_aware"` (`validation/concept_linkage.py`, what `/api/compare` uses in production). |
| `validation/concept_linkage.py` | Tags each extracted number with the known lens concept nearest it, so a number that can never be corroborated by the other producer (disjoint concept vocabularies, by construction) is excluded from comparison instead of auto-flagged. **Wired in as of 2026-09-11**: `run_cross_agent_validation`'s `contradiction_rule="concept_aware"` (the mode `/api/compare` and `scripts/run_cross_agent_live.py` now both use) delegates here. Measured against `tests/fixtures/cross_agent_real_runs_corpus.json`: kills 15 of 16 disjoint-concept false positives, preserves the one confirmed true positive, introduces none. See `tests/test_concept_linkage.py` and the module docstring for what it still can't do (a bare ratio/percentage is syntactically identical whether it's a legitimate derived metric or a fabrication) — the legacy `"symmetric_difference"` rule remains the default for backward compatibility. |

### `web/`, `scripts/`, `tests/`, `docs/`

| Path | What it is |
|---|---|
| `web/` | FastAPI server, JWT auth, SQLite store, step tracing, and the browser UI (`web/frontend/`, React; served at `/` since 2026-09-27 — the classic `web/static/` UI is archived in `archive/web-static-legacy/`). |
| `web/self_report.py` | The subsystem's own honest ledger: known issues and live-model-test results, each with a source reference and an OPEN/RESOLVED/BY_DESIGN/UNVERIFIED status. Served at `GET /api/self-report` and shown in the UI. Automated test counts are discovered live rather than hard-coded, so they cannot drift from the suite. |
| `scripts/run_cross_agent_live.py` | Manual script (not part of the automated suite) that runs Cross-Agent Validation with two real LLM calls — `producers/financial.py` vs. `producers/earnings.py` — instead of a fixture Producer B. Requires `GEMINI_API_KEY`. |
| `scripts/run_overlap_concept_live.py` | Manual script: unlike the one above, both sides read the **identical** context (Producer A's own concept set), so any divergence can only come from how each model reasoned over the same evidence — the live test nothing in the corpus had ever run. Defaults to two local Ollama models. See its docstring and `logs/RUN_LOG.md`'s 2026-09-11 entry for what four real runs found. |
| `scripts/smoke_langfuse_trace.py` | Manual LangFuse end-to-end trace check. Was named `test_langfuse_integration.py`, where it read as part of the automated suite while actually making a live EDGAR fetch. |
| `scripts/start-server.sh` | Convenience launcher; resolves its own directory and activates `env/` only if one exists. |
| `tests/` | Stdlib `unittest` only — no pytest, no network, no live model. |
| `docs/SYSTEM_DESIGN.md` | Detailed system workflow, data model, and design-decision rationale for both the accountability layer and Cross-Agent Validation, with an embedded honest-status snapshot. Start here for the full picture; this README stays the quick-reference layout. |
| `docs/DATA_CONTRACT.md` | The store's data contract. |
| `docs/index.html` | Index for the Week 1-3 walkthrough decks in `docs/` (the decks themselves are gitignored local artifacts). |

Nothing sits loose at the root except `README.md`, `CLAUDE.md`, `requirements.txt`,
`.env.example` and `.gitignore` — the files tooling expects to find there.

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

**3.** Run the test suite — no credentials or network needed, since the
mock and fixture adapters cover every path:

```bash
cd verification-layer && python -m unittest discover -s tests
```

**4.** Start the local server on http://localhost:8000:

```bash
cd verification-layer && python -m uvicorn web.server:app --reload --port 8000
```

`scripts/start-server.sh` does the same thing from any working directory, and activates
`env/` only if that virtualenv exists. It still needs a POSIX shell (`#!/bin/bash`), so on
Windows use the `uvicorn` command above or run it under Git Bash.

Copy `.env.example` to `.env` for real Gemini calls or LangFuse tracing; both degrade
gracefully when unset. `.env` is gitignored here and at the Mycroft root — never commit it.

## Self-contained by design

Every file this subsystem needs lives in this directory. It has its own
[`.gitignore`](.gitignore), [`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md), and
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
node scripts/conformance.mjs verification-layer/validation/cross_validation.py
```
