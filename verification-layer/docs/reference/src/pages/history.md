---
title: Earlier documents
slug: history
section: History
order: 10
summary: Older write-ups about this subsystem, what the archive holds, and where the full history is recorded.
---

This reference describes the system as it is. Earlier documents describe it as it was; they are
kept, not rewritten, and several no longer match the code (see
[Drift found while documenting](drift.html)).

## The run log

[[logs/RUN_LOG.md]] is the canonical history: every change, live run, gate and correction,
appended in order and never edited. The entry that documents it lists its major phases.

## Design documents in the repository

| Document | What it is | Current? |
|---|---|---|
| [[docs/SYSTEM_DESIGN.md]] | The system design: components, ADRs, data flow | Partly out of date: active directive, concept sets, concurrency |
| [[docs/DATA_CONTRACT.md]] | The data contract for inputs and records | Out of date in places |
| [[docs/index.html]] | An earlier index page for the documentation | Kept as it was; it predates this site and its styling |
| [[docs/video/archive/*]] | Scripts of two earlier explainer videos | Historical |

## Earlier walkthroughs (local only)

Three HTML write-ups sit in `docs/` on the author's machine. `.gitignore` excludes `docs/*.html`,
so they aren't in the repository and won't exist in a fresh clone. They are linked as they are,
unchanged, and describe the system at the time they were written.

- [Three mechanisms against silence](../accountability_layer_week1.html) (week 1)
- [Validation loop walkthrough](../validation_loop_walkthrough_week2.html) (week 2)
- [Inversion Audit Engine](../inversion_audit_engine_week3.html) (week 3)

## The archive

Files replaced by later work are moved to `archive/` with `git mv`, never deleted: the per-provider
adapters that LangChain replaced, and the classic UI that the review app replaced. See
[Archive](files-archive.html).
