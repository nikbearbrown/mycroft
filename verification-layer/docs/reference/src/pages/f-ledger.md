---
title: Self-checks and the Honest Ledger
slug: f-ledger
section: Features
order: 110
summary: The checks a single answer gets (claims, citation verification, a consistency probe), tracing, and the system's own list of what is known not to work.
---

## Claims and citation verification

For a chat run, and for each agent in a compare, the answer's text is turned into typed claims
and its citations are checked in code the agent doesn't control:

- [[validation/claims.py]] extracts citations (`[SOURCE: label, url]`), quantitative statements,
  hedges and causal claims.
- [[validation/verification.py]] fetches each cited URL and checks whether the answer's figures
  appear there, giving a `verification_rate`. It is the one network call in `validation/`.
- In a compare, each agent's claims are checked against its own citations only.

This step exists because a fabricated debt-to-equity figure (AAPL, 0.34) was once caught only by
a person reading the raw thought log ([fabrication-not-caught](ledger.html#fabrication-not-caught)).

## The consistency probe

A chat run can ask the same question a second time and score how far the answers drift
([[validation/consistency.py]], ADR-06). It is on by default for every non-Gemini model, because
the Ollama determinism claim is documented as unreliable
([ollama-determinism](ledger.html#ollama-determinism)). The probe's result is metadata on the run
([D-45](decisions.html#d-45)). Its call is traced as if it were a retry
([consistency-probe-shown-as-retry](ledger.html#consistency-probe-shown-as-retry)).

## Tracing

[[pipeline/observability.py]] wraps producer runs in LangFuse traces when a self-hosted LangFuse
is configured, and does nothing otherwise. The `langfuse` package must still be installed. The
web routes use the step trace, not LangFuse ([Live runs](f-live.html)).

## The Honest Ledger

The system keeps its own list of known problems in code: `KNOWN_ISSUES` in
[[web/self_report.py]], served at `GET /api/self-report` and shown in the review app
([D-46](decisions.html#d-46)).

- Each entry has an id, severity, area, title, detail, status and source. The statuses are
  `OPEN`, `UNVERIFIED`, `RESOLVED` and `BY_DESIGN`.
- **Append-only in spirit.** A fixed problem is marked `RESOLVED` with how and when; the entry is
  not deleted.
- **Test counts are discovered, not stated.** The report runs test discovery on each request
  rather than hard-coding a number.
- The full current list is generated into this site: [Honest Ledger](ledger.html).
