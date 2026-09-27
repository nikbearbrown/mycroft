---
title: Archive
slug: files-archive
section: Files
order: 130
summary: Retired source kept under archive/ - the three standalone model adapters and the classic browser UI.
---

`archive/` holds source files that are no longer part of the running system but are kept, not
deleted. The repository's rule (root `AGENTS.md`, "Never delete — archive instead") is that
hand-made files are never deleted: a superseded file is moved into an archive. In this
subsystem the move is done with `git mv`, so a file's history follows it to its new path.

The rule was applied by name at least once after a mistake: the 2026-09-22 entry "Remove
mock_adapter.py, add adapters/langchain_adapter.py" in `logs/RUN_LOG.md` records that a plain
`rm` was tried first and reverted with `git checkout` before the file was moved with `git mv`.

Nothing in the running code imports from `archive/`. Several live files point to it in
comments, so a reader can find what was replaced: [[adapters/registry.py]],
[[adapters/langchain_adapter.py]] and [[web/server.py]]. [[tests/test_cutover.py]] checks that
the classic UI files are here, that `web/static/index.html` is gone, and that the restore
command is written in the archive's README.

The archive has two parts:

- **`archive/adapters/`**: the three standalone model adapters that came before LangChain
  became the one agent framework. Mock was retired on 2026-09-22; Gemini and Ollama on
  2026-09-23.
- **`archive/web-static-legacy/`**: the vanilla-JavaScript browser UI that served `/` until
  the React app replaced it, archived on 2026-09-27.

Files here are not maintained. Their imports, paths and comments describe the code as it was
when they were moved, and they may not run against today's tree.

## `archive/adapters/gemini_adapter.py`

**Role:** the retired standalone adapter for Google Gemini, called through the `google-genai`
SDK.

What it was: `make_gemini_adapter(model="gemini-2.5-flash", temperature=0.0, seed=None)`
returned a callable matching the `AgentAdapter` contract, `(subject, context, directive) ->
AgentResponse`. Each call read `GEMINI_API_KEY` (raising `EnvironmentError` if unset), trimmed
the context to `CONTEXT_CHAR_LIMIT` (8,000 characters, with a truncation note), kept a minimum
gap between calls, sent the directive as the system instruction, and parsed the reply with
`core.parsing._parse_response`. On rate limits it told two cases apart:

- **Per-day quota:** raised `RateLimitDailyError` at once, since retrying cannot help until the
  quota resets.
- **Per-minute quota:** backed off exponentially with jitter, honouring the API's `retryDelay`
  hint, up to `MAX_RETRIES`, then raised `RateLimitMinuteError`.

Any other error was re-raised unchanged. Seed was passed only when set, with the docstring's
caveat that seed plus temperature 0 is reproducible only within one model version.

**When and why retired:** 2026-09-23, `logs/RUN_LOG.md`, "Make LangChain the sole agent
framework; replace the MCP fetch tool with Tavily search; frontend drops all model/provider
selection". The user chose to make LangChain the only framework. Gemini stayed as a model
family, driven by `langchain-google-genai` inside the LangChain adapter, not as a separate
provider. The adapter was moved with `git mv` and is "no longer reachable as separate
providers".

**Replaced by:** [[adapters/langchain_adapter.py]], which picks the Gemini family when the
model name contains "gemini" and passes `GEMINI_API_KEY` explicitly.

**How to restore:** no procedure is recorded. It would need at least a move back to
`adapters/`, a provider entry in [[adapters/registry.py]], and `google-genai`, which
`requirements.txt` no longer lists (judgment, not recorded).

### Limits and open issues
- The live Gemini path was never observed making a successful call. The 2026-09-23 entry
  records a real `403 CONSUMER_SUSPENDED` error from the configured key, and the ledger entry
  `gemini-key-unconfirmed` is still OPEN.
- [[scripts/run_cross_agent_live.py]] still imports its rate-limit exceptions, so that script
  fails at import.
- `README.md` still lists this file as a live adapter.

## `archive/adapters/mock_adapter.py`

**Role:** the retired scripted adapter: a network-free, model-free stand-in used to drive the
retry-then-halt loop (ADR-07) in tests and, before 2026-09-22, as a selectable provider in the
app.

What it was: `make_mock_adapter(failure_mode="none")` returned an adapter with a call counter
and three modes:

- `none`: every call returns a valid, templated `<thought_log>` / `<conclusion>` reply.
- `retry_success`: the first call raises `StructuralParseError` with a canned malformed reply;
  the second succeeds. This is ADR-07's recovery path.
- `halt`: every call raises `StructuralParseError`, so the loop halts after two attempts.

Any other mode raises `ValueError`.

**When and why retired:** 2026-09-22, `logs/RUN_LOG.md`, "Remove mock_adapter.py, add
adapters/langchain_adapter.py". The entry records that it was not throwaway: the registry used
it as the default provider, `web/server.py` validated failure modes against it, and six test
files and the LangFuse smoke script depended on it. The user chose to rewrite every dependent
onto a new LangChain adapter backed by Ollama. At first that adapter carried a scripted mode
(LangChain's `GenericFakeChatModel`, checked to reproduce these three modes). Later the same
day, "Remove all mock/scripted features from the running app..." removed the scripted mode from
the app entirely, at the user's request ("I would rather it fail or throw an error than give a
scripted answer").

**Replaced by:** two things, split by purpose.

- **In tests:** [[tests/support.py]], `make_scripted_adapter(failure_mode)`, which the
  2026-09-22 entry describes as functionally identical to this file but never registered as a
  provider and unreachable from the running app. It was kept because real models almost never
  break the response format, so without a scripted double the retry and halt paths could not
  be tested deterministically.
- **In the app:** [[adapters/langchain_adapter.py]], which always makes a real call.

**How to restore:** no procedure is recorded. The tests no longer need it.

### Limits and open issues
- **It does not import in the current tree.** It uses the pre-restructure flat imports
  `from parser import ...` and `from directive import ...`. Those modules are now
  `core/parsing.py` and `core/directive.py`; there is no `parser.py` or `directive.py` at the
  root.
- **The archived copy is probably the older version.** Its content matches the file as
  committed in `c53746a` (2026-08-21), apart from line endings. The 2026-09-22 entry says the
  file was restored with `git checkout` after the `rm`, which restores the committed version,
  so the archived copy is likely the pre-restructure one rather than the copy in use until
  2026-09-22 (judgment, inferred from the git history; not recorded).
- `README.md` still says the mock adapter covers every path in the test suite.

## `archive/adapters/ollama_adapter.py`

**Role:** the retired standalone adapter for a local Ollama server, written with stdlib
`urllib` only.

What it was: `make_ollama_adapter(model="llama3.2", ..., seed=42)` posted to
`OLLAMA_HOST/api/generate` (default `http://localhost:11434`) with the directive, the subject,
the context trimmed to `CONTEXT_CHAR_LIMIT` (6,000 characters, a margin for small-context
models such as `qwen2.5:3b`), and `seed` and `temperature` options, with a 120-second request
timeout. It raised `OllamaConnectionError` when the server could not be reached,
`OllamaModelError` when the model was not pulled (with the `ollama pull` command in the
message), and `RuntimeError` for other Ollama errors. The reply went through
`core.parsing._parse_response`.

Its docstring qualifies its determinism claim: seed plus temperature 0 reproduces output only
within a fixed model version, quantisation and Ollama version, and the seed and model name are
stored on every run so the conditions can be reconstructed.

**When and why retired:** 2026-09-23, in the same entry and for the same reason as
[[archive/adapters/gemini_adapter.py]]: LangChain became the one framework, and Ollama models
are driven through `langchain-ollama`.

**Replaced by:** [[adapters/langchain_adapter.py]], which keeps this adapter's host and model
conventions (the 2026-09-22 entry says its live path was "structurally mirrored from
`ollama_adapter.py`").

**How to restore:** no procedure is recorded. Like the Gemini adapter, it would need a move
back and a registry entry (judgment, not recorded). It has no third-party dependency.

### Limits and open issues
- The determinism claim was measured false for `qwen2.5:7b`: the ledger entry
  `ollama-determinism` (OPEN) records 3 distinct answers across 6 identical-input calls. That
  entry's title still names this archived file.
- [[scripts/run_cross_agent_live.py]] and [[scripts/run_overlap_concept_live.py]] still import
  its exception classes, so both scripts fail at import. Running
  `python scripts/run_overlap_concept_live.py --help` gives
  `ModuleNotFoundError: No module named 'adapters.ollama_adapter'`.

## `archive/web-static-legacy/README.md`

**Role:** explains why the classic UI was archived and how to bring it back.

It says the vanilla-JS UI served `/` from the first prototype until 2026-09-27, and that its
three files were moved with `git mv`. They were replaced by the React app in `web/frontend/`
(roadmap phase U9) after a parity checklist, with one deliberate exception: the "Clear all
runs" button, which calls `DELETE /api/runs`, was not ported, because that route drops every
table, including the append-only record and the human decisions, contrary to the never-delete
rule. The route itself is unchanged.

The restore procedure it gives:

1. `git mv` the three files from `archive/web-static-legacy/` back to `web/static/`.
2. In `web/server.py`, restore the `/static` mount
   (`app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")`) and make
   `root()` return `FileResponse(STATIC_DIR / "index.html")`.

It adds that the old UI still works against the API but cannot show anything added after
2026-09-24: the figure matrix, checks, the decision gate, sources or grades.

### Design notes
`web/server.py` keeps `STATIC_DIR` defined for exactly this reason; its comment says the
constant is kept "only so that restore is a two-line change".
[[tests/test_cutover.py]] checks that this README contains the first `git mv` line.

### Limits and open issues
It dates the role pills and verification banner to 2026-09-23. `logs/RUN_LOG.md` records both
under 2026-09-24 ("Role pills for who-wrote-what..." and "Make citation verification status
visible next to the conclusion, not buried").

## `archive/web-static-legacy/app.js`

**Role:** the classic UI's client script: one immediately-invoked function holding all state,
rendering and API calls.

It rendered Markdown with `marked` if loaded (falling back to escaped text), and kept the
current scope (auditor or investor), the running flag and the active tab as local state. The
routes it called include `/api/auth/token`, `/api/config`, `/api/chat`, `/api/compare`,
`/api/runs` (list, detail, flags and `DELETE`), `/api/runs/contradictions`, `/api/sessions`,
`/api/directive` and `/api/self-report`.

Features, per its code and the log entries that built it: a chat mode and a Cross-Agent Compare
mode (ticker or free subject); scope switching with a token re-issue on 401; claim, citation
and consistency badges; the four-band compare layout with a live step trace (2026-09-04,
"Compare UI v2..."); per-attempt context windows (2026-09-22); role pills and tool-call
queries in the timeline (2026-09-24); runs, sessions and flagged tabs; detail, directive and
ledger modals; and "Clear Runs".

**When and why retired:** 2026-09-27, `logs/RUN_LOG.md`, "B6 + U9: the audit export, the
remaining pages, and the cutover of '/'". The human decision to build a React + Vite app and
migrate strangler-style, keeping this UI at `/` until parity, is in "Human decisions:
audit-layer roadmap approved; web UI scope for brutalist/" (2026-09-24).

**Replaced by:** the React app under `web/frontend/` ([[web/frontend/src/App.tsx]]), served at
`/app/`, with `/` redirecting there.

**How to restore:** see [[archive/web-static-legacy/README.md]].

### Limits and open issues
- It can't show the features added from 2026-09-24 on.
- The cutover entry records a stale cached copy of this UI in one browser tab after the
  cutover; `/` now sends `Cache-Control: no-store`, and the ledger entry `cached-classic-ui`
  tracks it.

## `archive/web-static-legacy/index.html`

**Role:** the classic UI's single page: the markup every control in `app.js` binds to.

Layout: a top bar with buttons for the Honest Ledger, "View Directive" and "Clear Runs"; a left
configuration panel with the Auditor / Investor scope switch and run settings; a centre panel
with Chat and Cross-Agent Compare tabs (the compare view switches between "Financial (ticker)"
and "Generic (any subject)"); a right audit panel with Runs, Sessions and Flagged tabs; and
modals for the directive, the ledger and run detail.

It loads `/static/style.css`, `marked` version 12 from the jsDelivr CDN, and `/static/app.js`.

**When and why retired, replaced by, how to restore:** as for
[[archive/web-static-legacy/app.js]].

### Limits and open issues
- Its asset paths assume the `/static` mount, which the cutover removed, so opening the file
  from the archive does not load its script or styles.
- It loads a script from a third-party CDN at runtime.

## `archive/web-static-legacy/style.css`

**Role:** the classic UI's stylesheet.

It defines its palette as CSS custom properties on `:root` (background, surface, borders, a
blue primary, and status colours for success, warning, danger, halt and uncertainty), a
system-ui font stack at 14 px, radius and shadow tokens, and a 52 px top bar, followed by the
component styles for panels, tabs, badges, the compare bands and the modals.

These colours are the app's own palette. The 2026-09-24 decision entry records that
`brutalist/DESIGN.md` does not govern the web app, which keeps its existing palette, status
colours, system fonts, rounded badges and fixed top bar.

**When and why retired, replaced by, how to restore:** as for
[[archive/web-static-legacy/app.js]]. The React app's styles are in
[[web/frontend/src/styles.css]].
