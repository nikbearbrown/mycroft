---
title: The review app
slug: f-review-app
section: Features
order: 120
summary: The React app a reviewer uses — start runs, watch them live, read the figure matrix, checks, grades and sources, decide gate items, and export a review.
---

The review app is how a person works with the system. It holds no business rules: everything it
shows comes from the server, including what is withheld at investor scope. It is served at `/app`,
and `/` redirects there ([D-48](decisions.html#d-48)). Its code is documented file by file on
[Review app (frontend)](files-frontend.html).

## Pages

| Route | Page | What the reviewer does |
|---|---|---|
| `#/new` | New compare | Enter a ticker (or a subject), pick a pairing, start a run, watch both agents live. |
| `#/runs/{id}` | Run detail | Read the stored record: summary, figure matrix, checks, grades, sources, trace, gate, flags, export. |
| `#/chat` | Chat | Ask one agent a question and watch it work; hand over to the stored record. |
| `#/settings` | Settings | Temperature, seed, agent identity, starting confidence, the consistency probe. Read-only at investor scope. |
| `#/directive` | Directive | The active directive, in full, with its version. |
| `#/ledger` | Honest Ledger | Known issues, open first, in plain words. |
| (drawer) | History | Past runs, with outcome lines ("Mismatch · 1 of N figures", "Consensus A", "Grade AA"). |

The top bar shows the scope switch (auditor or investor), "Honest Ledger (N open)", the directive
version, and "Server unreachable" when it is. Below 1024 px wide the page links move into a Menu.

## The run record

- **Summary first**, with the accounting checklist before the details.
- **The figure matrix** ([[web/frontend/src/components/ComparisonMatrix.tsx]]): one row per metric,
  both agents' values and periods, the status in words, and a **Source** button that shows the
  figure in the filing itself or the search snippet the agent read
  ([[web/frontend/src/components/SourcePopover.tsx]]).
- **Grades** ([[web/frontend/src/components/Grades.tsx]], [[web/frontend/src/components/Assessment.tsx]]):
  each agent's grade, direction and assumptions, labelled as model judgments, and why they differ.
- **The decision gate** ([[web/frontend/src/components/DecisionGate.tsx]]): the open items, a form
  that mirrors the server's rules so a refusal isn't a surprise, a draft kept per run in
  `sessionStorage`, and the decision history.
- **The trace** ([[web/frontend/src/components/TraceLog.tsx]]) and "Technical details: the raw
  record".

## Accessibility and layout

- One polite `aria-live` announcer for the whole app, which survives the hand-over from a live run
  to its record.
- Withheld material is announced ("Pending human review"), not shown as empty boxes.
- **Phone layout.** Observed at 375 px on 2026-09-27: the Menu opened inside the viewport with no
  overflow (`logs/RUN_LOG.md`, "B6 + U9"). A later reading of the CSS suspects a rule that could
  hide page links below 768 px; see [[web/frontend/src/styles.css]].

## Tests

[Review app tests](files-frontend-tests.html): Vitest with jsdom, fixtures captured from real
server runs. `npm run verify` type-checks, tests and builds.
