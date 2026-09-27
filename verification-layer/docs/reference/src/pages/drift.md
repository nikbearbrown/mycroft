---
title: Drift found while documenting
slug: drift
section: Reference
order: 70
summary: Disagreements between the code and its documents, and latent defects, found while this reference was written on 2026-09-27. None is fixed here.
---

Writing an entry for every file meant reading every file against what the other documents claim
about it. This page records what didn't match, so it isn't lost (P6: a disagreement between
artifacts is a logged defect; no artifact silently wins). **Nothing on this page has been fixed.**
Each item says how it was established:

- **ran**: confirmed by running something;
- **read**: found by reading the code; not confirmed by a test or a run.

The file entries linked here have the detail under "Limits and open issues".

## Documents that no longer match the code

| Where | What it says | What the code does | How |
|---|---|---|---|
| [[README.md]] | The Gemini and Ollama adapters are live; the LangChain adapter has a scripted `failure_mode` | Both are archived; there is no scripted mode | read |
| [[README.md]] | "242 tests"; two contracts; the corrective directive is in `core/directive.py`; tracing is used by every producer | The count is discovered live; there are three contracts (with `ModelCall`); the corrective directive is in `pipeline/middleware.py`; the web routes don't use LangFuse | read |
| [[README.md]] | Omits `datasources/filings.py`, `select_fact`, the bull and bear lenses, shared concepts | They exist | read |
| [[docs/SYSTEM_DESIGN.md]] | Directive v1.1.0 is active, of two versions | v1.5.2 is active, of nine | read |
| [[docs/SYSTEM_DESIGN.md]] | The two agents run one after the other; the lenses are disjoint; lists removed provider fields | Concurrent by default; lens v2 shares two concepts | read |
| [[docs/SYSTEM_DESIGN.md]] | The structural check is the parser's only check; lists fewer investor-scope omissions | The parser also rejects empty and echoed conclusions; investor scope also omits directive text, context window and four assessment fields | read |
| [[docs/DATA_CONTRACT.md]] | Older counts, module paths and git status | Changed since | read |
| [[requirements.txt]], [[.env.example]] | Without `TAVILY_API_KEY` "the tool still binds, but a search call will fail" | The call runs with no tools | read |
| [[requirements.txt]] | Everything below the web app is optional; the core runs on a bare interpreter | `pipeline/observability.py` imports `langfuse` unconditionally, so anything importing the producers needs it | read |
| [[.env.example]] | — | Doesn't list `OLLAMA_HOST`, `CROSS_AGENT_MAX_CONCURRENCY` or `ACCOUNTABILITY_SECRET` | read |
| [[logs/RUN_LOG.md]] 2026-09-27 (commits) | The SSE parser "doesn't accept CRLF" | It normalises CRLF within a chunk; it breaks only when a CR/LF pair is split across two chunks, which is what the clean-checkout test hit. A correction is appended to the log | read |
| [[logs/RUN_LOG.md]] 2026-09-26 (U5 + U6) | Clicking outside a source popover returns focus | It doesn't | read |

## Comments and docstrings that no longer match

| File | Stale text | How |
|---|---|---|
| [[core/directive.py]] | names `reject_directive_echo`; the function is `reject_unusable_conclusion` | read |
| [[datasources/edgar.py]] | "the only network egress" (so are `filings.py`, the adapter and `verification.py`) | read |
| [[web/db.py]] | the purge runs "on startup and on every write" (startup only); the ticker is a "generated column" (filled in Python); the trigger bypass is "this connection only" (it drops the triggers for the whole database, and one `DROP` names a trigger that never exists) | read |
| [[web/server.py]] | the module docstring names the old `accountability_layer/` folder | read |
| [[web/self_report.py]] | comments say five live tests (the list has six); live test 5 is `OPEN` while its issue `disjoint-concepts` is `RESOLVED`; `escalation-undefined` and `http-no-model-override` describe gaps since closed | read |
| [[validation/concept_linkage.py]] | not used by `/api/compare`; verification not wired in | read |
| [[validation/gate.py]] | the B5 no-consensus trigger isn't built (policy v3 has it) | read |
| [[validation/verification.py]] | the rate's docstring describes a different fraction from the one computed | read |
| [[producers/earnings.py]] | cites a "sdd.md Open Question #1" heading that doesn't exist | read |
| [[tests/test_synthesis.py]] | `tests/__init__.py` blocks model calls (that guard was removed) | read |
| [[tests/support.py]] | "24 runs, zero retries" (resolved 2026-09-27: 13 retries, 9 halts) | read |
| [[tests/test_real_run_corpus.py]] | `/api/compare` uses `concepts_expected_to_overlap=False`; rerun `build_corpus.py` (stale since 2026-09-11; the script doesn't exist) | read |
| [[tests/test_phase1_schemas.py]], [[tests/test_producer_lens.py]] | names and docstrings from earlier versions (`TestV151Template` holds v1.5.2 checks; "the lenses don't overlap") | read |
| [[web/frontend/src/views/HistoryPanel.tsx]], [[web/frontend/README.md]] | a comment and the layout block predate later changes | read |

## Scripts that don't run

- [[scripts/run_cross_agent_live.py]] and [[scripts/run_overlap_concept_live.py]] import the archived
  adapters. `run_overlap_concept_live.py --help` fails with `ModuleNotFoundError` (**ran**); the
  other has the same imports (**read**). Both also call `with_model_override` with the wrong
  arguments.

## Latent defects

Found by reading unless marked. Each is described in its file's entry.

| Area | Defect | How |
|---|---|---|
| [[web/self_report.py]] | `load_errors` never fires: it looks for modules named `_Failed*`, but unittest files a failed import under `loader` | ran (discovery over a folder with a broken module) |
| [[validation/gate.py]] | `accept_a`/`accept_b` citing the grade together with a figure clears the grade item without recording a grade | read |
| [[validation/divergence.py]] | a `DERIVED_WRONG` row counts as both unchecked and unbacked | read |
| [[validation/facts.py]] | `ONE_SIDED` also covers dollar figures neither agent was given | read |
| [[validation/consistency.py]] | ordinary errors are marked as halts | read |
| [[adapters/langchain_adapter.py]] | `except EnvironmentError: raise` passes built-in `OSError` subclasses through unwrapped. A real refused connection was checked and is wrapped correctly; other paths weren't | ran (refused socket), read (the rest) |
| [[datasources/filings.py]] | a truncated gzip response raises an uncaught `EOFError`; the paragraph highlight marks the first match, not the figure's own position | read |
| [[web/server.py]] | replay runs with an empty context, has an operator-precedence quirk choosing the directive, and compare runs store no config to replay from | read |
| [[web/frontend/src/api/stream.ts]] | a CR/LF pair split across chunks becomes a false event boundary | read (and the clean-checkout test failure) |
| [[web/frontend/src/api/client.ts]] | the source-snippet request sends no scope token; cached tokens are never refreshed | read |
| [[web/frontend/src/components/Assessment.tsx]] | `abstained` and `extraction_failed` aren't handled, so the investor "withheld" notice doesn't show for extraction runs | read |
| [[web/frontend/src/views/CompareView.tsx]] | a running chat shows on the compare page; `new URL()` on source links isn't guarded | read |
| [[web/frontend/tests/fixtures/*]] | the investor fixtures carry `"scope": "auditor"`, because the field is set when a run is created and redaction doesn't change it; the run page shows it as a badge | read |
