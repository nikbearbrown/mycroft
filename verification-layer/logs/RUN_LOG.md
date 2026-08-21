# Run Log — Accountability Layer

Subsystem-local log. The repo-root `logs/RUN_LOG.md` remains the canonical Mycroft log;
this subsystem is self-contained and keeps its history here so its entries do not conflict
with the seven other authors who append to the shared file. Entries follow the same shape:
date, recipe, inputs, commands, outputs, result, open issues.

## 2026-08-14 -- Integrate accountability-layer into Mycroft (self-contained)

- **Recipe:** Repo integration (no data recipe run) — bring the standalone accountability-layer
  prototype into Mycroft without touching any file outside its own directory.
- **Inputs:** Standalone repo `divij-pawar/mycroft-accountability` at `fe45eb4` (34 tracked
  files, ~6,500 lines Python); its untracked `Report.md` technical audit.
- **Commands:** Copied the 34 tracked files to `accountability-layer/`. Brought the untracked
  audit in as `accountability-layer-audit.md` (SNICKERDOODLE `*-audit.md` convention). Applied
  the upstream working-tree `start-server.sh` shebang fix. Wrote `README.md`, this log, a
  subsystem-scoped `DATA_CONTRACT.md`, and a nested `.gitignore`. Ran the test suite in the new
  location and `node scripts/conformance.mjs accountability-layer` from the repo root.
- **Outputs:** `accountability-layer/` — 34 source files plus `README.md`,
  `accountability-layer-audit.md`, `DATA_CONTRACT.md`, `.gitignore`, and this log.
  **No file outside this directory was modified.**
- **Result:** 108/108 tests pass unchanged in the new location (stdlib `unittest`; LangFuse
  degrades gracefully without credentials, as documented). Conformance passes on the subsystem.
  Verified no secrets travelled: `.env`, `env/` (venv), `openclaw/`, `youtube/`, `context/`, and
  `web/data/*.db` were gitignored upstream and are gitignored here. Flat imports
  (`from parser import ...`, run from inside the directory) mean the hyphenated directory name
  breaks nothing today — but it also means no other project in the repo can import this package.
- **Open issues:**
  - [GATE OPEN] Four CRITICAL findings remain open in `accountability-layer-audit.md`: investor
    redaction bypassed at storage time; 14 of 16 API routes unauthenticated; unauthenticated
    `DELETE /api/runs` drops the audit tables; anyone can mint an `auditor` token. Localhost
    only — not deployable, and no recipe should claim `RUNNABLE-LIVE` on this layer until
    audit §7 is addressed.
  - Not registered in the shared `recipes/` or `conductor/` surface, and not in
    `scripts/conformance.mjs` `DEFAULT_PATHS` — deliberate, to keep the merge surface at zero
    files outside this directory. Consequence: **CI does not conformance-check this Python.**
    Run it manually (see `README.md`).
  - The subtree link to the standalone repo was lost when the merge commit was reset; this is
    now a plain copy. Syncing with `divij-pawar/mycroft-accountability` is manual.
  - Nothing from the run store has been promoted to `data/verified/`, and no run has been
    attested. `financial_grader.py` remains unwired to the web app.

## 2026-08-21 -- Rename accountability-layer/ to verification-layer/

- **Recipe:** Repo maintenance (no data recipe run) — rename the subsystem folder ahead of
  adding a second component, Cross-Agent Validation, on top of the same evidence store (see
  this session's `sdd.md`). Decision made with the user: `git mv accountability-layer
  verification-layer` rather than a new sibling folder, because every module here uses flat,
  same-directory imports (`from consistency import ...`, `from schemas import ...`) that only
  resolve when co-located — a sibling folder would have forced either packaging work or
  duplicating logic instead of reusing it.
- **Commands:** `git mv accountability-layer verification-layer` (git recorded all 38 files as
  clean renames, confirming content was untouched). Updated this folder's own self-descriptive
  docs to the new name/path: `README.md` (title, install/run commands, conformance command),
  `DATA_CONTRACT.md` (title), `.gitignore` (comment). Ran the test suite from the new location
  and compiled every tracked `.py` file directly (bypassing `scripts/conformance.mjs` — see open
  issues below).
- **Outputs:** Renamed directory tree; edited `README.md`, `DATA_CONTRACT.md`, `.gitignore`; this
  entry.
- **Result:** 108/108 tests pass unchanged from `verification-layer/`. All 23 tracked `.py` files
  compile cleanly (`python -m py_compile`, run directly per-file). Content of every renamed file
  is byte-identical to before the rename — this was a path change only.
- **Deliberately left unchanged, and why:**
  - `accountability-layer-audit.md` — its filename and content stay as-is. It is a dated
    technical audit of a specific commit (`fe45eb4`) of a component that was, at the time,
    genuinely called "the accountability layer." Rewriting it to match the new folder name would
    misrepresent what was true when it was written.
  - The prior log entry above (2026-08-14) is untouched for the same reason — P7 treats the
    record as append-only; this entry documents what changed, rather than editing history to
    pretend the folder was always called `verification-layer`.
  - No internal Python docstring, module header, or the FastAPI app's title string (e.g.
    `schemas.py`'s "Accountability Layer — Phase 1", `web/server.py`'s app title) was changed.
    The rename was scoped to the folder and to documentation that describes the folder's current
    state, not to the vendored source's internal terminology or its ADR/SEC/C-0X reference
    numbering, which stays internally consistent as originally authored.
  - The git branch (`feature/accountability-layer`, already pushed to `origin`) and the
    `accountability` remote (pointing at `divij-pawar/mycroft-accountability`) were left
    untouched. Renaming a pushed branch means deleting the remote ref, which is a shared-state
    change; that decision is left to the user, not made here.
- **Open issues:**
  - [BUG, confirmed] `scripts/conformance.mjs`'s `SKIP` set does not exclude `env/`. A local
    virtualenv left in this directory (`env/`, gitignored, ~143 MB, 3,086 `.py` files at time of
    discovery) makes `node scripts/conformance.mjs verification-layer` walk into
    site-packages and shell out to `py_compile` once per file — a multi-minute hang, not the
    "extra scan time" the README previously called it. README corrected to describe this
    accurately. Not fixed here: fixing `SKIP` is a change to a shared root script, out of scope
    for a self-contained subsystem to make unilaterally.
  - Verification of the rename therefore did not use `scripts/conformance.mjs` directly; it used
    a direct `py_compile` sweep of the tracked file list instead (see Commands/Result above).
  - The four CRITICAL findings in `accountability-layer-audit.md` remain open and are unaffected
    by this rename.

## 2026-08-21 -- Resolve duplicate subsystem paths after an upstream merge

- **Recipe:** Repo repair. Merge commit `f2855ca` (made outside this session) merged the remote
  `feature/accountability-layer` — which still carried the pre-rename path — into the local
  branch. Git did not recognise the incoming files as the source of the earlier rename, so HEAD
  ended up tracking the entire subsystem twice: `accountability-layer/` (38 files) and
  `verification-layer/` (35 files).
- **Diagnosis before acting:** 31 of the shared files were byte-identical across both paths. The
  4 that differed (`README.md`, `DATA_CONTRACT.md`, `.gitignore`, `logs/RUN_LOG.md`) were exactly
  the files edited during the rename, so `verification-layer/` held the current versions and
  `accountability-layer/` held the pre-rename originals. Three `docs/*.html` files were tracked
  only under the old path; `git check-ignore` confirmed they are now covered by a deliberate
  `/docs` rule in `verification-layer/.gitignore` (added outside this session, alongside
  `/divij`), so dropping them from tracking loses nothing on disk.
- **Commands:** `git rm -r accountability-layer` after confirming every file existed on disk under
  `verification-layer/`. Re-ran the test suite and confirmed `divij/` (7 files) and `docs/`
  (3 files) remain present on disk, gitignored.
- **Result:** one tracked subsystem path. 129/129 tests pass. `accountability-layer/` no longer
  exists in tracking or on disk; all content lives under `verification-layer/`.
- **Open issues:**
  - The remote branch `origin/feature/accountability-layer` still carries the old path. Pushing
    this resolution will re-delete it there; anyone who pulled the intermediate state will see the
    rename land as a delete-plus-add rather than a detected rename. The branch name itself is
    still `feature/accountability-layer`, unchanged — renaming a pushed branch is shared-state
    surgery and was left as the user's decision.

## 2026-08-21 -- Implement Cross-Agent Validation v1 (SDD v1)

- **Recipe:** Build the Cross-Agent Validation component specified in `divij/sdd.md`, integrated
  with the existing accountability store. Implements the orchestration-layer component of the
  published Mycroft architecture that previously had no implementation anywhere in the project.
- **Inputs:** `divij/sdd.md` (design), `divij/cross-agent-validation-proposal.md` (scope);
  existing unmodified modules `consistency.py`, `middleware.py`, `schemas.py`, `parser.py`,
  `financial_grader.py`, `web/db.py`.
- **Outputs (3 new files, no existing module changed):**
  - `cross_validation.py` — `ComparisonStatus`, `CrossAgentComparisonResult`,
    `run_cross_agent_validation`, plus `build_run_payload` / `persist_cross_agent_run` for the
    store integration.
  - `adapters/fixture_adapter.py` — `make_fixture_adapter`, a deterministic stand-in agent with a
    caller-chosen conclusion. Satisfies the same `(subject, context, directive) -> AgentResponse`
    contract as the other three adapters and routes through the real parser.
  - `tests/test_cross_validation.py` — 21 tests.
- **Result:** 129/129 tests pass (108 pre-existing + 21 new). Conformance passes on all three new
  files. The comparison correctly classifies the SDD §10 fixture matrix: matching numbers with
  different wording = no contradiction; differing values = flagged with both numbers reported;
  a number present in one conclusion and absent from the other = flagged (same
  symmetric-difference rule, no special-casing). End-to-end test builds Producer A's context from
  the real EDGAR helpers with an injected fetch, persists through `insert_run`/`insert_session`,
  and reads the comparison back via `get_run(run_id)["cross_agent_comparison"]`.
- **Verified by mutation testing, not just green checkmarks:** replacing
  `symmetric_difference` with `intersection` broke 7 tests; returning `False` instead of `None`
  for `contradiction_flag` on a halt broke 3. File restored byte-identical afterwards and the
  suite reconfirmed. The tests genuinely fail on broken logic.
- **No side effects on real state:** the e2e tests patch `web.db.DB_PATH` to a temp file, so
  `web/data/accountability.db` was never written to (confirmed: mtime unchanged).
- **Implementation notes beyond the SDD (all additive, all documented in the code):**
  - `run_cross_agent_validation` gained keyword-only `confidence_score`, `data_sources_a`,
    `data_sources_b`, passed straight through to `run_validation_loop` so real per-agent
    provenance can be recorded. Defaults match `run_validation_loop`'s own.
  - `build_run_payload` was split out of `persist_cross_agent_run` so a caller can inspect or
    amend the payload before writing. SDD §7.2 showed this as inline caller code; making it a
    function means the integration is real code rather than test-only.
  - Producer A composes via `financial_grader`'s `lookup_cik` / `fetch_company_facts` /
    `summarize_facts` to build the context, not via `analyze_ticker`. `analyze_ticker` runs its
    own validation loop internally, so its signature cannot serve as a `call_agent_fn`. This
    matches the SDD §4 diagram ("financial_grader-based" adapter) rather than deviating from it.
  - `fixture_adapter` rejects empty text or embedded XML block tags at construction time, since
    either would break the two-block structural contract it exists to satisfy.
- **Open issues:**
  - [DESIGN GAP, deliberate] Only `HaltError` is caught per agent. Any other adapter exception
    (rate limit, EDGAR fetch failure) propagates and aborts the comparison, discarding the other
    agent's already-collected records. `ComparisonStatus` has no `ERROR` state in v1 — adding one
    is a design decision, not something to improvise during implementation. Documented in the
    module docstring.
  - [SCOPE] Comparison is numeric only. Two conclusions that disagree in substance while citing
    the same figures will not be flagged. This detects number mismatches, not reasoning mismatches.
  - [SCOPE] Producer B remains a fixture. No real second agent exists yet, so no genuine
    cross-agent disagreement has been observed on live data — only on fixtures with known answers.
  - [SCOPE, per SDD §7.3] `cross_agent_comparison` lives inside the payload JSON blob, so it is
    retrievable by `run_id` but not queryable in SQL. "Every contradiction this month" needs a
    Python-side scan or SQLite's JSON1 extension.
  - The four CRITICAL findings in `accountability-layer-audit.md` remain open. v1 adds no HTTP
    route, so none of them are newly reachable by this component.
