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
