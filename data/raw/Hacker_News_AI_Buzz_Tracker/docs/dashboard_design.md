# Dashboard design (Week 8)

## What it is

A single static page, `dashboard/index.html`, that reads the `hn_buzz_runs` table directly
from the browser (via the Supabase JS client and the anon key — read-only, RLS should restrict
this key to `select` on `hn_buzz_runs` only) and renders four panels with Chart.js:

1. **Leaderboard** — latest complete run, ranked by Buzz Score, breakouts and low-confidence
   rows flagged.
2. **7-day / weekly trend** — Buzz Score over time for an entity picked from a dropdown, with a
   dashed vertical marker at each `watchlist_version` boundary (so a v1→v2 entity-list change
   reads as a visible break in the series, not a silent discontinuity — per the watchlist
   governance rule in `plan.md`).
3. **Narrative theme breakdown** — a doughnut of the latest run's per-entity `narratives.theme`
   values. Degrades to an explicit placeholder message if the run predates the Week 7 LLM layer
   or the LLM key was unset (no `narratives` column data) — no silent empty chart.
4. **Community Opinion** — placeholder only. This is Week 9 work; the panel says so rather than
   pretending to show data that doesn't exist yet.

Colors are the six `brutalist/DESIGN.md` tokens only (ink/red/secondary/border/ochre/white), with
the dark-mode block from that file, per the repo-wide visual-media rule. Red is reserved for the
primary series (Buzz Score) and breakout flags; ochre marks the version-boundary line only
(decorative/annotation, never a data-encoding color, per DESIGN.md).

## Why static HTML behind an n8n webhook, not a separate app

The plan calls for `GET /webhook/dashboard` serving HTML from the existing n8n instance — no new
server or hosting to run. Wiring:

1. Add a **Webhook** node: `GET /dashboard`, "Respond" set to "Using Respond to Webhook Node".
2. Add a **Read Binary File** node (or a **Code** node that reads `dashboard/index.html` from a
   volume mounted into the n8n container) pointing at this file.
3. Add a **Respond to Webhook** node with response type "Text", content-type `text/html`, body =
   the file contents.

This wasn't added to `Hacker News AI Tracker.json` in this pass: the repo export is already
flagged stale as of Week 7 ("still reflects the pre-Week-7 graph"), and wiring a webhook node
correctly (path, binary-vs-text response mode, container file mount) needs verifying against a
running n8n instance before it's committed to the exported graph, not guessed at from outside
it. Doing it by hand against the live n8n and re-exporting is Week 12 work per the plan
("export `workflow.json`" is an explicit Week-12 deliverable); until then this note plus the
static file are the artifact.

## Local testing without live Supabase/n8n

No `SUPABASE_URL` / `SUPABASE_ANON_KEY` are configured in this environment's `.env` (both empty),
and there's no running n8n instance here either, so the panels can't be exercised against a live
table right now. To make the rendering logic testable anyway:

* `dashboard/fixture_runs.json` is the real Week 5 backfill output (`backfill_output/backfill_v1.json`,
  13 weekly rows, `watchlist_version: "v1"` throughout) — same shape `hn_buzz_runs` rows have.
* Opening `dashboard/index.html?mock=1` (or opening it directly, since the page falls back to
  mock mode when no Supabase config is injected) fetches this fixture instead of Supabase.
* To point it at a real project: inject `window.__SUPABASE_URL__` / `window.__SUPABASE_ANON_KEY__`
  before the main script runs (e.g. a small `<script>` tag or the webhook response wrapping the
  file with those two lines templated in from n8n environment variables) — the anon key is safe
  to expose client-side only if RLS on `hn_buzz_runs` restricts it to `select`.

**Verified live (Om Mali, 2026-07-21):** the webhook wiring works end to end against the running
n8n instance and a real Supabase project — `GET /webhook/dashboard` returns the injected HTML and
the browser renders all four panels against live `hn_buzz_runs` data. Full node graph is in
`Hacker News Dashboard.json` (a separate workflow file from the main pipeline's
`Hacker News AI Tracker.json` — this is intentionally a standalone workflow, not merged into the
daily-run graph).

### Bugs found and fixed while wiring this up (not anticipated in the original design)

* **Malformed response expression.** `Respond to Webhook`'s `responseBody` was typed as
  `"= {{ $json.html }}"` (space after `=`) instead of `"={{ $json.html }}"` — n8n expressions must
  have no space after the leading `=`. Fixed in `Hacker News Dashboard.json`.
* **File-access sandboxing.** `Read/Write Files from Disk` only allows reads under
  `/home/node/.n8n-files` by default (`N8N_RESTRICT_FILE_ACCESS_TO`). The original plan mounted the
  dashboard folder at an arbitrary `/data/dashboard` path, which threw `NodeApiError: Access to the
  file is not allowed`. Fixed by remounting at `/home/node/.n8n-files/dashboard` in
  `docker-compose.yml` and updating the node's `fileSelector` to match.
* **`$env` blocked in Code nodes by default.** n8n blocks environment-variable access from
  Code/Function nodes since 1.x for security (`N8N_BLOCK_ENV_ACCESS_IN_NODE`, default `true`).
  Set to `false` in `docker-compose.yml` for the `n8n` service, and added `env_file: [.env]` so
  `SUPABASE_URL`/`SUPABASE_ANON_KEY` reach the container without hardcoding them anywhere.
* **First-occurrence-only `.replace()`.** The injected placeholder script originally referenced
  each `%%TOKEN%%` twice (once in a `.startsWith('%%')` guard, once as the fallback value) to make
  a direct `file://` open degrade to mock mode. `.replace()` only swaps the *first* match, so the
  second, unreplaced token silently became the literal string value handed to
  `supabase.createClient(...)`, producing `Failed to construct 'URL': Invalid URL`. Fixed by
  referencing each token exactly once in `dashboard/index.html`, moving the "not yet injected"
  detection to a `.includes('%%')` check instead, and switching the Code node to `.replaceAll()`
  as a defense against this class of bug recurring.
* **Wrong Supabase key.** The key initially placed in `.env`/wired through was the `service_role`
  key (`"role":"service_role"` in its JWT payload), not `anon` — full read/write/delete access to
  the whole project, exposed client-side. Caught before shipping; rotated in Supabase and replaced
  with the actual `anon` key. **Anyone repeating this wiring should double check the JWT payload's
  `role` claim before using a Supabase key client-side, not just its length/shape.**
* **`navigator.locks` denied.** `supabase-js` v2's `GoTrueClient` acquires a startup lock via the
  Web Locks API regardless of `persistSession`; some browser/context combinations deny that API
  outright (`SecurityError: ... LockManager ... denied`). Fixed by passing a no-op `auth.lock`
  override in the `createClient` call — this dashboard is read-only with no user session, so there
  is nothing to lock in the first place.
* **`community_opinions` column missing.** The live `hn_buzz_runs` table predates that column being
  added to `DATABASE_SETUP.md`'s schema (it's Week 9 work — the Community Opinion analyzer doesn't
  exist yet). Dropped it from the dashboard's `.select()` list for now; add it back to both the
  `.select()` and an `alter table` migration when Week 9 lands.

**Not yet verified:** the version-boundary marker's "boundary exists" rendering path (fixture and
live data are both all-`v1` today; genuinely untestable until Week 11's watchlist v2) and an
explicit RLS write-rejection check confirming the `anon` key truly can't mutate `hn_buzz_runs`
(recommended as a one-time manual check, not automated here).

## Because there is no live watchlist-v2 yet

The version-boundary marker logic is written and exercised against the fixture (which is all-v1,
so today it draws zero boundary lines) but is only meaningfully testable once Week 11 introduces
v2. Noting this now so it isn't mistaken for untested code later — it's tested against the
"no boundary" case; the "boundary exists" case is deferred to Week 11 by the plan itself.
