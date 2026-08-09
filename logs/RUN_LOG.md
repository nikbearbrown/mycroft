# Run Log

Use this file for meaningful recipe runs, blockers, generated artifacts, and
workflow changes.

## Template

```markdown
## YYYY-MM-DD -- Short task name

- **Recipe:** ...
- **Inputs:** ...
- **Commands:** ...
- **Outputs:** ...
- **Result:** ...
- **Open issues:** ...
```

## 2026-06-13 -- Bring Mycroft to Madison parity (instruction build + gate stack)

- **Skill:** Refactor Mycroft's agent context to the source-vs-adapter + enforced-gate architecture, reusing Madison's shared rule-module library.
- **Inputs:** Madison as template; Mycroft was earlier-stage (hand-written 18L/17L CLAUDE/AGENTS, no SNICKERDOODLE.md/DOMAIN.md/conformance.mjs).
- **Commands:** Ported `conformance.mjs` (SKIP mycroft-main), `to-markdown.mjs`, `build-instructions.mjs`. Added the constitution `SNICKERDOODLE.md` (the generic cross-domain one) + a new `DOMAIN.md` index. Vendored the 6 `_shared/` instruction modules; wrote `instructions/manifest.yml` (selects all 6 — it now has the backing tools/files) + `instructions/mycroft.md` (identity + Mycroft help menu: 99 recipes, 17 chapters, the gate scripts). Built + promoted root `AGENTS.md` (72L, generated) + `CLAUDE.md` (10L, `@AGENTS.md` import). Scaffolded `.claude/` hooks (archive-guard + conformance-check) + `.github/workflows/verify.yml` CI (conformance + drift guard). Updated package.json (verify/build-instructions/to-markdown) + .gitignore (build scratch + mycroft-main quarantine).
- **Outputs:** generated AGENTS.md/CLAUDE.md; SNICKERDOODLE.md, DOMAIN.md; instructions/ tree; ported scripts; .claude/ + .github/; package.json + .gitignore.
- **Result:** Mycroft now runs the same stack as Madison — generated instruction files (idempotent rebuild verified), conformance, hooks, CI drift guard. All checks pass. The two repos share the same `_shared/` module library (vendored per-repo so they can diverge); Mycroft's manifest selects all 6, Madison's the same 6 — proving the select-what-you-use design.
- **Open issues:** `_shared/` modules are vendored (one copy per repo) — kept in parity by hand for now; a shared-home/submodule is a later option if strict DRY is wanted. Mycroft has no prompts/ suites yet (content, not infra — not part of gate-stack parity).

## 2026-06-14 -- Research finance recipe opportunities

- **Recipe:** Research pass for entry- and mid-level finance recipe opportunities in Mycroft.
- **Inputs:** `SNICKERDOODLE.md`, `DOMAIN.md`, `DATA_CONTRACT.md`, `docs/recipes.md`, existing finance recipes and templates, plus current external grounding from BLS, SEC EDGAR API docs, FRED API docs, and PCAOB audit-evidence standards.
- **Commands:** Scanned existing finance recipe coverage with `find`/`rg`; reviewed representative recipes (`mycroft-financial-intelligence-hub`, `forecasting`); wrote a reusable deep-research prompt and the resulting research synthesis.
- **Outputs:** `reports/generated/entry-mid-finance-recipes-deep-research-prompt.md`; `reports/generated/entry-mid-finance-recipes-research.md`.
- **Result:** Identified highest-value gaps for finance practitioners: variance packs, budget-vs-actual commentary, reconciliations, close/flux analysis, AP/AR exception review, cash forecasting, KPI lineage, SEC filing comparison, covenant monitoring, audit binders, and CFO/board packet source checks.
- **Open issues:** These are research recommendations, not implemented recipes. Next pass can turn the top candidates into `recipes/` files and matching report templates.

## 2026-06-14 -- Add attached finance practitioner-map research

- **Recipe:** Add Bear's attached finance recipe-opportunity research to the Mycroft finance research corpus.
- **Inputs:** `/Users/bear/.codex/attachments/d6e90db6-64d5-4408-98a6-261e8381959f/pasted-text.txt`; existing `reports/generated/entry-mid-finance-recipes-research.md`.
- **Commands:** Copied the attached research into `reports/generated/mycroft-finance-recipe-opportunities-attached-research.md`; merged its most useful additions into the main finance synthesis.
- **Outputs:** `reports/generated/mycroft-finance-recipe-opportunities-attached-research.md`; updated `reports/generated/entry-mid-finance-recipes-research.md`.
- **Result:** Main report now includes the 22-recipe candidate map, occupational baseline, explicit do-not-automate list, additional recipe cards for budget requests/daily cash/control evidence/revenue billing, a stricter finance gate stack, concrete internal data contracts, and a revised build sequence.
- **Open issues:** Still research only; recipes and report templates have not yet been scaffolded.

## 2026-06-14 -- Rewrite TIKTOC for finance practitioner guide

- **Recipe:** Full TIKTOC architecture rewrite for Mycroft as a finance recipe engine.
- **Inputs:** Attached finance recipe opportunity research, attached Causal Reasoning TIKTOC template, existing Mycroft placeholder chapters, existing Mycroft finance recipes, `reports/generated/entry-mid-finance-recipes-research.md`, and `the-reallocation-engine/chapters` structure.
- **Commands:** Read attachments and existing chapter structure; compared against `the-reallocation-engine/chapters`; rewrote `TIKTOC.md` as a full architecture document with concept, learner profile, deployment, repo grounding, field positioning, act structure, chapter list, learning outcomes, running project, chapter anatomy, recipe strategy, risks, and open questions.
- **Outputs:** Updated `TIKTOC.md`.
- **Result:** `TIKTOC.md` now mirrors the reallocation-engine pattern: intro, chapters 1-5 framework, chapters 6-15 concrete finance practitioner recipes, chapter 16 honest run, and 97-99 appendices/back matter. It explicitly shifts the book from agentic investment intelligence toward entry/mid-level finance workflow recipes.
- **Open issues:** Current `chapters/01-chapter-01.md` through `chapters/12-chapter-12.md` are still placeholders and should be renamed or rewritten in a later chapter-writing pass.

## 2026-06-14 -- Gather research notes for missing finance chapters

- **Recipe:** Chapter Research Gatherer for the new Mycroft finance TIKTOC.
- **Inputs:** `TIKTOC.md`, finance research reports in `reports/generated/`, shared markdown library `/Users/bear/Documents/CoWork/bear-textbooks/MD`, official web grounding from BLS, SEC EDGAR API docs, FRED API docs, and PCAOB AS 1105.
- **Commands:** Extracted proposed named chapters 01-16 from `TIKTOC.md`; scanned 312 shared-library markdown files; copied 8 relevant `_lib_*.md` files into `pantry/`; generated chapter notes with `node scripts/generate-finance-chapter-research-notes.mjs`; inspected index and sample notes.
- **Outputs:** `pantry/chapter-research-index.md`; `pantry/01-the-fluency-trap_notes.md` through `pantry/16-the-build-and-the-honest-run_notes.md`; 8 `_lib_*.md` files; `scripts/generate-finance-chapter-research-notes.mjs`.
- **Result:** Every proposed named chapter now has a pantry research note covering TIKTOC summary, conceptual foundations, domain cases, dependencies, current field state, teaching considerations, and source references. The index records that the existing `chapters/01-chapter-01.md` style files are placeholders and the named chapter files remain missing.
- **Open issues:** Notes are research scaffolding, not chapter drafts. A later TIKTOC-driven writing pass should rewrite/rename the chapter files.

## 2026-06-14 -- TIKTOC-driven finance chapter write

- **Recipe:** Chapter Writer for Mycroft Finance Recipe Engine.
- **Inputs:** `TIKTOC.md`, `book.md`, pantry research notes, copied `_lib_*.md` files, finance research reports, and existing `chapters/97-fundamental-themes.md`.
- **Commands:** Read attached Chapter Writer prompt; confirmed named chapters from `TIKTOC.md` were missing while placeholder `chapters/01-chapter-01.md` style files still exist; generated named finance chapters with `node scripts/write-finance-tiktoc-chapters.mjs`; inspected representative chapter files and `logs/log.csv`.
- **Outputs:** Added `chapters/01-the-fluency-trap.md` through `chapters/16-the-build-and-the-honest-run.md`; rewrote `chapters/97-fundamental-themes.md` as a finance-specific appendix; added `scripts/write-finance-tiktoc-chapters.mjs`; appended chapter metadata to `logs/log.csv`.
- **Result:** The named Mycroft finance chapter set now mirrors the reallocation-engine style: framework chapters 01-05, concrete finance recipes 06-15, and an honest-run capstone in 16.
- **Open issues:** The older placeholder files `chapters/01-chapter-01.md` through `chapters/12-chapter-12.md` still exist and should be archived or superseded in a later cleanup pass if Bear approves.

## 2026-07-09 -- Add vendor-intelligence-brief recipe (Phase 1 scaffold)

- **Recipe:** vendor-intelligence-brief v0.1.0 (DRAFT) — structured vendor intelligence brief (6 sections, sourced).
- **Inputs:** User's existing vendor intelligence platform (5 specialized agents, supervisor routing, PostgreSQL signal storage, Neo4j competitive graph).
- **Commands:** 
  - Created `recipes/vendor-intelligence-brief.yaml` with full frontmatter, inputs/outputs, 5 phase gates (3 Phase 2 placeholders), architecture, and known issues.
  - Created `data/verified/ai_company_signals-schema.yaml` (signal table schema, validation rules, data quality notes, audit checks).
  - Updated `DATA_CONTRACT.md` to register vendor intelligence data layer + signal validation gate.
  - Logged this run in `logs/RUN_LOG.md` with status, blockers, and next steps.
- **Outputs:** 
  - `recipes/vendor-intelligence-brief.yaml` (DRAFT, 200L)
  - `data/verified/ai_company_signals-schema.yaml` (schema + validation rules)
  - Updated `DATA_CONTRACT.md` (vendor intelligence section)
  - This log entry
- **Result:** Mycroft vendor intelligence framework scaffolded at Phase 1 (DRAFT → SPECIFIED).
- **Blockers:**
  - [GATE OPEN] Signal validation (Phase 2) — zero signals validated; gate process not yet defined.
  - [GATE OPEN] Supervisor routing review (Phase 2) — Langfuse traces not logged to RUN_LOG.
  - [GATE OPEN] Brief approval (Phase 2) — no procurement owner review process.
  - [BLOCKER] Groq token limit at company #33 of 50 batch — blocks Phase 3 daily batch job.
- **Next steps:**
  - Phase 1 → Phase 2: Define signal validation gate (audit script, human sign-off process).
  - Phase 1 → Phase 2: Add gate decision logging to RUN_LOG (when running sample brief).
  - Phase 1 → Phase 2: Define brief approval gate (procurement owner + sign-off rule).
  - Phase 2: Run full sample brief (company: "Anthropic") with all gates open (no human decision yet, just logging).
  - Phase 2: Generate `signals-validation-audit.md` (spot-check 10 signals, assess quality).
  - Phase 3: Solve Groq token limit (upgrade tier or secondary provider for news classification).

## 2026-07-11 -- Hacker News AI Buzz Tracker: historical backfill, baselines, and watchlist-version guard

- **Recipe:** Hacker News AI Buzz Tracker (`data/raw/Hacker_News_AI_Buzz_Tracker/`) — historical backfill and trailing-baseline phase.
- **Inputs:** the project's 12-entity v1 watchlist config, existing scoring/parsing code from earlier phases (reused as-is, not rewritten), the Hacker News Algolia `search_by_date` API, Supabase (`hn_buzz_runs`, plus two new tables: a dedicated backfill table and an entity-baseline table).
- **Commands:**
  - Wrote and ran a 90-day historical backfill script (dry-run first, then live) — weekly chunked, paginated Algolia pulls, deduped by story ID, scored with the existing scoring code, inserted into the new dedicated backfill table.
  - Wrote and ran a trailing-baselines script against the backfilled data into the new entity-baseline table.
  - Diagnosed and fixed an Algolia query-matching bug (unquoted short terms, e.g. one entity's ticker-style term, matched hundreds of unrelated stories; some terms returned zero real hits) by quoting every query term and enabling exact-phrase matching, in both the backfill script and the live n8n workflow.
  - Fixing the live workflow required adding a separate quoted-term field threaded through the workflow's node schema, since an existing merge step matched the API's echoed query string against the original unquoted term field.
  - Migrated the live snapshot table to add a `watchlist_version` column and updated the live workflow's previous-run read query, row-builder, and insert step to close a gap: the version tag previously existed only as metadata on the backfill table, with no structural guard against a future watchlist-version comparison in the live velocity lookup.
  - Ran the live workflow manually post-migration to confirm the guard works without breaking velocity computation.
- **Outputs:** new backfill script and trailing-baselines script, updated live n8n workflow export, updated database setup documentation (new table schemas + migration note).
- **Result:** 13 weekly backfilled rows in the new backfill table (verified: full entity coverage per row, no duplicates, internally consistent confidence/score flags, query-matching fix holding at scale); one row per entity in the new baseline table; watchlist-version guard live and confirmed on a partial manual test run (velocity computed correctly, non-cold-start).
- **Open issues:**
  - [GATE OPEN] Full-watchlist live-run regression test of the watchlist-version guard — only tested with a subset of entities so far.
  - [BLOCKER] Backfilled engagement totals (points/comments) carry a look-ahead risk, since the source API returns current rather than point-in-time totals — unresolved; story count designated the primary metric for downstream analysis to route around it.
  - [GATE OPEN] Signal-validation backtest (pooled panel design with entity fixed effects, multiple-comparison correction, lead-lag test) specified but not yet implemented.

## 2026-07-16 -- Hacker News AI Buzz Tracker: signal-validation backtest (Week 6)

- **Recipe:** Hacker News AI Buzz Tracker (`data/raw/Hacker_News_AI_Buzz_Tracker/`) — Week 6 signal-validation backtest (early Phase 2).
- **Inputs:** Week 5 backfill (`backfill_output/backfill_v1.json`, 12 entities × 13 weeks, storyCount as primary point-in-time-safe metric); Alpha Vantage daily closes for the 9 public-ticker entities; `watchlist.json`.
- **Commands / artifacts:**
  - Installed and pinned the stats stack (`pandas`, `scipy`, `statsmodels`) in `requirements.txt`.
  - Wrote `docs/backtest_preregistration.md` **before** computing any correlation (lag family, metric, pooled-panel design, BH-FDR, bidirectional tests, weight-tuning decision rule, limitations all fixed up front).
  - Wrote and ran `fetch_prices.py` → `backfill_output/prices_v1.json` (9 tickers, 100 daily closes each, 2026-02-20 → 2026-07-15; rate-limit-aware + cached).
  - Wrote and ran `run_backtest.py` → `backfill_output/backtest_results.json` (pooled Pearson over 9 entities, 7-test lag family, BH-FDR q=0.05, both directions, per-entity descriptive).
  - Wrote `signal_validation.md` (the Week 6 deliverable report).
- **Result:** **Null result.** 0 of 7 pooled tests survive FDR. Forward buzz→price leads ≈0 / slightly negative; strongest raw cell is price→buzz at 2wk (r=0.23, p=0.027, q=0.19 — fails FDR), consistent with buzz reacting to, not leading, price. Investment framing downgraded to *unproven*, honestly, per the "building to learn" spirit.
- **Decision (logged):** Keep Buzz Score weights unchanged (30/30/20/20) per the pre-committed rule — no forward lead survived FDR with |r|≥0.20, so there is no validated target to tune toward; tuning would overfit a null. Re-evaluate at ≥26 weeks of backfill.
- **Open issues:**
  - [GATE OPEN] Human attestation (adequacy sign-off) of the backtest design and null verdict — machine conformance done (scripts run, JSON valid); human judgment pending.
  - Carried from Week 5: `watchlist_version` guard still missing on the live table (not blocking Week 6; must close before Week 11 v2 expansion).
  - Caveat: pooled Pearson p-values are optimistic under within-entity serial autocorrelation (bias runs downward, toward significance). The forward leads fail to clear even that lowered bar, so an autocorrelation-robust test would push the p-values up and leave them more clearly null — the bias runs against the null yet the null holds, which strengthens the verdict rather than threatening it. [Correction 2026-07-18: an earlier version of this caveat mis-stated the bias as "cutting toward the null"; the conclusion (verdict unchanged) was right but the reasoning was inverted — fixed here and in the report.]

## 2026-07-16 -- HN Buzz Tracker: Week 6 backtest attestation (gate cleared)

- **Recipe:** Hacker News AI Buzz Tracker — Week 6 signal-validation backtest.
- **Who/what/when:** Om Mali re-ran `run_backtest.py` independently (output matched the report exactly), hand-checked NVIDIA 2026-04-17 (storyCount 31 / NVDA close 201.68 against source files), and ran two break-checks (panel = 9 public entities; the 2026-07-03 holiday correctly falls back to the 2026-07-02 close). Adequacy sign-off and honest "did not test" list recorded in `docs/backtest_attestation.md`.
- **Result:** Human attestation gate **[GATE CLEARED]** by Om Mali, 2026-07-16. Null verdict accepted; keep-weights decision accepted; investment framing downgraded to *unproven* pending ≥26 weeks of backfill. This closes the [GATE OPEN] from the 2026-07-16 backtest entry above.

## 2026-07-16 -- HN Buzz Tracker: Week 7 LLM narrative layer

- **Recipe:** Hacker News AI Buzz Tracker — Week 7 LLM narrative/theme/tone layer.
- **Inputs:** project `GROQ_API_KEY` (Groq cloud, OpenAI-compatible endpoint); watchlist.json; live HN Algolia top stories; `metric_generation.parse_hit` (reused).
- **Commands / artifacts:**
  - Resolved the "free LLM" decision empirically: `GET /openai/v1/models` to list reachable models + a JSON-mode smoke test. Default `llama-3.3-70b-versatile`, fallback `llama-3.1-8b-instant`, Claude alt — documented in `docs/llm_narrative_design.md`.
  - Wrote `llm_narrative.py`: per-entity narrative/theme/tone via Groq (Claude path too), grounded prompt, controlled vocab, JSON mode, total graceful degradation.
  - Wrote `docs/llm_narrative_design.md` (model decision + prompt design + n8n integration steps for the user).
- **Result (verified):** Live NVIDIA → theme `controversy`, tone `neutral` (grounded in the GPU circular-financing story); offline GPT-5 fixture → `launch`/`neutral`; no-key path → `degraded=true` with reason. Unit checks passed: off-vocab enum coerced+flagged, prose-wrapped JSON parsed, garbage input → degrade. `py_compile` clean; workflow JSON unchanged and conformance-valid.
- **Open issues:**
  - [USER STEP] n8n workflow integration (add Groq credential + HTTP Request LLM node + rewire + persist `narratives`) is documented but must be applied and runtime-verified in the user's n8n — not testable from here (Pyodide code nodes have no network; needs live Postgres/SMTP). Steps in `docs/llm_narrative_design.md` §6.
  - Note: `ANTHROPIC_API_KEY` not set, so the Claude path is built but untested against the live Anthropic API.

## 2026-07-18 -- HN Buzz Tracker: Week 7 n8n LLM integration verified in n8n

- **Recipe:** Hacker News AI Buzz Tracker — Week 7 LLM narrative layer, live n8n verification (closes the [USER STEP] above).
- **What was applied (by Om Mali, in the running n8n):** Created a Groq Header-Auth credential; added `Explode Entities` (Code) → `LLM Narrative (Groq)` (HTTP Request, Body = "Using JSON" `{{ $json.groqBody }}`) → `Merge Narratives` (Merge, combine-by-position) → `Attach Narratives` (Code) → the three existing consumers; extended `Save Snapshot` INSERT to persist the `narratives` column.
- **Debugging notes (found during wiring):** (1) HTTP body must be "Using JSON", not "Using fields below" — a blank-named field yielded `{"error":"invalid syntax"}`. (2) This n8n build exposes neither an "Include Input Fields" toggle nor `_('Node')` in Python code nodes, so input (`entity`/`row`) is recombined with the Groq response via a Merge/combine-by-position node instead of passthrough. (3) Feeding only the single `topStory` gave a thin/misleading narrative; switched the prompt to the top 3 stories.
- **Result (verified):** Ran with NVIDIA enabled — `Attach Narratives` returned the full run row with the NVIDIA leaderboard entry carrying `narrative`/`theme`/`tone` (theme `controversy`, grounded in the Apple-overtakes-Nvidia + Chinese-alternatives stories) and a top-level `narratives` map; the row was written to `hn_buzz_runs` with a non-null `narratives` column. LLM narrative layer now confirmed working end-to-end in n8n.
- **Open issues:**
  - [OPTIONAL] Missing-key degrade path recommended to test once in n8n (bad Groq key → run completes with null narratives). Python-side degrade already verified 2026-07-16.
  - The repo's exported `Hacker News AI Tracker.json` still reflects the pre-Week-7 graph; re-export from n8n to sync the file (or defer to the Week 12 export deliverable).

## 2026-07-21 -- HN Buzz Tracker: Week 8 dashboard (build only, render/webhook unverified)

- **Recipe:** Hacker News AI Buzz Tracker — Week 8 dashboard.
- **Artifacts:** `dashboard/index.html` (static Chart.js: leaderboard, per-entity trend with watchlist-version boundary markers, narrative-theme breakdown, Community Opinion placeholder — colors restricted to the `brutalist/DESIGN.md` six-token palette); `dashboard/fixture_runs.json` (copy of `backfill_output/backfill_v1.json`, used for `?mock=1` local testing); `docs/dashboard_design.md` (design rationale + n8n `GET /webhook/dashboard` wiring spec, not yet applied to the exported graph).
- **Result:** JS syntax checked clean (`node -e` parse); `fixture_runs.json` passes `node scripts/conformance.mjs`. **Not verified:** actual browser rendering of the four panels (no browser tool in this session) and the live n8n webhook wiring (no running n8n instance here, and no `SUPABASE_URL`/`SUPABASE_ANON_KEY` configured in this environment's `.env`).
- **Open issues:**
  - [USER STEP] Open `dashboard/index.html?mock=1` in a browser and confirm all four panels render before this counts as done against the plan's "test the dashboard render" step; capture `preview.png` for the Month 2 milestone PR once confirmed.
  - [USER STEP] Apply the Webhook → Respond to Webhook wiring in `docs/dashboard_design.md` to the running n8n instance; re-export `Hacker News AI Tracker.json` (already deferred to Week 12 per plan.md).
  - Version-boundary marker logic only exercised against the "no boundary" case (fixture is all-v1); real test waits on Week 11's watchlist v2.
  - Carried open: `watchlist_version` guard missing on the live table (Week 5); this is unrelated to the dashboard and tracked separately.

## 2026-07-21 -- HN Buzz Tracker: Week 8 dashboard verified live (closes the [USER STEP]s from the earlier Week 8 entry)

- **Recipe:** Hacker News AI Buzz Tracker — Week 8 dashboard, live n8n + Supabase verification.
- **What was applied (Om Mali, in the running n8n/Docker/Supabase):** Built `Hacker News Dashboard.json` as a standalone workflow (Webhook -> Read/Write Files from Disk -> Extract from File -> Inject Config Code node -> Respond to Webhook); remounted `./dashboard` at `/home/node/.n8n-files/dashboard` in `docker-compose.yml` (the default-allowed path for file-read nodes); added `env_file: [.env]` + `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` so the Code node injects `SUPABASE_URL`/`SUPABASE_ANON_KEY` from the container env rather than hardcoding them.
- **Bugs found and fixed during wiring (full detail in `docs/dashboard_design.md`):** malformed `={{ }}` response expression; file-access sandbox restriction; `$env` blocked by default; a `.replace()`-first-match-only bug that silently left a literal `%%SUPABASE_URL%%` token as the "real" value; a `service_role` key mistakenly wired in place of `anon` (caught before shipping, rotated in Supabase); a `navigator.locks` `SecurityError` from `supabase-js`'s default auth-lock behavior (fixed with a no-op `lock` override); `community_opinions` requested in the dashboard's query before that column exists on the live table (dropped from `.select()` until Week 9 adds it).
- **Result (verified):** `GET http://localhost:5678/webhook/dashboard` returns the live, key-injected dashboard HTML; confirmed rendering in a browser against real `hn_buzz_runs` data (leaderboard, trend chart, theme breakdown/placeholder, Community Opinion placeholder).
- **Open issues:**
  - [USER STEP, recommended] Explicitly confirm the `anon`-role RLS policy on `hn_buzz_runs` rejects writes, not just that reads succeed — the anon key is visible in the page's source, so RLS is the only thing keeping that safe.
  - `preview.png` screenshot and the Month 2 milestone PR (Weeks 5-8) are still open — not done as part of this entry.
  - Carried from Week 5: `watchlist_version` guard still missing on the live table.

## 2026-07-22 -- HN Buzz Tracker: Week 9 Community Opinion analyzer (build + LLM smoke-test; n8n wiring/migration documented, not yet applied)

- **Recipe:** Hacker News AI Buzz Tracker — Week 9 Community Opinion analyzer (`data/raw/Hacker_News_AI_Buzz_Tracker/`).
- **Artifacts:** `community_opinion.py` (HN Firebase comment fetch, HTML-cleaning/dedupe, per-entity LLM opinion analyzer, cross-entity sector-theme clustering — mirrors `llm_narrative.py`'s Groq/Claude plumbing); `tests/test_community_opinion.py` (12 fixture tests, no network); `docs/community_opinion_design.md` (fetch strategy, token budget, prompt design, degrade table, `community_opinions` column migration SQL, n8n node-wiring spec mirroring `docs/llm_narrative_design.md`).
- **Result:** `tests/test_community_opinion.py` 12/12 passed. `python community_opinion.py --demo` hit this environment's real `GROQ_API_KEY`, got an API error on that call, and returned a clean `degraded=true` record — degrade contract confirmed live, not just in fixtures. `python community_opinion.py --sector --demo` succeeded against the real key and returned a genuine clustered sector narrative from two fixture entity opinions.
- **Not verified / open:**
  - [USER STEP] `alter table hn_buzz_runs add column if not exists community_opinions jsonb` — must be applied to the live Supabase table (it predates this column; same gap that caused the Week 8 dashboard's `column does not exist` error).
  - [USER STEP] The n8n node wiring in `docs/community_opinion_design.md` §8 (comment-fetch loop, Clean Comments Code node, Community Opinion + Cluster Sector Themes HTTP nodes, Save Snapshot INSERT extension) — needs applying and verifying against the running n8n instance, same pattern as Weeks 7-8.
  - Live comment-fetch path (`fetch_comments_for_story`) untested against a real entity this session — only LLM/parsing/degrade layers were smoke-tested.
  - Dashboard's Community Opinion panel (Week 8) remains a placeholder until this pipeline is live; wiring it is separate follow-up work.

## 2026-07-25 -- HN AI Buzz Tracker — Weeks 10-12 (attribution fix, digest, contract, config, launch)

- **Recipe:** Hacker News AI Buzz Tracker — Weeks 10-12 (`data/raw/Hacker_News_AI_Buzz_Tracker/`).
- **Constraint:** did NOT modify `Hacker News AI Tracker.json` (read-only for understanding); all code changes in `node code/` + reference modules + docs, per standing instruction.
- **Week 10 (verified):** `node code/Get Metrics.py` now relevance-filters top-story selection (query term must be in the story TITLE) — fixes the Bento misattribution where a name-drop Show HN topped OpenAI & Anthropic. Metrics stay over all hits; only narrative/opinion attribution is gated. New reference `story_relevance.py` + `tests/test_story_relevance.py` (8 fixtures incl. the real Bento case). `docs/relevance_fix_design.md`. Richer digest in `node code/Code in Python1.py` (sector narrative + badges + per-entity Community Opinion). `docs/alert_logic.md`.
- **Fixed pre-existing drift:** `compute_buzz_score.py` reference was Week-3 era (no ACCEL_MIN/MAX/velocity) and broke `tests/test_scoring.py` collection → synced to `node code/Computer Buzz Score.py`; converted `test_scoring.py::test_acceleration` return→assert.
- **Week 11:** `docs/json_signal_contract.md` (schema 1.0 formalized + additive 1.1 + `/webhook/signal` spec); `config/watchlist.v1.json` (conformance ✓) + `docs/watchlist_governance.md` (version guard status + v2 protocol as a human gate, not activated).
- **Week 12:** README signals/architecture updated; `.env.example` + SMTP/service_role; `docs/launch_article.md`.
- **Commands:** `python -m pytest tests/` → **21 passed, no warnings**; `python tests/test_scoring.py` → 5 passed; digest smoke-tested with sample row; `node scripts/conformance.mjs config/watchlist.v1.json` → conform.
- **Not verified / open (human/canvas):** paste updated Get Metrics + digest into live n8n and re-verify a full run (confirm Bento no longer tops OpenAI/Anthropic; check `relevantStories`); wire `/webhook/signal` + Error-Trigger failure alert; SMTP creds; watchlist v2 approval + lockstep writer/reader edit; re-export `workflow.json`; record demo; open final PR.

## 2026-08-08 -- Private AI Valuation Agent: Week 1 feasibility verification

- **Recipe:** `data/raw/Private_AI_Valuation_Agent/plan.md` (Week 1 — reproduce the verification, scaffold, lock universe v1).
- **Inputs:** SEC EDGAR `primary_doc.xml` for 8 NPORT-P accessions across 6 fund families (Fidelity 0000024238, T. Rowe Price 0000819930, Alger 0000003521, ARK 0001905088, BlackRock 0000887509, Capital Group 0000719608), period ends 2026-03-31 through 2026-05-31.
- **Commands:** Hand transcription from EDGAR by Om Mali; `python scripts/verify_week1_marks.py`.
- **Outputs:** `data/raw/Private_AI_Valuation_Agent/` — `docs/feasibility.md`, `docs/worklog.md`, `README.md`, `.gitignore`, `.env.example`, `requirements.txt`, `scripts/verify_week1_marks.py`, `tests/fixtures/week1_verified_marks.json`, `src/` package scaffold.
- **Result:** Core hypothesis supported by first-party evidence. 19 Anthropic PBC positions verified; four independent managers priced Anthropic identically to the cent ($259.14 / $259.1364) at 2026-03-31 and 2026-04-30, and after a repricing BlackRock (5/29) and Capital Group (5/31) both marked $589.0095. Staggered fiscal quarter-ends confirmed across four distinct observation dates, so propagation is observable. Write-up-all-classes convention (Gornall & Strebulaev) reproduced on this cohort, including common and preferred at an identical mark.
- **Open issues:** **Defect in `plan.md` lines 106/400** — the specified private-position filter (`IS_RESTRICTED_SECURITY='Y' AND FAIR_VALUE_LEVEL=3 AND CUSIP='N/A'`) keeps only 1 of 6 managers: filers use `000000000` as well as `N/A` for the CUSIP placeholder, and ARK and Capital Group report `isRestrictedSec='N'` on restricted stock. `FAIR_VALUE_LEVEL=3` was the only field constant across all 19 rows; replacement filter proposed in `docs/feasibility.md` §2, recall 19/19, **precision untested**. Three further factual errors in `plan.md` logged in `docs/feasibility.md` §6. Whether the DERA bulk TSVs preserve the raw XML placeholder values is untested and is the largest remaining risk. Universe v1 not frozen — human gate still open.

## 2026-08-08 -- Private AI Valuation Agent: bulk N-PORT verified against filings

- **Recipe:** `data/raw/Private_AI_Valuation_Agent/plan.md` (Week 1 de-risking — does the DERA bulk data behave like the raw XML?).
- **Inputs:** `2026q2_nport.zip` (440.7 MB, 32 files, 5,347,869 holding rows across 14,416 submissions); `tests/fixtures/week1_verified_marks.json` (19 hand-verified Anthropic positions).
- **Commands:** `python -m src.ingest.download_bulk 2026q2 --extract`; `python scripts/check_bulk_vs_xml.py data/2026q2_nport`.
- **Outputs:** `src/ingest/download_bulk.py`, `scripts/check_bulk_vs_xml.py`, `data/2026q2_nport/` (gitignored), updated `docs/feasibility.md` §5-§9 and `docs/worklog.md`.
- **Result:** **Bulk matches raw XML exactly — 15/15 rows, 0 mismatches.** `N/A` and `000000000` CUSIP placeholders both preserved verbatim; ARK's incorrect `IS_RESTRICTED_SECURITY='N'` passed through unrepaired. The largest open feasibility risk is closed. Universe measured across the full quarter: Databricks 360 rows/152 funds, SpaceX 154/69, Anthropic 149/84, OpenAI 142/73, Anduril 130/50, Cerebras 37/28; Perplexity 7, Groq 3, Scale AI 0 (drop confirmed). Two name-match false positives caught: `%COHERE%` returns 1,094 rows of **Coherent Corp** (public, 0 at Level 3) and `%X.AI%` is mostly bank debt and 144A bonds priced per $100 face.
- **Open issues:** **New defect — filter precision.** `plan.md` line 401 predicts "a few thousand" rows out per quarter; measured 606,028 (11.3% of the quarter) for the plan's filter and 693,951 for the corrected one. `CUSIP='N/A'` is the generic no-CUSIP placeholder (1.17M rows, 21.9%), not a private-company marker. **Decision: invert the pipeline** — name-match the universe first, confirm with `FAIR_VALUE_LEVEL=3` second, reducing entity-resolution input from ~600k rows to ~1k/quarter. Also measured: 5.35M rows/quarter, not the 10-15M in `plan.md` line 214; 985 Level-3 rows have zero balance; SpaceX spans $204.64-$5,265.90 in one quarter (unit artifact confirmed). Universe v1 still not frozen — human gate open; recommendation is six companies plus SpaceX added and Cohere dropped.

## 2026-08-08 -- Private AI Valuation Agent: universe v1 frozen (GATE)

- **Recipe:** `data/raw/Private_AI_Valuation_Agent/plan.md` (Week 1 — freeze universe v1 and write the selection criteria).
- **Gate decision:** universe v1 **frozen** by **Om Mali**, 2026-08-08.
- **Inputs:** coverage measured across all 5,347,869 holding rows of 2026Q2 (`docs/feasibility.md` §8); field definitions confirmed against `nport_readme.htm` bundled in the bulk zip.
- **Outputs:** `universe_v1.json` (machine-readable, with per-company rationale), `docs/feasibility.md` §8, `docs/worklog.md`.
- **Result:** Full members (6): Databricks, SpaceX, Anthropic, OpenAI, Anduril, Cerebras. Carried thin (1): Figure AI — marks published, dispersion and propagation suppressed. Excluded (5): Cohere (false positive — all 1,094 rows are Coherent Corp, a public NYSE company, 0 at Level 3), xAI (instrument mismatch — only 7 of 58 rows are Level 3 equity; the rest is bank debt and 144A bonds priced per $100 face), Perplexity (7 rows / 6 funds) and Groq (3 rows / 3 funds) for insufficient coverage, Scale AI (0 rows). Criterion: 28+ distinct filers per quarter, judged on Level 3 **equity** rows only. Two changes from `plan.md`'s universe — **SpaceX added** (69 funds, better coverage than four listed companies) and **Cohere removed**. Cerebras retained despite being the smallest full member because its Level 3 → Level 1 IPO transition is the project's only external validity check.
- **Open issues:** Schema check surfaced that **every field in `FUND_REPORTED_HOLDING` is nullable, including `FAIR_VALUE_LEVEL`** — the one field the corrected filter depends on — so `NULL` must be handled explicitly rather than assuming `= '3'` is well-defined. `ISSUER_CUSIP` is free-text `VARCHAR2(9)`, not a validated CUSIP. Only 2026Q2 is loaded; no cross-quarter movement observed. Supabase provisioned, no schema created. 2026Q1 not downloaded (Q2 was chosen because it contains the hand-verified May/June filings).
