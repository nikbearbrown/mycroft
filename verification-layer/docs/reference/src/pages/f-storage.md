---
title: The record store
slug: f-storage
section: Features
order: 100
summary: One SQLite file holds every run, session, reviewer flag and gate decision; runs and decisions are append-only, enforced by the database itself.
---

The record is the evidence. [[web/db.py]] keeps it in one SQLite file, `web/data/accountability.db`
(gitignored), with the database engine, not just the application, refusing to change history.

## Tables

| Table | One row per | Append-only |
|---|---|---|
| `runs` | run, chat or compare; the whole payload as one JSON blob, with a few fields copied into indexed columns | yes, by triggers |
| `sessions` | the serialised `RunSession` of a run | no (`INSERT OR REPLACE`) |
| `reviewer_flags` | a reviewer's flag on a run (`Hallucinated`, `Incorrect`, `Other`) | no, but nothing updates one |
| `gate_decisions` | a human decision on a gated run | yes, by triggers |

- **Triggers, not conventions.** `runs_no_update`, `runs_no_delete` and the two
  `gate_decisions` triggers abort any `UPDATE` or `DELETE` ([D-42](decisions.html#d-42)).
- **New fields go in the payload.** A feature adds keys inside `payload_json` rather than new
  columns, so old rows still read and nothing needs migrating ([D-43](decisions.html#d-43)).
- **One migration so far.** When `gate_decisions` gained decision values (`confirmed_error`,
  `set_grade`) and the `final_grade` column, the table is rebuilt once at startup with every row
  copied (`_migrate_gate_decisions`).
- **Retention.** Runs older than 90 days are purged at startup; the purge lifts the triggers for
  the duration. The docstring's "and on every write" is not what the code does (noted in
  [[web/db.py]]).

## The ticker column

It is only a ticker for ticker-mode compares. For a chat run or a subject compare it is the first
word of the message, so a question beginning "What year" is stored under `WHAT`.

## Clearing everything

`DELETE /api/runs` drops and recreates every table, decisions included. It is unauthenticated
([audit-criticals](ledger.html#audit-criticals)), and the review app deliberately has no button
for it ([D-49](decisions.html#d-49),
[clear-all-runs-not-in-ui](ledger.html#clear-all-runs-not-in-ui)).
