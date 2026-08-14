# Accountability Layer — Technical Audit

**Audit date:** 2026-08-13
**Commit audited:** `fe45eb4` (Week 9/10: financial grader skeleton, LangFuse tracing)
**Scope:** entire `accountability_layer/` codebase — core audit engine, web/API/auth/DB layer, browser UI, LLM adapters, tests
**Method:** every source file read and traced end-to-end; docstring claims verified against actual code paths; test suite executed (`python -m unittest discover -s tests` → **108 tests, all passing**)

---

## 0. Executive summary

The **core accountability engine is genuinely well-built**. The retry-then-halt validation loop, the structural parser, and the schema validation rules are correct, carefully reasoned, and backed by real tests that assert real behavior. The browser UI is fully wired — every control maps to a live backend route with real data, with no decorative dead ends. The adapter abstraction is consistent across all three providers. Several docstrings are commendably honest about their own limits (the determinism caveats and ADR-06's "log is evidence of output, not process" framing in particular).

The problems are concentrated in **three areas**, and they follow a consistent pattern: *guarantees that are stated in documentation and enforced at one call site, but not structurally*.

1. **The tiered-access model (SEC-01/SEC-02) is bypassable.** Investor-scope redaction works on the `/api/chat` response but is undone at storage time by `RunSession.to_dict()`, and the read routes that serve that stored data have no authentication at all. Anyone can also mint themselves an `auditor` token.
2. **The audit trail has holes it doesn't acknowledge.** Infrastructure failures (rate limits, connection drops) produce *no* `ReasoningObject` at all, despite the middleware's promise that every attempt is written.
3. **Several headline features are weaker than they're described.** The confidence penalty (ADR-04) is unreachable for real LLM providers. The consistency probe is near-tautological under the system's own default config. Replay silently drops `context`.

None of this is unusual for a research prototype at this stage, and much of it is explicitly flagged in the code's own TODOs. But the gap between "what the docs claim" and "what the code enforces" matters more than usual here, because *the entire product thesis is that claims must be verifiable*. See §7 for a prioritized fix list.

**Overall maturity:** solid Phase-1/2 prototype. Not deployable past localhost without addressing §2.

---

## 0.1 Re-orientation — where you left off

Since it's been a while, here's the state of play at a glance.

| | |
|---|---|
| **Last commit** | 2026-08-11 (`fe45eb4`) — Week 9/10 work |
| **Prior commit** | 2026-08-03 (`71efcf9`) — Week 6/7 determinism + verification |
| **Size** | ~6,500 lines of Python across 20 modules, 16 API routes, ~1,900 lines of frontend |
| **Tests** | 108, all passing, `unittest` only (no pytest, per the stdlib-only constraint) |
| **Working tree** | Clean as of this audit |

**The most recent work (Week 9/10)** was `financial_grader.py` + `observability.py` — an EDGAR-backed financial grader skeleton with LangFuse tracing. That work is complete and tested for what it claims to be (a skeleton), but it is **not yet wired into the web app at all**: `web/server.py` has no route that calls `analyze_ticker()`. It currently only runs via `test_langfuse_integration.py` (a manual script) and its unit tests. That's the most obvious "pick up here" thread.

**Two fully-built backend features have no UI**, which is easy to forget you built: `POST /api/runs/{id}/replay` and `GET /api/runs/drift`. Both work; neither is reachable from the browser.

---

## 1. What works correctly

Listing this first so the rest of the report reads as calibrated rather than a takedown. These are real strengths.

### Core engine
- **`parser.py` structural parsing is correct and exhaustively tested.** `_parse_response` (`parser.py:48-91`) anchors both tags at line-start, searches for `<conclusion>` only *after* the `<thought_log>` span ends (dodging fake tag-mentions inside the log body), and requires the remainder outside both spans to be blank. Tests cover happy path, each missing block, both missing, text before/after/between blocks, whitespace-only gaps, multiline content, and empty string (`tests/test_phase2_agent.py:42-122`). This is the best-tested module in the repo.
- **The retry-then-halt state machine (ADR-07) is correct** for the failure mode it targets. `run_validation_loop` (`middleware.py:76-179`) calls the agent, and on `StructuralParseError` logs a `PARSE_FAILURE` `ReasoningObject`, retries once with the hardcoded corrective directive (`middleware.py:27-29`), then on second failure logs a `HALT` object and raises `HaltError` carrying *both* records (`middleware.py:130-148`). Every branch is tested — happy path, fail→retry→success, fail→fail→halt, directive-switch verification, run_id/agent_id continuity (`tests/test_phase2_agent.py:129-278`).
- **`schemas.py` validation rules are real and tested.** `ReasoningObject._validate()` (`schemas.py:155-181`) enforces confidence bounds, `attempt_number ∈ {1,2}`, the ADR-07 rule that attempt 2 can never be `PARSE_FAILURE`, that `SUCCESS` requires a non-empty conclusion, that warnings require a degradation reason, and that timestamps are tz-aware. `RunSession._validate()` (`schemas.py:265-295`) enforces the ADR-08 cross-field rule that classification must match the `< 0.4` threshold — with the exact boundary tested (`tests/test_phase1_schemas.py:289-300`).
- **SEC-01 redaction is implemented correctly *at the `ReasoningObject` level*.** `to_dict(investor_scope=True)` (`schemas.py:187-225`) structurally *omits* the `thought_log`/`raw_output`/`llm_tokens` keys rather than nulling them — exactly right, and covered by belt-and-suspenders tests that assert the content doesn't appear anywhere in the serialized string (`tests/test_phase1_schemas.py:370-450`). (The bypass in §2.1 is at the `RunSession` level, not here.)

### Data layer
- **No SQL injection anywhere.** Every user-supplied value in `web/db.py` is passed as a bound parameter — `get_runs()` (`db.py:214-218`), `get_run()` (`db.py:223-228`), `insert_flag()` (`db.py:281-285`). The one place string interpolation touches SQL is the variable-length `IN (...)` clause in `purge_old_runs()` (`db.py:133`), where only the *count* of `?` placeholders is interpolated and the values remain bound. That's the correct, standard pattern.
- **Append-only enforcement is real, not conventional.** `runs_no_update` and `runs_no_delete` are genuine SQLite triggers issuing `RAISE(ABORT, ...)` (`db.py:55-65`). Normal application code physically cannot mutate the runs table. (Caveats in §2.3 and §4.)
- **WAL mode is enabled** for concurrent reader access (`db.py:93-99`).

### Adapters and integration
- **The adapter contract is consistently implemented.** All three adapters expose `(subject, context, directive) -> AgentResponse` and route through the same parser: Gemini (`gemini_adapter.py:106,154`), Ollama (`ollama_adapter.py:64,112`), mock (`mock_adapter.py:48`). No drift in return types.
- **Gemini rate-limit handling is thoughtful.** It distinguishes per-day (fail fast, `RateLimitDailyError`) from per-minute (back off and retry, `RateLimitMinuteError`) and honors the API's own `retryDelay` hint (`gemini_adapter.py:49-74`). These are mapped end-to-end into user-visible halt banners in the UI (`server.py:414-424` → `app.js:373-387`).
- **`mock_adapter.py` is simple and correct** — three deterministic failure modes driven by a closure-local call counter (`mock_adapter.py:46-75`), which is exactly what makes the middleware tests trustworthy.
- **Determinism claims are honestly hedged, not overclaimed.** Both `gemini_adapter.py:98-99` and `ollama_adapter.py:9-16` explicitly state that seed reproducibility holds only within a fixed model version and quantization. That intellectual honesty is worth preserving.
- **The LangFuse wrapper is appropriately minimal and self-aware.** `make_traced_adapter` (`observability.py:27-41`) is 8 lines that delegate entirely to the SDK decorator, and the docstring openly states that token/cost fields stay blank until adapters surface usage metadata (`observability.py:32-34`). Graceful degradation without credentials is real (it relies on the SDK's documented no-op behavior, and `.env.example:9-21` documents the vars as optional).

### UI
- **Every UI control is genuinely wired.** Traced each DOM element in `app.js` against `web/server.py`: provider dropdown, Gemini model/temperature, Ollama model/seed, agent ID, confidence knob, failure-mode selector, consistency-probe checkbox, chat submission, claims pills, verification badges, consistency badges, reviewer flag form, runs/sessions tabs, detail modals, scope toggle, directive modal, clear-runs. **No decorative or unwired UI element was found.** The gap runs the other direction (§4).
- **The chat error path is solid** — full try/catch, a `401` special-case that clears the cached token and retries once (`app.js:466-484`), and distinct rendering for network vs. server errors (`app.js:425-436,492-494`).

---

## 2. Critical findings

These break a guarantee the project explicitly claims. All are reachable over HTTP with no credentials.

### 2.1 [CRITICAL] SEC-01 investor redaction is bypassed at storage and read time

`RunSession.to_dict()` hardcodes the scope flag:

```python
"reasoning_objects": [
    ro.to_dict(investor_scope=False) for ro in self.reasoning_objects
],
```
— `schemas.py:313-315`

In `chat()`, the top-level list *is* correctly redacted per caller scope (`server.py:365-367`) and `payload["thought_log"]` is nulled for investors (`server.py:372`). But `payload["session"] = session.to_dict()` (`server.py:368`) embeds a **second, always-unredacted copy** of the same reasoning objects. That copy is what gets persisted (`insert_run`, `server.py:439`) and what every read route hands back.

**Consequence:** an investor-scoped chat response correctly hides the `thought_log` — and then the exact same content is retrievable seconds later, by anyone, from `GET /api/runs/{id}` or `GET /api/sessions/{id}`. SEC-01's stated requirement ("thought_log must provably never reach investor tier") is enforced at exactly one response-construction call site, not structurally.

This is the single most important finding in the report, because SEC-01 is the security property the tiered-rendering architecture (ADR-03, C-05/C-06) exists to provide.

### 2.2 [CRITICAL] Read routes have no authentication at all

Only **two** of sixteen routes carry `Depends(require_scope)` — `POST /api/chat` (`server.py:281`) and `POST /api/runs/{id}/flags` (`server.py:570`). Verified by inspecting every route decorator:

| Unauthenticated route | Returns |
|---|---|
| `GET /api/runs` (`server.py:448`) | full run payloads, all runs |
| `GET /api/runs/{run_id}` (`server.py:469`) | full run payload |
| `GET /api/sessions` (`server.py:594`) | all sessions |
| `GET /api/sessions/{session_id}` (`server.py:599`) | full session |
| `GET /api/runs/{run_id}/flags` (`server.py:584`) | all reviewer notes |
| `GET /api/runs/drift` (`server.py:458`) | confidence series |
| `POST /api/runs/{run_id}/replay` (`server.py:477`) | re-runs a live LLM call |
| `POST /api/config` (`server.py:247`) | mutates global server config |

This is what makes §2.1 exploitable in practice rather than theoretically. Note the asymmetry on flags specifically: *writing* a reviewer flag requires auditor scope (checked twice, `server.py:570,573-577`), but *reading* every flag requires nothing.

`POST /api/runs/{id}/replay` being open is independently notable — an unauthenticated caller can trigger arbitrary billable LLM calls against your Gemini quota.

### 2.3 [CRITICAL] `DELETE /api/runs` destroys the audit log with no auth

`server.py:609-613` → `clear_all()` (`db.py:302-313`) **drops and recreates all three tables**. No scope dependency, no environment gate. The docstring says "Test / dev use only" (`server.py:611`) but nothing enforces that.

The irony is structural: `db.py`'s triggers make the runs table genuinely immutable against `UPDATE`/`DELETE`, and then this route bypasses the triggers entirely by dropping the table. An "append-only, tamper-evident" store that anyone on the network can wipe with one unauthenticated `DELETE` is not tamper-evident.

### 2.4 [CRITICAL] Anyone can mint an `auditor` token

`POST /api/auth/token` (`server.py:223-232`) issues a JWT for whatever scope the caller asks for, with **no identity check of any kind**. The TODO is acknowledged in three places (`server.py:228`, `auth.py:16,59`), so this is known — but it's live code, not a stub, and it means the entire scope-tier model is self-service. Even if §2.1 and §2.2 were fixed, an "investor" could simply request an `auditor` token.

The JWT implementation itself is fine (HS256, 8h TTL, proper `exp`/`iat`, correct 401/403 handling in `require_scope`, `auth.py:92-117`). The cryptography is not the problem; the absence of authentication is.

### 2.5 [CRITICAL] Hardcoded fallback signing secret, undocumented env var

`_DEV_SECRET = "dev-only-not-for-production-change-via-ACCOUNTABILITY_SECRET"` (`auth.py:40`) is used whenever `ACCOUNTABILITY_SECRET` is unset (`auth.py:49-50`).

The compounding problem: **`ACCOUNTABILITY_SECRET` does not appear in `.env.example` at all.** The documented setup path is "copy `.env.example` to `.env` and fill in your values" (`.env.example:1`), which only lists `GEMINI_API_KEY` and the three `LANGFUSE_*` vars. A deployer following the documentation exactly ends up running with a signing secret that is published in this repo's source — and there is no startup check that warns or fails.

Anyone who has read this repo can forge a valid `auditor` token offline.

---

## 3. High-severity findings

Not remotely exploitable, but each one means a documented capability doesn't work as described.

### 3.1 [HIGH] ADR-04's "confidence is computed, not self-reported" is not enforced — and is unreachable for real providers

Two separate problems.

**(a) The core layer never computes it.** `middleware.py:82` takes `confidence_score: float = 0.7` — a bare literal default — and passes it straight through into every `ReasoningObject` it builds (`middleware.py:56,68,123,139,156,172`). `schemas.py:137`'s comment "ADR-04: computed, not self-reported" sits on a field that `_validate()` only range-checks (`schemas.py:156-159`). Nothing structurally prevents a caller from supplying an arbitrary number.

**(b) The one real computation is dead code for Gemini and Ollama.** `_degrade_confidence()` (`server.py:169-174`) genuinely implements the −0.1-per-degraded-source penalty. But its input is:

```python
data_sources: tuple[DataSource, ...] = (
    _mock_data_sources() if _config["provider"] == "mock" else ()
)
```
— `server.py:301-303`

For `gemini` and `ollama`, `data_sources` is **always an empty tuple**, so the penalty sum is always zero and confidence always equals the raw config value. The penalty only ever fires for the mock provider. `financial_grader.py` doesn't pass `data_sources` at all, so it inherits the middleware's empty default too.

This matters beyond code hygiene: `context.md` §10 item 6 lists the −0.1 penalty as a **live, uncalibrated risk** "already affecting investor-facing confidence scores on every run." In reality it affects no real-provider run at all. The risk register is describing a mechanism that doesn't execute in production paths — arguably a *worse* documentation problem than the miscalibration it's warning about.

### 3.2 [HIGH] The audit trail silently loses records on infrastructure failure

`run_validation_loop` catches **only** `StructuralParseError` (`middleware.py:116,132`). Every other exception — `RateLimitDailyError`/`RateLimitMinuteError` (`gemini_adapter.py:39-44`), `OllamaConnectionError`/`OllamaModelError` (`ollama_adapter.py:38-42`), the `EnvironmentError` for a missing API key (`gemini_adapter.py:113-117`), any network error — propagates out uncaught, and the locally-built `objects` list is **discarded**.

Contrast with `HaltError`, which was deliberately designed to carry `reasoning_objects` out with it (`middleware.py:32-41`) precisely so nothing is lost. That safety net exists for exactly one failure path.

Downstream, `server.py:414-436` catches these exception types itself and sets `payload["halted"]=True`, but never constructs a `ReasoningObject` or `RunSession` — so `insert_session` is skipped (guarded by `if payload["session"]:`) and the runs table gets a row with an error string and no structured audit record.

**Net effect:** a Gemini rate-limit exhaustion mid-run produces no evidence of what was attempted. The middleware docstring's promise that both attempts are always written (`middleware.py:5`) holds only when the failure is a parse failure.

### 3.3 [HIGH] Replay silently drops `context`, invalidating the comparison

`server.py:525-526`:

```python
subject,
"",          # context not stored separately — replay on subject only
```

The comment is honest, but the consequence isn't drawn out: for any run that used a non-empty `context`, replay is executing a **different prompt** than the original. A resulting mismatch is indistinguishable from genuine model nondeterminism, and a match is partly coincidental. The endpoint's stated purpose — verifying same-input-same-output — doesn't hold whenever context was used.

Two smaller replay issues:
- `confidence_score` is read from `config_snap` (`server.py:529`), which is the *pre-degradation* base value, not the post-degradation score actually stored on the original run. Doesn't affect the conclusion text, but the replayed `ReasoningObject` metadata won't match.
- The directive-version lookup at `server.py:513-514` reads `config_snap.get("directive_version")` first — but `_config` (`server.py:109-119`) has no such key, so that branch is always `None` and it always falls through to the `payload["session"]` fallback. Works by accident; the operator precedence in that chained `or`/ternary makes it hard to read.

### 3.4 [HIGH] The consistency probe is near-tautological under the shipped defaults

`run_consistency_probe` (`consistency.py:147-204`) re-runs with a fresh `run_id` but **the same `call_agent_fn`** (`consistency.py:153,173`) and no parameter perturbation.

The shipped default config is `temperature: 0.0, seed: 42` (`server.py:112-113`), and both real adapters are explicitly built for determinism at those settings. So the probe re-runs a deterministic function with identical inputs and compares the output to itself — which will score ~1.0 (HIGH) whether the reasoning was genuine or fabricated.

This directly undercuts the module's own stated premise: *"a model that confabulated a plausible-sounding conclusion will drift"* (`consistency.py:9-11`). Drift is structurally suppressed by the adapter layer at the system's own defaults. The probe is only informative against a stochastic configuration, which is not what ships.

The Week 7 decision to auto-enable the probe for Ollama (`server.py:383`) makes this more pointed, since `ollama_adapter.py:48-51` defaults to `temperature=0.0, seed=42` — the most deterministic configuration in the codebase is the one where the probe runs automatically.

### 3.5 [HIGH] Number normalization is duplicated three times and has already drifted

`_NUMBER_RE` exists in three near-identical copies: `claims.py:33-41`, `verification.py:30-38`, `consistency.py:53-61`. Only `verification.py` normalizes matches into canonical floats (`_normalize`, `verification.py:52-66`).

`consistency.py._extract_numbers` (`consistency.py:103-104`) returns **raw lowercased strings**. So `"14%"` and `"14.0%"` — or `"$1.2 billion"` and `"$1,200 million"` — are treated as *different numbers*, and `number_divergence_flag` (`consistency.py:78,192-203`) fires a hard red badge in the UI for a formatting difference.

That flag was added in Week 7 specifically to be prominent and non-ignorable. It currently produces false positives on numerically identical output, which is the fastest way to train yourself to ignore it.

---

## 4. Medium-severity findings

### API and server
- **[MED] Process-global mutable config.** `_config` (`server.py:109-119`) is a single dict shared by every request — not per-session, per-user, or per-token. Any caller hitting `POST /api/config` changes the provider/model/seed/failure-mode for **all** concurrent users. Fine for solo local use; a correctness bug the moment two people use it at once.
- **[MED] TTL purge runs once, at startup only.** `purge_old_runs()` is called at `server.py:91` and nowhere else (verified by full-repo grep). `db.py:10-11` claims it's "called automatically on startup **and on every write**" — `insert_run()` (`db.py:166-185`) does not call it. A long-running server never purges past 90 days until restarted. OPS-03's "scheduled job, daily off-peak" is not implemented.
- **[MED] Local import inside a route body.** `server.py:512` imports `directive` inside `replay_run()` with no evident circular-import reason, inconsistent with the rest of the file.

### Data layer
- **[MED] Ticker extraction is a naive first-token heuristic.** `_extract_ticker` (`db.py:26-29`) takes the first whitespace-delimited token of the message. For natural-language input like `"What's your outlook on Tesla?"` the stored ticker is `"WHAT"`. Since `GET /api/runs?ticker=` and the entire drift/BN-02 story depend on this grouping, free-text chat silently produces junk buckets. It also strips non-Latin characters rather than transliterating (`"Ünilever"` → `"NILEVER"`), and truncation at 10 chars can collide distinct first-words.
- **[MED] The same logic is hand-duplicated** in `server.py:124-126`, with a comment in `db.py` acknowledging the duplication rather than factoring it out. Worse, they're fed *different strings*: the session ticker comes from the raw `request.message` (`server.py:353,441`) while the run ticker comes from the canonicalized subject (`db.py:177`), so Unicode-composed input can produce two different tickers for one run.
- **[MED] New connection per call.** `_connect()` (`db.py:93-99`) opens a fresh connection and re-issues both PRAGMAs on every single operation. No pooling. Works, but pays avoidable overhead per request.
- **[MED] `reviewer_flags` has no immutability triggers** (`db.py:78-87`), unlike `runs`. Nothing currently updates or deletes flags, so it's latent — but ADR-02's premise is that flags are a permanent parallel record.

### Verification and claims
- **[MED] `verification.py`'s 300KB fetch cap silently truncates EDGAR filings.** `_MAX_BYTES = 300_000` (`verification.py:47,87`) — while `financial_grader.py:36` uses **10MB** for the same class of document, with the comment "large-cap companyfacts JSON can run ~4MB+". Truncation mid-JSON makes `json.loads` fail, which is swallowed by a bare `except Exception: return out` (`verification.py:101-102`), yielding `verified=None`. Silent false negatives on exactly the large-cap tickers most likely to be tested.
- **[MED] Verification is citation-scoped, not claim-scoped.** `verify_claims` pools *every* quantitative number from the whole thought_log into one set (`verification.py:160-165`), then marks a citation verified if *any* of those numbers matches *any* number in the fetched source. A citation can therefore be marked `verified=True` on the strength of an unrelated number elsewhere in the response. This is a false-positive risk in the design, not an edge case — and `verification_rate` is surfaced to users as a trust signal.
- **[MED] "Generic URL" verification is not HTML-aware.** `_numbers_from_text` (`verification.py:113-120`) regexes raw bytes with no tag stripping, so CSS widths, dates, and tracking params all count as "source numbers." `verification.py:8` lists this as a peer-tier supported source alongside EDGAR without the caveat. EDGAR JSON parsing (`_numbers_from_edgar`, `verification.py:96-110`) is genuinely solid; generic web is true-but-weak.
- **[MED] Hedge-word matching has no word boundaries.** `[w for w in _HEDGE_WORDS if w in lower]` (`claims.py:138`) is a substring test — `"may"` matches inside `"mayor"`, `"Mayfield"`, or the month "May". Guaranteed false positives on financial prose.
- **[MED] Claim dedup key can silently merge distinct claims.** `sentence[:80].lower()` (`claims.py:140,152`) means two different sentences sharing an 80-character prefix (plausible for boilerplate) collapse into one, dropping the second. For a system whose purpose is capturing every claim, silent loss is the wrong failure direction.
- **[MED] Case-sensitive `"N/A"` filter.** `verification.py:171` checks `not in ("N/A", "")`, so `"n/a"` or `"TBD"` gets passed to `urllib.request` as a URL, fails inside a broad `except`, and reports "unattainable" instead of "no URL given."

### Adapters
- **[MED] Unsynchronized module-level state in the Gemini adapter.** `_last_call_ts` (`gemini_adapter.py:87`) is read-then-written via `global` inside the returned closure (`gemini_adapter.py:107,129-137`) with no lock. Classic check-then-act race: two concurrent calls can both see the gap as elapsed before either updates it, defeating the throttle the comment calls "mandatory ... between ALL API calls" (`gemini_adapter.py:32`).
- **[MED] Rate-limit classification via substring matching.** `"PerDay"`/`"per_day"` sniffed out of `str(exc)` (`gemini_adapter.py:58-65`). Any SDK message-format change silently reclassifies a daily limit as a generic error.
- **[MED] Ollama's third error shape is inconsistent.** A response with an `error` key that doesn't mention "not found"/"pull" raises a bare `RuntimeError` (`ollama_adapter.py:109`), which misses the 🦙-prefixed handling its two siblings get and falls into the generic catch-all (`server.py:434-436`).
- **[MED] Context truncation is a blunt character cut** in both real adapters (`gemini_adapter.py:77-81`, `ollama_adapter.py:66-69`) — no token awareness, no sentence boundary, no per-model limit despite the UI's own hint that small models have tighter windows (`index.html:77`). A citation URL or number can be cut in half.
- **[MED] `parser._parse_response` is private-by-convention but imported everywhere.** Single-underscore (`parser.py:48`), yet imported across module boundaries by all three adapters and the tests. No public wrapper exists, and `middleware.py` never calls it — parsing is fully delegated to each adapter, so nothing structurally prevents a future adapter from skipping the contract entirely.

### UI
- **[MED] Two complete backend features have zero UI.** `POST /api/runs/{id}/replay` (`server.py:477-561`, including diff computation) and `GET /api/runs/drift` (`server.py:458-466`) have **no references anywhere** in `app.js`, `web/static/index.html`, or `style.css` (grep-confirmed). Both are working code reachable only via curl.
- **[MED] The seed control is unreachable for Gemini.** The slider is rendered only inside the Ollama panel (`index.html:73-77`), but the backend passes `seed` to the Gemini adapter too (`server.py:182`). To change a Gemini seed you must switch to Ollama, move the slider, then switch back. Given determinism is a headline Week 6 feature, this is a real usability gap.
- **[MED] Silent failures on list refreshes.** `refreshRuns`/`refreshSessions` wrap everything in `try {...} catch { /* silent */ }` (`app.js:593-632`). If `/api/runs` is down, the panel simply never updates with no indication. Config-push failures are only `console.warn`'d (`app.js:170-172`), so a failed config change leaves UI and server state silently divergent.
- **[MED] All-or-nothing init.** `loadConfig`/`loadDirective`/token fetches run in one `Promise.all` (`app.js:966-982`); any single failure red-dots the whole app with no partial-success handling or retry.

---

## 5. Low-severity / cleanup

- **[LOW] Dead schema fields.** Full-repo grep confirms these are declared and serialized but **never populated by any code path**: `citations`/`Citation` (only ever constructed in test fixtures, `tests/test_phase1_schemas.py:139,149` — `claims.py`'s `ExtractedClaim` is never converted into one), `reasoning_steps` (`schemas.py:144`), `llm_tokens` (`schemas.py:148` — no adapter captures usage metadata; Gemini's SDK exposes it but `gemini_adapter.py:154` discards everything except `.text`), `confidence_degradation_reason`, and the entire AAN surface (`aan_triggered`, `aan_affidavit`, `AgentID.AAN` — the enum member is never referenced outside its own declaration).
- **[LOW] Extracted claims live outside the tamper-evident record.** `payload["claims"]` (`server.py:334,377-380`) is a parallel structure never folded into the `RunSession`/`ReasoningObject` it describes — so the claims and their verification status aren't part of the append-only audit object.
- **[LOW] No integrity hash on directives.** `directive.py` registers versions at import time (`directive.py:39-98`) with no checksum. Editing `DIRECTIVE_V1_1_0`'s text while leaving the version string unchanged would silently corrupt every future run's provenance, and ADR-05's verbatim-storage mitigation only protects runs already written.
- **[LOW] Naive sentence splitting.** `re.split(r'(?<=[.!?])\s+', ...)` (`claims.py:85-87`) mis-splits on abbreviations ("Q3.", "Inc.", "U.S.").
- **[LOW] No size guard in the parser.** `_parse_response` runs DOTALL regexes over unbounded input (`parser.py:48-91`); a runaway generation has no cap.
- **[LOW] CDN dependency with no SRI.** `marked@12` from jsdelivr with no `integrity` attribute (`web/static/index.html:242`). Degrades gracefully offline thanks to the `typeof marked !== 'undefined'` guard (`app.js:7`), but it's an unpinned third-party script.
- **[LOW] Auth token cached for the privileged scope unconditionally.** Both scopes are pre-warmed at init (`app.js:973-974`), so an auditor JWT is always held in memory even in investor demos. No logout affordance exists.
- **[LOW] `.env.example` under-documents config.** Missing `ACCOUNTABILITY_SECRET` (see §2.5) and `OLLAMA_HOST` (read at `ollama_adapter.py:32`).
- **[LOW] Accessibility.** No ARIA attributes, roles, or `tabindex` anywhere; focus indication relies solely on a border-color shift with `outline: none` (`style.css:84,140,147,642,648`).
- **[LOW] FOUC on load.** `#geminiFields` lacks a default `hidden` class (`index.html:80`) while `#ollamaFields` has one (`index.html:55`), though the default provider is `mock` — Gemini fields flash before `loadConfig()` corrects them.
- **[LOW] Gemini model dropdown lists unvalidated model IDs** (`index.html:83-110`) with no server-side check against what the API actually offers; a bad pick surfaces as a raw adapter exception.
- **[LOW] Stray `=2.8.0` file** at repo root — a pip artifact from an unquoted version specifier. Already gitignored by the `=*` rule; safe to delete.

---

## 6. Test coverage

**108 tests, all passing.** The tests that exist are genuinely good — real assertions on real behavior, no smoke-test padding. `tests/test_phase1_schemas.py` (539 lines) and `tests/test_phase2_agent.py` (283 lines) thoroughly cover schemas, the parser, and the validation loop state machine.

The problem is what has **zero** coverage:

| Module | Tests | Notes |
|---|---|---|
| `claims.py` | **none** | No test file exists. All regexes, hedge/causal matching, dedup untested. |
| `verification.py` | **none** | No test file. Does network I/O, numeric parsing, tolerance math — all untested. |
| `consistency.py` | **none** | No test file. Scoring, classification, divergence flag, halt handling untested. |
| `web/server.py` | **none** | No `TestClient` anywhere in the repo. |
| `web/auth.py` | **none** | No test asserts which routes require which scope. |
| `web/db.py` | **none** | The append-only triggers' actual `ABORT` behavior is never verified. |
| `adapters/*` | **none direct** | `mock_adapter` exercised indirectly; Gemini backoff/classification and Ollama error-sniffing untested. |

Two observations worth drawing out:

1. **The ADR-06 mitigation stack is the least-tested code in the repo.** `claims.py`, `verification.py`, and `consistency.py` are the three modules that constitute the project's answer to "the thought_log might be a rationalization" — and none has a single automated test. Several of the §3/§4 bugs (hedge substring matching, number-format divergence, the 300KB truncation) are exactly the kind a modest test suite catches immediately.
2. **No test would have caught any Critical finding in §2.** A handful of `TestClient` assertions of the form "GET this route without a token → expect 401" would have caught §2.2 and §2.3 the day they were introduced.

There's also no regression test for the §3.2 exception gap, and no integration test gluing `run_validation_loop` output into a `RunSession` (that wiring exists only inside `web/server.py`, which is untested).

---

## 7. Prioritized fix list

Ordered by severity weighted against effort. The first three are small, contained changes with disproportionate impact.

**1. Close the tiered-access bypass.** *(Critical — a few hours)*
   - Add a `investor_scope` parameter to `RunSession.to_dict()` (`schemas.py:305-316`) instead of the hardcoded `False`, and thread the caller's scope through.
   - Add `Depends(require_scope)` to all read routes (§2.2) and redact per scope at read time, not just at chat time.
   - Gate `DELETE /api/runs` behind auditor scope *and* an explicit dev-mode env flag.
   - Gate `POST /api/runs/{id}/replay` (it spends real API quota).

**2. Make auth mean something.** *(Critical — small)*
   - Require a shared admin secret (or any credential check) before `POST /api/auth/token` will issue `auditor` scope.
   - Add `ACCOUNTABILITY_SECRET` to `.env.example`, and fail loudly at startup if it's unset outside an explicit dev mode — the current silent fallback (`auth.py:49-50`) is the dangerous part, not the constant itself.

**3. Stop losing audit records on infrastructure failure.** *(High — small)*
   Wrap the adapter call in `run_validation_loop` with a broad `except Exception` that writes a `ReasoningObject` (new `parse_status`, e.g. `INFRA_FAILURE`) and re-raises via an exception carrying the objects, mirroring `HaltError`'s design (`middleware.py:32-41`). Add the regression test.

**4. Resolve the ADR-04 contradiction.** *(High — medium)*
   Either wire real `DataSource` records through for Gemini/Ollama so `_degrade_confidence` actually applies, or amend `context.md` §10 item 6 to state the penalty is currently mock-only. Right now the risk register describes a live risk that doesn't execute — fix the code or fix the claim, but they can't both stand.

**5. Fix replay fidelity.** *(High — small)*
   Persist `context` alongside `subject` in the run payload and replay with it (`server.py:525-526`). Use the stored post-degradation confidence rather than the config base. Simplify the directive-version lookup at `server.py:513-514`.

**6. Extract one shared number utility.** *(High — small)*
   Consolidate the three `_NUMBER_RE` copies into a single module exposing both the regex and `normalize()`, and use it in all three consumers. This alone fixes the `number_divergence_flag` false positives (§3.5).

**7. Make the consistency probe actually probe.** *(High — medium, design work)*
   As shipped it compares a deterministic function to itself. Options: perturb the seed on the probe run, raise temperature for the probe only, or use a different model as the second sampler. Whichever you pick, document what the score now means — and if you keep it deterministic, say plainly that it measures adapter determinism, not reasoning stability.

**8. Add the missing tests.** *(High — medium)*
   Priority order: a `TestClient` suite asserting auth per route (catches regressions of §2), then `claims.py`, `verification.py`, `consistency.py`, then a trigger test proving `UPDATE`/`DELETE` actually `ABORT`.

**9. Cheap UI wins.** *(Medium — small)*
   Surface `/replay` and `/api/runs/drift` in the UI — both backends already work, so this is pure frontend. Move the seed slider out of the Ollama-only panel. Give `refreshRuns`/`refreshSessions` a visible error state.

**10. Verification hardening.** *(Medium)*
   Raise `_MAX_BYTES` to match `financial_grader.py`'s 10MB, scope verification per-citation rather than pooling all numbers, add `\b` boundaries to hedge matching, and use a stronger dedup key than an 80-char prefix.

**11. Housekeeping.** *(Low)*
   Either populate or remove the dead schema fields (§5) — `citations`, `reasoning_steps`, `llm_tokens`, and the AAN pair currently make the schema look more capable than it is. Factor out the duplicated ticker extraction. Delete the stray `=2.8.0` file.

---

## 8. A note on the project's own thesis

The stated thesis is *"an unauditable conclusion is a system failure — no matter how accurate it is."* Applied reflexively, several findings above are the same class of problem the project exists to solve:

- SEC-01 is **documented** as a structural guarantee and **implemented** as a single call-site behavior (§2.1).
- The −0.1 confidence penalty is **documented** as a live uncalibrated risk affecting every run, and is **implemented** as unreachable code for every real provider (§3.1).
- The consistency probe is **documented** as detecting confabulation drift, and **implemented** as comparing a deterministic function to itself (§3.4).
- The TTL purge is **documented** as running on every write, and **implemented** as startup-only (§4).

The codebase is unusually honest in places — ADR-06's admission about thought_log limits, the adapter determinism caveats, the ADR-11 note about v1.0.0 being falsified by live Gemini output. That instinct is the project's strongest asset. The fix for the items above is the same instinct applied to the four claims listed here: make the code match the documentation, or make the documentation match the code.

---

*Audit performed by reading every source file in the repository and verifying claims against executed code paths. Every finding carries a `file:line` reference; the most surprising findings (§2.1, §2.2, §3.1, §3.2, §3.3) were independently re-verified against source after initial analysis.*
