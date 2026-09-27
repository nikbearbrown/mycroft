---
title: The decision gate and scope
slug: f-gate
section: Features
order: 70
summary: Mismatched figures, failed hard checks and differing grades stop a run until a named reviewer decides each one; investor-scope reads withhold the disputed material until then.
---

The gate is where the machine stops and a person decides. It turns a compare run's two-sided
conflicts into *decision items*, accepts decisions only in a form that can be checked, stores
them append-only, and controls what an investor-scope reader sees while any item is open. It
lives in [[validation/gate.py]] and follows the constitution's rule that "a phase gate requires a
specific, testable handoff condition, cleared by a named human, logged with who/what/when".

## What opens the gate

Gate policy **v3** (`GATE_POLICY`), stamped on each new compare run. A run stored before the gate
existed is never gated retroactively ([D-38](decisions.html#d-38)).

| Kind | Opened by | Since |
|---|---|---|
| `figure` | a `MISMATCH` row ([comparison](f-compare.html)) | v1, 2026-09-25 |
| `check` | a failed hard check on an agent's figures ([checks](f-checks.html)) | v2, 2026-09-25 |
| `grade` | both agents graded and they differ ([synthesis](f-grades.html)) | v3, 2026-09-26 |

Only real two-sided conflicts gate. `UNCORROBORATED` rows, heuristics and checks on the filing are
shown, never gated.

## Decisions

A decision names a reviewer, cites one or more items, gives a decision and a rationale.

| Decision | `figure` | `check` | `grade` |
|---|---|---|---|
| `accept_a` / `accept_b` | yes | | yes (that agent's grade becomes the final grade) |
| `both_wrong` | yes | | |
| `not_a_conflict` | yes | yes | |
| `override_value` | yes | yes | |
| `confirmed_error` | | yes | |
| `set_grade` | | | yes, with a grade |

A decision is **refused, never repaired** ([D-39](decisions.html#d-39)): it's refused if the name
is under 2 characters or the rationale under 20, if an item isn't in this run, if the decision
doesn't fit every cited kind, or if a grade or value is missing or misplaced. The refusal reason
is returned in words (422).

- **Stored append-only.** Each decision is a row in `gate_decisions` ([[web/db.py]]); SQLite
  triggers refuse updates and deletes ([D-42](decisions.html#d-42)).
- **The latest decision on an item wins.** Earlier ones are marked superseded and stay in the
  history.
- **Status**: `NOT_GATED`, `NO_DECISION_NEEDED`, `AWAITING_DECISION`, or `DECIDED` once every
  item has a decision.
- **No AI decides.** The sessions that built the gate recorded no decision on a live gated run:
  that is exactly what the rule forbids.

## Scope

Every run is read at a scope, **auditor** or **investor**, from a JWT minted by
`POST /api/auth/token` ([[web/auth.py]]). A read with no token is served at the run's stored scope.

**An investor never sees** the internal tier (thought logs, raw model output, token counts,
directive text, context windows, assessments), the synthesis beyond the kind of disagreement,
or the agents' grades. The only grade an investor ever sees is one a human recorded.

**While the gate is `AWAITING_DECISION`, an investor also doesn't see** the agents' conclusions,
the disputed values (status and period stay), the arithmetic of pending checks, the claims, or
the text of search results in the trace (queries and URLs stay). A note says why
([D-40](decisions.html#d-40), [D-44](decisions.html#d-44)).

The same withholding applies to the live stream: an investor's compare stream carries no search
text and no conclusions, because whether the run will be gated isn't known until both agents
finish.

## Tested and observed

- **Tested** in [[tests/test_gate.py]], [[tests/test_trace_withholding.py]] and
  [[tests/test_synthesis.py]].
- **Observed**: the investor read of a gated run was found carrying a disputed value inside a
  search result on 2026-09-26, fixed the same day and verified on a restarted server
  ([trace-leaks-disputed-values](ledger.html#trace-leaks-disputed-values), resolved).
- **Pending, as of 2026-09-27**: two live gated runs were awaiting a human decision (`ec1a3b44`
  and `8ecb0922`). No AI records one.

## Limits

- **The decider's identity is self-declared**: a typed name, and anyone can mint an auditor token
  ([gate-identity-self-declared](ledger.html#gate-identity-self-declared)).
- **Withholding is only as strong as read authentication**: token-less reads are served at the
  stored scope, and several routes are unauthenticated ([audit-criticals](ledger.html#audit-criticals)).
- A decision citing the grade together with a figure can clear the grade item without recording a
  grade; see [[validation/gate.py]].
