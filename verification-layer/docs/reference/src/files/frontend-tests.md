---
title: Review app tests
slug: files-frontend-tests
section: Files
order: 110
summary: The Vitest suite for the React review app, and the real run records it replays.
---

The review app's tests live in `web/frontend/tests/`. They render components and views from
`web/frontend/src/` into a simulated browser and check what a reviewer would see and what the
app would send to the server. They never start the Python server and never call a model: every
network call is a stubbed `fetch`, and every run the app displays comes from a fixture file.

## How to run

From `web/frontend/`, `npm run verify` runs three steps in order, as defined in
`package.json`:

1. `tsc --noEmit`: the TypeScript typecheck, over the app and the tests.
2. `vitest run`: the test suite, once (no watch mode).
3. `vite build`: the production build into `dist/`.

`npm test` runs only the second step and `npm run typecheck` only the first. The
`logs/RUN_LOG.md` U1 entry (2026-09-24) records why `npm run verify` is the machine check for
TypeScript: `scripts/conformance.mjs` silently skips `.ts` and `.tsx` files.

## Environment

The `test` block in `web/frontend/vite.config.ts` sets:

- `environment: "jsdom"`: each test file runs against jsdom, a JavaScript implementation of the
  browser DOM, so components can be rendered and queried without a real browser.
- `setupFiles: ["./tests/setup.ts"]`: adds the DOM matchers and unmounts after every test (see
  [[web/frontend/tests/setup.ts]]).
- `include: ["tests/**/*.test.{ts,tsx}"]`: only files under `tests/` ending in `.test.ts` or
  `.test.tsx` are collected.

Tests use Testing Library (`render`, `screen`, `within`, `fireEvent`, `waitFor`, `renderHook`)
and query mostly by accessible role and name ("button", "Review and record decision"), so an
assertion that passes also says the control is reachable by a screen reader. The pinned
versions are in `package.json` and `package-lock.json`.

## How the network is stubbed

No test file installs a shared mock. Each test that needs the server replaces the global
`fetch` with `vi.stubGlobal("fetch", vi.fn(...))`, routing on the requested URL, and restores it
with `vi.restoreAllMocks()` in an `afterEach` or `beforeEach`. Common patterns:

- **The token call.** Any call through [[web/frontend/src/api/client.ts]] first requests
  `/api/auth/token`; stubs answer it with a fake `access_token`, and some tests assert the next
  call carries `Authorization: Bearer <token>`. Tests call `_resetTokens()` from the client
  first, so a token cached by an earlier test doesn't hide the call.
- **Streams.** A streamed response is a `ReadableStream<Uint8Array>` built in the test, fed
  either the captured stream fixture in chunks or a few hand-written SSE (server-sent events)
  lines. Chunked delivery is deliberate: a network doesn't deliver an event in one piece.
- **Browser APIs.** `sessionStorage` is cleared before the gate and grade tests (the decision
  form saves drafts there). `URL.createObjectURL` is stubbed for the download test, and
  `requestAnimationFrame` is stubbed to never fire in one live-run test.

## Real fixtures

The run records in `tests/fixtures/` are captured from the real server, not written by hand:
stored runs read back through `GET /api/runs/{id}`, one real filing-excerpt response, one real
search snippet, and one real `/api/compare/stream` response. Each test file that uses them
says so in a header comment, and the `logs/RUN_LOG.md` entry that added each one records it
(see the fixtures table below). The point, stated in the header of
[[web/frontend/tests/gate.test.tsx]], is that "what the investor view withholds is what the
server actually withheld, not a hand-made imitation of it". Where a test needs a case no real
run produced (a failed hard check, a superseded decision, a consensus grade), it builds that
case from a real fixture with a spread override or as a small literal object in the test, and
the test reads as such.

[[web/frontend/tests/contract.test.ts]] is the guard on this arrangement: the TypeScript types
in [[web/frontend/src/api/types.ts]] are hand-mirrored from the Python payloads, and the
contract test fails if a real stored record stops having the keys the renderers rely on.

## Line endings

`verification-layer/.gitattributes` marks `web/frontend/tests/fixtures/**` (and the Python
suite's `tests/fixtures/**`) as `-text`, so Git checks fixtures out byte-exact. The
`logs/RUN_LOG.md` entry "2026-09-27 -- Committing the work since c53746a, and a checkout-only
test failure" records why: on a clean checkout with `core.autocrlf=true`, the SSE fixture
`stream_compare_aapl_2026-09-24.txt` came out with CRLF line endings, and `npm run verify`
failed one test in [[web/frontend/tests/live.test.tsx]] ("delivers the same events however the
bytes are split"). The working tree had passed only because its copy was never re-checked-out.
After the fix, a fresh checkout was LF and the suite passed.

## `web/frontend/tests/setup.ts`

**Role:** the Vitest setup file, run before every test file.

It imports `@testing-library/jest-dom/vitest`, which adds DOM matchers such as
`toBeInTheDocument`, `toHaveTextContent`, `toBeDisabled` and `toHaveFocus` to `expect`. It
registers `afterEach(() => cleanup())`, which unmounts everything rendered in a test, so one
test's DOM can't satisfy another test's query.

Related: [[web/frontend/tests/raw.d.ts]]

## `web/frontend/tests/raw.d.ts`

**Role:** a type declaration that lets tests import a fixture file's text with Vite's `?raw`
suffix.

It declares any module ending in `?raw` as having a default export of type `string`. Its own
comment gives the reason: `vite/client` (which normally supplies this declaration) isn't in
`tsconfig.json`'s types. Without it, `tsc --noEmit` would reject the stream fixture import in
[[web/frontend/tests/live.test.tsx]]. It was added with the live-run tests (RUN_LOG,
2026-09-25, "BP + U4").

## `web/frontend/tests/contract.test.ts`

**Role:** checks that real stored runs match the shape the renderers assume.

Its header comment states the purpose: `src/api/types.ts` is hand-mirrored from the Python
payloads, so "if the backend's shape drifts, this fails before a renderer silently breaks".

What it locks in:

- **Every stored run** (both chat fixtures, the legacy compare run, and both reads of the gated
  run, via `describe.each`) has a string `run_id`, a boolean `halted`, and a
  `reasoning_objects` array whose items each have a known `parse_status` (`SUCCESS`,
  `PARSE_FAILURE` or `HALT`), a numeric `attempt_number` and a string `agent_id`.
- **Run kinds.** `isCompareRun` tells the compare fixture from the chat fixture; a compare
  run's comparison is `COMPARED` and carries both agents' conclusions.
- **SEC-01** (the rule that investor-scope reads omit the internal tier): in the investor chat
  run, reasoning objects have no `thought_log` or `raw_output` key at all. The test checks
  absence of the key, not a null value.
- **The decision gate.** Both gated reads carry a `gate` whose status is one of the four known
  values, with `items`, `pending` and `decisions` arrays and an `identity_note` saying the
  reviewer is not authenticated. The legacy compare run has no `gate_policy`, so a run stored
  before the gate existed is never gated retroactively.

No network stubbing: it only reads fixtures.

Related: [[web/frontend/src/api/types.ts]], [[validation/gate.py]]

## `web/frontend/tests/format.test.ts`

**Role:** unit tests for the display formatters in [[web/frontend/src/lib/format.ts]].

Pure function tests, no rendering and no fixtures:

- **`formatFigure`** scales dollar amounts to billions and millions with two decimals (including
  a negative amount, rendered with the minus before the dollar sign), renders `USD/shares` as a
  per-share value, and formats a unitless number with thousands separators. A missing value
  (`null`, `NaN`) renders as an em dash, never as a number.
- **`formatPeriodChip`** builds the filer's fiscal label from fiscal year, fiscal period and
  form (a quarter and a full year), and returns an empty string for no data.
- **`formatDuration`** switches between seconds and milliseconds and returns an empty string for
  `null`.
- **`formatClock`** returns a placeholder for an unparseable or missing timestamp, and keeps the
  milliseconds of a valid one. The hour is matched by pattern, not value, because it depends on
  the machine's time zone.
- **`shortId`** truncates a run id with an ellipsis.

Related: [[web/frontend/src/lib/format.ts]]

## `web/frontend/tests/components.test.tsx`

**Role:** tests for the shared UI primitives, the verification banner and the run trace.

What it locks in:

- **Status vocabulary.** A `StatusBadge` carries a text label and a glyph as well as its color
  class, so status is never conveyed by color alone. `RolePill` names the author (user, agent,
  verification layer). `Info` is a disclosure button with `aria-expanded` that reveals a note
  naming the technical term.
- **Markdown safety.** Model text containing an `<img onerror=...>` renders no `<img>` element,
  while ordinary Markdown bold still renders. This is the deliberate-break case for the
  `Markdown` primitive's raw-HTML handling.
- **`VerificationBanner`** says plainly that nothing was fetched or checked when there are no
  claims, and keeps the three outcomes distinct: couldn't check (`verified: null`), not found in
  source (`false`) and matches source (`true`).
- **`TraceLog`**, using the real steps from the auditor chat fixture: collapsed by default but
  always showing the latest step; steps listed in `seq` order even when passed reversed; a line
  expands to its detail; a tool step shows its query, a "Retried" marker, and its result URLs
  as hosts, with a string that isn't a URL shown as-is; the lane filter narrows the list; and
  `hostOf` never throws on a malformed URL.

No network stubbing.

Related: [[web/frontend/src/components/primitives.tsx]],
[[web/frontend/src/components/TraceLog.tsx]], [[web/frontend/src/components/RecordSections.tsx]]

## `web/frontend/tests/views.test.tsx`

**Role:** parity tests for the run detail view and the history panel, the first views moved
from the classic UI (roadmap U1).

What it locks in:

- **`RunDetailView`**:
  - a chat run shows its subject as the page heading, the conclusion, the source-verification
    result, the reasoning, what the agent was sent, and the run trace;
  - at investor scope, it first asserts the fixture really is redacted (no `thought_log` key),
    then that withheld reasoning and prompts are announced with a notice rather than shown;
  - the legacy compare run, which has only seven top-level keys, still renders both agent lanes
    and the comparison, and labels its prompts as two agents' prompts, not two attempts of one
    agent;
  - the reviewer flag form is offered at auditor scope and not at investor scope.
- **`HistoryPanel`**:
  - lists runs and reports the selected run id;
  - behaves as a WAI-ARIA tablist: arrow keys move both selection and focus between tabs;
  - a run card gives the same reading as the run's own headline (the stored MSFT B1 run shows
    "Needs review", and no "Mismatch" card, since nothing actually mismatched);
  - an empty Flagged tab says so in plain words.

The history tests stub `fetch` by URL: `/api/runs` returns fixtures, `/api/sessions` a single
literal session, `/api/runs/contradictions` and anything else an empty list.

Related: [[web/frontend/src/views/RunDetail.tsx]], [[web/frontend/src/views/HistoryPanel.tsx]]

## `web/frontend/tests/matrix.test.tsx`

**Role:** tests for the figure-by-figure comparison matrix and the summary headline built from
it (roadmap B1 and U2).

The `ComparisonMatrix` cases use a small set of synthetic rows built by a `row()` helper (a
mismatch, a derived figure that doesn't add up, a match, and a figure only one agent had):

- the difference cell and its verdict sit between the two agents' values, with `data-label`
  attributes for the phone layout, and a mismatch badge uses the danger class;
- a value is formatted for reading, and the agent's own wording is kept in the tooltip;
- a derived figure that doesn't add up shows the recomputation in its row;
- figures only one agent was given are folded into a closed group, so they never read as a
  disagreement;
- the Conflicts filter keeps only the rows that need attention;
- an empty matrix says there is nothing to compare.

The `ComparisonSummary` cases use the real stored B1 run (MSFT):

- its headline names the reason for review (figures cited by only one agent, with nothing to
  back them), and the recorded verdict is shown with the rule that produced it;
- when the recorded verdict and the figure check disagree (an override that sets the
  concept-aware rule's flag on a run whose rows find no conflict), both are shown and a note
  names the gap;
- the disagreement headline counts only real mismatches, and names a derived figure that
  doesn't add up separately;
- a shared figure that couldn't be compared (an unverifiable period) counts as neither
  agreement nor conflict;
- a run stored before B1 (the legacy compare fixture) falls back to the old comparison and says
  so.

No network stubbing.

Related: [[web/frontend/src/components/ComparisonMatrix.tsx]],
[[web/frontend/src/components/RecordSections.tsx]], [[validation/facts.py]]

## `web/frontend/tests/gate.test.tsx`

**Role:** tests for the human decision gate in the UI (roadmap BG and U3), from the real gated
run.

Both fixtures are the same live run (`ec1a3b44`, 2026-09-25): llama3.2 said the first Pokémon
game reached North America in 1998, qwen2.5 said 1996, and the gate is awaiting a decision.

What it locks in:

- **Awaiting a decision.** The gate sits under the verdict, names the disputed figure, and
  expands inline with no dialog, leaving the matrix on screen beside the form. A year gap reads
  in years, not as a percentage variance. The disputed item is pre-checked and shows agent A's
  value.
- **Form rules.** Submit stays disabled until a decision, a rationale of the minimum length and
  a name are given; a too-short rationale shows a character counter; choosing "Set the correct
  value" disables submit again until a value is entered. The test title says these are the
  rules the server enforces.
- **Posting.** With a stubbed `fetch`, the test asserts the decision is posted to
  `/api/runs/{id}/decisions` with the auditor's Bearer token and exactly the body the reviewer
  chose, that `onDecided` receives the server's new gate, and that the saved draft is removed
  from `sessionStorage`.
- **Refusal.** A 422 from the server is shown in an alert with the server's own reason.
- **Drafts.** A half-written decision survives unmounting and remounting (navigating away and
  back); the button says a draft is saved, and the name field is restored.
- **Investor scope while pending.** Both conclusions and both values of the disputed figure are
  announced as withheld, no decision form is offered, and the rendered page contains neither
  1996 nor 1998 anywhere.
- **Decided.** Built from the real gate with two literal decisions, one superseded: the gate
  collapses to the decision in effect, keeps the superseded one below, and offers a new
  decision.
- **History.** A gated run is marked in its card, listed under the Decide tab, and counted to
  `onNeedsDecision`.

Related: [[web/frontend/src/components/DecisionGate.tsx]],
[[web/frontend/src/views/RunDetail.tsx]], [[web/frontend/src/views/HistoryPanel.tsx]],
[[validation/gate.py]]

### Limits and open issues

- The investor-scope check scans the rendered page text. The 2026-09-26 correction entry in
  `logs/RUN_LOG.md` records that the original investor fixture did carry "1998" once, in a
  search result inside the run trace, which an earlier text check had missed; the fixture was
  regenerated after the trace fix. The server-side guarantee is tested in the Python suite
  (`tests/test_trace_withholding.py`, per that entry), not here.

## `web/frontend/tests/checks.test.tsx`

**Role:** tests for shared figures (B2), the accounting checks (B3) and the review summary's
constraint checklist (U5), from a real run where every check passed.

The fixture is live AAPL run `20c538e4` (2026-09-25), in which both agents cited the shared net
income and diluted EPS.

What it locks in:

- **Shared figures.** The two agents' net income meets in one matrix row, marked as a match,
  and the run's producers list the two shared concepts.
- **Answer first.** The summary gives the headline, each agent's count of cited figures that
  match the filing, and the accounting-issues line, and precedes the figures table in document
  order.
- **Passed checks** are folded into a closed group, with the arithmetic one click away.
- **A failed check** (a deliberate-break case: two literal failing checks substituted into the
  real comparison, one hard and gating, one a heuristic) is counted as needing a decision, opens
  by default, and says it is held for review, while the heuristic reads as unusual rather than
  an error.
- **Matrix cells** mark whether each agent's figure matches the filing.
- **The gate with failed checks** (a literal gate holding one disputed figure and one failed
  check): the heading names both kinds of problem, the check's arithmetic is shown, and the
  decisions offered narrow to those valid for every selected item.

No network stubbing; `sessionStorage` is cleared before each test.

Related: [[web/frontend/src/components/RecordSections.tsx]],
[[web/frontend/src/components/DecisionGate.tsx]],
[[web/frontend/src/components/SourcePopover.tsx]], [[validation/constraints.py]]

## `web/frontend/tests/sources.test.tsx`

**Role:** tests for showing a figure's source in place (roadmap U6): filing excerpts for filed
figures, and recorded search snippets for web citations.

What it locks in:

- **A filing figure's source**, with the real excerpt response for AAPL's Q3 FY26 revenue: the
  Source button opens a dialog titled for the figure and form, shows the row as filed with the
  value marked and the scale stated, shows agent A's check result, links to the filing, and
  expands to the other places the figure appears. Escape closes it and returns focus to the
  button. The test also asserts the exact query parameters sent to `/api/facts/excerpt`.
- **A point-in-time figure** (total assets) is looked up without a start date, and a
  `not_found` answer shows the server's message.
- **Where it isn't offered.** A run stored before the CIK was recorded gets no Source button,
  and the investor read of the gated run marks the disputed figure as withheld.
- **Coverage in the run view.** Every non-missing given figure in agent A's lane has its own
  Source button, and so do both cells of a matrix row.
- **A web citation's source**, with the real snippet from MSFT run `881a625e`: clicking agent
  B's cited page shows the search that found it, the recorded text with the agent's figures
  marked (even though that run halted and has no comparison rows), and a link to the page. A
  run from before snippets were kept says so plainly.
- **`figureSpans`** marks a figure by its number and not inside a longer number (a
  deliberate-break case: `182.9` and `4.275` in the same text must not match).
- **No run, no overlay.** A citation outside a run is a plain link.

A local `mockFetch(routes)` helper stubs `fetch` by URL prefix and records every URL requested,
so tests can inspect the query string.

Related: [[web/frontend/src/components/SourcePopover.tsx]],
[[web/frontend/src/views/RunDetail.tsx]], [[datasources/filings.py]]

## `web/frontend/tests/live.test.tsx`

**Role:** tests for live runs (roadmap U4): the SSE parser, the live-run state, the live view,
the compare form, and the hand-over from a stream to the stored record.

Its fixture is a real `/api/compare/stream` response for AAPL, captured live on 2026-09-24,
imported as text through `?raw`. The test file parses it once into `EVENTS` and builds partial
states by replaying events up to a chosen one.

What it locks in:

- **SSE parser.** The real stream yields the same events whether it is pushed in chunks of 1, 7,
  64 or 4096 characters, and includes a `result` event. A hand-written stream with CRLF line
  endings, a keep-alive comment, multi-line data and an unterminated final event yields only
  the complete event, with the data lines joined.
- **Reducer over the real stream.** The run ends done with the stored result, agent A finished
  and not halted, the shared steps recorded, and the announcements a screen reader needs.
  Replayed partway, agent B's lane reads "thinking", then "searching" with its real query, then
  back to thinking with sources found. `ranSequentially` is false for this capture (the agents
  ran concurrently) and true for a literal sequence where B starts after A finishes. A late
  `step_started` never overwrites a finished step.
- **`LiveRunView`** draws the shared fetch once above the lanes, with a link to the SEC company
  facts, and each lane's current activity. After a lost connection it says the run continues on
  the server; eleven minutes later it stops promising the run will appear and offers another
  run.
- **`CompareForm`** rejects an invalid ticker, upper-cases a valid one, and in question mode
  sends the subject and an empty context.
- **`useLiveRun` end to end.** A stubbed `fetch` serves the token, then the captured stream in
  97-character chunks: the hook hands the stored record over once, with the run id from the
  stream. A second test stubs `requestAnimationFrame` to never fire and still completes; its
  comment says this was found live, in a window that reported itself visible but never painted.
  A stream cut before `agent_finished` goes to `lost`, and the hook then polls until the run is
  stored (a 404 first, then the record).
- **`App` hand-over.** Starting a run from `#/new` ends at `#/runs/<id>` with the announcer
  saying the comparison is ready.

Related: [[web/frontend/src/api/stream.ts]], [[web/frontend/src/state/liveRun.ts]],
[[web/frontend/src/state/useLiveRun.ts]], [[web/frontend/src/views/CompareView.tsx]],
[[web/frontend/src/App.tsx]]

### Limits and open issues

- **The CRLF finding and the code disagree in part.** The 2026-09-27 commit entry in
  `logs/RUN_LOG.md` lists as an open issue that the parser "doesn't accept CRLF or CR line
  endings". The committed `createSSEParser` does normalise `\r\n` and `\r` to `\n` within each
  pushed chunk, and this file tests that. What the normalisation can't handle is a `\r\n` pair
  split across two chunks: the `\r` becomes one newline and the `\n` another, which can end an
  event early. That is a likely mechanism for the one-character-chunk failure the entry
  recorded (judgment from reading the code, not recorded). The `.gitattributes` fix avoids it
  for the fixture; the live path is not changed.

## `web/frontend/tests/assessment.test.tsx`

**Role:** tests for the structured assessment strip, mobile Compare mode (roadmap U7) and the
bull/bear pairing choice (B4).

Both fixtures are the same live run (`7a099f0c`, directive v1.6.0, AAPL, the original pairing):
the filings agent answered with a partial assessment whose `key_metrics` used XBRL tag names
the closed vocabulary refused, and the earnings agent failed the format check twice. The
header comment gives the date as 2026-09-26; the stored `initiated_at` is 2026-09-27 01:22 UTC.

What it locks in:

- **The strip, from the real record.** Agent A's lane shows grade, direction and the horizon
  assumption, labelled as a model judgment. What was refused is listed in a closed fold. At
  investor scope the strip is absent and a notice says it is withheld.
- **No usable assessment.** An invalid block says why and opens the raw output in place, with
  the block marked; an unclosed block is marked to the end of the output (a deliberate-break
  case); a block that was left out is described as allowed, with no raw-output button; for a
  corrective retry or an older directive that never asked for one, nothing is rendered.
  `asksForAssessment` compares versions numerically (v1.10.0 is later than v1.6.0), not as
  strings.
- **Mobile Compare mode.** Disputed figures come first; a side with a grade shows it with its
  key points; a side without one says "No structured grade" and falls back to an excerpt that
  is labelled as an excerpt, never presented as the agent's own summary. `summaryLines` takes
  the conclusion's first two sentences. Compare mode is offered alongside the one-lane tabs.
- **Bull/bear.** `CompareForm` sends `pairing: "bull_bear"` only when that option is chosen, and
  the lanes are labelled Bull and Bear when the producers' roles say so (the roles are
  overridden on the real fixture in the test).

No network stubbing.

Related: [[web/frontend/src/components/Assessment.tsx]],
[[web/frontend/src/views/RunDetail.tsx]], [[web/frontend/src/views/CompareView.tsx]],
[[core/assessment.py]]

### Limits and open issues

- The fixture records directive v1.6.0, which `logs/RUN_LOG.md` (2026-09-26, "B4 + U7") records
  as reverted as the default: v1.5.2 is active again. These tests cover the UI for a run that
  asked for an assessment, not the current default.

## `web/frontend/tests/grades.test.tsx`

**Role:** tests for grades in the review summary and setting a grade through the gate (roadmap
B5 and U8).

Both fixtures are the same live run (`8ecb0922`, AAPL, extraction `assess-extract-v1`): both
agents passed the format check, the extraction read AAA/buy and A/buy, B5 classed the
difference as an assumption (stable against expanding margins), and the gate asks a human for
the grade.

What it locks in:

- **Summary at auditor scope.** The grade panel names the kind of disagreement, then each
  agent's grade beside its counted evidence, labelled as a model judgment, and says there is no
  consensus. It asserts no confidence or score percentage appears: counts, not a score.
- **Investor scope.** No agent grade appears anywhere on the page; only the kind of
  disagreement, and a note that grades stay internal until a reviewer sets one.
- **A reviewer's grade** is shown with who set it, and is shown to investors.
- **A consensus** is shown as proposed, never as published: investors see no grade until a
  reviewer sets one.
- **The gate.** The heading says the grades differ, the item lists both candidates, the
  decisions offered are accept A, accept B and set grade, and the grade list is the closed
  scale from AAA to CCC. "Set the grade" won't submit without a grade, and when one is chosen
  the posted body carries `set_grade`, the grade, and `grade` as the cited item.

The submit test stubs `fetch` for the token and the decision post, capturing the posted body.

Related: [[web/frontend/src/components/Grades.tsx]],
[[web/frontend/src/components/DecisionGate.tsx]], [[validation/divergence.py]]

## `web/frontend/tests/pages.test.tsx`

**Role:** tests for the pages moved from the classic UI and the review export (roadmap U9).

What it locks in:

- **Settings** shows the server's settings and saves a change on blur, posting only the changed
  field; at investor scope the fields are read-only and a note says to switch scope.
- **Directive** shows the active directive in full with its version.
- **Honest Ledger** lists open issues first, reports the open count, and shows resolved ones
  only under "Everything". Its data is a literal ledger object in the test (its numbers are test
  input, not a record of the real ledger).
- **Chat** posts the question and added context to `/api/chat/stream` and shows the running
  state from the first streamed events. The chat hand-over announces "Answer ready", not
  "Comparison ready"; the RUN_LOG U9 entry (2026-09-27) records that the wrong announcement was
  found live and fixed with this test.
- **Download review** fetches `/api/runs/{id}/export.md` at the viewer's scope and creates a
  download, while the raw JSON record stays in a closed "Technical details" fold.
- **Navigation.** The top bar links reach every page and show the open-issue count and directive
  version; when `fetch` throws, the app says the server is unreachable.

A local `json()` helper wraps bodies in a `Response`; streams are small hand-written SSE
payloads.

Related: [[web/frontend/src/views/Pages.tsx]], [[web/frontend/src/views/RunDetail.tsx]],
[[web/frontend/src/App.tsx]], [[web/frontend/src/state/useLiveRun.ts]]

## `web/frontend/tests/fixtures/*`

**Role:** real records captured from the running server, replayed by the tests.

The run fixtures have the `GET /api/runs/{id}` shape. Dates below are the stored
`session.initiated_at` (UTC) unless a log entry is cited; test comments give local dates, which
can differ by a day.

| File | What it is | Origin, date | Used by |
|---|---|---|---|
| `excerpt_aapl_revenues.json` | A `GET /api/facts/excerpt` response: AAPL revenue for the quarter ending 2026-06-27, located in the 10-Q | Live excerpt response against the actual 10-Q, 2026-09-25 (test comment); added in RUN_LOG 2026-09-26 "U5 + U6" | [[web/frontend/tests/sources.test.tsx]] |
| `run_chat_auditor.json` | Chat run, auditor scope ("What year was the movie Interstellar released?"), directive v1.5.1, with its steps | Exported from `web/data`, RUN_LOG 2026-09-24 "U1"; initiated 2026-09-24 | [[web/frontend/tests/contract.test.ts]], [[web/frontend/tests/components.test.tsx]], [[web/frontend/tests/views.test.tsx]] |
| `run_chat_investor.json` | Chat run (TSLA), investor-scope read with the internal tier omitted; directive v1.1.0 plus a corrective attempt | Exported from `web/data`, RUN_LOG 2026-09-24 "U1"; initiated 2026-09-22 | [[web/frontend/tests/contract.test.ts]], [[web/frontend/tests/views.test.tsx]] |
| `run_compare_auditor.json` | Compare run (AAPL), auditor scope, stored before figure-by-figure comparison and before the gate: seven top-level keys only | Exported from `web/data`, RUN_LOG 2026-09-24 "U1"; initiated 2026-09-24 | [[web/frontend/tests/contract.test.ts]], [[web/frontend/tests/views.test.tsx]], [[web/frontend/tests/matrix.test.tsx]], [[web/frontend/tests/sources.test.tsx]] |
| `run_compare_b1.json` | Compare run (MSFT), auditor scope, with figure rows (`canonical_facts` rule) and no gate policy | Real stored run, RUN_LOG 2026-09-24 "B1 + U2"; initiated 2026-09-24 | [[web/frontend/tests/matrix.test.tsx]], [[web/frontend/tests/views.test.tsx]] |
| `run_compare_gated_auditor.json` | Generic compare run `ec1a3b44` (first Pokémon game in North America: llama3.2 1998, qwen2.5 1996), auditor read, gate `AWAITING_DECISION` | Live, RUN_LOG 2026-09-25 "BG + U3" | [[web/frontend/tests/contract.test.ts]], [[web/frontend/tests/gate.test.tsx]] |
| `run_compare_gated_investor.json` | The same run read at investor scope while the gate is open | Live, RUN_LOG 2026-09-25 "BG + U3"; regenerated through the fixed trace redaction, RUN_LOG 2026-09-26 "Correction" | [[web/frontend/tests/contract.test.ts]], [[web/frontend/tests/gate.test.tsx]], [[web/frontend/tests/sources.test.tsx]] |
| `run_compare_b3_aapl.json` | Compare run `20c538e4` (AAPL), auditor scope, lens v2, gate policy v2, every accounting check passed | Live, RUN_LOG 2026-09-25 "B2 + B3" | [[web/frontend/tests/checks.test.tsx]], [[web/frontend/tests/sources.test.tsx]] |
| `run_compare_msft_bp.json` | Compare run `881a625e` (MSFT), auditor scope; agent A halted, so there are no comparison rows | Real, RUN_LOG 2026-09-26 "U5 + U6"; initiated 2026-09-25 | [[web/frontend/tests/sources.test.tsx]] |
| `snippet_msft.json` | The search result agent B read for the page it cited in run `881a625e`: URL, title, snippet, query | Real, RUN_LOG 2026-09-26 "U5 + U6" | [[web/frontend/tests/sources.test.tsx]] |
| `run_compare_b4_auditor.json` | Compare run `7a099f0c` (AAPL), directive v1.6.0, auditor read: A's partial assessment, B halted after two format failures | Live, RUN_LOG 2026-09-26 "B4 + U7"; initiated 2026-09-27 01:22 UTC | [[web/frontend/tests/assessment.test.tsx]] |
| `run_compare_b4_investor.json` | The same run read at investor scope (no thought log, raw output or assessment) | Live, RUN_LOG 2026-09-26 "B4 + U7" | [[web/frontend/tests/assessment.test.tsx]] |
| `run_compare_b5_auditor.json` | Compare run `8ecb0922` (AAPL), gate policy v3, auditor read: grades AAA/buy and A/buy, driver "assumption", gate awaiting a grade decision | Live, RUN_LOG 2026-09-26 "Option 1 (assessment extraction) + B5 + U8"; initiated 2026-09-27 01:57 UTC | [[web/frontend/tests/grades.test.tsx]], [[web/frontend/tests/pages.test.tsx]] |
| `run_compare_b5_investor.json` | The same run read at investor scope while the gate is open | Live, RUN_LOG 2026-09-26 "Option 1 (assessment extraction) + B5 + U8" | [[web/frontend/tests/grades.test.tsx]] |
| `stream_compare_aapl_2026-09-24.txt` | A raw `/api/compare/stream` SSE response for AAPL (run `d4ec7b2d`, both agents llama3.2): both agents searched and finished, and the run was stored | Captured live 2026-09-24 (test comment and file name); added in RUN_LOG 2026-09-25 "BP + U4" | [[web/frontend/tests/live.test.tsx]] |

### Limits and open issues

- **The investor reads still say `"scope": "auditor"`.** In `run_compare_gated_investor.json`,
  `run_compare_b4_investor.json` and `run_compare_b5_investor.json`, the top-level `scope`
  field is `auditor`, although the content is redacted. The field is set when the run is
  created (`web/server.py` writes the caller's scope into the payload), and
  `validation/gate.py`'s `redact_for_scope` doesn't change it. [[web/frontend/src/views/RunDetail.tsx]]
  shows `run.scope` as a badge, so an investor read of these runs would carry an "auditor"
  badge. No test asserts on this badge. Only `run_chat_investor.json`, a run started at
  investor scope, says `investor`.
- These files must stay LF. `.gitattributes` marks them `-text`; see
  [Line endings](files-frontend-tests.html#line-endings) above.
- The fixtures freeze the payload shape at capture time. `contract.test.ts` checks a few keys
  every renderer relies on, not the full shape, so a new backend field is not caught until a
  test uses it.
