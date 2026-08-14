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
