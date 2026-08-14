# Data Contract — Accountability Layer

Scoped to this subsystem. The repo-root `DATA_CONTRACT.md` governs Mycroft's shared
`data/raw/` → `data/verified/` layers; this file covers only the run store, which is
machine-local and never enters either.

## Run store

| Dataset | Source | Location | Verified location | Gate | Owner |
|---|---|---|---|---|---|
| `runs` / `sessions` / `flags` | Live agent attempts through `middleware.run_validation_loop` — one `ReasoningObject` per attempt | `web/data/*.db` (SQLite, **machine-local, gitignored**) | none — nothing from this store has been promoted to the repo's `data/verified/` | **Structural parse gate** (machine, enforced): a response failing `parser._parse_response` twice raises `HaltError` and is recorded as `HALT`, never passed through. **Attestation gate** (human, not yet defined): no run here has been attested | Unassigned |

## Rules

- The store is **append-only by construction** — `UPDATE`/`DELETE` on `runs` raise `ABORT`
  via SQLite triggers (`web/db.py`). It is *not* tamper-evident in the stronger sense: an
  unauthenticated `DELETE /api/runs` still drops the tables (finding 2.3 of
  `accountability-layer-audit.md`).
- Run records may contain full raw LLM output (`thought_log`, `raw_output`). Treat the DB
  as sensitive; it is gitignored and must stay that way.
- Reproduction is by **replay** (`POST /api/runs/{id}/replay`), not by committing the DB.
  Replay currently drops `context` (audit §3).
- Never invent counts, rates, or confidence. Model judgments are labeled as judgments.
- No secrets in tracked files. Credentials live in `.env`, which is gitignored at both
  this level and the repo root.
