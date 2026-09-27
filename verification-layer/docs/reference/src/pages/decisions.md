---
title: Design decisions
slug: decisions
section: Architecture
order: 40
summary: Every significant design decision in the verification layer, with its status, date, implementing files, reasons and costs, each traced to the run log, the system design document or the code.
---

This page records the design decisions behind the verification layer, one record per decision. Each
record says whether the decision is still in force, when it was made, which files implement it, what
prompted it, what it costs, and where the record is. Most decisions were made in the conversations
behind `logs/RUN_LOG.md` and are cited by entry date and title. Some were inherited from the original
prototype and are only explained in `docs/SYSTEM_DESIGN.md` or in code comments; for those the
decision date is "not recorded". A reason that appears in neither the record nor the code is labelled
(judgment, not recorded).

Three terms recur. A **gate** is a hard stop that only a named human can clear (SNICKERDOODLE.md P4).
**Investor** and **auditor** are the two read scopes: an auditor sees the agents' reasoning, an investor
sees conclusions only (SEC-01). The **Honest Ledger** is the subsystem's own list of known issues, kept
in `web/self_report.py` as `KNOWN_ISSUES`; ledger ids appear in backticks, for example
[`audit-criticals`](ledger.html#audit-criticals).

A status of "Superseded" means a later record replaced the decision; the older record is kept, as the
log is. Where the code and a prose document disagree about a decision, the code is described and the
disagreement is noted in the record.

## Index

| Id | Decision | Status |
|---|---|---|
| **Foundations** | | |
| D-01 | The core engine is stdlib-only; other dependencies are named exceptions | In force |
| D-02 | Inward-pointing layers, enforced by an AST test | In force |
| D-03 | Contracts are Protocols, not base classes | In force |
| D-04 | The subsystem is self-contained in one folder | In force |
| D-05 | Never delete: archive files, and correct the log by appending | In force |
| **The structural contract** | | |
| D-06 | Validity is structural: exactly two XML blocks | In force |
| D-07 | One corrective retry, then halt (ADR-07) | In force |
| D-08 | Directives are code, versioned, and never edited in place | In force |
| D-09 | A conclusion that copies the directive is a structural failure | In force |
| D-10 | Directive v1.6.0 (the assessment block) made active | Reverted 2026-09-26 |
| D-11 | Assessments come from a separate extraction call ("option 1") | In force |
| D-12 | Schema types enforce their own invariants | In force |
| D-13 | Each attempt records the directive and inputs it was given | In force |
| **Agents and tools** | | |
| D-14 | Several selectable provider adapters | Superseded by D-15 |
| D-15 | LangChain is the only agent framework | In force |
| D-16 | The agent gets a search tool that supplements, never replaces, post-hoc verification | In force |
| D-17 | No scripted answers in the running application | In force |
| D-18 | The automated suite is network-free and model-free | In force |
| D-19 | Model calls have a stall timeout, `MODEL_TIMEOUT_S` | In force (uncommitted) |
| D-20 | The two agents run sequentially | Superseded by D-21 |
| D-21 | The two agents run concurrently, off the event loop, with a live stream | In force |
| **Data** | | |
| D-22 | Network egress is confined to named modules | In force |
| D-23 | One EDGAR fetch, read through two lenses | In force |
| D-24 | Facts carry their period and unit | In force |
| D-25 | Figures are located in the filing itself, and the lookup never fails loudly | In force |
| **Producers and comparison** | | |
| D-26 | A producer is a `ConceptLens` value | In force |
| D-27 | Producer A and B read disjoint concept sets | Superseded by D-28 |
| D-28 | Lens v2: overlapping metrics now, bull/bear later | In force |
| D-29 | Two pairings: lenses and bull/bear | In force |
| D-30 | Comparison is numeric only and does not decide who is right | In force |
| D-31 | "Could not check" is never recorded as "checked, found nothing" | In force |
| D-32 | One shared definition of "a number" | In force |
| D-33 | `concepts_expected_to_overlap=False` for the asymmetric pair | Superseded by D-34 |
| D-34 | `contradiction_rule` is opt-in; `concept_aware` decides ticker-mode lens runs | In force |
| D-35 | `canonical_facts` stays opt-in for ticker-mode lens runs | In force |
| D-36 | Claims are extracted from both blocks, per producer | In force |
| D-37 | Accounting checks split hard rules from heuristics | In force |
| **The human gate** | | |
| D-38 | Only a two-sided conflict opens the gate; the policy is versioned | In force |
| D-39 | Decisions are refused, never repaired, and never made by an AI | In force |
| D-40 | Investors see disputed values only after a decision | In force |
| D-41 | Divergence is classified and counted, never scored; consensus is narrow | In force |
| **Storage, scope and self-report** | | |
| D-42 | Append-only is enforced by SQLite triggers | In force |
| D-43 | New fields go inside the payload blob, not new columns | In force |
| D-44 | Scope redaction omits keys rather than nulling them | In force |
| D-45 | The consistency probe is metadata and is never persisted | In force |
| D-46 | The Honest Ledger lives in code and is served unauthenticated | In force |
| **User interface** | | |
| D-47 | `brutalist/` does not govern the web app | In force |
| D-48 | React replaces the classic UI by strangler migration | In force |
| D-49 | "Clear all runs" is not ported to the new UI | In force |

## D-01 · The core engine is stdlib-only; other dependencies are named exceptions
- **Status:** In force
- **Decided:** not recorded (the stdlib-only core predates the 2026-08-14 integration); the exception rule is in `CLAUDE.md`
- **Where:** [[requirements.txt]], [[adapters/langchain_adapter.py]], [[pipeline/observability.py]], [[validation/verification.py]], [[web/frontend/README.md]]

**Context.** The test suite had to run on a bare interpreter, and dependency risk had to stay in the
parts already flagged as not production-ready.

**Decision.** `core/` (parser, schemas, directive, contracts, numeric extraction) and the validation
loop use the standard library only. Any other dependency is added only as a deliberate exception,
documented in the importing file's docstring. `validation/verification.py` fetches with stdlib
`urllib` for the same reason, and `datasources/filings.py` parses filings with stdlib `html.parser`.
Every npm package in the React app is listed as an exception, with its reason, in
`web/frontend/README.md`.

**Consequences.** The suite runs with no install step. The web app and the live model path need
`requirements.txt`: FastAPI, PyJWT, python-dotenv, LangFuse, and the LangChain packages
(`langchain-core`, `langchain-ollama`, `langchain-google-genai`, `langchain-tavily`). The rule is
enforced by review, not by a test.

**Source.** `docs/SYSTEM_DESIGN.md` §4 ("Core engine is stdlib-only"); `logs/RUN_LOG.md` 2026-09-22
"Remove mock_adapter.py, add adapters/langchain_adapter.py"; 2026-09-24 "U1: React + Vite foundation".

## D-02 · Inward-pointing layers, enforced by an AST test
- **Status:** In force
- **Decided:** 2026-09-04
- **Where:** [[tests/test_layering.py]], [[core/numeric.py]], [[adapters/registry.py]], [[producers/lens.py]], [[datasources/edgar.py]]

**Context.** Sixteen modules sat flat at the root and imported each other by bare name, so the
dependency direction could not be stated, and `parser.py` shadowed a stdlib module name.

**Decision.** Every module moved into a layer: `core/` imports nothing internal; `adapters/`,
`pipeline/` and `datasources/` import only `core`; `producers/` adds `pipeline` and `datasources`;
`validation/` may reach `web.db` only through a function-local import; `web/` may use everything. No
loose `.py` file may sit at the root. The same change removed three duplications: the quantitative
regex (three copies, now `core/numeric.py`), the `_latest_value` helper (two copies, now
`datasources/edgar.py`), and adapter construction (now `adapters/registry.py`).
`tests/test_layering.py` reads the AST, so a violation names the file and the import.

**Consequences.** The test was checked by introducing three violations and seeing each fail. The
upward `validation/` to `web.db` dependency remains; the record names a persistence port in
`core/contracts.py` as the honest fix, not done. `web/server.py` was deliberately not split, because
it had no route tests at the time.

**Source.** `logs/RUN_LOG.md` 2026-09-04 "SOLID restructure: layered packages, no loose root modules,
three duplications removed"; `README.md` "Layout".

## D-03 · Contracts are Protocols, not base classes
- **Status:** In force
- **Decided:** 2026-09-04 (`ModelCall` added 2026-09-26)
- **Where:** [[core/contracts.py]], [[pipeline/middleware.py]], [[adapters/fixture_adapter.py]]

**Context.** The adapter and fetcher contracts existed only as prose in a comment.

**Decision.** `core/contracts.py` declares `AgentAdapter` (`(subject, context, directive) ->
AgentResponse`), `JsonFetcher` (`url -> dict`) and, since option 1, `ModelCall` as `typing.Protocol`s.
`run_validation_loop` depends on the shape, and a new provider satisfies it by its call signature,
with no inheritance.

**Consequences.** Test doubles are plain callables of the right shape (see D-18). Fetchers are
injectable, which is why the suite needs no patching of module globals.

**Source.** `docs/SYSTEM_DESIGN.md` §4 ("`AgentAdapter` is a `Protocol`"); `logs/RUN_LOG.md`
2026-09-04 "SOLID restructure"; 2026-09-26 "Option 1 (assessment extraction) + B5 + U8".

## D-04 · The subsystem is self-contained in one folder
- **Status:** In force
- **Decided:** 2026-08-14; folder renamed 2026-08-21
- **Where:** [[README.md]], [[CLAUDE.md]], [[logs/RUN_LOG.md]], [[docs/DATA_CONTRACT.md]], [[.gitignore]]

**Context.** The standalone prototype was brought into Mycroft, whose shared run log and root files
are touched by several other authors.

**Decision.** Nothing outside `verification-layer/` is modified. The subsystem keeps its own
`.gitignore`, data contract and run log. On 2026-08-21 the folder was renamed from
`accountability-layer/` with `git mv`, rather than adding a sibling folder, because every module then
used flat same-directory imports that only resolved when co-located.

**Consequences.** The merge surface against other branches is zero. The cost, stated in `README.md`:
CI does not conformance-check this code, because it is not in `scripts/conformance.mjs`'s default
paths, and running that script over the whole folder walks into a local `env/` virtualenv. One
recorded deviation: `.claude/launch.json` was created at the repo root on 2026-09-04 for the browser
tooling.

**Source.** `logs/RUN_LOG.md` 2026-08-14 "Integrate accountability-layer into Mycroft
(self-contained)"; 2026-08-21 "Rename accountability-layer/ to verification-layer/"; 2026-09-04
"Frontend for Cross-Agent Validation".

## D-05 · Never delete: archive files, and correct the log by appending
- **Status:** In force
- **Decided:** repository rule (`AGENTS.md`); first applied in this subsystem 2026-08-21 (log) and 2026-09-22 (files)
- **Where:** [[archive/adapters/mock_adapter.py]], [[archive/adapters/gemini_adapter.py]], [[archive/adapters/ollama_adapter.py]], [[archive/web-static-legacy/README.md]], [[logs/RUN_LOG.md]]

**Context.** Hand-made source, logs and records are evidence (P3, P7), and a deletion loses the
history a later reader needs.

**Decision.** Superseded source moves to `archive/` with `git mv`: `mock_adapter.py` (2026-09-22,
after a plain `rm` was tried and reverted), `gemini_adapter.py` and `ollama_adapter.py` (2026-09-23),
the classic UI (2026-09-27, with a README that says how to restore it). Earlier log entries are never
edited; a mistake gets a new correction entry. The same rule governs data: stored `stored_*` fields in
the real-run corpus stay as captured, and historical run records are not backfilled with fields added
later.

**Consequences.** Several corrections exist only as later entries (the v1.5.0 echo claim, the gated
run's "neither year" claim, the "five hangs" count, the chat run reported as retrying). A reader must
read forward to find them. Mock-provider smoke runs from 2026-09-04 remain in the store, because the
append-only table cannot remove only those rows.

**Source.** `logs/RUN_LOG.md` 2026-08-21 "Rename" ("Deliberately left unchanged"); 2026-09-22
"Remove mock_adapter.py"; 2026-09-24 "B0" (correction to the v1.5.0 entry); 2026-09-26 "Correction:
two claims in earlier entries were wrong"; 2026-09-27 "A model-call timeout, and a ledger refresh".

## D-06 · Validity is structural: exactly two XML blocks
- **Status:** In force
- **Decided:** not recorded (inherited from the prototype)
- **Where:** [[core/parsing.py]], [[core/directive.py]]

**Context.** A model's own account of its reasoning is not evidence; the system needs a contract it
can check mechanically.

**Decision.** A reply must be exactly a `<thought_log>` block and a `<conclusion>` block with nothing
outside them. `_parse_response` raises `StructuralParseError` otherwise. The check is regex-based and
says nothing about whether the content is correct. When a model breaks the contract, the directive is
changed, not the parser: v1.1.0 added "begin with `<`" for Gemini's pre-tag reasoning, and v1.5.2
spelled out the closing tags after `[/conclusion]` closed 3 of 22 v1.5.1 first attempts. Accepting
`[/conclusion]` was left as the human's call because it would change ADR-07's contract.

**Consequences.** Semantic checks are layered on top (D-36, D-37), never merged into validity. The
optional `<assessment>` third block is accepted only under `allow_assessment`, which no active
directive sets (D-10). In tool-calling runs, the adapter's `_parse_across_turns()` joins the model's
own turns when the opening tag was written in the turn that called the tool.

**Source.** `docs/SYSTEM_DESIGN.md` §2.2 and §2.4; `logs/RUN_LOG.md` 2026-09-24 "B1 + U2" (v1.5.2 and
tool-loop responses).

## D-07 · One corrective retry, then halt (ADR-07)
- **Status:** In force
- **Decided:** not recorded (inherited from the prototype)
- **Where:** [[pipeline/middleware.py]], [[core/schemas.py]], [[tests/support.py]]

**Context.** A pipeline that degrades or guesses on malformed output passes along an answer it cannot
verify (P4).

**Decision.** Attempt 1 uses the active directive. If it fails the structural check it is recorded as
`PARSE_FAILURE`, and attempt 2 uses the fixed `CORRECTIVE_DIRECTIVE_TEXT`. A second failure is
recorded as `HALT` and raises `HaltError` carrying every attempt; no conclusion is delivered.
`ReasoningObject.__post_init__` refuses an attempt 2 recorded as `PARSE_FAILURE`, so a third outcome
cannot be constructed.

**Consequences.** Failed attempts are stored as evidence. Known limit, found 2026-09-24 and left
unchanged because it alters the contract: the corrective directive replaces the whole directive, so
attempt 2 runs without the grounding and citation rules, and llama3.2 often wrote its tool call as
JSON text on attempt 2. The retry path was first observed on real models in the 2026-09-27 count
(48 agent-runs, 13 retries, 4 recovered, 9 halted), which moved `retry-halt-unproven` to RESOLVED; the
9 halts have not been reviewed individually.

**Source.** `docs/SYSTEM_DESIGN.md` §2.3; `logs/RUN_LOG.md` 2026-09-24 "Directive echo, properly"
(open issues); 2026-09-24 "B1 + U2" (open issues); 2026-09-27 "A model-call timeout, and a ledger
refresh".

## D-08 · Directives are code, versioned, and never edited in place
- **Status:** In force
- **Decided:** not recorded (ADR-01b, ADR-05, SEC-04 in the prototype)
- **Where:** [[core/directive.py]], [[core/schemas.py]], [[tests/test_phase1_schemas.py]]

**Context.** A system prompt that a request parameter could change would open a prompt-injection path,
and a run could not be audited against the text that produced it.

**Decision.** Directives are hardcoded in `core/directive.py` and registered by version (`v1.0.0` to
`v1.6.0` today). A change is a new version, never an edit; old versions stay retrievable through
`get_directive(version)`. Each `RunSession` stores `directive_text` verbatim. A new directive is
proposed to the human for approval before it is made active (2026-09-22, v1.2.0).

**Consequences.** The version history is itself a record of observed failure modes: grounding (v1.2.0),
citation format (v1.3.0), domain-neutral wording (v1.4.0), echo (v1.5.0 and v1.5.1), bracketed
closing tags (v1.5.2). Each promotion updates the version pins in `tests/test_phase1_schemas.py`.
Every directive change is model-dependent, not a mechanical guarantee; the record repeatedly says so.
`docs/SYSTEM_DESIGN.md` §2.3 and §2.4 still name v1.1.0 as active; the code's `ACTIVE_DIRECTIVE` is
v1.5.2.

**Source.** `docs/SYSTEM_DESIGN.md` §2.4 and §4; `logs/RUN_LOG.md` 2026-09-22 "Add DIRECTIVE_V1_2_0";
2026-09-22 "Make citation verification actually fire"; 2026-09-23 "Generalize the accountability
layer".

## D-09 · A conclusion that copies the directive is a structural failure
- **Status:** In force (replaced v1.5.0's marker approach)
- **Decided:** 2026-09-24
- **Where:** [[core/parsing.py]], [[pipeline/middleware.py]], [[web/step_trace.py]], [[tests/test_directive_echo.py]]

**Context.** Models copied the directive's block descriptions into `<conclusion>`. v1.5.0 added an
"(Instruction — do not copy this into your response)" marker, reported fixed on one live chat run; a
later count found 7 of 10 stored v1.5.0 compare conclusions echoed, marker included.

**Decision.** The human chose "restructure + detect". v1.5.1 moves block descriptions out of the tags
and leaves the template's tags empty. `find_directive_echo()` rejects a conclusion that copies any 8
consecutive words of the directive, and an empty conclusion is rejected too. The middleware treats a
rejection as a `StructuralParseError`, so ADR-07's retry and halt apply. The window size was chosen by
replaying 135 stored conclusions: windows of 6 to 12 words flagged the same 17. Three sentences in
which the directive tells the model what to say when Context is thin are exempt.

**Consequences.** Live, 0 of 8 v1.5.1 conclusions echoed; the live rejection path has not fired. A
legitimate conclusion quoting 8 or more words of the directive would be rejected; the replay found no
such case.

**Source.** `logs/RUN_LOG.md` 2026-09-24 "Stop the model echoing the directive's own instructions";
2026-09-24 "B0" (correction); 2026-09-24 "Directive echo, properly: v1.5.1".

## D-10 · Directive v1.6.0 (the assessment block) made active
- **Status:** Reverted 2026-09-26; superseded by D-11
- **Decided:** 2026-09-26
- **Where:** [[core/directive.py]], [[core/assessment.py]], [[core/parsing.py]]

**Context.** Roadmap B4 needed each agent's grade, direction and assumptions in a structured form.

**Decision.** v1.6.0 added a third `<assessment>` JSON block after `</conclusion>`, with a closed
vocabulary and one narrow exception to the grounding rule. Live, 2 of 10 first attempts passed the
format check under it, against 7 of 8 under v1.5.2 the day before; in 7 of 8 failures the model left
`</thought_log>` unclosed. `ACTIVE_DIRECTIVE` was set back to v1.5.2 the same day.

**Consequences.** v1.6.0 stays registered, and the parser, schema fields and UI support stay in place,
idle. The comment above `ACTIVE_DIRECTIVE` in `core/directive.py` records the reversion and its
numbers. How to obtain assessments was left to the human (D-11).

**Source.** `logs/RUN_LOG.md` 2026-09-26 "B4 + U7: structured assessments and bull/bear, built and
reverted as the default"; `core/directive.py` (comment on `ACTIVE_DIRECTIVE`).

## D-11 · Assessments come from a separate extraction call ("option 1")
- **Status:** In force
- **Decided:** 2026-09-26
- **Where:** [[core/assessment.py]], [[core/contracts.py]], [[adapters/langchain_adapter.py]], [[pipeline/middleware.py]]

**Context.** After D-10's reversion, the options were a separate extraction call, a reworded directive,
or a larger model. The human chose the first.

**Decision.** After an answer passes the unchanged two-block check, one more call to the same model
(`make_langchain_model_call`, no tools, no directive) reads the finished answer and returns only the
assessment JSON. The validator never coerces a value; `{"abstain": true}` is kept as abstained;
`ground_in` drops key points quoting figures absent from the answer or inputs; a failed call is
recorded as `extraction_failed` and never fails the run. The prompt is versioned
(`EXTRACTION_PROMPT_VERSION`, now `assess-extract-v2`), and v2 added a check that a growth assumption
looks forward.

**Consequences.** It runs for ticker compares only; chat runs get no extraction. It is the same model
judging its own answer. In the recorded live batch, 5 of 5 successful answers got a usable, `partial`
assessment. `assessment-not-produced` is RESOLVED; [`synthesis-thin-and-lexical`](ledger.html#synthesis-thin-and-lexical) is OPEN.

**Source.** `logs/RUN_LOG.md` 2026-09-26 "Option 1 (assessment extraction) + B5 + U8".

## D-12 · Schema types enforce their own invariants
- **Status:** In force
- **Decided:** not recorded (ADR-03, ADR-04, ADR-08 in the prototype)
- **Where:** [[core/schemas.py]]

**Context.** A rule applied at call sites can be forgotten at one of them.

**Decision.** Every schema is a frozen dataclass, mirroring the append-only store at the type level.
`confidence_score` must lie in `[0.0, 1.0]` and is computed, not self-reported (ADR-04). A
`RunSession` below 0.4 must be classified `HIGH_UNCERTAINTY_SPECULATIVE` and at or above must be
`STANDARD`; the wrong pairing raises `ValidationError`.

**Consequences.** Two layers enforce the same guarantee (type and database, D-42). A model's
self-reported "confidence level" in its text is not the score; the figure check excludes it from
comparison (D-35).

**Source.** `docs/SYSTEM_DESIGN.md` §2.5 and §4 ("Every schema is a frozen dataclass").

## D-13 · Each attempt records the directive and inputs it was given
- **Status:** In force
- **Decided:** 2026-09-22
- **Where:** [[core/schemas.py]], [[pipeline/middleware.py]]

**Context.** `RunSession.directive_text` named only the active directive, so the corrective directive
used on a retry was never recorded, and the subject and context sent to the model were discarded.

**Decision.** `ReasoningObject` gained `directive_version`, `directive_text` and `context_window`,
filled per attempt from what the middleware actually knows: the directive used for that attempt and
the `{subject, context}` handed to the adapter. The choice not to reconstruct each adapter's wire bytes
is stated in the field docstrings.

**Consequences.** A retry's different prompt is visible. `context_window` is not a wire capture (an
adapter may truncate or reformat). Both text fields are auditor-tier only.

**Source.** `logs/RUN_LOG.md` 2026-09-22 "Feature: expose per-attempt context window".

## D-14 · Several selectable provider adapters
- **Status:** Superseded by D-15 (2026-09-23)
- **Decided:** not recorded (prototype); registry consolidated 2026-09-04
- **Where:** [[adapters/registry.py]], [[archive/adapters/gemini_adapter.py]], [[archive/adapters/ollama_adapter.py]], [[archive/adapters/mock_adapter.py]]

**Context.** The prototype shipped Gemini, Ollama and mock adapters, chosen by config and by UI.

**Decision.** On 2026-09-04 the provider set moved into one registry, so request models validated
against `provider_names()` rather than a frozen `Literal`, and adding a provider was one entry. On
2026-09-22 the `mock` entry was replaced by `langchain`.

**Consequences.** This is the arrangement `docs/SYSTEM_DESIGN.md` §2.1 and `README.md`'s adapters table
still describe; both are out of date against the code, where the registry has one entry.

**Source.** `logs/RUN_LOG.md` 2026-09-04 "SOLID restructure"; 2026-09-22 "Remove mock_adapter.py".

## D-15 · LangChain is the only agent framework
- **Status:** In force
- **Decided:** 2026-09-23
- **Where:** [[adapters/langchain_adapter.py]], [[adapters/registry.py]], [[web/server.py]], [[.env.example]]

**Context.** The human redirected mid-review: rather than three selectable adapters, one framework,
with the underlying model configured outside the app.

**Decision.** Every agent call goes through LangChain. `_build_chat()` infers the family from the model
name: a name containing "gemini" selects `ChatGoogleGenerativeAI`, anything else `ChatOllama`. The
default model comes from `LANGCHAIN_MODEL`. The UI lost its provider and model selectors; seed and
temperature stayed, as ADR-04 reproducibility evidence rather than model choice. Compare requests keep
per-agent model names.

**Consequences.** One error type, `LangchainConnectionError`, replaced the granular Gemini and Ollama
errors, a named simplification. The Gemini path is wired but has never been observed succeeding
([`gemini-key-unconfirmed`](ledger.html#gemini-key-unconfirmed)).
[`http-no-model-override`](ledger.html#http-no-model-override) is still OPEN.

**Source.** `logs/RUN_LOG.md` 2026-09-23 "Make LangChain the sole agent framework; replace the MCP
fetch tool with Tavily search".

## D-16 · The agent gets a search tool that supplements, never replaces, post-hoc verification
- **Status:** In force (the tool itself changed from MCP fetch to Tavily on 2026-09-23)
- **Decided:** 2026-09-22; tool replaced 2026-09-23
- **Where:** [[adapters/langchain_adapter.py]], [[validation/verification.py]], [[web/server.py]]

**Context.** No agent had any tool; only the verifier fetched URLs, after the answer. The human asked
for agent-side fetching and chose to supplement, not replace, the independent check, since a model's
self-report is not trusted.

**Decision.** On 2026-09-22 the agent got the reference MCP fetch server (robots.txt respected, a fresh
subprocess per call). On 2026-09-23 Tavily search replaced it. Without `TAVILY_API_KEY` the call runs
with no tools and the route surfaces a capability warning, because `TavilySearch()` raises at
construction. When tools are active, the adapter's prompt tells the model to search when Context lacks
the answer and treats a search result as a valid source. Placeholder arguments are dropped
(`_sanitize_tool_args`), and a failed or error-returning call gets one query-only retry
(`_call_tool`). Every tool call is traced as a step with its query, URLs and, since BP, per-result
snippets.

**Consequences.** The agent now reaches the network, which is a named relaxation of P2 (D-22).
Citation fidelity is not guaranteed: a model has cited a URL that did not match its search result. The
verifier still never checks that a cited URL matches the one in the user's context. The
`requirements.txt` comment says the tool "still binds without" a key; the code
(`tools_active`) runs without tools instead.

**Source.** `logs/RUN_LOG.md` 2026-09-22 "Give the agent a real MCP fetch tool"; 2026-09-22 "Log every
MCP tool call"; 2026-09-23 "Make LangChain the sole agent framework"; 2026-09-23 "Configure
TAVILY_API_KEY"; 2026-09-23 "Make the agent search first"; 2026-09-24 "B0" (tool errors).

## D-17 · No scripted answers in the running application
- **Status:** In force
- **Decided:** 2026-09-22
- **Where:** [[adapters/langchain_adapter.py]], [[tests/support.py]], [[adapters/fixture_adapter.py]], [[web/server.py]]

**Context.** The human asked that the app fail or raise rather than give a scripted answer.

**Decision.** The scripted mode, the "Failure Simulation" control and the fabricated mock data
sources were removed; `/api/chat` reports `data_sources: []`. The scripted double survives only as
`tests/support.py`'s `make_scripted_adapter`, never registered and unreachable from the app;
`fixture_adapter.py` is documented as test-only.

**Consequences.** A real-call failure surfaces as `halted: true` with the real error. The test count
dropped from 244 to 241 because tests of the removed feature were removed. `fixture_adapter.py` still
lives in `adapters/`, not `tests/`; the record leaves the move as a follow-up.

**Source.** `logs/RUN_LOG.md` 2026-09-22 "Remove all mock/scripted features from the running app".

## D-18 · The automated suite is network-free and model-free
- **Status:** In force
- **Decided:** stated in `CLAUDE.md`; reaffirmed 2026-09-22
- **Where:** [[tests/support.py]], [[datasources/edgar.py]], [[tests/fixtures/cross_agent_real_runs_corpus.json]], [[tests/fixtures/edgar_aapl_companyfacts_sample.json]]

**Context.** In the 2026-09-22 mock removal the human first chose to remove every test double. Real
models almost never fail the format, so ADR-07's retry and halt path would have become untestable.

**Decision.** Test doubles stay as dependency injection against the `AgentAdapter` contract (a fake
callable, `MagicMock`), testing the subsystem's own control flow rather than simulating an answer.
EDGAR calls take an injected fetcher; real payloads are captured as fixtures with provenance notes.
A test that needs a live call or a new dependency is treated as wrong, not the environment.

**Consequences.** Behaviour on real data is covered by replaying captured records, such as the
real-run corpus. The timeout tests (D-19) run against a stub server on 127.0.0.1, not a model. A
suite-wide guard placed in `tests/__init__.py` on 2026-09-26 broke live calls, because
`web/self_report.py` imports the test package to count tests; it was replaced by a per-test
`no_model_extraction()` and a regression test.

**Source.** `CLAUDE.md` ("Test before claiming done"); `docs/SYSTEM_DESIGN.md` §6; `logs/RUN_LOG.md`
2026-09-22 "Remove all mock/scripted features"; 2026-09-26 "Option 1" ("Found and fixed").

## D-19 · Model calls have a stall timeout, `MODEL_TIMEOUT_S`
- **Status:** In force in the working tree; not yet committed
- **Decided:** 2026-09-27
- **Where:** [[adapters/langchain_adapter.py]], [[.env.example]]

**Context.** Ollama stopped responding during compares four times, and with no timeout a wedged model
blocked a compare's worker indefinitely.

**Decision.** `MODEL_TIMEOUT_S` (default 120) is how long a call may receive nothing before it is
abandoned. It reaches ChatOllama's httpx client and Gemini's `timeout`. Because ChatOllama streams, it
is a stall limit, not a cap on length. The default was chosen above the slowest successful attempt in
the store (85.3 s over 56 attempts). A timeout raises `LangchainTimeoutError`, a subclass of
`LangchainConnectionError`, so routes record a halt and extraction records `extraction_failed` without
server changes. Tests are in `tests/test_model_timeout.py`, not yet tracked.

**Consequences.** It bounds a hang but does not fix it;
[`ollama-hangs-under-compare`](ledger.html#ollama-hangs-under-compare) stays OPEN. Each call builds a
new ChatOllama client.

**Source.** `logs/RUN_LOG.md` 2026-09-27 "A model-call timeout, and a ledger refresh that found two
wrong claims".

## D-20 · The two agents run sequentially
- **Status:** Superseded by D-21 (2026-09-24)
- **Decided:** not recorded
- **Where:** [[validation/cross_validation.py]]

**Context.** The v1 comparator ran agent A to completion, then agent B, and B always ran even if A
halted.

**Decision.** Sequential execution; the 2026-09-04 UI drew it as such so symmetric columns would not
imply concurrency.

**Consequences.** "Agent B always runs, even if agent A halted" carried over to D-21.
`docs/SYSTEM_DESIGN.md` §3.3 and §3.6 still describe sequential calls.

**Source.** `docs/SYSTEM_DESIGN.md` §3.3; `logs/RUN_LOG.md` 2026-09-04 "Compare UI v2".

## D-21 · The two agents run concurrently, off the event loop, with a live stream
- **Status:** In force
- **Decided:** 2026-09-24 (human decision 4)
- **Where:** [[validation/cross_validation.py]], [[web/server.py]], [[web/step_trace.py]], [[tests/test_concurrency_and_stream.py]]

**Context.** The human decided the agents run concurrently. While planning, `async def` routes were
found running the blocking model loop on the event loop, stalling every other request.

**Decision.** The run routes are plain `def`, so FastAPI uses its threadpool. Both agents run on a
two-thread pool, each in its own `contextvars` copy. `CROSS_AGENT_MAX_CONCURRENCY=1` restores A-then-B.
`reasoning_objects` stay in A-then-B order whichever finishes first. `/api/chat/stream` and
`/api/compare/stream` send server-sent events; a disconnect ends the stream, not the run.

**Consequences.** Observed: reads stayed responsive during runs, and agent spans overlapped. The
record's "summed" sequential times are estimates. There is no automatic fallback when Ollama runs out
of memory; the hang hypothesis (two concurrent tool-calling requests) is untested.

**Source.** `logs/RUN_LOG.md` 2026-09-24 "Human decisions: audit-layer roadmap approved"; 2026-09-24
"BL: unblock the event loop, run agents concurrently, stream live events".

## D-22 · Network egress is confined to named modules
- **Status:** In force
- **Decided:** P2 (SNICKERDOODLE.md); enforced by test since 2026-09-04
- **Where:** [[tests/test_layering.py]], [[datasources/edgar.py]], [[datasources/filings.py]], [[validation/verification.py]]

**Context.** P2 says only ingest code touches the network.

**Decision.** `tests/test_layering.py` fails if `urllib.request` or `requests` appears outside
`datasources/` and `adapters/`, except `validation/verification.py`, which fetches the document it
verifies against and is named in the test rather than excused.

**Consequences.** The rule is narrower than P2's wording: model adapters and the agent's search tool
(D-16) reach the network, and the test checks import text, not all egress. SEC requests use
`SEC_USER_AGENT`.

**Source.** `tests/test_layering.py` (`test_datasources_is_the_only_package_that_opens_a_socket`);
`logs/RUN_LOG.md` 2026-09-04 "SOLID restructure"; 2026-09-22 "Give the agent a real MCP fetch tool".

## D-23 · One EDGAR fetch, read through two lenses
- **Status:** In force
- **Decided:** not recorded (found and made visible 2026-09-04)
- **Where:** [[web/server.py]], [[producers/lens.py]], [[web/step_trace.py]]

**Context.** A draft UI would have drawn a fetch under each agent.

**Decision.** `/api/compare` calls `lookup_cik` and `fetch_company_facts` once and hands the same
payload to both lenses. The step trace records the fetch once, in a shared phase.

**Consequences.** Both agents see figures from the same filing data, so a disagreement cannot come
from two different fetches. Filing-level accounting checks reuse that payload with no new request
(D-37).

**Source.** `logs/RUN_LOG.md` 2026-09-04 "Compare UI v2"; `docs/SYSTEM_DESIGN.md` §3.6.

## D-24 · Facts carry their period and unit
- **Status:** In force
- **Decided:** 2026-09-24
- **Where:** [[datasources/edgar.py]], [[producers/lens.py]], [[tests/test_edgar_facts.py]]

**Context.** `latest_value()` took `max(end)` and returned a bare float. On a live AAPL payload that
handed agents FY2018 revenue under a retired tag, and year-to-date values where the quarter was meant.

**Decision.** A frozen `Fact` carries unit, period, form, frame and accession. `select_fact()`
classifies the period by its actual duration and in `auto` prefers an instant, then a quarter, then an
annual figure, with year-to-date a labelled last resort; ties go to the latest end, then the latest
filing. `CONCEPT_TAGS` reads every candidate tag for a concept. Context lines keep the value first, so
older parsers still read it.

**Consequences.** Every run before this carries the old picks, including the corpus; the corpus is not
relabelled because it is about comparator behaviour. Non-calendar filers and 20-F/40-F filers are not
exercised.

**Source.** `logs/RUN_LOG.md` 2026-09-24 "B0: period- and unit-aware facts; a retired revenue tag".

## D-25 · Figures are located in the filing itself, and the lookup never fails loudly
- **Status:** In force
- **Decided:** 2026-09-25
- **Where:** [[datasources/filings.py]], [[tests/test_filings.py]], [[web/server.py]]

**Context.** A reviewer needs to see where a figure comes from in the filing, not only the structured
companyfacts value.

**Decision.** A Fact is found in the filing's primary document by its inline XBRL tag and a context
with the same period and no dimension, so segment figures are not mistaken for the consolidated one.
Parsing uses stdlib `html.parser`. Requests are rate-limited, size-capped and cached under
`web/data/filing_cache/` (gitignored). An odd filing returns a status and the index URL, never a 500.
Route parameters are checked against exact formats before they reach a URL or a file name.

**Consequences.** Live, 24 of 24 figures were found and each filed value equalled its companyfacts
value; layout heuristics were checked on four filers
([`filing-excerpt-coverage`](ledger.html#filing-excerpt-coverage)).

**Source.** `logs/RUN_LOG.md` 2026-09-25 "BP + U4: figures located in the filing".

## D-26 · A producer is a `ConceptLens` value
- **Status:** In force
- **Decided:** 2026-09-04
- **Where:** [[producers/lens.py]], [[producers/financial.py]], [[producers/earnings.py]], [[tests/test_producer_lens.py]]

**Context.** The two graders were near-identical modules, and a third producer meant copying a third.

**Decision.** A producer is a `ConceptLens` (concepts, `AgentID`, header, trace name, and since B2 a
`version`) run by one `run_lens`. The `Concept: value` context format is a contract that the UI parses
back, pinned by tests.

**Consequences.** ADR-07 behaviour cannot drift between producers, because there is one call site. A
lens cannot change how the model is called (stated in `producers/lens.py`).

**Source.** `logs/RUN_LOG.md` 2026-09-04 "SOLID restructure"; `docs/SYSTEM_DESIGN.md` §3.2 and §4.

## D-27 · Producer A and B read disjoint concept sets
- **Status:** Superseded by D-28 (2026-09-25)
- **Decided:** 2026-08-28
- **Where:** [[producers/financial.py]], [[producers/earnings.py]], [[tests/fixtures/cross_agent_real_runs_corpus.json]]

**Context.** Producer B had been a fixture. Information asymmetry, rather than a different model, was
taken as what makes a disagreement meaningful.

**Decision.** Producer A read `Assets`, `Revenues`, `NetIncomeLoss`; Producer B read
`EarningsPerShareDiluted`, `EarningsPerShareBasic`, `OperatingIncomeLoss`, from the same payload.

**Consequences.** Measured on 2026-09-07 against 31 stored runs: 16 disjoint-concept false positives
and no genuine conflict, because the producers were never asked about the same fact. This drove D-33
to D-35 and then D-28. `producers/earnings.py` cites "divij/sdd.md's Open Question #1" for the
rationale; the record says that heading does not exist and the real deliberation is the 2026-08-29
entry.

**Source.** `logs/RUN_LOG.md` 2026-08-28 "Replace fixture Producer B with a real second grader";
2026-08-29 "Five model tests run against the live AAPL result"; 2026-09-07 "Real-run regression
corpus + structural diagnosis".

## D-28 · Lens v2: overlapping metrics now, bull/bear later
- **Status:** In force
- **Decided:** 2026-09-24 (human decision 2); built 2026-09-25
- **Where:** [[producers/lens.py]], [[producers/financial.py]], [[producers/earnings.py]], [[validation/concept_linkage.py]], [[validation/facts.py]]

**Context.** Disjoint lenses could never produce a same-fact disagreement.

**Decision.** `FINANCIAL_LENS` adds `EarningsPerShareDiluted` and `EARNINGS_LENS` adds `NetIncomeLoss`,
so both share two figures; new concepts are appended so v1 lines keep their positions. Lenses carry
`version="v2"`, and runs store the lens version and the shared set. `concept_aware` compares shared
figures by value, with the shared set derived from the lens definitions. A new neutral status,
`CITED_BY_ONE`, marks a figure both agents were given but only one cited, so it is not mislabelled as
one-sided.

**Consequences.** The first same-figure agreement in ticker mode was observed on AAPL. Agents often
ignored the new shared line, so no live ticker-mode disagreement on a shared figure has been seen.
Corpus entries are tagged `lens_version: "v1"`.

**Source.** `logs/RUN_LOG.md` 2026-09-24 "Human decisions"; 2026-09-25 "B2 + B3: overlapping lens
metrics".

## D-29 · Two pairings: lenses and bull/bear
- **Status:** In force
- **Decided:** 2026-09-26
- **Where:** [[producers/bull.py]], [[producers/bear.py]], [[producers/__init__.py]], [[web/server.py]]

**Context.** The "bull/bear later" half of human decision 2.

**Decision.** Bull and bear lenses read the same six filing figures with opposite briefs, under
`AgentID.BULL` and `BEAR`. `/api/compare` takes `pairing: "lenses" | "bull_bear"` through
`producers.PAIRINGS`. Bull/bear defaults to `canonical_facts`, because both agents see identical
figures.

**Consequences.** Too few runs to judge the briefs; under v1.5.2 bear passed 2 of 2 and bull 0 of 2
([`bull-bear-unmeasured`](ledger.html#bull-bear-unmeasured)).

**Source.** `logs/RUN_LOG.md` 2026-09-26 "B4 + U7".

## D-30 · Comparison is numeric only and does not decide who is right
- **Status:** In force
- **Decided:** 2026-08-21
- **Where:** [[validation/cross_validation.py]]

**Context.** Cross-Agent Validation had no implementation, and the proposal scoped v1 narrowly.

**Decision.** The comparator detects numeric disagreement between two conclusions. It does not judge
reasoning, does not decide which agent is right, does not cover non-numeric claims, and is not to be
described as "Pattern Recognition". It reuses the accountability layer's loop, schemas and store
unmodified.

**Consequences.** Two conclusions that disagree in substance over the same figures are not flagged.
Whether a conclusion matches its source is a separate job (D-36). Only `HaltError` is caught per agent;
there is no `ERROR` comparison state, left as a design decision.

**Source.** `logs/RUN_LOG.md` 2026-08-21 "Implement Cross-Agent Validation v1 (SDD v1)"; 2026-09-24
"Same-source Cross-Agent Validation tests"; `docs/SYSTEM_DESIGN.md` §3.1.

## D-31 · "Could not check" is never recorded as "checked, found nothing"
- **Status:** In force
- **Decided:** 2026-08-21 (`contradiction_flag`); not recorded for `verify_claims`
- **Where:** [[validation/cross_validation.py]], [[validation/verification.py]], [[web/frontend/src/components/RecordSections.tsx]]

**Context.** P3: a value no check produced must not look like a result.

**Decision.** `contradiction_flag` is `None` unless the status is `COMPARED`. `verify_claims` returns
`None` for an unreachable source. The UI labels "no citations extracted" separately from "0 verified",
and shows unchecked citations as unchecked.

**Consequences.** Mutation testing confirmed tests fail if `None` becomes `False`. `list_contradictions`
excludes `None`. `_fetch()` collapses every failure to `None`, so blocked, timed out and DNS failures
cannot be told apart.

**Source.** `logs/RUN_LOG.md` 2026-08-21 "Implement Cross-Agent Validation v1"; 2026-09-22 "Fix: 'X%
citations verified' collapses"; 2026-09-24 "Make citation verification status visible";
`docs/SYSTEM_DESIGN.md` §3.3 and §4.

## D-32 · One shared definition of "a number"
- **Status:** In force
- **Decided:** 2026-08-29 (bare decimals); consolidated 2026-09-04; comma groups 2026-09-11
- **Where:** [[core/numeric.py]], [[tests/test_numeric.py]], [[validation/claims.py]], [[validation/consistency.py]]

**Context.** The fabricated AAPL ratio `0.34` was invisible to the regex, and the pattern existed in
three hand-synced copies.

**Decision.** `QUANTITATIVE_RE` in `core/numeric.py` is the one definition. It accepts a bare decimal
as a known false positive (it also matches "2.1"). A comma-grouped alternative stops
"13,971,000,000.0" truncating to "000.0". A test asserts the modules share one object.
`normalize_number` and `close_enough` moved here in B1.

**Consequences.** A bare integer, such as a year, is not matched; a test pins that as expected
behaviour. The figure check (D-35) extracts years only when enabled.

**Source.** `logs/RUN_LOG.md` 2026-08-29 "Widen the quantitative-number regex"; 2026-09-04 "SOLID
restructure"; 2026-09-11 (continued) "Fix core comparator correctness"; 2026-09-24 "Same-source
Cross-Agent Validation tests".

## D-33 · `concepts_expected_to_overlap=False` for the asymmetric pair
- **Status:** Superseded by D-34 in production (2026-09-11); still available
- **Decided:** 2026-08-29
- **Where:** [[validation/cross_validation.py]]

**Context.** The live breadth run flagged 11 of 12 tickers, mostly because one agent quoted numbers and
the other did not.

**Decision.** With the flag `False`, a contradiction requires both sides to cite a number. The default
`True` kept every fixture test unchanged. Reported fields were computed identically either way.

**Consequences.** On the recorded sample it cut flags from 11 of 12 to 7 of 12. On 2026-09-07 it was
found to suppress the one confirmed true positive (AAPL `0.34`), because B's side was empty.

**Source.** `logs/RUN_LOG.md` 2026-08-29 "Comparator semantics for information-asymmetric agents";
2026-08-29 "Item 3 results"; 2026-09-07 "Real-run regression corpus".

## D-34 · `contradiction_rule` is opt-in; `concept_aware` decides ticker-mode lens runs
- **Status:** In force
- **Decided:** 2026-09-11
- **Where:** [[validation/cross_validation.py]], [[validation/concept_linkage.py]], [[web/server.py]], [[tests/test_real_run_corpus.py]]

**Context.** The corpus showed the over-flag was structural. A concept-tagging prototype was measured
before being wired in.

**Decision.** `run_cross_agent_validation` takes `contradiction_rule`, default
`"symmetric_difference"`, so existing callers are unchanged. `concept_aware` tags each number with the
nearest lens concept and compares only untagged numbers (and, since lens v2, shared figures by value).
`/api/compare` uses it for the lenses pairing unless the request names another rule.

**Consequences.** Measured on the corpus: 15 of 16 disjoint-concept false positives removed, the true
positive kept, no new flags; `disjoint-concepts` and
`asymmetry-fix-suppresses-historic-true-positive` moved to RESOLVED. B1 later found the 15 of 16 partly
an artifact: "Return on Assets" was tagged as `Assets` and excluded. A legitimate derived ratio and a
fabricated one remain indistinguishable to this rule.

**Source.** `logs/RUN_LOG.md` 2026-09-11 "Concept-linkage prototype"; 2026-09-11 (continued) "Fix core
comparator correctness"; 2026-09-24 "B1 + U2" ("The acceptance test failed").

## D-35 · `canonical_facts` stays opt-in for ticker-mode lens runs
- **Status:** In force
- **Decided:** 2026-09-24
- **Where:** [[validation/facts.py]], [[validation/cross_validation.py]], [[web/server.py]], [[tests/test_facts.py]]

**Context.** B1 built a figure-by-figure comparison by (metric, period), with statuses such as `MATCH`,
`MISMATCH`, `DIFFERENT_PERIODS`, `UNCORROBORATED` and `DERIVED_WRONG`. The plan's bar was "corpus
replay no worse than `concept_aware`, else opt-in".

**Decision.** It failed the bar (6 flags against 1 on the 16 false positives), so it is opt-in for the
lenses pairing. It is the default for subject mode (with years) and for bull/bear. Every compared run
stores `metric_comparisons` and the rule that decided the flag, whichever rule it was.

**Consequences.** It found two genuine errors hidden by `concept_aware` (asset turnover 0.13 against a
recomputed 0.693) and cleared correct ratios. The 5 extra flags cannot be adjudicated because the
corpus did not record contexts; stored runs now do. Tagging is lexical
([`checks-lexical-coverage`](ledger.html#checks-lexical-coverage)).

**Source.** `logs/RUN_LOG.md` 2026-09-24 "B1 + U2: figure-by-figure comparison".

## D-36 · Claims are extracted from both blocks, per producer
- **Status:** In force
- **Decided:** 2026-09-11 (per producer); 2026-09-22 (both blocks)
- **Where:** [[validation/claims.py]], [[validation/verification.py]], [[web/server.py]], [[tests/test_compare_route.py]]

**Context.** The AAPL fabrication was caught by a human reading the log. Later, a scan of 62 stored
runs found no citation claim ever extracted, because the directive asked for citations in
`<conclusion>` while the routes read only `<thought_log>`.

**Decision.** `/api/compare` runs `extract_claims` and `verify_claims` on each producer's own
successful attempt, independently. Both routes use `extract_claims_from_response`, which reads both
blocks. Investors get the verification rate but not the claims list.

**Consequences.** On the historic case `verification_rate` is 0.0, which marks unsupported citations
but not which number is fabricated.

**Source.** `logs/RUN_LOG.md` 2026-09-11 (continued) "Fix core comparator correctness"; 2026-09-22
"Make citation verification actually fire".

## D-37 · Accounting checks split hard rules from heuristics
- **Status:** In force
- **Decided:** 2026-09-25
- **Where:** [[validation/constraints.py]], [[tests/test_constraints.py]], [[validation/gate.py]]

**Context.** Roadmap B3: check each agent's own figures and each cited figure against the filing.

**Decision.** Three passes, stored as `structural_flags`: hard rules on an agent's own figures (basic
EPS at least diluted; FCF = OCF − CapEx; assets = liabilities + equity to 2%); heuristics
(net income ≤ operating income ≤ gross profit ≤ revenue), never gated, each with the reason it is not
an identity; claim against source, where rounding to the digits written is not misquoting. Figures
for different periods are skipped with the reason, never failed. The same rules run on the filing
itself and are reported, never gated.

**Consequences.** A check that does not run is not shown, so no failure does not mean correct. GOOGL's
net income above operating income failed the heuristic on the filing too, the case heuristics exist
for.

**Source.** `logs/RUN_LOG.md` 2026-09-25 "B2 + B3: overlapping lens metrics, and accounting checks".

## D-38 · Only a two-sided conflict opens the gate; the policy is versioned
- **Status:** In force (policy v3)
- **Decided:** 2026-09-25 (v1, v2); 2026-09-26 (v3)
- **Where:** [[validation/gate.py]], [[tests/test_gate.py]], [[web/db.py]]

**Context.** P4 needs a specific, testable handoff condition, and the plan ruled out gating old runs
retroactively.

**Decision.** A compare run is `AWAITING_DECISION` while a gated item lacks a decision, then `DECIDED`.
v1 gates `MISMATCH` rows; v2 adds failed hard checks on an agent's own figures; v3 adds differing
grades. `UNCORROBORATED` rows, heuristics and filing checks never gate. Each run is stored with
`gate_policy` and judged under it; runs without one are `NOT_GATED`. `GATE_POLICY` is `"v3"`.

**Consequences.** `escalation-undefined` moved to RESOLVED, for mismatches only. Adding decisions
required rebuilding `gate_decisions` by copying every row and count-checking, the subsystem's first
schema migration. A consensus cannot be confirmed as the published grade; only a disagreement opens a
grade item.

**Source.** `logs/RUN_LOG.md` 2026-09-25 "BG + U3: the human decision gate"; 2026-09-25 "B2 + B3";
2026-09-26 "Option 1 + B5 + U8"; `validation/gate.py` (module docstring and `GATE_POLICY` comment).

## D-39 · Decisions are refused, never repaired, and never made by an AI
- **Status:** In force
- **Decided:** 2026-09-25
- **Where:** [[validation/gate.py]], [[web/db.py]], [[web/frontend/src/components/DecisionGate.tsx]]

**Context.** P3 and P4: a gate decision must be complete and made by a named human.

**Decision.** Each decision needs a type that fits the item, a name of at least 2 characters, a
rationale of at least 20, and the items it covers; anything else is refused with the reason (422).
A value is allowed only with `override_value` for one figure. A later decision on the same item
supersedes an earlier one; both stay in the append-only table. `decided_by` is self-declared, and
every gate payload says so (`IDENTITY_NOTE`). The AI sessions that opened live gates recorded no
decision, and said why.

**Consequences.** Any auditor token can decide, and anyone can mint one
([`gate-identity-self-declared`](ledger.html#gate-identity-self-declared),
[`audit-criticals`](ledger.html#audit-criticals)). Run `ec1a3b44` was left `AWAITING_DECISION` for the
human.

**Source.** `logs/RUN_LOG.md` 2026-09-25 "BG + U3"; 2026-09-26 "Option 1 + B5 + U8".

## D-40 · Investors see disputed values only after a decision
- **Status:** In force
- **Decided:** 2026-09-25; widened 2026-09-26
- **Where:** [[validation/gate.py]], [[web/server.py]], [[tests/test_trace_withholding.py]], [[validation/audit.py]]

**Context.** While a run awaits a decision, showing investors the contested figures would publish a
result no human has cleared.

**Decision.** `redact_for_scope` withholds both conclusions, cited numbers, claims, disputed values and
a pending check's arithmetic from investor reads, and strips the internal tier from the nested session.
After a correction found a disputed year in a search preview, `strip_search_content()` also removes
search results from trace steps, and the investor stream, snippet route and decisions route were
closed. Exports are built after redaction.

**Consequences.** Withholding happens at read time; storage holds everything. A token-less read is
served at the stored scope, kept so the classic UI worked; that is recorded as a human call. Context a
user supplies for a generic run is still shown to investors.

**Source.** `logs/RUN_LOG.md` 2026-09-25 "BG + U3"; 2026-09-26 "Correction: two claims in earlier
entries were wrong"; 2026-09-26 "Verified: the trace fix holds"; 2026-09-27 "B6 + U9".

## D-41 · Divergence is classified and counted, never scored; consensus is narrow
- **Status:** In force
- **Decided:** 2026-09-26
- **Where:** [[validation/divergence.py]], [[tests/test_synthesis.py]], [[validation/gate.py]]

**Context.** Roadmap B5: say why two graded agents differ and who sets the grade.

**Decision.** The primary driver is chosen in a fixed order: data, then assumption, then weighting as
the residual, then none or insufficient. Evidence per agent is counted (matching, contradicting,
unchecked, unbacked, failed hard checks), never turned into a score. No model is called.
`consensus_grade` exists only when grade and direction agree and no hard check failed. Investors see
a grade only once a named human has recorded one.

**Consequences.** Both live grade conflicts were classified with the flawed v1 extraction prompt. The
forward-looking check is a word list.

**Source.** `logs/RUN_LOG.md` 2026-09-26 "Option 1 (assessment extraction) + B5 + U8";
`validation/divergence.py` (module docstring).

## D-42 · Append-only is enforced by SQLite triggers
- **Status:** In force
- **Decided:** not recorded for `runs` (C-03, prototype); 2026-09-25 for `gate_decisions`
- **Where:** [[web/db.py]], [[docs/DATA_CONTRACT.md]]

**Context.** Application discipline alone would let a bug elsewhere rewrite history.

**Decision.** `BEFORE UPDATE` and `BEFORE DELETE` triggers call `RAISE(ABORT)` on `runs` and on
`gate_decisions`, which also repeats the decision minimums as CHECKs. The 90-day TTL purge
(`RETENTION_DAYS`) drops and recreates the triggers around a dated delete, now including the decisions
of expired runs.

**Consequences.** The store is not tamper-evident: `clear_all()` behind the unauthenticated
`DELETE /api/runs` drops every table. Unwanted rows cannot be removed selectively.

**Source.** `docs/SYSTEM_DESIGN.md` §2.7 and §4; `docs/DATA_CONTRACT.md` "Rules"; `logs/RUN_LOG.md`
2026-09-25 "BG + U3".

## D-43 · New fields go inside the payload blob, not new columns
- **Status:** In force
- **Decided:** 2026-08-21 (SDD §7.3)
- **Where:** [[web/db.py]], [[validation/cross_validation.py]]

**Context.** Cross-agent results needed storing without a schema change.

**Decision.** A run is one `payload_json` blob, with `ticker`, `scope` and `status` pulled out for
indexing. `cross_agent_comparison` and later fields live inside it. "Every contradiction" is
`list_contradictions`, a Python scan.

**Consequences.** Zero migrations for run data, at the cost of in-process scans, to be revisited only
if measured slow. Stored compare runs grew from 7 keys to 14 in B1, so older records lack trace and
input facts.

**Source.** `logs/RUN_LOG.md` 2026-08-21 "Implement Cross-Agent Validation v1"; 2026-08-28 "Configure
GEMINI_API_KEY; add queryable contradictions"; 2026-09-24 "B1 + U2"; `docs/SYSTEM_DESIGN.md` §4.

## D-44 · Scope redaction omits keys rather than nulling them
- **Status:** In force
- **Decided:** not recorded (SEC-01, SEC-02 in the prototype)
- **Where:** [[core/schemas.py]], [[web/auth.py]], [[validation/gate.py]]

**Context.** An investor must not receive the internal tier, and must be able to tell "withheld" from
"the model produced nothing".

**Decision.** `to_dict(investor_scope=True)` leaves `thought_log`, `raw_output`, `llm_tokens`, the
directive and context window, and the assessment fields out of the dict. Scope travels in a JWT
(`web/auth.py`). A test checks that `redact_for_scope` drops what `to_dict` drops, after new assessment
keys once slipped through.

**Consequences.** `RunSession.to_dict()` still nests full-tier objects, and storage is full
([`session-scope-leak`](ledger.html#session-scope-leak)). `issue_token` mints any scope, and several
routes are unauthenticated ([`audit-criticals`](ledger.html#audit-criticals)): not deployable beyond
localhost.

**Source.** `docs/SYSTEM_DESIGN.md` §2.8 and §4; `logs/RUN_LOG.md` 2026-08-28 "add an HTTP route";
2026-09-26 "B4 + U7" ("Found before calling it done").

## D-45 · The consistency probe is metadata and is never persisted
- **Status:** In force
- **Decided:** not recorded (ADR-06 mitigation, prototype); auto-enable rule reworded 2026-09-23
- **Where:** [[validation/consistency.py]], [[web/server.py]]

**Context.** Re-asking the same agent is weak positive and strong negative evidence.

**Decision.** `/api/chat` re-runs the query and scores word and number overlap. The probe run is never
stored. It is on for non-Gemini model names, since the Ollama determinism claim was measured false,
and opt-in otherwise.

**Consequences.** Two consistent fabrications still pass. The probe reuses the traced adapter, so the
live view labels it a retry
([`consistency-probe-shown-as-retry`](ledger.html#consistency-probe-shown-as-retry)).

**Source.** `docs/SYSTEM_DESIGN.md` §2.6 and §4; `logs/RUN_LOG.md` 2026-09-23 "Make LangChain the sole
agent framework"; 2026-09-27 "A model-call timeout, and a ledger refresh".

## D-46 · The Honest Ledger lives in code and is served unauthenticated
- **Status:** In force
- **Decided:** 2026-09-04
- **Where:** [[web/self_report.py]], [[web/server.py]]

**Context.** The human asked for the UI to show tests run, their results and what is going wrong.

**Decision.** `web/self_report.py` holds known issues and live-model tests, each with a source and a
status; a fixed issue changes status and keeps its history rather than being deleted. Test counts are
discovered live. `GET /api/self-report` is unauthenticated on purpose.

**Consequences.** Entries are hand-maintained and can go stale; the 2026-09-27 refresh found two wrong
claims. Discovery imports the test package into the server, which is how D-18's guard reached live
calls.

**Source.** `logs/RUN_LOG.md` 2026-09-04 "Frontend for Cross-Agent Validation, including an
honest-ledger surface"; 2026-09-27 "A model-call timeout, and a ledger refresh".

## D-47 · `brutalist/` does not govern the web app
- **Status:** In force
- **Decided:** 2026-09-24 (human decision 1)
- **Where:** [[web/frontend/src/styles.css]], [[web/frontend/README.md]]

**Context.** The repo-root `AGENTS.md` says all visual output follows `brutalist/`.

**Decision.** The human ruled that `brutalist/DESIGN.md` is for videos, articles and documents, not web
pages. The app keeps its palette, status colours, system fonts, rounded badges and fixed top bar.

**Consequences.** This conflicts with the root `AGENTS.md` wording, which sits outside the subsystem and
was not edited.

**Source.** `logs/RUN_LOG.md` 2026-09-24 "Human decisions: audit-layer roadmap approved; web UI scope
for brutalist/".

## D-48 · React replaces the classic UI by strangler migration
- **Status:** In force (cutover done 2026-09-27)
- **Decided:** 2026-09-24 (human decisions 3 and 5)
- **Where:** [[web/frontend/src/App.tsx]], [[web/server.py]], [[archive/web-static-legacy/README.md]], [[tests/test_cutover.py]]

**Context.** The human chose React and Vite over vanilla modules and Preact, with rollout order: data
tables, comparison matrix, inline gates.

**Decision.** The React app mounted at `/app` while the classic UI kept `/` until parity. Model text
renders through `react-markdown` with raw HTML ignored. HTML is served `no-cache`. At cutover the
classic files were archived and `/` redirects to `/app/` with `Cache-Control: no-store`, or returns a
503 page without a build.

**Consequences.** `conformance.mjs` skips `.ts` and `.tsx`, so `npm run verify` is the machine check.
A browser tab cached the classic UI after cutover
([`cached-classic-ui`](ledger.html#cached-classic-ui)). Fixtures are marked `-text` in
`.gitattributes`.

**Source.** `logs/RUN_LOG.md` 2026-09-24 "Human decisions"; 2026-09-24 "U1: React + Vite foundation";
2026-09-27 "B6 + U9"; 2026-09-27 "Committing the work since c53746a".

## D-49 · "Clear all runs" is not ported to the new UI
- **Status:** In force (ledger `clear-all-runs-not-in-ui`, BY_DESIGN)
- **Decided:** 2026-09-27
- **Where:** [[web/server.py]], [[web/self_report.py]], [[archive/web-static-legacy/README.md]]

**Context.** The classic UI had a button for `DELETE /api/runs`.

**Decision.** The React app has no such button, because the route drops every table, decisions
included, against the never-delete rule. The route itself is unchanged, for admin and test use.

**Consequences.** It is still unauthenticated
([`audit-criticals`](ledger.html#audit-criticals)).

**Source.** `logs/RUN_LOG.md` 2026-09-27 "B6 + U9"; `web/self_report.py` (`clear-all-runs-not-in-ui`).
