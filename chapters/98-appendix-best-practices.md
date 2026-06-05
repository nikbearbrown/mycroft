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

## Logging

Use `skills/RUN_LOG.md` for meaningful runs, blockers, generated artifacts, and
workflow changes. Do not log secrets or private user details.
