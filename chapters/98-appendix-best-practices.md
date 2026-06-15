# Appendix: Best Practices for Agentic Book Repos

This appendix is the operating compact for the repo.

## Two Customers

Every operating artifact has two customers:

1. Agents that read skills, scripts, data contracts, and gate definitions.
2. Humans who must understand what agents do, why it is safe, and when to stop.

Skills and recipes are primarily for agents to execute. Each one should begin
with a human-readable executive summary.

## Verified Data First

Before external lookup or model inference, check local verified evidence:

- `data/`
- generated audits
- metadata
- source exports
- tracker files
- stored reports

If verified local data is missing, stale, or insufficient, say so before looking
elsewhere.

## Vetted Scripts First

Before writing new code, check:

1. `scripts/`
2. `scripts/README.md`
3. `package.json`

Use stored scripts when they fit. Create ad hoc scripts only when no suitable
stored script exists. Promote reusable ad hoc scripts into `scripts/` after
review.

## Phase Gates

Do not run a fully automated pipeline until these gates pass:

1. Problem gate
2. Local evidence gate
3. Stored script gate
4. Small-run gate
5. Verification gate
6. Review gate
7. Logging gate

![The seven phase gates in sequence — problem, local evidence, stored script, small-run, verification, review, and logging — each a checkpoint a fully automated pipeline must clear before it proceeds.](images/98-appendix-best-practices-fig-01.png)
*Figure 98.1 — The seven phase gates*

## Logging

Use `skills/RUN_LOG.md` for meaningful runs, blockers, generated artifacts, and
workflow changes. Do not log secrets or private user details.

---

## Prompts

### Figure 98.1 — The seven phase gates
**Files:** images/98-appendix-best-practices-fig-01.svg
**Prompt:** Seven sequential gate checkpoints — problem, local evidence, stored script, small-run, verification, review, logging — drawn as an ordered pipeline that a run must clear in order. Single-headed connectors, ink on white, one red accent on the gate a run is currently held at.
