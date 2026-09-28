---
title: Scripts
slug: files-scripts
section: Files
order: 120
summary: Manual entry points - live cross-agent runs, a LangFuse smoke check, the server launcher and the docs builder.
---

`scripts/` holds entry points a person runs by hand. None of them is part of the automated
suite: the Python scripts make real SEC EDGAR fetches and real model calls, which the suite's
"no network, no live model" rule (see [[CLAUDE.md]]) keeps out of `tests/`. The shell script
starts the server.

Dependency rule: a script sits outside the layers and may import from any of them. Each Python
script puts the subsystem root on `sys.path` first, so `core.*`, `producers.*` and so on
resolve whether it is run as `python scripts/<name>.py` or `python -m scripts.<name>`.

The folder took its current shape in the 2026-09-04 layered restructure (`logs/RUN_LOG.md`,
"SOLID restructure: layered packages, no loose root modules, three duplications removed"),
which moved the root-level scripts here and renamed the LangFuse check.
`scripts/build_docs.py`, the builder for this reference site, is being added alongside this
page.

> The two cross-agent live scripts do not start in the current tree. Both import
> `adapters.gemini_adapter` and `adapters.ollama_adapter`, which were archived on 2026-09-23.
> Running `python scripts/run_overlap_concept_live.py --help` ends in
> `ModuleNotFoundError: No module named 'adapters.ollama_adapter'` (run when this page was
> written). `run_cross_agent_live.py` has the same imports and was checked by reading, not
> run. Details are in each entry.

## `scripts/__init__.py`

**Role:** an empty file that makes `scripts` a package, so the scripts can be run with
`python -m scripts.<name>`.

It has no content. The comment at the top of each script names both ways of running it.

## `scripts/run_cross_agent_live.py`

**Role:** a manual run of Cross-Agent Validation with two real models, Producer A
(`producers/financial.py`) against Producer B (`producers/earnings.py`), on one company's live
EDGAR data.

What it does, in order:

1. Loads `.env` with `python-dotenv` (searching upward from the working directory), so keys in
   `.env` reach `os.environ`.
2. Resolves the ticker (default `AAPL`) to a CIK and fetches the company-facts payload once
   through `datasources/edgar.py`.
3. Builds two different contexts from that one payload: `summarize_facts` (balance sheet and
   revenue) and `summarize_earnings_facts` (per-share and operating income). It prints both.
4. Builds one adapter per side through the registry, with temperature 0 and seed 42, and wraps
   each in `make_traced_adapter` so both model calls appear in LangFuse.
5. Calls `run_cross_agent_validation` with `contradiction_rule="concept_aware"`, the rule
   `/api/compare` uses. The whole run is wrapped in one LangFuse `observe` span named
   `cross_agent_validation:<TICKER>`, so the fetch and both model calls nest under one trace.
6. Prints status, both conclusions, the contradiction flag, divergent numbers, agreement and
   score, then persists the run with `persist_cross_agent_run`.

Options: `--agent-a-provider` and `--agent-b-provider` (default `gemini`), `--agent-a-model`
and `--agent-b-model`. When both sides are Gemini it defaults to `gemini-2.5-flash` against
`gemini-2.5-flash-lite`, to get two different models without a second provider. It returns 1
on a halt, a rate limit, an Ollama error, a configuration error or any other adapter error,
each with its own message.

### Design notes
- Temperature 0 and a fixed seed are there so a disagreement can be put down to the evidence or
  the model rather than sampling noise (the comment on `_LIVE_DEFAULTS`).
- The final catch-all `except` was added after a live key came back `CONSUMER_SUSPENDED` and
  matched no specific branch (the comment above it).
- It routes model overrides through `adapters/registry.py` so it cannot disagree with the HTTP
  route about which config key a model name belongs in (the `_build_adapter` docstring).

### Limits and open issues
- **It cannot start.** It imports `RateLimitDailyError` and `RateLimitMinuteError` from
  `adapters.gemini_adapter`, and `OllamaConnectionError` and `OllamaModelError` from
  `adapters.ollama_adapter`. Both modules are archived at
  [[archive/adapters/gemini_adapter.py|archive/adapters/]] (`logs/RUN_LOG.md`, 2026-09-23,
  "Make LangChain the sole agent framework..."), which did not update this script.
- Past the imports it would still fail. It calls `with_model_override(_LIVE_DEFAULTS,
  provider, model)` with three arguments; the current signature in [[adapters/registry.py]] is
  `with_model_override(config, model=None)`. Its provider defaults (`gemini`) are not among
  `provider_names()`, which is now `('langchain',)`.
- The docstring says it "Requires GEMINI_API_KEY". With LangChain as the one framework, Gemini
  is selected by model name through `LANGCHAIN_MODEL`, not by a provider flag.
- The docstring of [[scripts/run_overlap_concept_live.py]] says this script sets
  `concepts_expected_to_overlap=False`; it does not pass that argument, and uses the
  concept-aware rule instead (switched 2026-09-11, "Fix core comparator correctness...").
- `web/self_report.py`'s `http-no-model-override` entry cites this script's model flags as the
  way to run two different models; that path is unavailable until the script is updated.

Related: [[validation/cross_validation.py]], [[producers/financial.py]], [[producers/earnings.py]]

## `scripts/run_overlap_concept_live.py`

**Role:** a manual live test in which two models read the same context, to see whether the
contradiction flag can fire on a real disagreement about the same fact.

Its docstring gives the reason: across the stored runs, Producer A and Producer B never shared
a concept, so they were never in a position to disagree about the same figure. This script
gives both sides the identical context, Producer A's `summarize_facts` output, so any
divergence comes from how each model read that evidence. Side A runs as `AgentID.FINANCIAL`,
side B as `AgentID.EXTERNAL`. It calls `run_cross_agent_validation` with
`concepts_expected_to_overlap=True` and no `contradiction_rule`, so the default rule applies.

Arguments: one or more tickers (default `AAPL`), and provider and model flags per side,
defaulting to local Ollama with `qwen2.5:7b` against `mistral-7b`. Each ticker is fetched,
compared, printed and persisted; the exit code is the worst of the per-ticker results. It
does not load `.env` and does not trace to LangFuse.

### Design notes
- It defaults to two local Ollama models because a Gemini key had never been confirmed working
  (`gemini-key-unconfirmed` in [[web/self_report.py]]), and both models were already pulled on
  the author's machine (the docstring).
- The docstring warns that an unflagged run does not prove the mechanism works, and that a
  flagged run is the more informative result either way.

### Limits and open issues
- **It cannot start.** It imports `OllamaConnectionError` and `OllamaModelError` from the
  archived `adapters.ollama_adapter`. Observed: `--help` fails with `ModuleNotFoundError` at
  that import.
- It has the same `with_model_override` and provider-name mismatches as
  [[scripts/run_cross_agent_live.py]].
- Observed results are in `logs/RUN_LOG.md`, 2026-09-11, "Concept-linkage prototype + the
  first overlapping-concept live test": four real Ollama runs (AAPL, then MSFT and NVDA, then
  AAPL with the models swapped). That record led to the ledger entry
  `mistral-7b-context-grounding-failure`.

## `scripts/smoke_langfuse_trace.py`

**Role:** a manual end-to-end check that a real run produces a LangFuse trace.

It loads `.env`, reports whether `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are set (and,
if not, prints setup steps), then runs `producers.financial.analyze_ticker("AAPL", ...)` with
`make_langchain_adapter()`: a real EDGAR fetch and a real Ollama call with the default model,
`llama3.2`. It prints the first reasoning object's agent, parse status, confidence and the
start of its conclusion, and says which trace to look for: `analyze_ticker`, with spans for
`fetch_company_facts` and `llm_call:AAPL`. It returns 1 on any exception, with a traceback.

It prints the first 20 characters of the public key when one is set.

### Design notes
- It was named `test_langfuse_integration.py`, which made it look like part of the automated
  suite although it makes a live EDGAR fetch; it was renamed in the 2026-09-04 restructure.
- Since 2026-09-22 it has no scripted fallback; if Ollama is unreachable it fails loudly
  (the docstring; `logs/RUN_LOG.md`, "Remove all mock/scripted features from the running
  app...").

### Limits and open issues
- Its docstring still calls it a "Test script" and it prints "LangFuse Integration Test".
- It prints `cd .langfuse` as the LangFuse start step; `.env.example` says `cd ../.langfuse`.
- It uses a Unicode check mark and warning sign in its output.
- This page does not record a run of it.

Related: [[pipeline/observability.py]], [[producers/financial.py]]

## `scripts/start-server.sh`

**Role:** the launcher for the web server, usable from any working directory.

In order, it:

1. Resolves the subsystem root from its own location and changes to it.
2. Activates `env/bin/activate` or `env/Scripts/activate` if either exists; otherwise uses
   whatever `python` is on `PATH`.
3. If `web/frontend/dist` is missing and `npm` is available, runs `npm ci && npm run build` in
   `web/frontend/`. Without `npm`, it prints a note that the UI cannot be built but the API
   still runs.
4. Runs `python -m uvicorn web.server:app --reload` on `PORT`, default 8000.

It uses `set -e`, so a failed build stops the script.

### Design notes
- It used to hard-code `source env/bin/activate` and assume a working directory; the
  2026-09-04 restructure made it resolve its own location and activate a virtualenv only if
  one exists.
- The build step was added with U1 (`logs/RUN_LOG.md`, 2026-09-24, "U1: React + Vite
  foundation..."). The comment explains it matters more since the classic UI, which needed no
  Node, was archived on 2026-09-27: without a build, `/` returns a page explaining how to make
  one.

### Limits and open issues
- It needs a POSIX shell (`#!/bin/bash`). `README.md` says to use the `uvicorn` command or Git
  Bash on Windows.
- A second launcher, [[start-web-server.sh]], sits at the root with a hard-coded WSL path.

## `scripts/build_docs.py`

**Role:** builds this reference site: HTML pages from the Markdown sources in
`docs/reference/src/`, plus everything that can be read off the code, generated fresh on every
build.

```bash
python scripts/build_docs.py            # build into docs/reference/
python scripts/build_docs.py --check    # build in memory, print problems, write nothing
```

It exits non-zero when it finds a problem. Standard library only, like the rest of the core.

### How it works

1. **Project files.** `project_files()` asks git for tracked files plus new files that aren't
   ignored (`git ls-files` and `git ls-files --others --exclude-standard`). A tracked file deleted
   in the working copy is still listed, and its inventory says so.
2. **Sources.** Each page in `src/pages/` and `src/files/` has front matter (`title`, `slug`,
   `section`, `order`, `summary`). Every level-2 heading holding a backticked path or glob is a
   file entry. Headings inside fenced code blocks are examples, not entries.
3. **Coverage.** Every project file must match exactly one entry: an exact path wins, otherwise
   one glob (`*` within a folder, `**` across folders). Every entry must match a file. Anything
   else is a problem.
4. **Inventory.** Source is parsed, never imported, so a module with a missing dependency or a
   syntax error can't stop the build:
   - Python with `ast`: classes and public methods, functions with signatures and the first
     paragraph of each docstring, upper-case constants, internal imports (module-level and inside
     functions, told apart), third-party imports, `os.environ` / `os.getenv` reads, FastAPI route
     decorators, and test counts;
   - TypeScript with regular expressions: exports, relative imports resolved to files, npm
     packages, and `it(` / `test(` counts;
   - every file: its kind, lines and bytes.
   The reverse of the import map gives "Imported by".
5. **Rendering.** A small Markdown renderer covers what AUTHORING.md documents. Code spans are
   protected first, so a `[[link]]` inside backticks stays literal. `[[path]]` resolves to the page
   and anchor of the entry that covers the path. File-entry headings get `f-<path>` anchors;
   decision headings (`D-07 · ...`) get short `d-07` anchors. Each file entry gets its generated
   inventory appended at the end of its section.
6. **Generated blocks.** A page can include `{{routes}}`, `{{env}}`, `{{layers}}` (the import
   matrix between packages), `{{ledger}}` (`KNOWN_ISSUES` from [[web/self_report.py]], read with
   `ast.literal_eval`), `{{files-index}}` or `{{stats}}`.
7. **Pages.** Each page gets the header with search and the theme toggle, a one-line `<head>`
   script that applies a saved dark choice before the first paint, the sidebar (by section), breadcrumbs, a table
   of contents when it has three or more sections, previous and next links, and a footer naming
   its source file. The search index is written as a script (`window.DOCS_INDEX = ...`), not JSON,
   so it loads from `file://` too.
8. **Link check.** Every `href` in the output is checked: pages, anchors, assets, and relative
   links out of the site. External links are not fetched.

### Design notes

- **Generate what can be generated.** The parts most likely to go stale when written by hand
  (signatures, imports, routes, variables, the ledger, counts) are the ones generated.
- **The build date is the only varying text.** The footer shows the day of the build, not a
  commit, so an unchanged source rebuilds to the same bytes on the same day.
- **Styling** follows `brutalist/DESIGN.md` (see [[docs/reference/**]]).

### Limits and open issues

- The TypeScript inventory is regex-based: exports defined unusually (re-exports, `export {}`
  lists) aren't listed.
- The drift test checks coverage and links, not accuracy.

Related: [[tests/test_docs_coverage.py]], [[docs/reference/**]]

