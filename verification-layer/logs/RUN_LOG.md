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
