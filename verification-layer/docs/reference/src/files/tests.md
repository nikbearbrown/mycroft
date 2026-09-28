---
title: Python tests
slug: files-tests
section: Files
order: 100
summary: The unittest suite under tests/ — what each module locks in, how it stays network-free and model-free, and where its fixtures came from.
---

The `tests/` package is the machine half of the verification stack for the Python side: conformance checks that halt, not reports. Each module pins a behaviour that an earlier change broke, or that a later change could quietly break, and most docstrings name the log entry or live run that motivated them.

### Running the suite

From inside `verification-layer/`:

```
python -m unittest discover -s tests -t .
```

From the repository root, `python -m unittest discover -s verification-layer/tests -t verification-layer`. Both commands are the ones `CLAUDE.md` in this folder gives. The suite is plain `unittest`; no module needs pytest (the one docstring that mentions pytest, in [[tests/test_phase1_schemas.py]], is a leftover).

The number of tests is not written here. [[web/self_report.py]] counts them by discovery at runtime and the build generates the count; the RUN_LOG records the result of each full run.

### The design rule: no network, no model

`CLAUDE.md` states it directly: the suite is network-free and model-free by design, and if a change needs a new dependency or a live call to pass, the test is wrong, not the environment. The modules keep to it in five ways:

- **Injected fetchers.** Code in [[datasources/edgar.py]] and [[datasources/filings.py]] takes a `fetch_fn` / `fetch` argument; tests pass a function that returns a fixed payload (`_fake_fetch`, `FakeSec`).
- **Patched import sites.** Route tests patch `web.server.lookup_cik`, `web.server.fetch_company_facts`, `web.server.find_excerpt` and `web.server._build_adapter` where the route looks them up, and point `web.db.DB_PATH` at a temporary SQLite file that is deleted in `tearDown`.
- **Scripted agents.** An agent is any callable `(subject, context, directive) -> AgentResponse`. Tests supply one from [[tests/support.py]], from [[adapters/fixture_adapter.py]], a `MagicMock`, or a small local closure that returns `_parse_response(...)` of a fixed reply.
- **No assessment extraction.** Ticker compares make one extra model call per agent (the B4 option 1 extraction). `tests.support.no_model_extraction()` replaces `web.server._build_model_call` with a builder whose call raises `ConnectionError`, so the route takes its `extraction_failed` path. Generic-subject compares don't make that call (see the comment above `assess_a` in [[web/server.py]]), so tests that only use generic subjects, such as the gate and trace-withholding route tests, don't need the patch.
- **Loopback only.** [[tests/test_model_timeout.py]] is the one module that opens a socket. It binds a stub Ollama server to `127.0.0.1` on an ephemeral port, so it exercises the real ChatOllama and httpx client without leaving the machine.

### Shared helpers

[[tests/support.py]] holds the two helpers several modules share: `make_scripted_adapter(failure_mode)` for the ADR-07 retry and halt paths, and `no_model_extraction()`. Every other double is local to the module that uses it.

### The layering test

[[tests/test_layering.py]] is the enforcement for the package layout the README describes. It reads imports by AST, so a layering violation fails as an assertion naming the file and line rather than as an import error during collection. Changing the allowed layers means editing its table, deliberately.

### Known pitfall: a global guard in `tests/__init__.py`

`tests/__init__.py` must stay inert. [[web/self_report.py]] runs `unittest.TestLoader().discover()` over this folder inside the running server to count tests, which imports every test module and the package itself. In the code, that happens whenever `GET /api/self-report` builds its report (`build_self_report()` calls `_discover_test_counts()`); the RUN_LOG and the `tests/support.py` docstring describe it as happening at startup. The RUN_LOG entry "2026-09-26 (continued) -- Option 1 (assessment extraction) + B5 + U8" records what happened when a suite-wide guard lived there: it made LangChain's chat builder raise, the live server inherited it, and three compares failed before any model call. The fix removed the guard, moved to per-test `no_model_extraction()`, and added `TestTestPackageIsInert` in [[tests/test_synthesis.py]]. The `no_model_extraction()` docstring in [[tests/support.py]] carries the same warning.

A corollary: module-level code in any test file also runs inside the server whenever the self-report counts tests. Keep test modules free of import-time side effects.

## `tests/__init__.py`

**Role:** the package marker, and nothing else, on purpose.

The file is empty. It makes `tests` importable as a package, which [[tests/test_layering.py]] requires of every top-level folder and which lets modules write `from tests.support import ...`.

### Design notes
It is empty because the server imports it (see "Known pitfall" above). The RUN_LOG entry "2026-09-26 (continued) -- Option 1 (assessment extraction) + B5 + U8" lists it as "back to empty" after the model guard was removed. `TestTestPackageIsInert` in [[tests/test_synthesis.py]] imports `tests` and `tests.support` and checks that `adapters.langchain_adapter._build_chat` is still the real function.

Related: [[tests/support.py]], [[web/self_report.py]]

## `tests/support.py`

**Role:** test-only doubles shared across modules: the scripted adapter for ADR-07's retry and halt paths, and the patch that keeps route tests from reaching a model.

### Key functions
- `make_scripted_adapter(failure_mode="none")`: returns an `AgentAdapter` with a per-instance call counter. `"none"` returns a valid two-block reply on the first call; `"retry_success"` raises `StructuralParseError` on call 1 and returns a valid reply on call 2; `"halt"` raises on every call. Any other mode raises `ValueError`. The valid reply is built by the real `_parse_response` from a template that echoes the subject and context into both blocks, so tests can check that the context actually reached the agent (for example, that the patched Assets figure appears in extracted claims in [[tests/test_compare_route.py]]).
- `no_model_extraction()`: returns an unstarted `unittest.mock.patch` of `web.server._build_model_call` whose built call raises `ConnectionError("no model in tests")`. Callers `start()` it in `setUp` or add it to their patch list.

### Design notes
The module docstring explains why a scripted adapter exists: a real model can't be made to produce a structural parse failure on demand, so the retry-then-halt control flow can only be exercised deterministically by injecting a callable. It is dependency injection of the project's own control flow, never registered in [[adapters/registry.py]] and not reachable from the running application.

`no_model_extraction()` is a per-test patch rather than a package-wide guard for the reason in its docstring, found live on 2026-09-26 (see "Known pitfall" above).

### Limits and open issues
- The docstring's supporting evidence is out of date. It says real models "essentially never fail" the format, citing the ledger's `retry-halt-unproven` entry and 24 agent-runs with zero retries. The RUN_LOG entry "2026-09-27 (continued) -- A model-call timeout, and a ledger refresh that found two wrong claims" marks that entry RESOLVED, observed, with retries and halts counted from stored runs. The reason for the scripted adapter still holds (a failure can't be produced on demand); the cited count doesn't.

Related: [[core/contracts.py]], [[core/parsing.py]], [[pipeline/middleware.py]], [[web/server.py]]

## `tests/test_adapter_registry.py`

**Role:** pins [[adapters/registry.py]] as a data-driven provider table.

What it locks in:
- **Credential-free construction.** Every registered provider builds with no API key. The docstring explains the stakes: if `make_langchain_adapter` moved its key check into construction, the whole suite would start needing a live key and the failure would look like an environment problem.
- **Actionable errors.** `resolve("not-a-provider")` raises `ValueError` naming every valid provider.
- **Spec consistency.** Each spec's key matches its `name`; `model_key` and `default_model` are declared together or not at all; `supports_tools` is a callable returning a bool (it depends on whether `TAVILY_API_KEY` is set at call time).
- **Model labels and overrides.** `model_label` names the configured model or falls back to the declared default. `with_model_override` writes to the key the provider reads, doesn't mutate its input, and, as a deliberate case, ignores the override for a provider with no model key. That branch is exercised by registering a throwaway `test-no-model` spec, because the one shipped provider always has a model key.
- **Open for extension.** A provider registered at runtime (`test-echo`) is immediately resolvable, buildable, labelled and overridable with no caller edits.

Stubs: throwaway `ProviderSpec`s built on `make_scripted_adapter`, removed in `finally` / `tearDown` so they don't leak into other tests.

Related: [[adapters/langchain_adapter.py]], [[tests/support.py]]

## `tests/test_assessment.py`

**Role:** the structured `<assessment>` block (B4): validator, parser contract, recording, internal-tier handling, directive v1.6.0, and the bull/bear pairing through `/api/compare`.

What it locks in:
- **A closed vocabulary, nothing coerced.** `parse_assessment` keeps a valid block whole; `"A-"` and `"Strong Buy"` become issues and are dropped, not mapped to the nearest value. Invalid JSON is not repaired, is reported with its line, and keeps the raw text. Unclosed, empty and absent blocks each get their own status. Bounds are enforced: `key_points` beyond the first three are dropped, a non-numeric assumption or an unknown assumption key is dropped with an issue, unknown `key_metrics` are filtered, and a non-object body is `invalid_fields`.
- **Which directives ask.** `expects_assessment` is true for v1.6.0 and later (including a two-digit minor like `v1.10.0`) and false for v1.5.2, v1.0.0, `corrective`, `None` and an unparseable version.
- **`KEY_METRICS` tracks the comparator.** It must equal the names in `validation.facts.METRICS`, minus the `self_report` and `year` families.
- **The old parser contract is unchanged.** Without `allow_assessment`, a third block is text outside the XML blocks and fails. With it, the block is accepted closed, unclosed or absent, but only directly after `</conclusion>`: placed before the conclusion, or after other trailing text, it still fails.
- **Recording.** Under v1.6.0 a valid block is stored on the reasoning object and absent from the investor projection; a broken block never fails the attempt and the raw text is kept; the corrective retry isn't asked for one; older directives record nothing.
- **One list of internal keys.** `redact_for_scope` in [[validation/gate.py]] must drop every key `to_dict(investor_scope=True)` drops. The comment records that the two lists had drifted on 2026-09-26.
- **Directive v1.6.0.** Registered but not active (the active directive is v1.5.2; the test comments say v1.6.0 was reverted on 2026-09-26, see [[core/directive.py]]). Undoing `V1_6_0_CHANGES` in reverse must give back v1.5.2's text exactly, and the text must still carry the grounding and citation rules.
- **Bull/bear through the route.** Both sides get the same figures (their contexts differ only in the `Brief:` line), each side's assessment is recorded, both steps run on v1.6.0, and the rule is `canonical_facts`. Under the active v1.5.2, the same scripted reply halts both agents, which is the pre-B4 contract. The default pairing is unchanged (`lenses`, `concept_aware`).

Stubs: local scripted adapters; the route class patches the database path, `lookup_cik`, `fetch_company_facts` (with the AAPL companyfacts fixture), `_build_adapter`, applies `no_model_extraction()`, and patches `core.directive.ACTIVE_DIRECTIVE` to v1.6.0 to reach the assessment path.

Related: [[core/assessment.py]], [[core/parsing.py]], [[pipeline/middleware.py]], [[producers/__init__.py]]

## `tests/test_audit.py`

**Role:** the B6 audit record ([[validation/audit.py]]) and its two routes, `GET /api/runs/{id}/audit` and `GET /api/runs/{id}/export.md`.

What it locks in:
- **Shape from the record.** `audit_record` returns the design's keys and reads each from the stored run: conflict driver, gate status, grade candidates, and filing accession and index URL.
- **A review, not a dump.** `to_markdown` produces the named sections, a readable figure row, the model-judgment note and the "adequacy is a human judgment" sentence, and no raw JSON above the Sources section. A recorded decision is reported with who, what and the rationale as a quote. A table cell with `|` or a newline stays on one line with the separator escaped.
- **Scope parity.** An investor export and an investor audit read carry no agent grade and no disputed value, exactly like an investor run read.
- **Read-only.** Exporting at either scope leaves the stored record byte-for-byte unchanged.
- **Only compare runs.** A chat run's audit is 422; an unknown run is 404.

Stubs: none beyond a temporary database. The run is a real stored AAPL compare (`8ecb0922`, live on 2026-09-26, per the docstring), loaded from the frontend fixture `web/frontend/tests/fixtures/run_compare_b5_auditor.json`, not from `tests/fixtures/`.

Related: [[web/server.py]], [[web/db.py]], [[validation/gate.py]]

## `tests/test_claims.py`

**Role:** claim extraction in [[validation/claims.py]], centred on the 2026-08-29 widening to bare decimals.

What it locks in:
- **Citations.** `[SOURCE: label, url]` yields the label and URL; a repeated label is de-duplicated.
- **Quantitative claims.** Dollar amounts with a magnitude word, percentages, multiples and basis points are extracted. So are bare decimals, using the two live cases that motivated the change: the fabricated debt-to-equity `0.34` (AAPL) and the EPS pair `14.41` / `14.24` (GOOGL).
- **Deliberate limits, asserted.** A bare integer (a year, a count) is not a claim. A section number like `2.1` *is* extracted: the accepted false positive of catching unitless ratios, pinned so nobody removes it by accident.
- **Hedges and causal phrases** are each detected; `None` and `""` return an empty list; `to_dict` omits empty source fields.

Stubs: none; pure functions.

Related: [[core/numeric.py]], [[tests/test_numeric.py]]

## `tests/test_compare_route.py`

**Role:** route-level tests for `POST /api/compare`, the first route test in the subsystem.

What it locks in:
- A ticker compare returns 200, is not halted, and is `COMPARED`.
- **Claims per producer.** At auditor scope, claims and a verification rate are present for both slots, and the claims come from real content: one cites the patched Assets figure. This locks in the fix for the ledger's `fabrication-not-caught` entry (the route previously never called `extract_claims` / `verify_claims`).
- **What is stored.** A stored run keeps producers, contexts, facts, steps (including an `llm` step) and claims, with the first fact for slot A being `Assets` and the rule `concept_aware`. The comment records that before 2026-09-24 a stored compare kept too little to review later.
- **Rule selection.** Generic subjects use `canonical_facts`; a ticker request can opt into `canonical_facts`.
- **Investor scope** withholds claims and `thought_log` but keeps the verification rate, which is derived.

Stubs: temporary database; `lookup_cik` and `fetch_company_facts` patched with a small inline payload; `_build_adapter` returns `make_scripted_adapter("none")`; `no_model_extraction()`. The app is imported after patching.

Related: [[web/server.py]], [[validation/cross_validation.py]], [[validation/claims.py]], [[validation/verification.py]]

## `tests/test_concept_linkage.py`

**Role:** measures the concept-linkage rule ([[validation/concept_linkage.py]]) against the real-run corpus instead of assuming it works.

What it locks in:
- **Tagging.** A natural-language phrase ("Assets of $383.266 billion") and a raw XBRL tag name echoed from the context ("EarningsPerShareDiluted (6.88)") are both tagged; a ratio with no known concept nearby is untagged. A regression case from GOOGL run `2c3c4f23`: a decimal point inside `14.41` must not end the sentence and hide the "diluted EPS" keyword before it.
- **Against the corpus.** Among `disjoint_concepts` runs, only the historic true positive `f4a4c782-…` still flags (`test_kills_fifteen_of_sixteen_disjoint_concept_false_positives`); that run still flags with `0.34` divergent; no run outside the `disjoint_concepts` and `genuine_conflict` labels newly flags; and the corpus has no `genuine_conflict` run to measure against.

The corpus class docstring says each expected value was measured by running the module, not decided in advance, and that a changed result is news to be explained, not silenced. The labels themselves are AI-assigned judgments pending human review; the counts inherit that caveat.

Stubs: none; pure functions over `tests/fixtures/cross_agent_real_runs_corpus.json`.

### Limits and open issues
- The module docstring still calls concept linkage "a PROTOTYPE, not a replacement". Since 2026-09-11 it is what `/api/compare` uses for the ticker pairing (see [[tests/test_compare_route.py]] and the RUN_LOG entry "2026-09-11 (continued) -- Fix core comparator correctness"). The tests are still correct; the framing is dated.

Related: [[tests/test_real_run_corpus.py]], [[tests/test_facts.py]]

## `tests/test_concurrency_and_stream.py`

**Role:** concurrent agents, the thread-safe step trace, two LangChain adapter helpers, and the server-sent-event (SSE) stream routes.

What it locks in:
- **StepTrace under threads.** Many threads appending at once get unique, gap-free sequence numbers. Subscribers see `step_started` and `step_finished` as copies (mutating the copy doesn't change the trace), a timed step's start snapshot has no duration, and a listener that raises doesn't break the run.
- **Real overlap.** Both agents must reach a `threading.Barrier(2)` together, so a sequential run fails rather than passing by accident. `CROSS_AGENT_MAX_CONCURRENCY=1` restores strict A-then-B. When B finishes first, the reasoning objects are still ordered A then B. Concurrent and sequential runs give the same status, flag, divergent numbers, score and agreement.
- **Tool calls (`_call_tool`).** A tool that *returns* an error is retried once with the query only; a second returned error is recorded as `"error"`, not as a result; a raised error is also retried. The class docstring dates the finding to a live run on 2026-09-24.
- **A reply split across tool turns (`_parse_across_turns`).** The final message wins when it parses on its own; a `<thought_log>` opened before a tool call and closed after it is kept whole; on failure the raised error carries everything the model wrote.
- **Result URLs.** `_result_urls` keeps rank order and skips entries without a URL; an error string has none.
- **Stream routes.** `/api/compare/stream` emits `run_started` first and `result` last, one `agent_finished` per slot, `fetch`, `llm` and `compare` step kinds, every agent finish before the comparison, and a result with the same run id and the same top-level keys as the plain route. `/api/chat/stream` ends with a non-halted result and an `llm` step.

Stubs: `make_fixture_adapter` and `make_scripted_adapter`; a `_FakeTool` scripted stand-in for Tavily search; the same route patches as [[tests/test_compare_route.py]], plus an explicit `init_db()` because a bare `TestClient` never fires the app's startup event.

Related: [[web/step_trace.py]], [[validation/cross_validation.py]], [[adapters/langchain_adapter.py]], [[web/server.py]]

## `tests/test_constraints.py`

**Role:** B2 (the overlapping lens metrics) and B3 (accounting checks in [[validation/constraints.py]]), and how a failed hard check feeds the decision gate.

What it locks in:
- **B2 overlap.** With the shared concepts passed in, `concept_aware` compares shared figures by value (`$2.02` vs `$2.10` flags); with the v1 default it still excludes them. Rounding, and a shared figure cited by only one side, are not conflicts. In the canonical comparison, a shared figure only one agent cites is `CITED_BY_ONE`, while a figure only one agent was given is `ONE_SIDED`; shared EPS now matches.
- **Rules on an agent's own figures.** Diluted EPS above basic is a hard failure that gates, with the arithmetic shown; equal EPS with a loss passes; the free-cash-flow identity fails on a wrong total and passes on the right one; net income above operating income is a heuristic that warns but never gates; figures from different stated periods are skipped, not failed; a rule missing one of its figures isn't shown.
- **Claims against what the agent was given.** Rounding, truncating or writing the full number is not misquoting; a misquoted input is a gating failure whose arithmetic names the given value, period and form; a prior-period figure beside the right one is fine; a different stated period is skipped; per-share figures are checked to the cent; only metrics the agent was actually given are checked.
- **The filing itself.** The real AAPL payload passes and never gates; a filing whose balance sheet doesn't add up is reported but never gated.
- **The gate.** A failed hard check opens the gate as a `check` item, refuses decisions that don't apply to a check (`accept_a`), accepts `confirmed_error`, withholds its arithmetic and the contested figure from investors, and passing checks don't gate.
- **Migration.** A `gate_decisions` table created before `confirmed_error` existed is rebuilt once on `init_db()`, every row kept, a second startup is a no-op, the append-only triggers still refuse `UPDATE` and `DELETE`, and no temporary table is left behind.
- **Through the route.** A ticker run records the shared concepts, lens version v2, a matching shared EPS, and gates on agent A's misquoted revenue; the stored run carries the check policy and gate policy.

Stubs: local scripted agents (`_agent`), temporary database, the AAPL companyfacts fixture for `fetch_company_facts`, `no_model_extraction()`. The migration test writes an old-schema table directly with `sqlite3`.

Related: [[validation/gate.py]], [[validation/facts.py]], [[validation/concept_linkage.py]], [[producers/lens.py]], [[web/db.py]]

## `tests/test_cross_validation.py`

**Role:** the cross-agent comparator ([[validation/cross_validation.py]]) against SDD §10: agreement, contradiction, halts, the rule options, shared run ids, persistence and contradiction queries.

What it locks in:
- **Agreement and contradiction under the default rule** (`symmetric_difference`). The same number in different words is not a contradiction; identical conclusions score perfectly; no numbers on either side is not a contradiction. Different values flag; a number present on one side and absent on the other flags; bare-decimal EPS values diverge (the GOOGL live case of 2026-08-29).
- **Halts are evidence, not discards.** A halt on A, B or both is reported distinctly, and every attempt from both agents is kept. With no comparison, the flag, score, agreement and overlaps are `None`, not `False`: `False` would claim "checked, found nothing" (P3). A retry that recovers is compared normally.
- **`concepts_expected_to_overlap=False`.** It suppresses pure presence/absence while reporting the divergent numbers in full, still flags a genuine value conflict, and, as a deliberately asserted gap, still flags two non-empty sets about different concepts.
- **`contradiction_rule="concept_aware"`.** It closes that gap for known concepts, still flags an untagged conflict, and still flags the historic fabrication when the other side cites no numbers at all (which `concepts_expected_to_overlap=False` suppresses).
- **One run id** across both agents' records, including a caller-supplied one, with both agent ids recorded.
- **Serialisation** survives a normal run and a double halt.
- **Fixture adapter guardrails.** An empty conclusion, or one containing an XML closing tag, is rejected at construction; the fixture's output passes the real parser.
- **End to end with persistence.** Real EDGAR helpers with an injected fetch build the contexts, the run is persisted to a temporary store, and the read-back keeps the flag, both agent ids, divergent numbers, both attempt histories and data-source provenance. A halted run persists as halted with its failed attempts. Two real producers read different concepts from one payload, apart from the two figures lens v2 shares.
- **Same-source runs.** With identical context, matching conclusions agree and a different figure flags. A bare-year disagreement is invisible to the old rule (no bare-integer pattern) and flagged by `canonical_facts` with years.
- **`list_contradictions`** returns flagged runs only, never halted ones (their flag is `None`), and filters by ticker.

Stubs: `make_fixture_adapter` and `make_scripted_adapter`; `_fake_fetch` for EDGAR; temporary database for persistence classes. Data sources are marked `SIMULATED` because the fetch is injected.

### Limits and open issues
- The module docstring says the model call is "a fixture or the mock adapter". The mock adapter was removed on 2026-09-22 (RUN_LOG "Remove mock_adapter.py, add adapters/langchain_adapter.py"); the scripted adapter from [[tests/support.py]] took its place.

Related: [[adapters/fixture_adapter.py]], [[validation/concept_linkage.py]], [[validation/facts.py]], [[web/db.py]], [[scripts/run_cross_agent_live.py]]

## `tests/test_cutover.py`

**Role:** the U9 cutover: `/` serves the React app, and the classic UI is archived, not deleted.

What it locks in:
- `/` redirects (302 or 307) to `/app/` with `Cache-Control: no-store`. The comment says a cached `/` once outlived the cutover.
- With no frontend build, `/` returns 503 and says to run `npm run build`.
- `archive/web-static-legacy/` holds `index.html`, `app.js`, `style.css` and a `README.md` whose restore instructions include the `git mv` command, and `web/static/index.html` no longer exists. This is the repo's "never delete, archive" rule turned into a check.

Stubs: `web.server.FRONTEND_DIST` patched to an existing directory or to a path that doesn't exist.

Related: [[web/server.py]]

## `tests/test_directive_echo.py`

**Role:** a conclusion that restates the directive is a structural failure, not an answer.

The docstring records why: a count of stored runs on 2026-09-24 found conclusions that opened with the directive's own block instruction and passed the XML parse, plus NFLX runs that copied the v1.3.0 citation example as if it were a finding. The counts and the replay over stored conclusions are in the docstring and in the RUN_LOG entry "2026-09-24 (continued) -- Directive echo, properly".

What it locks in:
- **Detection.** `find_directive_echo` finds the real v1.5.0 echo, the copied citation example, and a copy of the v1.5.1 description. It ignores case and punctuation differences but doesn't treat a paraphrase as an echo. Clean answers, including an honest "insufficient context", are never flagged under v1.3.0, v1.5.0 or v1.5.1.
- **Rejection.** `reject_unusable_conclusion` raises `StructuralParseError` naming the problem and keeping the raw reply, for an echo and for an empty conclusion.
- **Through ADR-07.** Echo then clean gives `PARSE_FAILURE` then `SUCCESS` with the echoed attempt kept; empty twice halts; a clean first attempt is untouched.
- **In the trace.** A wrapped adapter's step reads `parse_failure` with the reason.
- **Prevention in the template.** The active directive is v1.5.2; v1.5.1 and v1.5.2 have nothing inside the template's tags; v1.5.2 names the exact closing tags and forbids `[/conclusion]`, and removing those two additions gives back v1.5.1 exactly; the grounding and citation rules remain.

Stubs: `_sequence_adapter` returns canned conclusions in order; no model, no network.

### Limits and open issues
- The class `TestV151Template` now holds v1.5.2 checks, including `test_active_directive_is_v152`. The name reflects when the class was written.

Related: [[core/parsing.py]], [[core/directive.py]], [[pipeline/middleware.py]], [[web/step_trace.py]]

## `tests/test_docs_coverage.py`

**Role:** the drift check for this reference: every project file is documented, and the built site
has no broken link.

What it locks in:
- **Coverage.** Every project file (tracked by git, or new and not ignored) matches exactly one
  entry in `docs/reference/src/`, and every entry matches a file. A new file without an entry fails
  here, with the list of problems and the command to rebuild.
- **Consistency.** The site builds in memory with no problems: every `[[file link]]`, page link
  and anchor resolves. The builder and this test are themselves documented.
- **Every page** links the stylesheet and the search index.
- **The renderer.** File links resolve or are reported; code spans aren't markup; file-entry
  headings get `f-` anchors; tables, nested lists and callouts render; text is escaped.
- **Globs.** `*` stays in one folder; `**` crosses folders.

Stubs: none needed. The builder parses source with `ast` and regular expressions and imports no
project module. It calls `git ls-files`; without git the coverage class is skipped, not failed.

### Limits and open issues
- It checks that an explanation *exists*, not that it is *right*. Whether an entry is accurate is
  still a human judgment ([[scripts/build_docs.py]]).
- It doesn't check that the committed HTML matches the sources: run `python scripts/build_docs.py`
  after changing either.

Related: [[scripts/build_docs.py]], [[docs/reference/**]]

## `tests/test_earnings_grader.py`

**Role:** Producer B, the earnings lens ([[producers/earnings.py]]), end to end through the validation loop.

What it locks in:
- **Context.** The summary names the ticker, picks the latest diluted EPS, marks a missing concept as `not reported`, marks every concept `not reported` on empty facts, and carries no Assets or Revenues line.
- **Analysis.** `analyze_earnings` returns a `ValidationLoopResult` attributed to the earnings agent under the caller's run id; the earnings figures reach the agent (the scripted reply echoes them); retry-then-success gives two records; a halt raises `HaltError` with both attempts; an EDGAR fetch error propagates.
- **One CIK path.** Both producers resolve the ticker through the same `lookup_cik`.

Stubs: injected `fetch_fn` payloads and `make_scripted_adapter`. The docstring notes that LangFuse tracing is not asserted, since it degrades without credentials ([[pipeline/observability.py]]).

### Limits and open issues
- A comment still says "mock_adapter echoes the context"; it is now the scripted adapter from [[tests/support.py]].

Related: [[tests/test_financial_grader.py]], [[producers/lens.py]], [[datasources/edgar.py]]

## `tests/test_edgar_facts.py`

**Role:** period- and unit-aware fact selection in [[datasources/edgar.py]] (B0), on a real payload.

The docstring records the bug: before B0, `latest_value()` took the entry with the latest end date and returned a bare number. On AAPL's real payload that gave FY2018 revenue (Apple stopped using `us-gaap:Revenues` after FY2018) and the nine-month year-to-date EPS instead of the quarter.

What it locks in:
- **The old rule, pinned as a record.** `TestLegacyRuleOnRealData` reproduces the old rule and asserts its two wrong picks, so the bug's evidence doesn't depend on memory.
- **The fix on real data.** Diluted EPS is the Q3 quarter with fiscal year, period, form, frame, unit and accession; revenue comes from the current ASC 606 tag while keeping the concept name `Revenues`; Assets is a point-in-time value; an annual basis can be requested; `latest_value` now agrees with `select_fact`.
- **Selection rules on synthetic entries.** A later filing (a restatement) wins; a quarter is recognised by duration when the frame is missing; year-to-date is a labelled last resort; entries with no metadata degrade to "period unknown"; an absent concept is `None`; a `Fact` is frozen and JSON-serialisable.
- **Context lines** carry value, unit, period and tag, and keep the value first, because the legacy UI's provenance check reads the leading number after the first colon.

Stubs: none; pure functions over `tests/fixtures/edgar_aapl_companyfacts_sample.json` and small inline payloads.

Related: [[producers/financial.py]], [[producers/earnings.py]], [[tests/test_producer_lens.py]]

## `tests/test_facts.py`

**Role:** canonical, period-aware figure comparison in [[validation/facts.py]] (B1).

The docstring says the expected values were decided before the code ran, several from real stored conclusions, and that the corpus class pins measured behaviour so a rule change shows as a changed number.

What it locks in:
- **Extraction.** The corpus's true-positive conclusion yields total assets, revenue, net income and the `0.34` debt-to-equity figure. The nearest alias in the same clause wins, even when the alias follows the figure; a longer alias wins a tie; current assets are not total assets; a percent next to a level metric is a change; a self-rated "Confidence level: 90%" is not a figure (the comment says NVDA was flagged on this alone, live on 2026-09-24); numbers inside citations and URLs are ignored; an unnamed ratio is its own metric; context lines parse as inputs.
- **Periods.** Quarter, fiscal year, "third quarter of", TTM, "nine months ended" and no period each parse; a missing year is compatible, a different quarter isn't.
- **Comparison.** The same figure formatted differently matches (a live MSFT case); per-share tolerance is one cent; different periods, one unstated period, and two unstated periods each get their own status and note; unspecified EPS pairs with, or merges into, the specific one; market cap and share price are named and never count as inputs; "per share" makes a figure EPS; stock moves are share-price changes; a lens metric cited by one side is expected (`ONE_SIDED`) and doesn't flag.
- **Derivations.** A correct ratio from the agent's own figures is `DERIVED_OK`; a wrong one is `DERIVED_WRONG` with the correct value in the note, and does not count as a cross-agent contradiction; a ratio with no components anywhere stays uncorroborated and flags; context inputs make a ratio checkable.
- **Years** are compared only when enabled, and period years never become values.
- **Wiring.** Figure rows are computed whatever rule decides the flag; `canonical_facts` with years catches a bare-year disagreement.
- **One alias source.** Every keyword in `concept_linkage.CONCEPT_KEYWORDS` must have a counterpart among its metric's aliases in `METRICS`.
- **Against the labelled corpus** (measured 2026-09-24, per the class docstring, with the reading in the RUN_LOG's B1 entry): the true positive is preserved; exactly six named `disjoint_concepts` runs flag (the true positive and five that state a ratio with no components); nothing flags where there is nothing to compare; both AAPL runs' wrong asset turnover is found; and `concept_aware` still flags fewer disjoint-concept runs than `canonical_facts`, which is why `canonical_facts` is not the default for the financial pairing.

Stubs: `make_fixture_adapter`; corpus fixture; no network.

Related: [[validation/concept_linkage.py]], [[validation/cross_validation.py]], [[tests/test_constraints.py]]

## `tests/test_filings.py`

**Role:** locating a companyfacts figure in its filing's inline XBRL ([[datasources/filings.py]], BP), the `/api/facts/excerpt` and `/api/runs/{id}/source-snippet` routes, and the per-result search snippets the LangChain adapter records.

What it locks in:
- **Finding the cell.** Quarterly revenue is the "Total net sales" row under the ASC 606 tag, with its displayed text, value, scale, a column header naming the three months ended June 27, and a highlight covering exactly its own cell. Net income, diluted EPS and total assets are found the same way, and a section title is not taken as a column header. The nine-month figure and the Products/Services split are different contexts and are not returned for the quarter. A synthetic prose fact checks sign and scale handling and the out-of-table case.
- **`find_excerpt`.** A found excerpt carries form, filing date, scale words, the best row, the document URL and the filing index URL; the document is fetched once and then cached. Every odd case (no inline XBRL, accession not in the index, document too large, fetch failed, concept not found) returns its own status, a message, and still links the filing.
- **Search snippets.** `_result_snippets` keeps one entry per result with a URL, truncates long content, allows a missing snippet, and returns nothing for an error string.
- **Routes.** The excerpt route returns the best row; malformed `accn`, `cik`, `concept` or `end` values are refused with 422 before they reach a URL. The snippet route finds the figure in a stored search result, reports `not_found` for an unknown URL, and explains when a run predates stored snippets.

Stubs: `FakeSec`, a callable that serves a fake submissions index and the fixture document and records every URL requested; `web.server.find_excerpt` is patched to use it with a temporary cache directory; temporary database.

Related: [[adapters/langchain_adapter.py]], [[web/server.py]], [[datasources/edgar.py]]

## `tests/test_financial_grader.py`

**Role:** Producer A, the financial lens ([[producers/financial.py]]), plus the EDGAR lookup helpers.

What it locks in:
- `lookup_cik` finds a known ticker case-insensitively and raises `EdgarFetchError` for an unknown one; `fetch_company_facts` returns the injected payload.
- The summary names the ticker, picks the latest Assets value, and marks missing concepts `not reported`.
- `analyze_ticker` mirrors the earnings grader's checks: result type, financial agent id, run id, the context reaching the agent, retry-then-success, halt with both attempts, and fetch errors propagating.

Stubs: injected `fetch_fn` payloads and `make_scripted_adapter`; LangFuse tracing not asserted, as in the earnings tests.

### Limits and open issues
- The docstring still calls this a "Week 9/10 analyst skeleton", and a comment still says "mock_adapter echoes the context".

Related: [[tests/test_earnings_grader.py]], [[datasources/edgar.py]], [[producers/lens.py]]

## `tests/test_gate.py`

**Role:** the human decision gate (BG): [[validation/gate.py]], the `gate_decisions` table in [[web/db.py]], the `/api/runs/{id}/decisions` routes, and scope-aware reads.

What it locks in:
- **The handoff condition (P4).** A run is `AWAITING_DECISION` while any `MISMATCH` row lacks a decision and `DECIDED` once every one has one. Uncorroborated and matching rows don't open it; an uncompared run needs no decision; a run stored before the gate policy existed is `NOT_GATED`, never gated after the fact. The state carries a note that the reviewer's identity is not authenticated.
- **Supersession.** A later decision on the same item wins, and the history keeps both, newest first, with the earlier one marked superseded.
- **Refused, not repaired (P3).** `validate_decision` trims names and de-duplicates cited items, and refuses: an unknown decision, a too-short rationale, a blank name, no cited items, a cited `MATCH` row, an override with no value, a value on a non-override decision, an override citing two figures, a boolean as a value, and any decision on an ungated run.
- **Scope.** Auditors see everything plus the gate, and the stored payload isn't mutated. Investors, while pending, lose the contested row's values, both conclusions, divergent numbers, claims and internal reasoning fields, see a "Pending human review" marker, and keep agreed figures. Once decided, investors get the figures and conclusions back; `thought_log` stays withheld (SEC-01).
- **Store (P7).** Decisions round-trip in insertion order; the database itself refuses `UPDATE`, `DELETE` and an empty rationale even past the route; the retention purge removes a run's decisions with it and restores the delete guard afterwards.
- **Through the routes.** A generic compare that disagrees on a release year opens the gate and is stored with the gate policy. Investor reads of the run and session are withheld until decided; an investor can't decide (403); a bad rationale or a non-contested cited item is 422; a valid decision returns `DECIDED`, after which investors see the figures and the decision and the run list shows the new status. An investor who starts the run gets it withheld live; a read with no token uses the stored scope; a pre-gate run is `NOT_GATED` and takes no decision.

Stubs: payload builders (`_row`, `_payload`, `_decision`); local scripted agents patched in through `_build_adapter`; temporary database. The route tests use a generic subject, so no extraction call is made and `no_model_extraction()` isn't needed.

Related: [[validation/gate.py]], [[web/db.py]], [[web/server.py]], [[tests/test_trace_withholding.py]]

## `tests/test_layering.py`

**Role:** enforces the package layering by reading imports from the source, so the structure has to be broken deliberately, by editing the table.

What it locks in:
- **Allowed layers.** Each package may import only from its allowed set: `core/` from nothing internal; `adapters/`, `pipeline/` and `datasources/` from `core/` only; `producers/` from `core`, `pipeline` and `datasources`; `validation/` from `core`, `pipeline` and `web`; `web/` from everything but `scripts` and `tests`; `scripts/` and `tests/` from everything. Intra-package imports are always allowed.
- **`core/` stands alone**, asserted separately because every other layer relies on it.
- **The one upward exception.** `validation/` may import `web` (to persist through `web.db`) only inside a function body. At module level it would make the comparator unimportable without the database layer and create a cycle with [[web/server.py]]. The test also fails if no such lazy import exists, so a move is noticed rather than silently passing.
- **Network egress.** Outside `datasources/` and `adapters/`, only [[validation/verification.py]] may contain `urllib.request` or `import requests`; a new egress point has to be named in the test (P2).
- **No loose root modules.** The subsystem root holds no `.py` file except `__init__.py`, and every package has an `__init__.py`. The class docstring says a loose root module once shadowed a stdlib name.

Stubs: none. It parses files with `ast`; it imports none of them.

### Limits and open issues
- The egress check is a text search for two strings. Other ways of opening a connection (`http.client`, `socket`, `httpx`) are not caught.
- The root check looks only at `*.py` directly in the root.

Related: [[README.md]], [[core/contracts.py]]

## `tests/test_model_timeout.py`

**Role:** the model-call stall limit, `MODEL_TIMEOUT_S` in [[adapters/langchain_adapter.py]].

What it locks in:
- **A silent server ends the call.** A server that reads the request and never answers ends both the plain model call (the assessment extraction) and the agent adapter with `LangchainTimeoutError`, well before the test's ten-second bound. That error is a `LangchainConnectionError`, so the existing route handlers record a halted run; the message says it sent nothing for the configured limit.
- **A stall limit, not a length cap.** The deliberate break attempt: a server that streams the answer slowly but steadily, for longer than the limit in total, still succeeds and returns the conclusion.
- **Classification.** A refused connection is reported as unreachable, not as a timeout. A timeout wrapped in another exception is still recognised as one.
- **Plumbing.** The limit reaches the Ollama client as `client_kwargs={"timeout": ...}`.

Stubs: `_StubOllama`, a `ThreadingHTTPServer` on `127.0.0.1` that either hangs or streams NDJSON chunks, driven by the real ChatOllama and httpx client; `OLLAMA_HOST` and `MODEL_TIMEOUT_S` patched on the module. The refused-connection case builds an `httpx.ConnectError` directly because, per its comment, a real refused socket takes seconds on Windows.

### Design notes
The RUN_LOG entry "2026-09-27 (continued) -- A model-call timeout, and a ledger refresh that found two wrong claims" gives the default's reasoning (above the slowest stored successful attempt) and records the timings seen when these tests first ran. The timeout bounds an Ollama hang but doesn't fix it; the ledger's `ollama-hangs-under-compare` entry stays open.

### Limits and open issues
- Only the Ollama path is exercised. The entry above says the limit is also passed to Gemini's `timeout`; no test covers that path.

Related: [[pipeline/middleware.py]], [[web/server.py]]

## `tests/test_numeric.py`

**Role:** the single quantitative pattern in [[core/numeric.py]], and the proof that there is only one copy of it.

What it locks in:
- **One object, not three copies.** [[validation/claims.py]] and [[validation/verification.py]] hold the same `QUANTITATIVE_RE` object, and [[validation/consistency.py]] the same `extract_numbers` function; none defines a private `_NUMBER_RE` or `_QUANTITATIVE_RE`; the comparator's `_extract_numbers` still reaches the shared extractor. The docstring explains why identity is the check: three identical copies pass every behavioural test until one is edited.
- **Behaviour.** A dollar amount with its magnitude word is taken whole; percent, multiple and basis points match; a bare decimal matches; a bare integer doesn't; results are lowercased and stripped; duplicates are kept for the caller.
- **Accepted false positives, asserted.** A section number and a version string both match.

Stubs: none.

### Limits and open issues
- `test_suffix_map_covers_every_magnitude_the_pattern_matches` checks a hand-written word list against `SUFFIX_MAP`, not the words the pattern can actually match. A magnitude word added to the pattern but not to the list would pass.

Related: [[tests/test_claims.py]], [[validation/cross_validation.py]]

## `tests/test_phase1_schemas.py`

**Role:** the Phase 1 records: `ReasoningObject` and `RunSession` in [[core/schemas.py]], the SEC-01 investor projection, and the directive registry in [[core/directive.py]].

What it locks in:
- **ReasoningObject.** Built with ids and timezone-aware timestamps; confidence rounded to four places; every `AgentID` accepted; `PARSE_FAILURE` and `HALT` valid without a conclusion; data sources and citations stored. Refused: a `SUCCESS` with no conclusion, confidence outside 0–1, an attempt number other than 1 or 2, attempt 2 with `PARSE_FAILURE` (ADR-07), data-quality warnings with no degradation reason (ADR-04), and mutation after construction.
- **RunSession.** The ticker is upper-cased and stripped; the directive text is stored verbatim (ADR-05); the confidence classification must match the score, with the 0.4 boundary as `STANDARD` (ADR-08). Refused: `completed_at` on an open session, a mismatched classification either way, a too-long or empty ticker, blank directive text, mutation.
- **SEC-01.** The investor projection has no `thought_log`, `raw_output` or `llm_tokens` key, and none of their content appears anywhere in the JSON; the auditor projection keeps them; safe fields survive unchanged.
- **Directives.** The active directive is v1.5.2, has both blocks, warns about structural validation, is frozen (SEC-04), is in the registry under its own version, and is not trivially short; `get_directive` finds v1.0.0 and raises `KeyError` for an unknown version.
- **Serialisation** gives valid JSON with enum values and the session's ticker and directive version.

Stubs: none; pure constructors.

### Limits and open issues
- The docstring suggests `python3 -m pytest`; the suite's documented runner is `unittest`.
- A `sys.path` insert with the comment "Allow running from accountability_layer/ directory" survives from the subsystem's earlier folder name; `-t .` discovery doesn't need it.
- `test_active_directive_is_v1` asserts v1.5.2. The version is hard-coded here and in two serialisation tests, so each directive change edits this file.

Related: [[tests/test_directive_echo.py]], [[tests/test_assessment.py]]

## `tests/test_phase2_agent.py`

**Role:** the Phase 2 structural parser (`_parse_response` in [[core/parsing.py]]) and the ADR-07 validation loop in [[pipeline/middleware.py]].

What it locks in:
- **The parser.** A reply is exactly a `<thought_log>` block and a `<conclusion>` block. Each block's content is extracted and the raw text is preserved. Missing one block, missing both, or any text before, between or after the blocks raises `StructuralParseError`, which carries the raw reply. Whitespace between blocks is allowed; multi-line content is kept; an empty string fails.
- **The loop, happy path.** One `SUCCESS` record at attempt 1 with the final response, thought log, conclusion, context window and the active directive's version and text recorded.
- **Fail then recover.** Two records: `PARSE_FAILURE` at attempt 1, `SUCCESS` at attempt 2. The retry record carries the corrective directive's version (`corrective`) and text while the context window is unchanged, which a session-level directive field alone couldn't show.
- **Fail twice.** `HaltError` carrying both records, `PARSE_FAILURE` then `HALT`, written whatever the outcome.
- **Directives and identity.** The first call gets the active directive and the retry gets exactly `CORRECTIVE_DIRECTIVE_TEXT`; run id and agent id are the same across attempts, including on a halt.

Stubs: `unittest.mock.MagicMock` as `call_agent_fn`, with `return_value` or `side_effect` lists of responses and parse errors.

Related: [[tests/support.py]], [[tests/test_directive_echo.py]]

## `tests/test_producer_lens.py`

**Role:** the single lens runner ([[producers/lens.py]]), the lens declarations, and the registry in [[producers/__init__.py]].

What it locks in:
- **Context format.** The first line is the ticker; every concept gets a line in declaration order; an absent concept renders as `not reported` rather than disappearing, so a missing figure can be told apart from one never requested; the latest value wins; a header appears only when the lens declares one; each line parses back as concept, value first, then unit and period (here `(period unknown)`, since these inline entries carry no metadata).
- **Information asymmetry under lens v2.** The two lenses share exactly `NetIncomeLoss` and `EarningsPerShareDiluted` (B2), both at version v2; each still sees only its own other concepts; v1's first three lines keep their positions so a v1 reader of line N reads the same concept; both contexts come from one payload; the lenses have distinct names, agent ids and trace prefixes.
- **Immutability.** A lens can't be mutated mid-run, because the audit trail reports the concepts the run read.
- **The runner.** A run is attributed to the lens's agent id; the agent receives its own lens's context only; a third lens is a value, not new code; ADR-07 retry behaviour is the same for every lens.
- **Registry.** Lenses are reachable by name; the order is financial, earnings, bull, bear; bull and bear read the same figures (the union of the two lenses) and differ only in their brief; the `lenses` pairing is the original A/B pair.

Stubs: injected `_fetch`, `make_scripted_adapter`, and a spy adapter that records the context it was given.

### Limits and open issues
- The module docstring still lists "the disjointness of the two concept sets" as a pinned property. Since B2 (RUN_LOG "2026-09-25 (continued) -- B2 + B3"), the tests pin a two-concept overlap instead, following the human's decision recorded there.
- `test_producer_order_is_a_then_b` now asserts four lenses; the name predates bull/bear.

Related: [[producers/financial.py]], [[producers/earnings.py]], [[tests/test_edgar_facts.py]]

## `tests/test_real_run_corpus.py`

**Role:** regression tests that replay every stored real cross-agent run in `tests/fixtures/cross_agent_real_runs_corpus.json` through today's comparator.

What it locks in:
- **The fixture keeps its contract.** It loads and isn't empty; every run's label is in the vocabulary (`genuine_conflict`, `disjoint_concepts`, `no_numbers_either_side`, `halted`, `mock_smoke_test`); `_meta.label_counts` matches the actual counts; and `_meta` still carries the labelling caveat and says the extraction was not reviewed. The caveat check exists so the corpus isn't mistaken for attested ground truth (P8).
- **The headline finding.** No run is labelled `genuine_conflict`, and every run that flags today is `disjoint_concepts`. Both failure messages say to update the diagnosis rather than silence the test.
- **Replay equals the snapshot.** Under `symmetric_difference` with `concepts_expected_to_overlap=False`, each run's status, flag and number lists equal its recorded `replay_today` values; a run missing a conclusion must be recorded as `SKIPPED_NO_CONCLUSION`. `test_six_runs_flip_from_stored_true_to_replay_false` asserts how many runs changed from their stored flag, and that none changed from unflagged to flagged.
- **`concept_aware` through the public API.** `TestConceptAwareRuleAgainstCorpus` repeats [[tests/test_concept_linkage.py]]'s three corpus checks through `run_cross_agent_validation(..., contradiction_rule="concept_aware")`, proving the wiring and not just the module.

Stubs: `make_fixture_adapter` replays each stored conclusion verbatim; contexts are placeholders; no model, no network.

### Limits and open issues
- The docstring says `concepts_expected_to_overlap=False` is "the same default web/server.py's /api/compare route uses". Since 2026-09-11 the route uses `concept_aware` for tickers and `canonical_facts` for generic subjects ([[tests/test_compare_route.py]]). The fixture's `_meta.replay_methodology` repeats the same dated claim.
- `TestReplayReproducesRecordedBehaviour` tells the reader to "rerun build_corpus.py" after an intended change. No file of that name exists in this subsystem.
- The labels are AI judgments not yet reviewed by a human; every count asserted here inherits that.

Related: [[validation/cross_validation.py]], [[adapters/fixture_adapter.py]], [[tests/test_facts.py]]

## `tests/test_synthesis.py`

**Role:** the assessment extraction call (B4 option 1, `extract_assessment` in [[core/assessment.py]]) and B5: divergence classification in [[validation/divergence.py]], counted evidence, grade candidates, consensus and the set-the-grade gate item. It also holds the inertness check for the test package.

What it locks in:
- **The test package is inert.** Importing `tests` and `tests.support` leaves `adapters.langchain_adapter._build_chat` as the real function (see "Known pitfall" in the introduction).
- **The extraction adds nothing.** A faithful reply is `valid`. A key point quoting a figure the agent never wrote is dropped; an assumption the agent never stated is dropped (and kept when the agent did state it); a past growth rate is not an assumption, while guidance is. The comment records the live 2026-09-26 case where "up 16% year over year" came back as an assumption under extract v1. An abstention is kept as `abstained` with its reason; a fenced reply is read and the wrapping reported; a failed call is recorded as `extraction_failed`, not raised.
- **Recording in the loop.** A successful answer gets an assessment with the extraction prompt version as its source, the extraction's reply is kept in `raw_output`, and the agent's own text is untouched; a failed extraction never fails the answer; a retry's answer is extracted too; a halt gets none.
- **Classification is deterministic.** Data conflicts come before assumption differences, which come before the residual, named as weighting. A consensus grade exists only when grade and direction agree and no hard check failed; with one side missing, the driver is `insufficient`. Evidence is counted per agent (matches, contradictions, unchecked, unbacked, hard-check failures), not scored.
- **The grade gate.** Differing grades open a `grade` item with both candidates and the driver. `set_grade` needs a grade from the closed list; `both_wrong` doesn't apply; `accept_b` takes B's grade; a set grade decides the gate and is recorded with who set it. Investors see the kind of disagreement but no candidate grade until a human sets one.
- **Migration.** A B3-era `gate_decisions` table is rebuilt with a `final_grade` column, old rows kept.
- **Through the route.** A ticker compare whose agents agree on every figure but not on the grade is classed as weighting, lists both grade candidates, gates on `grade`, records an `extract` step, and after a `set_grade` decision shows investors only the human's grade.

Stubs: `reply(obj)` builds a model call that returns fixed JSON; local scripted agents; the route class patches `_build_adapter`, `_build_model_call` (with scripted grades in order), `lookup_cik`, `fetch_company_facts` (AAPL fixture), and `validation.cross_validation._max_concurrency` to 1 so the grades arrive A then B.

### Limits and open issues
- The module docstring ends "tests/__init__.py makes a real model call impossible". That was the guard the RUN_LOG says was removed; `tests/__init__.py` is empty, and the first test in this file asserts the opposite property. Model calls are kept out by per-test patches.

Related: [[validation/gate.py]], [[pipeline/middleware.py]], [[web/db.py]], [[tests/test_assessment.py]]

## `tests/test_trace_withholding.py`

**Role:** the gate must withhold disputed figures from investors everywhere they appear, including inside the run trace's search results.

The docstring records the finding: on 2026-09-26 the investor read of gated run `ec1a3b44` carried agent A's disputed value inside a search result in a trace step. The RUN_LOG entry "2026-09-26 -- Correction: two claims in earlier entries were wrong; the trace leak they hid is fixed" is the record.

What it locks in:
- **`strip_search_content`.** A tool step keeps its query and URLs, loses the result text and snippets, is marked `result_withheld`, and the stored step isn't mutated. An agent error keeps only its exception type, since the message can quote a disputed value.
- **Stored reads.** A deliberate precondition first: the fixture's trace really contains the disputed value, so the next test can't pass vacuously. Then the investor read contains neither disputed value, the auditor read still has the full trace, and once a decision is stored investors get the trace back. The source-snippet route returns `withheld` to investors while pending and not to auditors.
- **The decisions route.** A pending failed check's arithmetic is `None` for investors and present for auditors.
- **The live stream.** With scripted agents that each make one search through the route's own tool-event hook, no investor tool-step event and no investor result contains either disputed value, the result is `AWAITING_DECISION`, and the auditor stream of the same kind of run keeps the search text.

Stubs: temporary database; the real gated run (live 2026-09-25, per the class docstring) loaded from the frontend fixture `web/frontend/tests/fixtures/run_compare_gated_auditor.json`; `_searching_agent` builders that call `cfg["_on_tool_event"]` with a scripted search result. Generic subject, so no extraction call.

Related: [[validation/gate.py]], [[web/server.py]], [[web/step_trace.py]], [[tests/test_gate.py]]

## `tests/fixtures/*`

**Role:** real data captured from SEC EDGAR and from the subsystem's own run store, trimmed and kept byte-exact, so tests can check behaviour against what production actually saw.

`.gitattributes` marks `tests/fixtures/**` as `-text`, so Git checks the fixtures out without line-ending conversion. The RUN_LOG entry "2026-09-27 -- Committing the work since c53746a, and a checkout-only test failure" records why: `core.autocrlf` had rewritten a frontend SSE fixture on a clean checkout and broken a test.

| File | Origin and provenance | Captured | Used by |
|---|---|---|---|
| `tests/fixtures/aapl_10q_2026q3_trimmed.htm` | Apple Inc. Form 10-Q, accession 0000320193-26-000020, primary document `aapl-20260627.htm`, from SEC EDGAR. Its header comment says every `xbrli:context` from `ix:header`, the condensed consolidated statement of operations table and the balance sheet table are kept verbatim, with everything else removed. Added in RUN_LOG "2026-09-25 (continued) -- BP + U4". | Fetched 2026-09-25 (header comment) | [[tests/test_filings.py]] |
| `tests/fixtures/cross_agent_real_runs_corpus.json` | Every real (non-mock) cross-agent comparison run in `web/data/accountability.db` as of extraction, with stored fields, a replay snapshot (`replay_today`) and an AI-assigned label per run. `_meta` records the purpose, source database (gitignored), extractor ("NOT reviewed by a human yet"), the labelling caveat, the replay method and the headline finding. Added in RUN_LOG "2026-09-07 -- Real-run regression corpus + structural diagnosis". Later edits, all recorded: run `515f263a`'s `replay_today` corrected after the comma-grouping regex fix, stored fields untouched (RUN_LOG "2026-09-11 (continued)"); every entry tagged `lens_version: "v1"` with a `_meta.lens_version_note` (RUN_LOG "2026-09-25 (continued) -- B2 + B3", which says the file was re-saved with only those keys added and whitespace may differ). | Extracted 2026-09-07 (`_meta.extracted_on`) | [[tests/test_real_run_corpus.py]], [[tests/test_concept_linkage.py]], [[tests/test_facts.py]] |
| `tests/fixtures/edgar_aapl_companyfacts_sample.json` | SEC EDGAR companyfacts payload for AAPL (`https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json`). Its `_fixture_note` says it keeps the us-gaap concepts the producer lenses read, every entry field, and entries ending on or after 2025-01-01, except `Revenues`, kept whole because AAPL stopped using that tag after FY2018; values unmodified. Added in RUN_LOG "2026-09-24 (continued) -- B0". | Fetched 2026-09-24 (`_fixture_note`) | [[tests/test_edgar_facts.py]], [[tests/test_constraints.py]], [[tests/test_assessment.py]], [[tests/test_synthesis.py]] |

### Limits and open issues
- The corpus's labels are judgments, not ground truth, and no human review of them is recorded.
- The corpus's `_meta.replay_methodology` says `concepts_expected_to_overlap=False` is the `/api/compare` default. That was true when it was extracted and is no longer (see [[tests/test_real_run_corpus.py]]).
- Two test modules read fixtures from the frontend's folder instead: [[tests/test_audit.py]] uses `run_compare_b5_auditor.json` and [[tests/test_trace_withholding.py]] uses `run_compare_gated_auditor.json`, both under `web/frontend/tests/fixtures/`. A change to those files affects the Python suite too.

Related: [[datasources/edgar.py]], [[datasources/filings.py]], [[validation/cross_validation.py]]
