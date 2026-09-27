---
title: Review app (frontend)
slug: files-frontend
section: Files
order: 90
summary: The React 18 + Vite review app served at /app: live runs, the figure matrix, checks, sources, grades and the human decision gate.
---

The review app in `web/frontend/` is the interface a reviewer uses to start runs, watch them
happen, read what the agents said and what the verification layer found, and record the human
decisions the gate requires. It is a React 18 single-page app written in TypeScript and built
with Vite. [[web/server.py]] serves the built `dist/` folder at `/app`, and `/` redirects there
since the U9 cutover (`logs/RUN_LOG.md`, 2026-09-27, "B6 + U9: the audit export, the remaining
pages, and the cutover of "/""). The classic UI it replaced is archived in
`archive/web-static-legacy/`.

The app holds no business rules of its own. Everything it shows comes from the server: the
comparison rows from `validation/facts.py`, the checks from `validation/constraints.py`, the
gate from `validation/gate.py`, the grades from `validation/divergence.py`, and the withholding
from the server's scope redaction. Where the app repeats a server rule (the decision form's
validation), it does so only so a reviewer is not surprised by a refusal, and the server still
decides.

## Dependency rule

- `src/api/` talks to the server and nothing else talks to it directly. `types.ts` has no
  imports; `client.ts` imports only types; `stream.ts` imports `client.ts` for the Bearer header.
- `src/lib/` holds pure helpers with no React and no network.
- `src/state/` owns the one live run. `liveRun.ts` is a pure reducer; `useLiveRun.ts` is the
  React hook that feeds it from the stream.
- `src/components/` render parts of a run record. They read from props and, for sources, from a
  React context (`SourcesProvider`). Only `DecisionGate`, `SourcePopover` and the flag form in
  `RunDetail` call the API, and only on a reviewer's action.
- `src/views/` are whole pages: they load data, own page state and compose components.
- `App.tsx` is the shell: route, scope, the live run, the announcer and the top bar.

Every npm package is a documented deliberate exception to the subsystem's no-new-dependency
rule (`verification-layer/CLAUDE.md`), listed with its reason in [[web/frontend/README.md]].
Nothing is loaded from a CDN at runtime.

## Architecture

### Routing

The route lives in the URL hash, so a view is linkable and the back button works (comment in
[[web/frontend/src/App.tsx]]). `readRoute()` matches `#/runs/{id}` first (the id must be word
characters or hyphens), then the page names `new`, `chat`, `settings`, `directive` and `ledger`
by prefix. Anything else, including an empty hash, shows the "Pick a run to review" empty state.
Navigation sets `window.location.hash`; a `hashchange` listener re-reads the route. There is no
router library.

### State

There is no global store. State sits where it is used:

- `App` holds the viewer's scope, the route, the History drawer's open state, a refresh counter
  that makes History reload, the count of runs awaiting a decision, the ledger's open-issue
  count, the directive version, whether the server answered, and the text of the one live
  region.
- The single live run is owned by `useLiveRun`, called once in `App` and passed down as
  `live` to the Compare and Chat pages. It lives at app level so a run keeps streaming while
  the reviewer browses History (comment in [[web/frontend/src/state/useLiveRun.ts]]).
- `RunDetail` holds the loaded run and its flags; `HistoryPanel` holds its lists; each page
  holds its own form state.
- A half-written gate decision is kept in `sessionStorage` per run (`gate-draft:{runId}`).

### API client and scopes

[[web/frontend/src/api/client.ts]] is the one place that calls the REST routes. The viewer's
scope (auditor or investor) travels as a Bearer JWT from `POST /api/auth/token`, never as a query
parameter (SEC-02). Tokens are cached per scope for the page's life. Reads of runs, sessions and
History pass the viewer's scope, so an investor gets the server's own withholding
(`validation/gate.py`) rather than a client-side imitation of it (`logs/RUN_LOG.md`, 2026-09-25,
"BG + U3: the human decision gate, backend and inline UI"). A read without a token is served at
the run's stored scope (`_read_scope` in [[web/server.py]]).

The scope toggle in the top bar is not a login. `POST /api/auth/token` issues a token for
whichever scope is asked for; its docstring calls this a Phase 1 prototype limit (see
[[web/auth.py]]). The scope resets to auditor on reload.

### Streaming

Live runs use `POST /api/compare/stream` and `POST /api/chat/stream`, which answer with a
`text/event-stream`. The browser's `EventSource` can't POST or send an Authorization header, so
[[web/frontend/src/api/stream.ts]] uses `fetch` with a `ReadableStream` reader and its own
incremental parser. Events flow into a reducer ([[web/frontend/src/state/liveRun.ts]]) that
derives everything the live view shows from real server events: a step is running only because a
`step_started` arrived without its `step_finished`, and elapsed time is measured from the step's
server-side `started_at`. Nothing simulates progress (the "honest liveness" rule, U4).

When the server stores the run, the app opens the stored record at the viewer's scope, with its
gate, and History reloads. The live view is only for watching; the record is what is reviewed.

### How it degrades

| Situation | What the app does |
|---|---|
| No build in `dist/` | Not the app's code: `/` returns a 503 page from [[web/server.py]] saying how to build one. |
| Server down at load | `/api/directive` fails, and the top bar shows "Server unreachable". |
| A request fails | The view shows the error text in a `role="alert"` block; nothing is retried automatically, except the lost-run poll. |
| Stream drops mid-run | The reducer goes to `lost`; the hook polls `GET /api/runs/{id}` every 5 s and opens the record once stored. After 10 minutes the text stops promising the run will appear. |
| A window that isn't drawn | Batched events flush on the next animation frame or after 100 ms, whichever is first. |
| Runs stored before a feature existed | Every field added later is optional in `types.ts`; renderers fall back (pre-B1 runs show the old raw-number comparison and say so; pre-gate runs are never gated). |
| No CIK recorded, or the gate withholds a figure | No Source button is offered. |
| `sessionStorage` unavailable | The decision draft just doesn't survive a reload. |
| Investor scope | Withheld material is announced ("withheld at investor scope", "Pending human review"), not rendered as empty boxes. |

### Accessibility

- One polite `aria-live` region for the whole app, in `App`. It lives there, not in the live
  view, because the live view unmounts the moment a run is handed over to its record; found live
  on MSFT run `881a625e`, when "Comparison ready" was removed before a screen reader could say it
  (`logs/RUN_LOG.md`, 2026-09-25, "BP + U4: figures located in the filing, and live compare runs
  in /app").
- Every status has a text label and a glyph, never colour alone (`StatusBadge`).
- History is a WAI-ARIA tablist: arrow keys move selection and focus.
- Source overlays are non-modal dialogs: focus moves into the panel, Escape closes it and returns
  focus to its button.
- Disclosures use native `<details>` or buttons with `aria-expanded` / `aria-controls`.
- A closed History drawer is `visibility: hidden`, so its cards leave the tab order.
- Touch targets are at least 44px on coarse pointers, and `prefers-reduced-motion` turns off
  transitions and animations.

The record says what was checked: the accessibility tree and Testing Library queries by role and
name, not a real screen reader, and emulated widths, not touch devices (`logs/RUN_LOG.md`,
2026-09-24, "U1: React + Vite foundation, stored-record views at parity, served at /app").

### Responsive layout

| Width | Layout |
|---|---|
| 1280px and up | History is a 340px side panel beside the main column. |
| Below 1280px | History becomes a slide-in drawer opened from the top bar, with a scrim. |
| Below 1024px | The page links (Chat, Honest Ledger, Directive, Settings) move behind a Menu button. |
| Below 768px | Single column; the figure matrix becomes one card per figure; the two agent lanes become A / B tabs plus Compare mode; source overlays become bottom sheets. |

### Visual system

The app keeps the classic UI's palette, verbatim. `brutalist/DESIGN.md` does not govern the web
app: the human decided it is for videos, articles and documents, "NOT for web pages"
(`logs/RUN_LOG.md`, 2026-09-24, "Human decisions: audit-layer roadmap approved; web UI scope for
brutalist/"). That entry also notes the repo-root `AGENTS.md` wording is broader than this
decision and was not edited from this subsystem.

## Page map

| Route | View | What the reviewer does there |
|---|---|---|
| (empty) | empty state in `App` | Picks a run from History, or starts a compare or a chat. |
| `#/runs/{id}` | `RunDetail` | Reads a stored run answer first: the review summary, grades, checks, the decision gate, the figure matrix, the agent lanes, then reasoning, prompts, trace, sources, claims, attempts, flags and the raw record. Records a gate decision or a flag (auditor scope). Downloads the review. |
| `#/new` | `CompareView` | Starts a compare run (a ticker, with the lens or bull/bear pairing, or any question), then watches both agents live until the record opens. |
| `#/chat` | `ChatView` | Asks one agent a question, watches it live, and is taken to its record. |
| `#/settings` | `SettingsView` | Reads and (auditor scope) changes the server's run settings. |
| `#/directive` | `DirectiveView` | Reads the active directive in full, with its version. |
| `#/ledger` | `LedgerView` | Reads the Honest Ledger: what is open first, or everything. |

History (Runs / Sessions / Flagged / Decide) sits beside or over every page.

## `web/frontend/README.md`

**Role:** the app's own readme: how to run it, why each npm package is here, the source layout
and the UI rules the components follow.

It gives the four npm commands (`npm ci`, `npm run build`, `npm run dev`, `npm run verify`) and
says `npm run verify` passing is what "done" means. Its dependency table names each package, the
version the lockfile resolves, and why it is here: `react-markdown` is there to render model text
as Markdown without raw HTML, closing the legacy UI's `innerHTML` path. The versions in the table
match the resolved versions in `package-lock.json` at the time of writing.

The "UI rules" section is the design brief in short: answer first; one status vocabulary; who
wrote what; SEC-01 omissions announced; "couldn't check" never shown as "checked and wrong";
honest liveness; sources in place; humans decide; responsive breakpoints; and the legacy palette.

### Limits and open issues
- The layout block lists the views as `RunDetail, HistoryPanel, CompareView` and omits
  `Pages.tsx` (U9), which holds the Chat, Settings, Directive and Honest Ledger pages.

Related: [[web/frontend/package.json]], [[scripts/start-server.sh]]

## `web/frontend/index.html`

**Role:** the HTML shell Vite builds from.

It sets `lang="en"`, the viewport meta tag and the title "Verification Layer", provides the
`#root` element, and loads `/src/main.tsx` as a module. Vite rewrites the script path at build
time under the `/app/` base (see [[web/frontend/vite.config.ts]]).

### Design notes
[[web/server.py]] serves this file with `Cache-Control: no-cache`, because it names the current
build's content-hashed assets and a cached copy kept pointing a browser at the previous build
(`_FrontendFiles` docstring; `logs/RUN_LOG.md`, 2026-09-24, U1 entry, "Stale builds from cache").

## `web/frontend/package.json`

**Role:** the npm manifest: scripts and declared dependency ranges.

Scripts:

- `dev`: the Vite dev server.
- `build`: `tsc --noEmit && vite build`, so a type error stops the build.
- `test`: `vitest run`, once, no watch mode.
- `typecheck`: `tsc --noEmit`.
- `verify`: typecheck, tests, then build.

Runtime dependencies are `react`, `react-dom` and `react-markdown`; everything else is a dev
dependency (Vite, the React plugin, TypeScript, Vitest, jsdom, Testing Library and the React
types). The package is `private` and `type: "module"`.

### Design notes
The ranges here are caret ranges; the exact versions installed come from the lockfile via
`npm ci` (README). Vitest 3 is used because Vitest 2 pins its own Vite 5, which conflicts with
Vite 6 (README dependency table).

## `web/frontend/package-lock.json`

**Role:** the npm lockfile (lockfile version 3) that pins every installed package, direct and
transitive, with its resolved URL and integrity hash.

`npm ci` installs exactly what it records. It is committed so the build is reproducible and so
the README's version table can be checked against it. It is generated by npm; don't edit it by
hand.

## `web/frontend/tsconfig.json`

**Role:** TypeScript compiler settings for the app, the tests and the Vite config.

Strict mode is on, with `noUnusedLocals`, `noUnusedParameters` and
`noFallthroughCasesInSwitch`. It targets ES2022 with DOM libraries, uses bundler module
resolution, the `react-jsx` transform and `isolatedModules`, and never emits (`noEmit`): Vite
does the compiling and `tsc` only checks. `types` loads the Vitest globals and the jest-dom
matchers, and `include` covers `src`, `tests` and `vite.config.ts`.

## `web/frontend/vite.config.ts`

**Role:** the Vite build, dev-server and Vitest configuration.

- `base: "/app/"`: every asset URL is rooted at `/app/`, because [[web/server.py]] mounts
  `dist/` there.
- `server.port: 5173` and a proxy from `/api` to `http://127.0.0.1:8000`, so `npm run dev` works
  against a running uvicorn. The comment notes streamed responses pass through the proxy too.
- `test`: the jsdom environment, `tests/setup.ts`, and `tests/**/*.test.{ts,tsx}`.

Related: [[web/frontend/tests/setup.ts]]

## `web/frontend/src/main.tsx`

**Role:** the entry point: mounts `App` into `#root` inside `StrictMode` and imports the
stylesheet.

`StrictMode` runs effects twice in development, which is one reason the loaders in `RunDetail`
and `Pages` guard against setting state after unmount with a `live` flag.
(judgment, not recorded)

## `web/frontend/src/App.tsx`

**Role:** the workspace shell: hash routing, scope, the app-level live run, the single
screen-reader announcer, the top bar and the History drawer.

### What it renders
- An `sr-only` `aria-live="polite"` `aria-atomic` region (`data-testid="announcer"`).
- The top bar: logo, title, a "Prototype" pill; the Auditor / Investor scope toggle (a
  `role="group"` of `aria-pressed` buttons); a "1 running" chip while a live run is running and
  the reviewer is not on `#/new`; a "N need(s) a decision" chip when History reports gated runs
  (it opens History on the Decide tab); "Server unreachable" when the directive request failed;
  "New compare"; the page links (Chat, "Honest Ledger (N open)", "Directive vX", Settings) marked
  with `aria-current="page"`; and the Menu and History toggle buttons with `aria-expanded` and
  `aria-controls`.
- The main column, switching on the route.
- The History `aside` (`id="history-drawer"`) and, while it is open, a scrim that closes it.

### Key functions
- `readRoute()` / `useRoute()`: parse the hash and follow `hashchange`; `go(hash)` sets it.
- `onStored(run)`: called by `useLiveRun` when a live run reaches the store. It announces
  "Comparison ready; showing its record" for a compare run or "Answer ready; showing its record"
  for a chat run ("Run finished without a comparison / an answer" if the run halted), navigates
  to `#/runs/{id}`, bumps History's refresh counter and resets the live run.
- An effect copies the live run's latest announcement ("Run started", "Agent A finished",
  "Connection lost", "The run failed") into the announcer, except once the run is `done`, which
  `onStored` announces instead.
- On mount it calls `api.directive()` (version and reachability) and `api.selfReport()` (the
  open-issue count). `LedgerView` updates the count when the ledger page loads.

### Design notes
- The announcer lives here because the live view unmounts at hand-over (comment in the file;
  `logs/RUN_LOG.md`, 2026-09-25, "BP + U4").
- A chat run was once announced as "Comparison ready"; the hand-over now checks for
  `cross_agent_comparison` (comment in the file; `logs/RUN_LOG.md`, 2026-09-27, "B6 + U9").
- The pages that were the classic UI's panels and modals are routes here, in the workspace, not
  modals over it (comment in the file and in `Pages.tsx`).

### Limits and open issues
- There is no React error boundary. A component that throws while rendering blanks the whole
  app rather than one section. (Found reading the code; no test covers it.)
- The "1 running" chip always links to `#/new`, even when the running run is a chat run. See the
  shared live-run note under [[web/frontend/src/views/CompareView.tsx]].
- The "needs a decision" count comes from History's `/api/runs` read, so it covers only the runs
  that list returned (the route's default `limit` is 50 in [[web/server.py]]).

Related: [[web/frontend/src/state/useLiveRun.ts]], [[web/frontend/src/views/HistoryPanel.tsx]],
[[web/frontend/tests/live.test.tsx]], [[web/frontend/tests/pages.test.tsx]]

## `web/frontend/src/styles.css`

**Role:** the whole visual system in one stylesheet: palette variables, layout, components and
the responsive rules.

All hex colours sit in `:root` as custom properties (`--bg`, `--primary`, the badge, role and
lane pairs, `--warn-surface`); every rule below uses the variables (header comment). The palette
is the classic UI's, verbatim. Lane A is tinted blue (`--lane-a-*`) and lane B orange
(`--lane-b-*`) everywhere a side appears: agent lanes, matrix cells, gate value tags, grade
candidates, Compare-mode columns and trace rows.

The file is organised by phase: shell, badges and pills, run detail, the comparison summary and
matrix, trace, History, responsive rules, then one block each for U3 (gate), B3 (checks), U4
(live runs), U5 (review summary), U6 (source overlays), U7 (assessment and Compare mode), U8
(grades) and U9 (pages and navigation).

### Design notes
- `minmax(0, 1fr)` and `min-width: 0` on grid and flex items: without them one long no-wrap line
  (a trace row, a URL) stretched the whole column past a phone's width. Found at 375px, where a
  684px trace line overflowed (comment in the file; `logs/RUN_LOG.md`, 2026-09-24, U1 entry).
- The closed drawer is `visibility: hidden`, flipped after the slide-out transition, so its cards
  leave the tab order and the accessibility tree (comment in the file; U1 entry, "Hidden-drawer
  focus").
- Below 768px the matrix value columns share the card's width and badges wrap inside their
  cells. The U5/U6 badge and Source button had made the columns size to their content and
  overflow at 375px on a real run (comment in the file; `logs/RUN_LOG.md`, 2026-09-26, "U5 + U6:
  review summary with the constraint checklist first, and sources in place").
- Below 768px a source overlay is a fixed bottom sheet, at most 70% of the viewport high.
- `@media (pointer: coarse)` gives buttons, chips, tabs and the scope buttons a 44px minimum
  height; `prefers-reduced-motion: reduce` disables transitions and animations everywhere.

### Limits and open issues
- Below 768px the rule `.topbar-title, .prototype-pill, .btn-ghost[href] { display: none; }`
  also matches the page links inside `.topnav`, which are `<a class="btn-ghost" href>`
  elements. Read literally, the Menu opens an empty panel on a phone and the Chat, Honest Ledger,
  Directive and Settings links can't be reached from the top bar there. The 2026-09-27 B6 + U9
  entry records that "at 375px the Menu opens inside the viewport, with no overflow", which does
  not say the links were visible. Found reading the CSS; not checked in a browser, and the jsdom
  tests don't apply CSS.
- `.btn:disabled` is declared twice with slightly different opacity (0.5, then 0.55); the later
  one wins.

## `web/frontend/src/api/types.ts`

**Role:** TypeScript shapes of every payload the server sends, hand-mirrored from the Python
side.

The header names its sources: the run payloads in [[web/server.py]], `ReasoningObject.to_dict`
in [[core/schemas.py]], `ExtractedClaim.to_dict` in [[validation/claims.py]], the steps from
[[web/step_trace.py]] and `Fact.to_dict` in [[datasources/edgar.py]]. Later types add the
comparison rows (`MetricComparison`, from [[validation/facts.py]]), checks (`Check`,
[[validation/constraints.py]]), the synthesis (`Synthesis`, `GradeCandidate`,
[[validation/divergence.py]]), the gate (`Gate`, `GateItem`, `GateDecision`, `DecisionInput`,
[[validation/gate.py]]), filing excerpts (`Excerpt`, `Occurrence`, [[datasources/filings.py]]),
web snippets (`Snippet`), the Honest Ledger (`SelfReport`, `KnownIssue`,
[[web/self_report.py]]) and reviewer flags (`Flag`).

A `Run` is either a chat run or a compare run; `isCompareRun(run)` tells them apart by the
presence of the `cross_agent_comparison` key. Several fields are unions to fit both: `claims` is
a list on a chat run and `{a, b}` on a compare run, and so is `verification_rate`.

### Design notes
- Optional fields are optional because stored runs predate them; every renderer must tolerate
  their absence (header comment). The comments on each late field say when it appeared (for
  example `metric_comparisons` absent before 2026-09-24, `structural_flags` before 2026-09-25,
  `synthesis` before 2026-09-26).
- SEC-01: at investor scope `thought_log`, `raw_output`, `directive_text`, `context_window` and
  the assessment fields are omitted, not nulled. Renderers use `"key" in object` to tell
  "withheld" from "never recorded" (comment in the file).
- [[web/frontend/tests/contract.test.ts]] parses real stored payloads against these shapes.

### Limits and open issues
- `ReasoningObject.assessment_status` lists `valid`, `partial`, `invalid_fields`,
  `invalid_json`, `unclosed`, `empty` and `absent`. [[core/assessment.py]] also produces
  `abstained` and `extraction_failed` (added with option 1, the extraction call). The type
  doesn't name them, and `Assessment.tsx` treats them as a broken block (see its entry).
- The types are maintained by hand. The contract test catches a stored payload that lacks a key a
  renderer relies on, not a new server field the UI ignores.

## `web/frontend/src/api/client.ts`

**Role:** the one module that calls the REST routes, with the Bearer scope token.

### Key functions
- `token(scope)`: `POST /api/auth/token` once per scope, cached in a module-level `Map` for the
  page's life.
- `authHeader(scope)`: the Authorization header, shared with `stream.ts`.
- `getJson(url, scope?)`: a GET, with the token only when a scope is given; throws
  `GET {url} failed (HTTP n)` on a non-2xx.
- `postJson(url, scope, body, what)`: a POST with the token. On refusal it reads the server's
  `detail` and puts it in the error, so the reviewer sees why a decision was refused (for
  example the 422 reasons from the decision route).
- `download(url, scope, fallbackName)`: fetches with the token (a plain link can't carry it),
  takes the file name from `Content-Disposition`, and saves the blob through a temporary link.
- `api`: `runs`, `run`, `sessions`, `contradictions` (all scope-aware), `flags`, `excerpt`,
  `snippet`, `addFlag`, `addDecision`, `downloadReview` (`/export.md`), `downloadAudit`
  (`/audit`), `config`, `setConfig`, `directive` and `selfReport`.
- `_resetTokens()`: clears the cache, for tests only.

### Design notes
- The token is a header, never a query parameter (SEC-02), as in the legacy UI (header comment).
- Reads send the token when a scope is given, so an investor gets the gate's withholding from the
  server (header comment; `logs/RUN_LOG.md`, 2026-09-25, "BG + U3").

### Limits and open issues
- `snippet(runId, url)` and `flags(runId)` never send a token. The snippet route is scope-aware
  (it answers `withheld` to an investor while the gate is open), so without a token it answers at
  the run's stored scope, not the viewer's. In the current UI a web-citation overlay is not
  offered in a compare lane while the conclusions are withheld, which covers the gated case, but
  the client itself does not carry the viewer's scope on this read.
- `setConfig` sends no token, and `POST /api/config` doesn't require one. Settings is read-only
  at investor scope only in the UI (`logs/RUN_LOG.md`, 2026-09-27, "B6 + U9", open issues;
  ledger `audit-criticals`).
- A cached token is never refreshed. Tokens expire after the TTL set in [[web/auth.py]]; after
  that every scoped request fails until the page is reloaded.
- `snippet` doesn't pass the route's optional `figure` parameter; the overlay marks figures
  client-side instead (`figureSpans`).

Related: [[web/server.py]], [[web/auth.py]]

## `web/frontend/src/api/stream.ts`

**Role:** starts a live run and reads its event stream.

### Key functions
- `createSSEParser(onEvent)`: returns `push(chunk)` and `end()`. It normalises `\r\n` and `\r`
  to `\n`, splits on blank lines, skips comment lines (keep-alives starting with `:`), reads
  `event:` and `data:` fields, joins multi-line data with `\n`, and delivers the data parsed as
  JSON, or as text if it isn't JSON. An event is only delivered once its blank-line terminator
  has arrived; `end()` drops an unterminated tail.
- `streamRun(path, scope, body, onEvent, signal?)`: POSTs to `/api/compare/stream` or
  `/api/chat/stream` with the Bearer header, and feeds decoded chunks to the parser. It rejects
  only if the request was refused before streaming (with the server's `detail`). It resolves
  `"done"` if a `result` or `error` event was seen before the stream closed, and `"lost"` if the
  connection broke or closed without one. A lost run is still going on the server: a closed tab
  can't cancel it (docstring).
- `streamCompare(...)`: `streamRun` on the compare route.

`CompareRequestBody` carries `ticker` or `subject`, `pairing` (`lenses` or `bull_bear`),
`context` and optional per-agent models; `ChatRequestBody` carries `message` and `context`.

### Design notes
- fetch plus a reader, because `EventSource` can't POST or send the Bearer token (header
  comment; `logs/RUN_LOG.md`, 2026-09-25, "BP + U4").
- The parser is incremental because a network chunk can end mid-line or mid-event (header
  comment). [[web/frontend/tests/live.test.tsx]] feeds a captured real stream in chunks of
  several sizes and expects the same events each time.

### Limits and open issues
- The 2026-09-27 entry "Committing the work since c53746a, and a checkout-only test failure"
  says the parser splits on `\n\n` only and doesn't accept CRLF or CR line endings. The code does
  normalise both within a chunk. What it gets wrong is a CRLF pair split across two chunks: the
  `\r` ending one chunk becomes `\n`, then the `\n` starting the next makes a false blank line.
  That matches the recorded failure (a CRLF checkout of the fixture, fed one byte at a time).
  Checked by running a copy of the parser's logic on a CRLF event in one-byte chunks; the real
  module was not changed or run for this. The server sends LF, so this isn't hit today.
- `signal` is accepted but no caller passes one, so the app never aborts a stream.

## `web/frontend/src/state/liveRun.ts`

**Role:** the reducer for one live run, and pure readings of its state for the live views.

`LiveState` holds the status (`idle`, `starting`, `running`, `done`, `failed`, `lost`), the run
id, the mode, a title, the producers, every step by `seq`, each agent's finished / halted /
conclusion, the final `result` run, an error, when the connection dropped (`lostAt`, client
clock) and the list of announcements for the live region.

### Key functions
- `liveReducer(state, action)`: `start` resets and sets `starting`; `events` applies a batch;
  `failed` and `lost` set their status (a `lost` after `done` or `failed` is ignored); `reset`
  returns to idle. Events handled: `run_started` (status, id, mode, title, producers),
  `step_started` / `step_finished` (keyed by `seq`), `agent_finished`, `result` and `error`.
- `stepsOf(state, phase)`: a phase's steps in `seq` order.
- `laneLine(state, slot)` / `phaseLine(state, phase)`: what an agent is doing now. In order: an
  open search (the last tool step is `started`), an open extraction call, an open model call
  (`thinking`, with its attempt number), otherwise the last step's label, or `waiting` with no
  steps. A finished agent reads `finished` / halted.
- `laneSources(state, slot)`: every URL an agent's finished searches returned, de-duplicated, with
  the page title when recorded.
- `ranSequentially(state)`: true when agent B's first model call started at or after the end of
  agent A's last step.

### Design notes
- A late `step_started` never overwrites the finished snapshot of the same step (comment;
  tested).
- `ranSequentially` exists so two lanes side by side never imply parallelism that didn't happen,
  for example with `CROSS_AGENT_MAX_CONCURRENCY=1` or a local model server that serialises
  (docstring).
- Announcements are kept as a list, oldest first, so `App` can speak the latest.

### Limits and open issues
- The `result` event always adds "Comparison ready" (or "Run ended: ..."), even for a chat run.
  `App` doesn't speak it once the run is `done` and announces the hand-over itself, so a reviewer
  doesn't hear it; the reducer's list still holds it.
- Elapsed times compare the client's clock with the server's `started_at`. A skewed client clock
  would skew the seconds shown. (judgment, not recorded)
- A chat run's consistency probe is a second traced model call, so the live view reads it as
  "Retrying (attempt 2)" when the record holds one attempt (ledger
  `consistency-probe-shown-as-retry`; `logs/RUN_LOG.md`, 2026-09-27, "A model-call timeout, and
  a ledger refresh that found two wrong claims").

## `web/frontend/src/state/useLiveRun.ts`

**Role:** the React hook that owns the one live run for the whole app: starts it, batches its
events into the reducer, recovers a lost connection and hands a stored run over.

### Key functions
- `useLiveRun(onStored?, pollMs = 5000)` returns `{ state, start, startChat, reset, running }`.
  `start(scope, body, title)` runs a compare; `startChat(scope, body)` runs a chat with the
  message as title. `running` is true while starting or running.
- `frame(cb)`: runs `cb` once, on the next animation frame or after 100 ms, whichever is first.
- Events are queued and dispatched as one batch per frame, so a burst of steps re-renders once
  (header comment).
- When the status is `lost` and a run id is known, it polls `GET /api/runs/{id}` at the viewer's
  scope every `pollMs` until the run is stored, then calls `onStored`. It polls that one id and
  nothing else.
- When the status is `done` and the result carries a `session` (it was persisted), it calls
  `onStored` so the reviewer sees the stored record, redacted for their scope, with its gate.

### Design notes
- The timer fallback in `frame`: a window that isn't being drawn (minimised, behind another
  window) never fires `requestAnimationFrame` while still reporting itself visible. Found live on
  2026-09-25 on an AMZN run, when events queued up unseen (comment in the file; `logs/RUN_LOG.md`,
  2026-09-25, "BP + U4"). [[web/frontend/tests/live.test.tsx]] covers a window where the frame
  never fires.
- The hook lives in `App`, not in the view, so the stream keeps going while the reviewer looks at
  History (header comment).

### Limits and open issues
- The lost-run poll never gives up; only the Compare view's text changes after 10 minutes.

Related: [[web/frontend/src/state/liveRun.ts]], [[web/frontend/src/api/stream.ts]]

## `web/frontend/src/lib/format.ts`

**Role:** number, time and period formatting for reading.

- `formatFigure(value, unit)`: dollar amounts scaled to T, B or M with two decimals
  (`$94.93B`); `USD/shares` as `$2.02/share`; percentages as `38.1%`; small values with up to two
  decimals. A missing or non-finite value is `—`, never a number.
- `formatDuration(ms)`: `128ms` or `36.9s`.
- `formatClock(iso)`: local `HH:MM:SS.mmm` for trace lines; a bad timestamp is `--:--:--.---`.
- `formatPeriodChip(fact)`: the filer's fiscal label and form, `Q3 FY26 · 10-Q`, or empty.
- `shortId(id)`: the first eight characters and an ellipsis.

### Design notes
Formatting is for reading, never a replacement for the record: callers keep the raw value in a
tooltip (header comment). `FactValue` and the matrix both do.

Related: [[web/frontend/tests/format.test.ts]]

## `web/frontend/src/lib/glossary.ts`

**Role:** plain phrases for technical terms, each with the technical term and a one-line
definition.

`GLOSSARY` has entries for `thought_log` ("Reasoning"), `context_window` ("What the agent was
sent"), `adr07` ("Format check"), `sec01` ("Investor view"), `contradiction_null` ("No
comparison was possible"), `verified_null` ("Couldn't check"), `score` ("Similarity score") and
`gate` ("Needs your decision"). The `Info` component in `primitives.tsx` shows an entry on
demand.

### Design notes
Plain language first, technical terms one click away and never deleted (header comment).

### Limits and open issues
- The `gate` definition describes only disputed figures ("The agents gave different values for
  the same figure"). Since B3 and B5 a gate item can also be a failed hard check or a grade, and
  the server's pending-review note was generalised for the same reason (`logs/RUN_LOG.md`,
  2026-09-27, "B6 + U9").

## `web/frontend/src/components/primitives.tsx`

**Role:** the small shared pieces: the status vocabulary, author pills, glossary disclosures,
safe Markdown, a reported figure, and a collapsible section.

### Key components
- `StatusBadge({ state, children? })`: one entry per state in a fixed table, each with a label,
  a glyph (hidden from screen readers) and a colour class; `children` overrides the label. States
  cover figure comparison (`match`, `mismatch`, `different_periods`, `one_sided`,
  `uncorroborated`, `unverifiable_period`, `derived_ok`, `derived_wrong`, `cited_by_one`),
  citations (`verified`, `not_found`, `unchecked`), attempts (`success`, `parse_failure`,
  `halted`, `retried`), the gate (`awaiting_decision`, `decided`, `withheld`), checks
  (`check_pass`, `check_fail`, `check_warn`, `check_skipped`) and sources (`source_match`,
  `source_mismatch`). The badge carries `data-state`.
- `RolePill({ role })`: "User", "Agent" or "Verification Layer", marking who wrote each part of
  the record.
- `Info({ term })`: an ⓘ button with `aria-expanded`, `aria-controls` and the label `What does
  "…" mean?`; it toggles a `role="note"` with the technical term and definition.
- `Markdown({ text })`: `react-markdown` with its defaults, which ignore embedded HTML.
- `FactValue({ fact })`: a formatted figure with the raw value and period in its tooltip, and a
  period chip, or "Period not reported"; a missing fact reads "not reported".
- `Section({ title, role?, badge?, defaultOpen = true })`: a `<details>` with a role pill and
  title in its summary.

### Design notes
- Every state has text and a glyph, so nothing depends on colour alone (comment; tested).
- `Markdown` never uses `dangerouslySetInnerHTML`, closing the legacy `renderMd()` innerHTML path
  for model text (comment; [[web/frontend/tests/components.test.tsx]] checks an `<img onerror>`
  renders no image).

## `web/frontend/src/components/TraceLog.tsx`

**Role:** the terminal-style, chronological record of everything a run did.

`TraceLog({ steps })` renders nothing without steps. Otherwise it is a `<details>`, collapsed by
default, whose summary shows the step count and the latest step's line. Open, it offers lane
filter chips (All plus each phase present), a "Copy log" button that copies the visible lines,
and an ordered list of steps; each line is a button with `aria-expanded` that reveals the step's
detail, its error, its URL, and pills for a search's result URLs. A step whose search results
are withheld says "What this search returned is withheld: pending human review".

### Key functions
- `stepLine(step)`: `HH:MM:SS.mmm  phase  what  duration  status`, where a tool step shows the
  tool, its phase and its query.
- `hostOf(url)`: the hostname for a pill, or the raw string if it doesn't parse.

### Design notes
- Collapsed by default so it never competes with the answer (header comment; README "answer
  first").
- URLs come from model and tool output, so `hostOf` never assumes they parse (comment; tested).
- The withheld line is the frontend half of the fix for search text carrying a disputed value past
  the gate (`logs/RUN_LOG.md`, 2026-09-26, "Correction: two claims in earlier entries were wrong;
  the trace leak they hid is fixed"; ledger `trace-leaks-disputed-values`).

### Limits and open issues
- The copy button uses `navigator.clipboard` if present and shows "Copied" either way.

## `web/frontend/src/components/ComparisonMatrix.tsx`

**Role:** the figure-by-figure table: Figure, Period, Agent A, Difference, Agent B.

### What it renders
- Filter chips (All, Needs attention, Conflicts), each with its count, as `aria-pressed`
  buttons. "Needs attention" is `MISMATCH`, `UNCORROBORATED`, `DERIVED_WRONG`,
  `DIFFERENT_PERIODS` and `UNVERIFIABLE_PERIOD`; "Conflicts" is `MISMATCH` and `DERIVED_WRONG`.
- A table with a screen-reader caption. Each row has the figure as a row header, the period (one
  chip, or "A: … B: …" when they differ, or "not stated"), each agent's value, and the
  difference between them. A row note (for example a recomputation) sits in the next row.
- Figures only one agent was given (`ONE_SIDED`) are folded into a separate `<details>`, "expected:
  each agent reads a different part of the filing", open only when there is nothing else.
- "Neither agent cited a figure, so there is nothing to compare" when there are no rows.

A value cell shows the value formatted for its family (currency and per-share formatted; other
families as the agent wrote them), with the agent's own wording in the tooltip; a "Matches the
filing" / "Doesn't match the filing" badge from the claim-vs-source check when one ran; and the
Source button. A withheld value reads "Withheld".

### Key functions
- `gap(row)`: the distance in the unit a reader thinks in: years apart for a year, otherwise the
  variance percentage.
- `matrixCounts(rows)`: shared, matched, mismatched, uncorroborated and derived-wrong counts,
  and whether any row flags. The summary headline and History cards both use it.

### Design notes
- The difference and its verdict are one column between the two values, so the eye goes A, Δ, B
  (header comment; `logs/RUN_LOG.md`, 2026-09-24, "B1 + U2: figure-by-figure comparison (metric,
  period, derivations) and the matrix UI").
- Rows arrive severity-sorted from [[validation/facts.py]]; the component doesn't re-sort.
- One-sided figures are folded because they are expected and must never read as a disagreement
  (header comment).
- A year gap reads "2 years", not a percentage: "0.1%" for 1996 against 1998 is true and useless
  (comment; found in the browser, `logs/RUN_LOG.md`, 2026-09-25, "BG + U3").
- Below 768px each row becomes a card (CSS in `styles.css`).

### Limits and open issues
- The matrix doesn't mark a row as decided; that lives in the gate above it (`logs/RUN_LOG.md`,
  2026-09-25, "BG + U3", open issues).

Related: [[web/frontend/src/components/SourcePopover.tsx]], [[web/frontend/tests/matrix.test.tsx]]

## `web/frontend/src/components/DecisionGate.tsx`

**Role:** the inline human decision on disputed figures, failed checks and differing grades.

`DecisionGate({ runId, gate, rows, scope, onDecided })` renders nothing for `NOT_GATED` and
`NO_DECISION_NEEDED`. Otherwise it is a labelled `<section>` under the comparison headline with:

- a heading that says what kind of problem is open (disputed figures, failed checks, the grade,
  or how many of how many items remain), with a `gate` glossary disclosure;
- while awaiting, what investors see meanwhile and which items are still open;
- the decisions in effect, each with its label, value or grade, cited items, "Decided by
  {name} · {when}" and rationale; superseded decisions folded below;
- at investor scope, "Pending human review. An auditor records the decision." and no form;
- at auditor scope, a button ("Review and record decision" / "Record a new decision") that
  expands the form in place, noting "(draft saved)" when a draft exists.

The form has checkboxes for the items (a figure shows A's and B's values; a check shows its
arithmetic; a grade shows each agent's grade, direction and assumptions), radio cards for the
decisions that fit the items picked, a grade select for "Set the grade", a number field for "Set
the correct value", a rationale with a live character count, and a name field marked "Recorded
as entered; not verified". The submit button stays disabled, and the missing items are listed,
until every rule is met. A refusal from the server is shown in a `role="alert"`.

### Key functions
- `DECISIONS_FOR`: which decisions fit a figure, a check or a grade; mirrors `DECISIONS_FOR` in
  [[validation/gate.py]] (comment).
- `allowedDecisions(items, cited)`: the decisions that fit every item picked.
- `problems(draft, allowed)`: at least one item; a decision that fits; exactly one figure and a
  numeric value for an override; a grade from `GRADES` (AAA to CCC) for Set the grade; at least
  `MIN_RATIONALE` characters of rationale; a name of at least two characters.
- `loadDraft` / the save effect: the draft lives in `sessionStorage` under `gate-draft:{runId}`
  while it is dirty, and a `beforeunload` warning covers it.
- `submit`: posts a `DecisionInput` at the viewer's scope and passes the new gate to
  `onDecided`; `RunDetail` then re-reads the run so the server decides what the scope may now
  see.

### Design notes
- Inline, never a modal, so the figures it is about stay readable while the reviewer writes
  (header comment; P1 humans decide, P4 gates are hard stops).
- The form mirrors the server's rules only so a reviewer isn't surprised by a refusal; the server
  enforces them (header comment).
- Decisions can't be edited or deleted; a later one supersedes (the form says so). The store is
  append-only (`logs/RUN_LOG.md`, 2026-09-25, "BG + U3").
- For a grade item, "accept A/B" reads "Agent A's grade is right" (B5; `logs/RUN_LOG.md`,
  2026-09-26, "Option 1 (assessment extraction) + B5 + U8: grades, why they differ, and who sets
  them").
- The AI sessions that built and verified this recorded no decisions on live gated runs: clearing
  a human gate is what P4 forbids (both entries above).

### Limits and open issues
- The decider's name is self-declared (ledger `gate-identity-self-declared`), and any caller can
  obtain an auditor token (see [[web/auth.py]]).
- A saved draft keeps the items it had when saved, even if the gate's pending list has changed
  since.
- A consensus grade can't be confirmed as the published grade: only a disagreement opens a grade
  item (`logs/RUN_LOG.md`, 2026-09-26, option 1 + B5 + U8, open issues).

Related: [[web/frontend/tests/gate.test.tsx]], [[web/frontend/tests/grades.test.tsx]]

## `web/frontend/src/components/Grades.tsx`

**Role:** the grade question in the review summary: what kind of disagreement it is, each
agent's grade beside its counted evidence, a consensus, and a grade a reviewer set.

### Key components
- `GradesPanel({ synthesis, decided? })`: at auditor scope, the driver sentence ("They disagree
  because the figures conflict", "... because of an assumption", "... on how to weigh the same
  evidence", "Both agents give the same grade", "There is no pair of grades to compare") with the
  audit recommendation; then, if any agent has a grade, one card per agent with the grade,
  direction (arrow glyph hidden from screen readers), assumptions in words, and five counts
  (figures matching the filing, contradicting it, unchecked, with nothing to back them, failed hard
  checks); then "Consensus" with the note that investors see no grade until a reviewer sets one,
  or "No consensus: needs your decision", or the reason there is none.
- At investor scope (`synthesis.withheld`): the reviewer-set grade if there is one, otherwise a
  notice that the agents' grades are model judgments and stay internal; and the driver sentence.
- `DecidedGrade({ decided })`: "Grade set by a reviewer", the grade, who and when.

### Design notes
- Counts, no scores or gauges (P3); grades are labelled model judgments (P8); the one grade an
  investor can see is the one a named human recorded (header comment; `logs/RUN_LOG.md`,
  2026-09-26, option 1 + B5 + U8).
- A consensus is shown as proposed, never as published (tested in
  [[web/frontend/tests/grades.test.tsx]]).

### Limits and open issues
- Assumption keys other than `revenue_growth_pct` and `horizon_months` are all rendered as
  "{value} margins". That fits the one other key the vocabulary has (`margin_trend`), but any new
  key would be misworded.
- The evidence behind live grade conflicts is thin; the ledger entry is
  `synthesis-thin-and-lexical`.

## `web/frontend/src/components/SourcePopover.tsx`

**Role:** "where does this number come from?", answered in place: the filing row a figure sits
in, or what the agent read at a cited web page.

### Key pieces
- `sourcesOf(run)` and `SourcesProvider`: what the page knows about a run's sources: its id, the
  CIK (from the first step that recorded one), the facts each agent was given, the checks, the
  metrics the gate is withholding, and each agent's cited figures (the matrix's raw values plus
  the comparison's extracted numbers). `useSources()` reads it.
- `CONCEPT_METRIC`: maps an XBRL concept (Assets, Revenues, NetIncomeLoss, the two EPS concepts,
  OperatingIncomeLoss) to the metric key the comparison rows use.
- `givenFact` / `sourceCheck`: the fact an agent was given for a metric, and the claim-vs-source
  check (`source:agent_{slot}:{metric}`) for it.
- `useOverlay()` / `Overlay`: the shell. A non-modal `role="dialog"` with a labelled title and a
  close button, anchored under its button (to the right edge for agent B). Opening moves focus
  into the panel; Escape closes and returns focus to the button; a mouse-down outside closes it.
- `FilingSource({ slot, metric?, fact?, cited?, label })`: the Source button for a filing
  figure. On first open it calls `/api/facts/excerpt` (a point-in-time figure is looked up
  without a start date) and shows the statement row and column, the excerpt with the value marked
  (screen readers hear "highlighted value: …"), "Value as filed" with its scale and the scaled
  dollar value, the agent's cited value with its match badge, the other places it appears, and a
  link to the filing. A not-found filing shows the server's reason and still links the filing.
- `WebSource({ url, label, slot })`: the button for a cited web page. It calls
  `/api/runs/{id}/source-snippet` and shows the search that found the page, the snippet with the
  agent's cited figures marked, and "As recorded when the agent searched; the page may have
  changed since". Outside a run (no provider) it is a plain link.
- `figureSpans(text, figures)`: finds each cited figure by its numeric core, not inside a longer
  number, and drops overlapping spans.

### Design notes
- An overlay anchored to the figure, a bottom sheet on a phone, never a page-covering modal
  (header comment; `logs/RUN_LOG.md`, 2026-09-26, "U5 + U6").
- Not offered where nothing can be looked up (no CIK recorded: runs before B0) or where the gate
  is withholding the figure (comment; README).
- Web snippets are recorded at search time and not re-fetched (header comment).
- Excerpt requests are cached per figure, and a failed one is removed from the cache so it can be
  retried (comment).
- Cited figures include the extracted numbers because a halted run has no comparison rows; found
  live on MSFT run `881a625e` (comment; U5 + U6 entry).
- The overlay title uses the plain name, not the raw tag, which it showed before a live fix (U5 +
  U6 entry).

### Limits and open issues
- The U5 + U6 entry says a click outside returns focus to the button, as Escape does. The code's
  outside-click handler only closes the overlay; it does not move focus.
- Excerpt coverage is limited to recent primary documents, with layout heuristics checked on four
  filers (ledger `filing-excerpt-coverage`).
- The live lanes in `CompareView` still link sources directly, not through this overlay (U5 + U6
  entry, open issues).

Related: [[datasources/filings.py]], [[web/frontend/tests/sources.test.tsx]]

## `web/frontend/src/components/Assessment.tsx`

**Role:** an agent's structured assessment (grade, direction, assumptions, key points) where
the agent is, the empty state when there isn't a usable one, and the phone Compare mode.

### Key components and functions
- `AssessmentView({ ro })`: for one agent's final attempt. With a `valid` or `partial`
  assessment it shows a strip: "Grade" and the grade badge, the direction with an arrow, a
  "Model judgment" tag, an assumptions table, key points, and a folded list of what was left out.
  With `absent`: "No structured grade: the agent left the optional assessment out". With a null
  status (not asked for, as on a corrective retry) it shows nothing. Any other status shows "No
  structured grade" and, for a broken block, its first issue; "View raw output" opens the raw
  response in place with the assessment block marked, or the spot after `</conclusion>` where it
  was expected. With no `assessment_status` key at all it shows "withheld at investor scope" only
  if the directive asks for the block and the raw output is also absent.
- `asksForAssessment(version)`: true for directive v1.6.0 and later.
- `finalAttempt(objects, agentId)`: the agent's successful attempt, or its last.
- `RawOutput({ raw })`: the raw text with the region marked.
- `summaryLines(ro, conclusion)`: up to three lines for Compare mode: the agent's key points; else
  bullets from its thought log; else the conclusion's first two sentences, flagged as an excerpt.
- `CompareModeView({ lanes, rows })`: the disputed figures first, then both sides' grade,
  direction and summary lines side by side; a withheld lane says so.

### Design notes
- The grade is labelled "Grade", because a bare "A" under lane A read as the lane (comment; seen
  live, `logs/RUN_LOG.md`, 2026-09-26, "B4 + U7: structured assessments and bull/bear, built and
  reverted as the default").
- The raw output opens in place so a dropped tag can be told from a mangled one without leaving
  the page (header comment).
- Compare mode never generates a summary; a fallback is labelled "Excerpt" (U7 entry; tested).

### Limits and open issues
- The component was written for B4, when the block came inside the agent's answer under directive
  v1.6.0. Since option 1 the assessment comes from a separate extraction call under v1.5.2
  (`logs/RUN_LOG.md`, 2026-09-26, option 1 + B5 + U8). From reading the code:
  - `abstained` and `extraction_failed` fall into the broken-block branch. Neither is in the
    `BROKEN` set, so no reason is shown, and "View raw output" marks "no `<assessment>` block
    here, after `</conclusion>`", although under option 1 the answer never contains one.
  - At investor scope the withheld notice depends on the directive being v1.6.0 or later. The
    stored option 1 investor fixture (`run_compare_b5_investor.json`) is v1.5.2 with no assessment
    keys, so for such runs the lane shows no notice at all.
- Chat runs get no extraction, so a chat conclusion shows an assessment only for runs stored under
  v1.6.0 (U8 entry, open issues).

Related: [[core/assessment.py]], [[web/frontend/tests/assessment.test.tsx]]

## `web/frontend/src/components/RecordSections.tsx`

**Role:** each section of a stored run record, as a component, including the comparison summary
that leads a compare run.

### Key components
- `VerificationBanner({ claims })`: the citation check next to a chat conclusion. With no
  citation extracted it says "Not verified" and that nothing was fetched; otherwise one row per
  citation with "Matches source", "Not found in source" or "Couldn't check" (with its glossary
  note), and the page as a `WebSource`.
- `ClaimsTable`, `DataSourcesTable`: the extracted claims (folded) and the data sources.
- `ContextWindow({ objects })`: the system and user prompt for every attempt. At investor scope
  it says the prompts are withheld. On a compare run the title counts prompts and agents and each
  attempt names its agent.
- `Attempts({ objects })`: every attempt with its format-check status and raw output, or "Raw
  output withheld at investor scope".
- `ThoughtLog({ text, withheld })`: the reasoning, folded, or its withheld notice.
- `Checklist({ checks })`: one line per check. What didn't pass is open, with its arithmetic,
  what it means ("Held for review: a reviewer must decide." for a gating hard failure; "Unusual,
  worth a look. Not an error on its own." for a heuristic; the filing's own figures not lining up
  otherwise) and its reason. What passed is folded under "N checks passed". A withheld check says
  its figures are pending review.
- `ComparisonSummary({ cmp, producers, facts, gate, withheld, claims, objects, decidedGrade })`:
  the review summary, then the matrix, then the lanes:
  - the headline and details from `summarize()`;
  - per-agent evidence lines ("Agent A: 2 of 2 figures it cited from its inputs match the SEC
    filing") and the issues indicator;
  - `GradesPanel` when there is a synthesis, then the checklist;
  - the recorded verdict with the rule that produced it, and a note when it and the figure rows
    disagree;
  - a note when both agents ran on the same model;
  - the decision gate passed in as `gate`;
  - "Figure by figure" (`ComparisonMatrix`);
  - below 768px, chips to show agent A, agent B or Compare mode;
  - two lanes (Bull / Bear for that pairing), each with its model, assessment, given facts with
    Source buttons, conclusion or its withheld / halted notice, cited web pages and cited figures
    (those that diverged highlighted);
  - "Technical details" with the similarity metrics.

### Key functions
- `summarize(cmp)`: the headline, built only from what was compared. A halted comparison says
  which agent failed the format check. A pre-B1 run says only raw numbers were compared. Otherwise
  it counts from the rows, in order of what matters: real mismatches, then figures with nothing
  to back them, then full agreement. Shared figures that couldn't be compared are counted apart
  and never as agreement or conflict.
- `evidenceLines(checks, facts)`: per agent, from the `matches_source` checks, skipped checks
  counted separately; an agent given no filing figures gets no line.
- `laneName(producer, slot)`: "Bull" / "Bear" for that pairing, otherwise "Agent A" / "Agent B",
  cased in code because chips and Compare-mode headers show it (comment; found live reading
  "Agent a").

### Design notes
- Ported from the legacy `renderRunDetailHtml` / `appendAgentBubble` with the same honesty rules:
  SEC-01 omissions are announced, and "couldn't check" is never shown as "checked and failed"
  (header comment).
- Answer first: headline, evidence, issues and the checklist come before the figures
  (`logs/RUN_LOG.md`, 2026-09-26, "U5 + U6").
- The recorded verdict and the figure check are both shown when they disagree, so neither
  silently wins (U2 entry; P6).
- The withheld notice uses the omitted key (`"directive_text" in o`), which is how "withheld" is
  told apart from "never recorded" (comment).

### Limits and open issues
- Compare runs stored before B1 kept only 7 keys (no steps, producers, contexts, facts or
  claims), so they show no trace, input facts or cited pages (`logs/RUN_LOG.md`, 2026-09-24, U1
  entry, open issues). The B1 + U2 entry records that stored compare runs keep those keys from
  then on ("records had been 7 keys, now 14").

Related: [[web/frontend/tests/checks.test.tsx]], [[web/frontend/tests/views.test.tsx]],
[[web/frontend/tests/matrix.test.tsx]]

## `web/frontend/src/views/RunDetail.tsx`

**Role:** loads a stored run and its flags at the viewer's scope and renders the whole record,
answer first.

### Key components
- `RunDetail({ runId, scope, onChanged })`: fetches `api.run(runId, scope)` and `api.flags(runId)`
  (a flags failure becomes an empty list). A re-read after a decision keeps the current view on
  screen so there is no flash and focus stays put; a different run or scope clears it first
  (comment). After a decision it re-reads the run, because the server decides what the scope may
  now see, and bumps History.
- `RunDetailView({ run, flags, scope, onFlagged, onDecided })`: wraps everything in
  `SourcesProvider`. The header shows the short run id, Compare or Chat, the subject, "Download
  review" (compare runs), and status badges. Then the run's error and any tool-capability warning,
  then for a compare run `ComparisonSummary` with the `DecisionGate`, or for a chat run the
  conclusion, its assessment and the verification banner followed by confidence, consistency,
  citations verified and directive version. Then the reasoning, what was sent, the trace, data
  sources, claims, attempts, reviewer flags, and "Technical details: the raw record" (the run as
  JSON, with "Download the audit record (JSON)" for compare runs).
- `DownloadReview`: downloads `/export.md` at the current scope; errors show beside it.
- `Flags`: the reviewer flags and, at auditor scope only, a form (Hallucinated, Incorrect or
  Other, with a note).

### Design notes
- Inline in the workspace, no modal, so it can sit beside anything else on screen (header
  comment).
- The Markdown review is the default download and JSON sits under Technical details, following
  the repo's "Markdown for humans" rule (docstring).
- Reads at the viewer's scope, so an investor gets the gate's withholding from the server
  (docstring).

Related: [[web/frontend/src/components/RecordSections.tsx]], [[validation/audit.py]],
[[web/frontend/tests/views.test.tsx]]

## `web/frontend/src/views/HistoryPanel.tsx`

**Role:** History: Runs, Sessions, Flagged and Decide, as a proper tablist.

`HistoryPanel({ selectedId, onSelect, refreshKey, scope, requestedTab, onNeedsDecision })` loads
`/api/runs`, `/api/sessions` and `/api/runs/contradictions` at the viewer's scope together, and
reloads when the scope or `refreshKey` changes or the ↻ button is pressed. Each tab shows a count
(or "…" while loading). Decide lists the runs whose gate is `AWAITING_DECISION`, and the count
is reported to `App` for the top-bar chip. A `requestedTab` switches tabs (the chip uses it).

A run card shows Done or Halted, Compare or Chat, the short id and the subject; for a compared run
it adds the outcome, the reviewer-set grade or a consensus grade, and "Needs decision" or
"Decided". Session cards show status, id, ticker and directive version.

### Key functions
- `Outcome({ cmp })`: the same reading as the run's own headline: "Mismatch · n of m figures"
  only for real mismatches, "Needs review (n)" for a run flagged for one-sided or derived
  figures, else "Figures agree"; a pre-B1 run uses the raw-number verdict.
- `onTabKey`: Left and Right arrows move selection and focus, wrapping; only the selected tab is
  in the tab order.
- `needsDecision(run)`: exported for tests.

### Design notes
- A WAI-ARIA tablist (header comment; tested).
- The Decide label is short because four tabs share a narrow panel; the fourth tab wrapped at
  panel width before the fix (comment; `logs/RUN_LOG.md`, 2026-09-25, "BG + U3").

### Limits and open issues
- The header comment names three tabs (Runs / Sessions / Flagged); there are four.
- The lists are what the routes return, and `/api/runs` defaults to 50 runs, so older gated runs
  don't appear under Decide or in the count.
- Session cards have no selected state.

Related: [[web/frontend/tests/views.test.tsx]], [[web/frontend/tests/gate.test.tsx]]

## `web/frontend/src/views/CompareView.tsx`

**Role:** the start form for a compare run and the live view of it.

### Key components
- `CompareForm({ onStart, disabled })`: a choice between "A company (SEC filings)" and "Any
  question". For a company: a ticker (validated against a letter followed by up to nine letters,
  dots or hyphens, sent upper-cased) and the pairing, "Filings agent vs earnings agent" or "Bull
  vs bear" (the `pairing` field is sent only for bull/bear). For a question: the question (at
  least three characters) and optional context. Optional per-agent model names are folded under
  "Models (optional)".
- `LiveRunView({ state, onReset })`: the header with the short run id and status; a lost-connection
  notice (`role="status"`), a failure (`role="alert"`) or "ended without a stored record", each
  with "Start another run"; the shared work, drawn once above both lanes ("Shared: one fetch, both
  agents": the SEC ticker list, company facts, each agent's prepared inputs, each resolving into
  a link with its duration); two lanes; a note when the agents ran one at a time; and "Comparing
  the two answers…" once both agents are done.
- `Lane`: the agent's role and model; its current activity from `laneLine` ("Waiting to start",
  "Thinking… Ns", "Retrying (attempt n)… Ns", "Searching: {query}… Ns", "Reading its answer for a
  grade… Ns", the last step's label, "Finished" or "Halted: failed the format check twice"); up to
  six source links titled with the page name the agent saw; and its conclusion when finished.
- `CompareView({ live, scope })`: the form when the live run is idle, otherwise the live view.
- `useNow(active)`: a one-second clock while a run is active.

### Design notes
- The shared SEC fetch is drawn once because it happened once (header comment).
- Elapsed seconds count from the server's `started_at`; nothing simulates progress (U4 entry).
- `LOST_PATIENCE_MS` is 10 minutes: after that a lost run is probably not coming back (a server
  restart ends it), and saying "it will appear" forever would be a promise nothing backs
  (comment). Found live on a META run lost with a restarted server (`logs/RUN_LOG.md`,
  2026-09-25, "BP + U4").
- The sequential-run note exists so side-by-side lanes never imply parallelism that didn't happen
  (see `ranSequentially`).
- When the run is stored, `App` opens its record, so the answer is read from the store (header
  comment).

### Limits and open issues
- The live state is shared by the Compare and Chat pages. `CompareView` shows the live view for
  any non-idle run, so a chat run in progress appears here as two lanes that never leave
  "Waiting to start", and the "1 running" chip always leads here. `ChatView` has the mirror
  problem for a compare run. (Found reading the code; not tested.)
- `CompareView` passes `disabled={false}` and shows the form only when idle, so the form's "One
  run at a time" note can't appear.
- Source links use `new URL(url).hostname` when a result has no title; a malformed URL would
  throw during render. `TraceLog` guards this case with `hostOf`.

Related: [[web/frontend/src/state/liveRun.ts]], [[web/frontend/tests/live.test.tsx]]

## `web/frontend/src/views/Pages.tsx`

**Role:** the pages that lived only in the classic UI, brought into the app for the cutover:
Chat, Settings, the active directive, and the Honest Ledger.

### Key components
- `useLoad(load)`: loads once on mount, keeping data and error.
- `ChatView({ live, scope })`: "Ask one agent". A question (at least two characters) and optional
  context behind "Add context"; "Ask" is disabled while any run is running. While a run is live it
  shows one lane with the same activity lines as a compare lane (from `phaseLine(state, "chat")`),
  up to six result hostnames, a lost-connection notice, and a failure with "Ask again". When the
  run is stored, `App` opens its record.
- `SettingsView({ scope })`: the server's model (read-only here), temperature, seed, chat agent
  identity, starting confidence score (with the note that below 0.4 a run is classed
  high-uncertainty, ADR-08) and the consistency probe. Ranges save on mouse-up or key-up, the
  seed on blur, the select and checkbox on change; a `role="status"` line reports what was saved
  or the error. At investor scope every control is disabled.
- `DirectiveView()`: the active directive's version and full text.
- `LedgerView({ onCount })`: the counts (open of recorded, critical, automated tests, deployment
  state), then the issues sorted by severity, "Still open" (OPEN and UNVERIFIED) by default or
  "Everything", each folded with its status in plain words (Open, Not yet shown to work, Fixed,
  By design), severity, area, title, detail as Markdown, and source. It reports the open count to
  the top bar.

### Design notes
- Each is a page in the workspace, not a modal over it (header comment), and completes the parity
  checklist that let `/` switch to this app (`logs/RUN_LOG.md`, 2026-09-27, "B6 + U9").
- "Clear all runs" was deliberately not ported: `DELETE /api/runs` drops every table, decisions
  included, contrary to the never-delete rule (same entry; a BY_DESIGN ledger entry).
- The ledger's "open" filter matches the server's `issues_open` count, which also counts
  UNVERIFIED items ([[web/self_report.py]]).

### Limits and open issues
- Settings is read-only at investor scope only in the UI; `POST /api/config` is unauthenticated
  (B6 + U9 entry; ledger `audit-criticals`).
- The chat lost-connection notice has no 10-minute variant, unlike the Compare view.
- The chat lane shows result hosts with `new URL(u).hostname`, which throws on a malformed URL.
- A chat run's consistency probe reads as a retry in the live lane (ledger
  `consistency-probe-shown-as-retry`).
- Range settings save on mouse-up or key-up only. Whether a touch drag triggers a save was not
  checked. (judgment, not recorded)

Related: [[web/self_report.py]], [[web/frontend/tests/pages.test.tsx]]
