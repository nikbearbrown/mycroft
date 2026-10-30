

## 2026-10-02 (renumber) -- Private AI Valuation Agent: the schedule renumbered, 12 weeks to 11

- **Recipe:** `data/raw/Private_AI_Valuation_Agent/plan.md` -- the schedule itself was edited, at the user's instruction.
- **Gate decision:** none. No measurement, artifact or number changed; this is the recipe's week numbering and the documentation that cites it.
- **Change:** the two weeks covering the MCP server and the signal contract are merged into **Week 10 "Interface and the signal contract"**, and the former Week 12 becomes **Week 11 "Documentation, catalogue, and launch"**. The plan is now an 11-week schedule.

| Was | Now |
|---|---|
| Week 10 -- MCP server | **Week 10 -- Interface and the signal contract** |
| Week 11 -- Commentary graph, signal contract, scheduling | *(merged into Week 10)* |
| Week 12 -- Documentation, catalogue, and launch | **Week 11 -- Documentation, catalogue, and launch** |

- **The merge is substantive, not only bookkeeping.** Both halves exist for one reason: so that something other than this repository can consume the panel. The MCP server is the interactive reader and the signal is the machine-readable one, and the token-bounding work and the contract-freezing work are the same discipline aimed at two audiences. The merged plan entry says so, and both docs now carry a cross-link to the other as the other half of one week.
- **Files changed:** `plan.md` (entries merged, last renumbered, "12-week" -> "11-week"); `README.md` (status heading, layout line); `DATABASE_SETUP.md` (the deferred consolidated schema listing is now Week 11's job); `docs/worklog.md` (week labels in two dated entries, plus a new entry carrying the mapping table); `docs/mcp_server.md` and `docs/signal_and_commentary.md` (cross-linked, both labelled Week 10); `src/graphs/quarterly_graph.py` and `scripts/schedule.py` (docstrings citing "week 11"); `scripts/make_week1011_figures.py` (docstring).
- **Deliberately NOT changed: this log's existing entries.** `logs/RUN_LOG.md` is the governance audit trail and append-only (P7). Its entries describing "Weeks 10 and 11" were accurate when written, and rewriting them would falsify the record of what was done and when. This entry is the record of the renumbering; the mapping table above is how a later reader reconciles the two.
- **Deliberately NOT changed: the figure filenames.** `w10-*` and `w11-*` are referenced by name in the built video reels' `pantry/` directories and `beat_sheet.json` files, which live outside this repository. Renaming would break artifacts this repo does not own. All four `w10`/`w11` figures are Week 10 figures regardless of prefix, and the generator's docstring now says so. Same reasoning for `docs/_figdata_week1011.json` and `scripts/make_week1011_figures.py`.
- **Verified:** no stale `Week 12`, `Weeks 10 and 11` or `12-week` string remains outside the worklog's mapping table; `plan.md` holds 11 week entries; the suite and conformance pass unchanged.
- **Open issues:** carried forward unchanged -- **milestone PR 1 and PR 2 not opened** (git is the user's), `openai/gpt-oss-120b` substitutes for the retired model plan.md named, qualitative adjectives in the commentary unchecked by design, the Cerebras event study unblocked only when `2026q3_nport.zip` publishes, N-CSR entry dates a floor rather than a history, Week 3's live EDGAR path, non-USD currency guarded but unexercised, 314 of 322 golden-set labels unattested, and the 28 `%COHERE%` holdings still inside the shipped universe layer.

## 2026-10-09 -- Private AI Valuation Agent: Week 11, documentation, catalogue and demo

- **Recipe:** `data/raw/Private_AI_Valuation_Agent/plan.md` (Week 11 -- the final week).
- **Gate decision:** none. Documentation and a read-only demo; no measurement, schema or artifact value changed.
- **Commands:** `python -m scripts.analyze --findings`; `python -m scripts.demo --write`; `python -m pytest tests/ -q` -> **310 passed, 39 skipped**; `node scripts/conformance.mjs` over the new and changed documents -> **60 files, all conform**.
- **Outputs:** `proposal.md`, `system_architecture.md`, `data_architecture.md` (all new); `scripts/demo.py`, `docs/demo.md` (new); `n8n/README.md` (new); `scripts/analyze.py` (+sections 6 and 7), `docs/findings.md`; `docs/entity_resolution.md` (+section 11); `DATABASE_SETUP.md`; `README.md`.

- **Three of the six documents `plan.md` names did not exist.** `proposal.md`, `system_architecture.md` and `data_architecture.md` were absent entirely -- the week's audit found them rather than the week's plan predicting them. Written from the project's own measured figures and the decisions already recorded in `docs/worklog.md`, not from the plan's prose.
- **One explicit requirement had zero coverage.** `plan.md` week 11: "citing the prior-art literature honestly". A grep for Caplight, Gornall, Strebulaev, Agarwal, Chernenko and Kwon across `docs/findings.md` and `docs/entity_resolution.md` returned **0 matches in both**. The project's own plan is emphatic that this source is "commercially exploited" and "academically mature" and that "claiming novelty of the data source would not survive a literature review" -- and none of that had reached the published documents. Now in `proposal.md`, `docs/findings.md` §7 and `docs/entity_resolution.md` §11.1.
- **The citation is load-bearing in one place, and that is stated.** Gornall & Strebulaev (JFE 2020) establishes that funds write up *all* share classes to the latest round price. That is **reproduced on this cohort** and is the reason dispersion is measured at company level with the class recorded rather than within-class only -- an earlier draft's rule, overturned by the verified data. The other citations frame the contribution as open infrastructure rather than discovery.
- **`docs/findings.md` stopped at Week 8 and was extended through its generator, not by hand.** It is a generated artifact (P3), so `scripts/analyze.py` gained sections 6 (Form D x N-CSR corroboration, 10 of 18 acquisition dates landing on a filed round date, with the denominator caveat) and 7 (the literature). Regenerating reproduces them.
- **`DATABASE_SETUP.md` schema block completed.** On 2026-10-02 I found it listing only the four Week 2 core tables while the database held fifteen, and deferred the consolidated listing to this week as "Week 11's job". Done: all fifteen with row counts, verified against `information_schema`, plus the four LangGraph checkpoint tables named as not belonging to this project's schema.
- **The demo is a runnable script rather than a recording.** `scripts/demo.py` prints five acts in the order `plan.md` names them and writes `docs/demo.md`. The reasoning is in its docstring: a recording is true on the day it was made, and this re-runs with every figure queried live, so a transcript that disagrees with the database is a bug rather than an old file. **Act II is read-only on purpose** -- it displays a decision a named human already recorded and does not make a new one, because a demo that recorded a judgment would be a demo that clears a gate for the sake of a screenshot (P4). Act I likewise shows the ingest reconciliation rather than re-downloading 6 GB.
- **Catalogue entry: the path in `plan.md` does not exist here.** It says `n8n_Workflows/README.md`; this repository has no such directory and the path refers to a sibling Humanitarians AI repo. Rather than inventing a top-level directory, the entry is `n8n/README.md`, beside the workflow it describes, carrying a paste-ready catalogue row to copy across when the two repos are in the same place. Stated in the file itself so the deviation is visible.
- **Open issues:** **milestone PRs 1, 2 and 3 are not opened** -- git is the user's, and this is now the only item of the eleven-week plan outstanding on this side. Carried forward unchanged: `openai/gpt-oss-120b` substitutes for the retired model plan.md named; qualitative adjectives in the commentary are unchecked by design; the Cerebras event study unblocks only when `2026q3_nport.zip` publishes; N-CSR entry dates are a floor rather than a history; Week 3's live EDGAR path; non-USD currency guarded but unexercised; 314 of 322 golden-set labels unattested; and the 28 `%COHERE%` holdings still inside the shipped universe layer.

## 2026-10-09 -- Private AI Valuation Agent: final-week figures and narration script

- **Recipe:** `data/raw/Private_AI_Valuation_Agent/plan.md` (week 11 deliverable -- the video).
- **Gate decision:** none. Figures and a narration script; no measurement, schema or artifact value changed.
- **Commands:** `python scripts/make_week12_figures.py`; `npm run svg-to-png` (+ `audit:layout`, postinstall hook) -> **4 new SVGs, 0 layout errors, 0 warnings on them**; `node scripts/conformance.mjs` -> conforms.
- **Outputs:** `docs/_figdata_week12.json`, `scripts/make_week12_figures.py` (new); `images/private-ai-valuation-agent/w12-{docs,priorart,provenance,demo}.{svg,png}`; narration script, `figdata.json` and `images/` copied to the video folder outside this repo.
- **The `w12-` prefix is historical.** `w10-` and `w11-` were taken by figures built before the schedule merge and are referenced by name in built reels, so the final week's figures take the next free prefix rather than a renumbering that would break artifacts outside this repository. Stated in the generator's docstring.
- **Every "before" number comes from `git show HEAD:<path>`, not from memory.** The documentation audit (three of six named documents absent) and the prior-art count (0 mentions in both published documents, now 9 / 8 / 5) are both computed at build time against the last commit, so the figures cannot drift from the repository (P3).
- **The demo's read-only claim is scanned, not asserted.** The generator greps `INSERT INTO` / `UPDATE ... SET` / `DELETE FROM` across `scripts/demo.py` and `src/mcp/*.py` -> **0 across 5 files** -- the figure prints the count it measured.
- **Two accuracy-pass corrections before the figures were accepted:** the provenance chain's closing lines sat 10px from the source line (chain step tightened 30 -> 28px), and the demo figure's caption read "15 tables read" when the demo reads a subset -- reworded to "15 project tables, by layer". A third fix cleared the only layout warning, a section-sign glyph.
- **Open issues:** unchanged from the week 11 entry above; milestone PRs 1, 2 and 3 remain unopened (git is the user's).
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
## 2026-07-24 -- Project 29 regulatory workflow: Layer-1 hardening pass (working copy)

- **Context:** Inherited n8n "Financial Regulatory Intelligence System" (orig. Darshan Rajopadhye). Goal: "noise generator -> signal provider" in 4 layers; this pass = Layer 1 (hardening) + unambiguous detection bugs. Original workflow JSON is quarantined Tier 3 and left untouched.
- **Inputs:** `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json` (read-only ref) + `docs/mycroft-main/n8n_Workflows/Regulatory_Scanning_Agent/{README,DATABASE_SETUP,proposal}.md`.
- **Commands / actions:**
  - Created working copy `scripts/regulatory-intel/workflow.dev.json` (byte-identical seed; source of truth for edits — user copies node-by-node into a hand-built n8n workflow).
  - Local DB: created `mycroft_intelligence` on Postgres.app `localhost:5431` with `regulatory_feeds` (schema + indexes incl. unique `(title, DATE(published))` + `updated_at` trigger); widened `source`/`source_feed` to `TEXT`; loaded 7 sample rows. User's live n8n run reached 337 rows.
  - Applied fixes to workflow.dev.json (validated JSON after each): A1 local report path; A2 parameterized INSERT ($1..$14, jsonb via JSON.stringify+::jsonb) and removed now-redundant `Prepare Data` node; A3 per-feed retry+continueRegularOutput+alwaysOutputData on all 5 RSS nodes; A4 decode-then-escape `esc()` in Generate HTML Report; A5 `settings.timezone=America/New_York`; A6 robust new-insert detection (`Number.isInteger(id) && title`); B1 dropped the `content isNotEmpty` filter (recovers title-only items); B4 aligned report high-priority threshold `>7`->`>6`.
  - Verified: parameterized insert exercised via `pg` driver with nasty inputs (apostrophes/backslash/>255 char/RFC-822 date) in rolled-back txns; ON CONFLICT dedup returns 0 rows on duplicate. Live feed-health probe: all 5 feeds HTTP 200; Federal Register feed = 73/140 items with empty description (quantifies the B1 signal loss).
- **Outputs:** `scripts/regulatory-intel/workflow.dev.json` (8 fixes), `scripts/regulatory-intel/reports/.gitignore`; local `mycroft_intelligence` DB. Helper/mutation scripts kept in session scratchpad (not committed).
- **Result:** Insert path now robust (no more VARCHAR/quote/backslash/timeout failure class); one dead feed no longer halts the run; empty-content SEC/agency items recovered. Original workflow untouched.
- **Open issues:**
  - `Generate Email` node still has unescaped HTML + dead `>7` var; SMTP nodes hardcode `therrshan@gmail.com` — kept OFF during testing.
  - Remaining fixes: A7 (scope "Mark email sent" UPDATE to current-run ids), B2 (source mislabel — all Federal Register items tagged "…Securities"), B3 (Google News URL unwrap); optional rename of default-named "Code in JavaScript" node.
  - C1: keyword scorer (Node 10, baseline-5 compression + misfires) intentionally UNCHANGED — it is the Layer-2 benchmark baseline. Freeze baseline on the post-B1 pipeline.
  - Provenance note: shipped n8n credential pointed at abandoned remote DB `157.230.84.79:5433`; project now runs local per-developer (localhost:5431), consistent with DATABASE_SETUP.md.

## 2026-08-30 -- Project 29 regulatory workflow: A7 fix (scope Mark-email-sent update to run ids)

- **Recipe:** Project 29 regulatory intelligence hardening (Layer 1), follow-up to 2026-07-24 entry.
- **Inputs:** `scripts/regulatory-intel/workflow.dev.json`; local `mycroft_intelligence` DB @ `localhost:5431` (already running, not started for this task).
- **Commands / actions:**
  - Read the "Mark email sent" Postgres node: it ran `UPDATE regulatory_feeds SET email_sent=TRUE ... WHERE (urgency_score > 7 OR impact_level IN ('Critical','High')) AND email_sent = FALSE` — a blanket condition over the whole table, unscoped to the current run, and using a stale `>7` threshold (the "High Priority Filter" node upstream actually gates on `>6`, so the two conditions had already drifted apart).
  - Traced the node graph: `Insert data into DB` (`RETURNING *`, so `id` is present) -> `Code in JavaScript` -> `If2` -> `High Priority Filter` -> `Generate Email` -> `If` -> `Send Email Alert` -> `Mark email sent`. Every downstream node already carries the exact row ids that went into this run's email; the old query ignored them and re-derived its own (drifted) match condition.
  - Fixed: query now scopes to `WHERE id = ANY($1::int[]) AND email_sent = FALSE`, with `queryReplacement` = `$("High Priority Filter").all().map(i => i.json.id)`.
  - Verified in a rolled-back transaction against the local DB: seeded rows 3/4/5 match the old blanket condition (urgency_score/impact_level) and have `email_sent = FALSE`; ran the new query with an id list that excludes them (`[1,2,999999]`) — rows 3/4/5 were correctly left untouched, proving the old query would have silently marked them "sent" without them ever being emailed.
  - Ran `node scripts/conformance.mjs scripts/regulatory-intel/workflow.dev.json` — valid JSON.
- **Outputs:** Updated `scripts/regulatory-intel/workflow.dev.json` (`Mark email sent` node).
- **Result:** A7 closed. Mark-email-sent is now idempotent and scoped to the actual run, independent of any future drift between the alert-gate threshold and the report threshold.
- **Open issues:** B2 (source classifier — 21 Unknown Source + 157 lumped as "Federal Register - Securities"; read `Regulatory_QA/crud.py` first) and B3 (Google News URL unwrap) remain open. B3 is more involved than a regex fix: live-checked the FINRA/Investment-Advisor feeds today and confirmed modern Google News RSS links are `news.google.com/rss/articles/<opaque-id>?oc=5` with no `url=` query param, so the existing `extractRealUrl()` regex never matches; unwrapping now requires following the redirect page (JS-rendered, not a plain 302 to the article) or scraping — a separate, larger task. Per copy-paste working model, next step is telling the user which single node (`Mark email sent`) changed so they can update it in their hand-built n8n workflow.

## 2026-08-30 -- A7 addendum: measured the real drift (12 live rows), not just a rolled-back synthetic test

- **Recipe:** Same as above (A7 fix), additional verification.
- **Inputs:** local `mycroft_intelligence` DB @ `localhost:5431` (already running).
- **Commands:** Read `Keyword Analysis & Urgency Scoring`'s `determineImpactLevel()` — confirmed `impact_level` can reach `'High'`/`'Critical'` from an enforcement/fraud keyword hit alone, independent of `urgency_score`, which is exactly why the old "Mark email sent" query's `impact_level IN ('Critical','High')` clause could diverge from "High Priority Filter"'s `urgency_score > 6` gate. Queried the live table for rows matching that exact divergence (`impact_level IN ('Critical','High') AND urgency_score <= 6 AND email_sent = FALSE`).
- **Outputs:** `scripts/regulatory-intel/A7-VERIFICATION.md` — full 12-row result + honest caveats (live/growing count, forward-looking claim only, some rows are known C1-class noise).
- **Result:** 12 real rows (as of today), including genuine SEC/FINRA enforcement actions (e.g. "SEC Charges 21 Individuals With Alleged Wide-Reaching Insider Trading Scheme"), that "High Priority Filter" would never place in an email but that the old query would have silently flipped to `email_sent = TRUE`. Confirms A7 was a real, currently-latent bug, not a hypothetical edge case.
- **Open issues:** none new; B2/B3 remain open per the earlier entry.

## 2026-08-30 -- Project 29 regulatory workflow: B2 fix (source classification)

- **Recipe:** Project 29 regulatory intelligence hardening (Layer 1), follow-up to the 2026-07-24 and 2026-08-30 (A7) entries.
- **Inputs:** `scripts/regulatory-intel/workflow.dev.json` (`Normalize Data` node); live RSS feeds (all 5); `Regulatory_QA/backend/app/crud.py` (read to confirm no hardcoded `source_feed` value list — it does exact-match/GROUP BY passthrough, so new labels are safe).
- **Commands / actions:**
  - Read `identifySource()`: every `federalregister.gov` item defaulted to `'Federal Register - Securities'` unless a CFTC heuristic matched (`link.includes('commodity-futures')` or `title.includes('cftc')`).
  - Live-checked the actual CFTC Regulations RSS feed and the "securities+investment" term-search feed: Federal Register document permalinks never embed the agency slug, and CFTC titles rarely say "CFTC" literally — so the CFTC heuristic is dead code for real CFTC items. Confirmed the term-search feed pulls in unrelated agencies (FCC, EEOC, DOT-Maritime) verbatim in `dc:creator`.
  - Fixed: `identifySource()` now reads `dc:creator` (the actual issuing agency, always present and reliable on Federal Register items) — SEC/CFTC/FINRA map to their existing labels; any other named agency gets `Federal Register - <agency name>` instead of a blanket false "Securities" label.
  - Verified live: extracted old vs. new `identifySource()` into a standalone script, ran both against all 5 live feeds. Result: CFTC feed 12/12 reclassified (100% were wrong), term-search feed 83/146 reclassified, SEC/FINRA/Investment-Advisor feeds 0 changed (no regression).
  - Ran `node scripts/conformance.mjs scripts/regulatory-intel/workflow.dev.json` — valid JSON.
- **Outputs:** Updated `scripts/regulatory-intel/workflow.dev.json` (`Normalize Data` node); `scripts/regulatory-intel/B2-VERIFICATION.md`.
- **Result:** B2 closed for the Federal Register mislabeling (157-item complaint from `FINDINGS.md`). The 21 "Unknown Source" Google News fallthrough is explicitly left open — no reliable signal exists there (no `dc:creator` on Google News items; some headlines don't contain any of the matched keywords).
- **Open issues:** 21 Unknown Source (Google News fallthrough, no clear fix path), B3 (Google News URL unwrap, confirmed bigger scrape-based task).

## 2026-09-02 -- Gateway Sprint 1: request logbook

> Logged retroactively on 2026-09-10. Commit `b46d48e` merged these files on
> 2026-09-02 without a RUN_LOG entry, which the logging rule requires; this
> entry backfills the record and is not a contemporaneous account.

- **Recipe:** Adaptive Model Routing & Inference Gateway (Sprint 1 of 17). No
  recipe file yet; this builds the measurement layer routing depends on.
- **Inputs:** None. No live calls, no fixtures, no API keys, no network.
- **Commands:** `python -m pytest scripts/gateway/tests -q` (24 passed at merge)
- **Outputs:** `scripts/gateway/` — `schema.py`, `prices.py`, `prices.json`,
  `logbook.py`, `report.py`, 4 test files. Merged as `b46d48e`.
- **Result:** Append-only logbook that separates logical requests from physical
  attempts, so an escalated request's cost rolls up instead of averaging down.
  Cost is frozen at log time with its price-table version. An unpriced model
  raises instead of costing zero. The incorrect per-attempt average is kept,
  labelled incorrect, and pinned by a test ($4.65 vs $9.30 on a two-attempt
  escalation).
- **Broke during testing, fixed:** The writer used `O_APPEND` with one
  `os.write` per row, which is safe on POSIX. On Windows, concurrent appends
  through separate handles are not atomic: the concurrency test wrote 153 of
  200 rows and raised no error. Rows were lost silently. Fixed with a
  process-local `threading.Lock` plus an OS file lock on a sidecar `.lock` file.
- **Open issues:** 101 scripts under `scripts/tools|gigo|ingest/` cannot be
  imported (hyphenated filenames, underscore imports, no `__init__.py`). Not
  fixed; `scripts/gateway/` avoids that tree. See `scripts/gateway/FINDINGS.md`.

## 2026-09-10 -- Gateway Sprint 2: model connection and first live calls

> Calls 1-3 below ran on 2026-09-02 and were committed in `f8c80ee` with no
> RUN_LOG entry; they are logged retroactively here. Calls 4-6 ran 2026-09-10.

- **Recipe:** Adaptive Model Routing & Inference Gateway (Sprint 2 of 17).
- **Gate:** First live call per tier, watched by a human.
- **Cleared by:** Simba · 2026-09-10
- **Inputs:** GROQ_API_KEY (free tier); `prices.json` v2026-09-02;
  `tiers.json` v0.3.0.
- **Commands:** `python scripts/gateway/first_live_call.py [cheap|mid|strong]`
  (6 calls).
- **Outputs:** `scripts/gateway/adapters/` (`base.py`, `fake.py`, `groq.py`),
  `client.py`, `tiers.py`, `tiers.json`, `first_live_call.py`, 4 test files;
  `logs/gateway/first-live-call.jsonl` (6 rows); `FINDINGS.md` updated.
- **Result:** One client for all three tiers; every call, including failures,
  writes a logbook row before returning. All three tiers live-gated on Groq:
  `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3.6-27b`. Every
  successful call's cost was recomputed from the price table and matched the
  log exactly. A real 401 classified as `provider_error` with a row written and
  no crash. Total spend $0.00138.
- **Broke during testing, fixed:**
  - `max_tokens=16` returned empty text: `gpt-oss` spent the whole budget on
    reasoning. Raised to 256.
  - `qwen3.6-27b` returned its reasoning inline in `<think>` tags ahead of the
    answer. The response passed every gate check. Fixed with
    `strip_reasoning()` in the adapter and an answer check in the gate script;
    verified on a second live call.
  - The gate script exited 0 even when it listed problems. Now exits 1.
  - `test_the_shipped_config_loads` still asserted the Ollama tier after the
    ladder changed. Updated.
- **Findings:** see `scripts/gateway/FINDINGS.md` section 5. In short: observed
  tier spreads were 1.4x and 19-26x against sticker 2x and 10x; qwen's
  reasoning length varied 35% on an identical prompt; the strong tier used 245
  of 256 tokens; input tokens depend on the model (78 vs 17); `ok` does not
  mean the answer is usable.
- **Not verified:** Groq console usage for these calls — the one check the
  code cannot do on itself.
- **Open issues:**
  - GROQ_API_KEY used for these calls must be rotated before further use (it
    was exposed outside the terminal).
  - Groq publishes no per-token rate for the repo's evidenced Llama models;
    tiers moved to publicly priced models. See FINDINGS.md section 4.
  - All tiers share one provider and key: a rate limit or auth failure takes
    out the whole ladder. Relevant to Sprint 4.
  - `f8c80ee` committed `logs/gateway/first-live-call.jsonl.lock`, a runtime
    lock sidecar. It should be untracked and ignored.

## 2026-09-10 -- Gateway Sprint 3: task policy, router, frozen fixture set

- **Recipe:** Adaptive Model Routing & Inference Gateway (Sprint 3 of 17).
- **Gate:** Fixture labels set by a named human before any model run; set frozen.
- **Labeled and frozen by:** Simba · 2026-09-10
- **Inputs:** LLM node scripts under `scripts/tools/` and their recipes, as
  evidence of what task types Mycroft performs. No live calls, no API key.
- **Commands:** `python scripts/gateway/bench/label.py --by "Simba"` (plus
  `--ids` relabel passes); `python scripts/gateway/bench/audit.py --freeze`;
  `python -m pytest scripts/gateway/tests -q` (96 passed).
- **Outputs:** `policy.json` v0.1.0 + `policy.py` (six locked task types, per-tier
  `max_tokens`, start tier and escalation target per type); `router.py`;
  `bench/fixtures.py`, `bench/audit.py`, `bench/label.py`; 24 fixtures in
  `bench/fixtures/*.jsonl`; `bench/manifest.json` (frozen 2026-09-10, SHA-256
  per file); tests `test_policy.py`, `test_router.py`, `test_fixtures.py`,
  `test_label.py`.
- **Result:**
  - Six task types locked: sentiment, topic, structured extraction,
    contradiction detection, summarization, RAG answer. Each cites evidence
    files; a test fails if any evidence path stops existing.
  - Router is a pure function of task type and input length (characters, not
    tokens, since token counts depend on the model). Pinned and unknown task
    types are refused, never defaulted. Every decision carries a one-sentence
    explanation. The break-even rule is deliberately excluded: it is the
    Sprint 8 "clever version" and needs measured pass rates.
  - 24 synthetic fixtures, 4 per type (2 easy, 2 hard), fictional companies.
    Labeler tiers: cheap 6, mid 11, strong 7. Router: cheap 8, mid 16, strong 0.
    Router agrees with the labels on 9 of 24. The labels are predictions; this
    is not yet a measurement.
- **Decisions:**
  - Fixtures are synthetic, not real as the board specified. No real request
    corpus exists in the repo: 203 of 217 script sample payloads are generic
    placeholders, `data/raw/market-sentiment-analysis-part-1/sample/` declares
    itself synthetic, and the Klarna mock transactions file holds 0 records.
    Claims are scoped to how models handle these task types, not to Mycroft's
    traffic mix.
  - `expected_tier` means the cheapest tier the labeler expects to get it
    right: a judgment, not the router's rule applied by hand.
  - Task types and routing rules share one file so they cannot disagree.
- **Broke during testing, fixed:**
  - The labeling tool did not show the task definition (e.g. "sentiment toward
    the named company"). Now prints a `TASK:` line. `--redo` and `--ids` added.
  - The first labeling session put every fixture on cheap, traps included; the
    second used the two-question standard (trap? reasoning step?). The first
    session's fixtures were relabeled.
- **Findings:** see `scripts/gateway/FINDINGS.md` section 6. The simple router
  cannot send a short input to strong. Deterministic validators catch malformed
  answers, not wrong ones, so a misread trap returns a valid label and does not
  escalate.
- **Open issues:**
  - **Answer key flagged in review, pending the labeler's decision:** `sent-001`
    is frozen as `negative` for a headline about beating estimates and raising
    guidance; `sent-004` is `negative` though the named company won the
    contract; `contra-003` is `contradiction` where the draft had
    `insufficient_evidence` (debatable). Must be resolved — unfreeze, relabel,
    refreeze, logged — before any Sprint 7 run grades against it.
  - The label prompt says "Expected label", which reads as a prediction of the
    model's output. It means the correct answer; the wording should say so.
  - Coverage is 4 of the 30 targeted per type; 26 short per type carried over.
  - No long-input fixtures: the router's length promotion is covered by unit
    tests only.
  - One labeler; no agreement measure.
  - Recommendation for Sprint 7: run every fixture on all three tiers (about a
    cent) so the cheapest correct tier is measured rather than predicted.
- **[BLOCKER] Wrong-entity claims found in a finished brief.** `labeled_briefs.csv`
  captures a real Scale AI brief attributing to Scale AI: "a Rs 170 Cr raise by Elevate
  Education", "a $2.2 million raise by SambaNova", and "a $900m credit facility to scale
  AI data centers" — two other companies' funding rounds, plus "scale AI" matched as an
  ordinary verb phrase. Its COMPETITIVE POSITION names Ecolab (water treatment) as a
  competitor. Scale AI's seed entry carries aliases ["Scale AI", "ScaleAI"] and no
  `exclude_entities` or `exclude_terms`, so the deterministic filter had nothing to
  reject on.
  - *Effect on the gate:* **Signal validation stays CLEARED.** Its clearance on
    2026-08-22 was explicitly batch-level and named common-word names as residual risk;
    this is that risk confirmed, not a new one concealed. Decision by Muskan Khandelwal,
    2026-08-26. `last_gate` and `todos_open` unchanged.
  - *What changed:* the risk is no longer hypothetical, and it is now known to reach
    finished briefs rather than stopping at the signal table.
  - *Not yet applied:* populate `exclude_entities`/`exclude_terms` for common-word
    vendors (Adept, Writer, Notion, Glean, Modal, Replicate, Scale AI).

- **[LIMIT] Grounding checks cannot catch this class.** `check_date_grounding` and
  `check_amount_grounding` verify that a claim traces to a *collected signal*. A
  wrong-entity signal already in the corpus passes — the figure is real, it just belongs
  to another company. This is why the Scale AI claims were not flagged. A clean eval run
  is not evidence that a brief's signals belong to the right company.

- **[DEFECT] README drift in the platform repo.** `README.md` (commit `2b44793`) states
  that briefs write prose for COMPETITIVE POSITION when Neo4j is unreachable and that
  the fix is "pending". The fix landed in the very next commit (`0fa8a10`). The README
  has not been updated — a P6 mismatch between stated intent and shipped code. Not fixed
  here: this log governs Mycroft, and the file lives in the other repo.

- **Outputs:**
  - `recipes/vendor-intelligence-brief.yaml` v0.3.0 — new `evaluation:` section (6
    checks with severities, the harness limit, the human accuracy set, 17 tests, CI),
    new `architecture.unknown_enforcement`, three issues added
  - `data/verified/ai_company_signals-schema.yaml` v0.3.0 — residual risk upgraded to
    CONFIRMED with the Scale AI instance; new note on the grounding-check limit
  - Amended the 2026-08-22 entry: its open provenance issue is closed by `5edd72c`
  - This entry
- **Result:** Mycroft records the machine half of brief evaluation. Recipe stays
  **DRAFT** — no gate closed this round, `todos_open` still 2, no attestation.
- **Open issues:**
  - [BLOCKER] No accuracy rate exists. `labeled_briefs.csv` has 6 queued claims and an
    empty `accurate` column — the machine half runs, the human half has not started.
    No accuracy figure may be quoted for this system (P3).
  - [BLOCKER] Common-word vendors still lack exclusion lists (above).
  - [GATE OPEN] Supervisor routing review (Phase 2) — no Langfuse trace reviewed.
  - [GATE OPEN] Brief approval (Phase 2) — no procurement owner review process.
  - [BLOCKER] Per-source signal counts still stale (pre-purge). Recount before citing.
  - [BLOCKER] Groq token limit at company #33 of 50 — Phase 3 batch job still blocked.
  - [OPEN] `eval_runner.py` is not wired to any Mycroft phase gate. It reports; nothing
    yet requires it to pass before a brief ships. Deliberate for now — a gate is a hard
    stop and needs a named owner.
## 2026-07-26 -- Implement Mycroft Finance Investigator Weeks 1-3

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`); no lifecycle promotion or human gate clearance attempted.
- **Inputs:** Local synthetic finance pack in `data/raw/mycroft-finance-investigator/` containing provenance, account mapping, budget, actuals, ledger, customer drivers, and headcount drivers for one sample entity and period.
- **Commands:** Ran `python3 -m unittest discover -s tests -v`; ran `python3 -m mycroft_finance_investigator.cli all --run-id sample-2026-02`; parsed generated JSON; reviewed the validation audit and human report; ran targeted `node scripts/conformance.mjs`; parsed `pyproject.toml`; ran `git diff --check`; ran `npm run verify`.
- **Outputs:** `projects/Mycroft-Finance-Investigator/`; `recipes/mycroft-finance-investigator.md`; `conductor/mycroft-finance-investigator.md`; `reports/templates/mycroft-finance-investigator.md`; `data/verified/mycroft-finance-investigator/`; `logs/mycroft-finance-investigator-sample-2026-02.json`; `reports/generated/mycroft-finance-investigator-sample-2026-02.md`; updated data contract, indexes, and current status.
- **Result:** All 12 unit tests pass, including deliberate ledger-mismatch, unmapped-account, agent-step-limit, and complete-category-bridge checks. Validation accepted 43 synthetic rows across six datasets; account coverage, single period/entity scope, actuals-to-ledger, customer-to-revenue, and headcount-to-payroll checks reconciled. The deterministic bridge calculated sample budget EBITDA of 350000.00 and actual EBITDA of 230000.00, a -120000.00 variance. The investigator completed seven conditionally selected tool steps, retained 41 evidence references, wrote separate machine/human artifacts, and kept the human gate open. Targeted conformance and repository-wide verification pass.
- **Open issues:** The 10000.00 materiality amount is a demo fixture, not an approved finance policy. No human has supplied or approved causal explanations or authorized distribution. The local policy demonstrates the stateful observe-plan-act contract without a hosted model; an LLM planning policy, persistent database, reviewer agent, scenario engine, and UI remain future-week work.

## 2026-07-31 -- Add Finance Investigator human review gate

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`); no human decision or lifecycle promotion recorded.
- **Inputs:** Completed synthetic sample run `logs/mycroft-finance-investigator-sample-2026-02.json` and its 41 evidence references.
- **Commands:** Ran the project unit suite; generated an open review request with `review-request`; parsed the artifact; ran targeted conformance and repository verification.
- **Outputs:** `mycroft_finance_investigator/review.py`; `schemas/review-decision.schema.json`; review CLI commands; `logs/gate-decisions/mycroft-finance-investigator-sample-2026-02-review-request.json`; review tests and updated contracts.
- **Result:** The review gate binds decisions to the exact run hash, rejects agent identities and unknown evidence, requires evidence-backed explanations for approval, and refuses to overwrite a recorded decision. The committed sample request is `OPEN`; it is not an approval.
- **Open issues:** No named finance reviewer has completed the request. Demo materiality, causal adequacy, and distribution remain human decisions.

## 2026-08-07 -- Add Finance Investigator adversarial evaluation

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`); evaluation does not clear an adequacy or release gate.
- **Inputs:** The committed synthetic finance pack, completed sample run, and seven explicit cases in `projects/Mycroft-Finance-Investigator/evaluations/cases.json`.
- **Commands:** Ran the complete project unit suite; ran the `evaluate` CLI; parsed the JSON scorecard; checked that raw-source hashes were unchanged; ran targeted conformance and repository verification.
- **Outputs:** `mycroft_finance_investigator/evaluation.py`; evaluation case/schema files; evaluation tests; `logs/mycroft-finance-investigator-evaluation-week32.json`; `reports/generated/mycroft-finance-investigator-evaluation-week32.md`; updated recipe, conductor, project documentation, and status.
- **Result:** All seven named expectations matched: the reconciled baseline completed with the expected EBITDA, tool trace, evidence count, and open human gate; four planted reconciliation/mapping defects stopped validation; the step limit stopped the investigator; and an agent identity could not clear the human gate. Every mutation ran in a temporary copy.
- **Open issues:** This finite synthetic case set is not model confidence or production certification. A named human still owns test adequacy, materiality, causal explanation, and distribution.

## 2026-08-13 -- Add Finance Investigator scenario decision pack

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`); no planning, adequacy, or release gate was cleared.
- **Inputs:** Verified synthetic sample, exact baseline run `sample-2026-02`, and three explicitly unapproved exercises in `projects/Mycroft-Finance-Investigator/config/sample-scenarios.json`.
- **Commands:** Ran the complete project unit suite; ran the `scenario` CLI; parsed and reconciled the machine decision pack; reviewed the human Markdown view; ran targeted conformance and repository verification.
- **Outputs:** `mycroft_finance_investigator/scenario.py`; scenario plan/schema and tests; `logs/mycroft-finance-investigator-scenarios-week33.json`; `reports/generated/mycroft-finance-investigator-scenarios-week33.md`; updated recipe, conductor, project documentation, and status.
- **Result:** The engine bound the plan to the exact baseline log and reproduced actual EBITDA of 230000.00. It calculated three transparent sensitivities at 275500.00, 250000.00, and 252300.00, retaining baseline records and plan references for every assumption. Outputs are labeled `SIMULATION_NOT_FORECAST`, contain no recommendation, and require a human decision.
- **Open issues:** The sample assumptions are not approved forecasts or operating plans. A named finance owner must approve or replace assumptions, judge scenario adequacy, and own any decision, causal explanation, materiality policy, or distribution.

## 2026-08-21 -- Add Finance Investigator audit-bundle handoff

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`); packaging and integrity checks did not clear any human gate.
- **Inputs:** Exact synthetic raw and verified data; baseline investigation `sample-2026-02`; open review request; Week 32 evaluation; Week 33 scenario pack; current recipe, conductor, implementation, schemas, and tests.
- **Commands:** Rebased the feature branch onto current `origin/main` while preserving historical commit dates; ran the complete unit suite; generated the Week 34 bundle with `bundle`; independently checked it with `verify-bundle`; deliberately changed packaged files and manifest content in tests; ran targeted conformance, repository verification, and Git whitespace checks. The first root-directory `verify-bundle` invocation could not import the project package, so it was rerun from the documented project directory.
- **Outputs:** `mycroft_finance_investigator/bundle.py`; `schemas/audit-bundle.schema.json`; bundle CLI commands and tests; `reports/generated/mycroft-finance-investigator-audit-week34/`; updated recipe, conductor, project documentation, and status.
- **Result:** All 41 project tests pass. The bundle validates the cross-artifact run IDs and hashes before packaging 54 source, data, specification, implementation, test, machine, and human artifacts. The integrity verifier recomputes the manifest, review view, byte counts, every artifact SHA-256, and the exact inventory. Deliberate manifest, review, artifact, and extra-file modifications are rejected. The initial inventory check exposed the macOS `/var` to `/private/var` temporary-directory symlink; resolving both bundle and artifact roots fixed the false mismatch. The human view reports `BLOCKED_PENDING_HUMAN_REVIEW` and distinguishes checksums from signatures.
- **Open issues:** No named finance reviewer has approved materiality, causation, evaluation adequacy, scenario assumptions, or distribution. The recipe remains `DRAFT`; the bundle is an integrity-preserving handoff, not production certification or attestation.

## 2026-08-28 -- Add Finance Investigator multi-month trend investigation

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`); historical comparison did not clear materiality, causation, adequacy, or release gates.
- **Inputs:** Independently validated synthetic January and March finance packs, the existing February sample, their three completed investigation logs, and `projects/Mycroft-Finance-Investigator/config/sample-trend.json`.
- **Commands:** Ran `all` separately for January and March; ran the `trend` CLI; parsed the machine comparison; reviewed the human report; ran all project tests; ran targeted conformance, repository-wide verification, and Git whitespace checks.
- **Outputs:** `data/raw/mycroft-finance-investigator-history/`; `data/verified/mycroft-finance-investigator-history/`; January and March machine logs and human reports; `mycroft_finance_investigator/trend.py`; trend plan/schema/tests; `logs/mycroft-finance-investigator-trend-week35.json`; `reports/generated/mycroft-finance-investigator-trend-week35.md`; updated recipe, conductor, data contract, project documentation, and status.
- **Result:** Both added monthly packs validated 43 synthetic rows across six datasets and passed mapping, single-scope, actuals-to-ledger, customer-to-revenue, and headcount-to-payroll controls. The comparison verified every source hash and recomputed actual EBITDA of 261000.00 for January, 230000.00 for February, and 265000.00 for March. It reported a -31000.00 then +35000.00 historical movement and found revenue, COGS, and operating expense materially adverse in all three sample periods under the 10000.00 demo threshold. All 49 project tests pass, including source tampering, duplicate period, entity mismatch, and period mismatch checks. Targeted conformance and repository verification pass.
- **Open issues:** The threshold remains demo-only. Recurrence is a deterministic historical pattern, not a causal explanation, forecast, recommendation, or approved business decision. No named finance reviewer has judged the history adequate or authorized distribution; the recipe remains `DRAFT`.

## 2026-09-04 -- Add Finance Investigator specialist-agent routing

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`); specialist execution did not clear an adequacy or release gate.
- **Inputs:** Exact Week 35 trend log, its three source investigation logs and verified packs, and `projects/Mycroft-Finance-Investigator/config/sample-routing.json`.
- **Commands:** Rebased PR 17 onto current `origin/main` while preserving upstream and Finance history; ran the pre-change 49-test baseline; ran the complete project unit suite; generated the Week 36 orchestration log and human work queue; parsed the machine artifact and reviewed the Markdown report.
- **Outputs:** `mycroft_finance_investigator/orchestration.py`; routing plan/schema/tests and CLI command; `logs/mycroft-finance-investigator-routing-week36.json`; `reports/generated/mycroft-finance-investigator-routing-week36.md`; updated recipe, conductor, project documentation, and status.
- **Result:** The lineage specialist verified all three source-run and verified-file chains before category work. The supervisor used four of four permitted delegations and deterministically prioritized revenue (200000.00 cumulative material adverse impact), COGS (100000.00), and operating expense (36000.00). It routed revenue to the revenue specialist and both cost categories to the cost specialist, retained calculation and correlated-record evidence separately, and fingerprinted every result. All 57 project tests pass, including deliberate source tampering, category drift, specialist-scope, and delegation-limit failures.
- **Open issues:** The work queue is not a causal analysis or recommendation. COGS and operating expense still lack operational driver records; all three tasks require an owner-supplied causal explanation. Materiality, evidence adequacy, and distribution remain open human gates.

## 2026-09-10 -- Add Finance Investigator review-driven re-investigation

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`); the committed follow-up is a synthetic review exercise, not a human gate decision.
- **Inputs:** Exact Week 36 orchestration log and its recorded routing-plan, trend-log, source-task, and specialist-result hashes; `projects/Mycroft-Finance-Investigator/config/sample-follow-up-request.json`.
- **Commands:** Ran the complete project unit suite; ran the `follow-up` CLI; parsed the machine closure log; reviewed the human before/after report; exercised hash, task-inventory, citation, and append-only failures in tests.
- **Outputs:** `mycroft_finance_investigator/reinvestigation.py`; follow-up request/schema/tests and CLI command; `logs/mycroft-finance-investigator-follow-up-week37.json`; `reports/generated/mycroft-finance-investigator-follow-up-week37.md`; updated recipe, conductor, project documentation, and status.
- **Result:** The engine bound the request to the exact Week 36 SHA-256, revalidated upstream plan and trend hashes, and reproduced all three specialist result fingerprints. One existing evidence set replayed exactly, one synthetic causal claim was classified unsupported because it cited calculation evidence without an approved causal evidence class, and one operational evidence request remained open. All 66 project tests pass, including deliberate orchestration tampering, unknown citation, missing task, duplicate task, and overwrite attempts.
- **Open issues:** `VERIFIED` means evidence integrity only, not verified causation. The COGS claim is a synthetic rejection test and is not an endorsed explanation. A named finance reviewer still must inspect unresolved gaps, approve or replace materiality, supply causal evidence, judge adequacy, and authorize distribution.

## 2026-09-17 -- Gateway Sprint 4: retry system and first full run

- **Recipe:** Adaptive Model Routing & Inference Gateway (Sprint 4 of 17).
- **Gate:** First full live sweep of the frozen fixture set, watched by a human.
- **Cleared by:** Simba · 2026-09-17
- **Inputs:** 24 fixtures frozen 2026-09-17; policy 0.2.0; tiers 0.4.0;
  prices 2026-09-17; GROQ_API_KEY (free tier).
- **Commands:** `python -m pytest scripts/gateway/tests -q` (146 passed);
  `bench/run.py --dry-run`; `bench/run.py --limit 3`; `bench/run.py` (three
  sweeps); `first_live_call.py strong --max-tokens 896`.
- **Outputs:** `validators.py`, `prompts.py`, `gateway.py`, `bench/run.py`;
  updates to `adapters/base.py`, `adapters/fake.py`, `adapters/groq.py`,
  `client.py`, `policy.json`, `tiers.json`, `prices.json`; tests
  `test_validators.py` (21), `test_prompts.py` (10), `test_gateway.py` (11),
  `test_grade.py` (8); three run logs under `logs/gateway/runs/` and matching
  `bench/results/*.json`.
- **Result:** Final sweep (`2026-09-17T015116`): 24 requests, 26 attempts,
  escalation 8%, failure 0%, cost $0.00250 total and $0.000104 per request,
  latency p50 393 ms and p95 734 ms. 16 of 24 graded, 14 correct. Both
  escalations (`rag-001`, `rag-004`) failed `cites_context` on mid and then
  answered correctly on strong. Every model answer that completed was correct;
  the two graded "wrong" are answer-key errors, not model errors.
  Retry rule as built: one retry only, on a failed check or a retryable
  provider error, never a chain, and never on a terminal error.
- **Broke during testing, fixed:**
  - `verdict_with_quote` required one contiguous span, but models quoted both
    conflicting statements joined together. All three escalations in the
    01:44 sweep were false alarms caused by the check, not the models. The
    prompt now asks for one continuous span from a single statement; all four
    contradiction fixtures then passed and graded correct.
  - The strong tier's `qwen/qwen3.6-27b` returned 404 "does not exist or you
    do not have access" after two successful calls on 2026-09-10. It is gone
    from Groq's model list. Replaced with `qwen/qwen3.8-27b` ($0.80/$4.00 per
    1M). Groq's deprecation page still recommends 3.6 as a migration target,
    so their docs contradict their API.
  - Strong's `max_tokens` of 1024 exceeded this account's output-tokens-per-
    minute cap of 1000, so every strong call was refused before the model ran.
    Lowered to 896 (policy 0.2.0) and gated live: 19 in / 2 out, $0.0000232.
  - A 429 meaning "request too large" is now classified terminal. Waiting
    cannot help it; only a smaller budget can.
  - `bench/run.py` wrote one log file per day, so a smoke run's 3 requests were
    counted inside the full sweep's summary (27 requests for 24 fixtures). Log
    files are now stamped to the second and the summary is scoped to the run's
    own request ids.
  - `test_promoted_to_the_top_has_nowhere_to_escalate` hardcoded 1024 as the
    strong budget and failed when the budget changed. Now asserts against
    `policy.max_tokens("strong")`.
- **Findings:** see `scripts/gateway/FINDINGS.md` section 7. In short:
  no wrong-but-valid answers appeared across 24 fixtures; escalated requests
  were 8% of requests and 23% of spend; and the cost ladder is not monotonic
  on trivial prompts -- strong answered the gate prompt for 20% less than
  cheap, with the crossover at roughly five output tokens.
- **Not verified:** Groq console usage for these calls; the correctness of the
  8 extraction and summarization fixtures, which no deterministic check can
  judge and which wait on the Sprint 5 judge.
- **Open issues:**
  - `sent-001` and `sent-004` are still keyed `negative`. Both entries under
    "wrong but passed the check" are this key error, not model error. Fix
    before any Sprint 7 result is quoted.
  - The strong tier's 1000 OTPM cap allows roughly one strong call per minute
    at an 896 budget. Sprint 7 wants every fixture on every tier several times
    over, so it needs pacing or a paid tier.
  - GROQ_API_KEY still needs rotating; it was exposed outside the terminal.
  - 20 of 24 fixtures start on mid, so the cheap tier served only 4 requests.
    Sprint 7 must try cheap on everything, not only where policy prefers it.
  - Coverage is still 4 of the 30 fixtures targeted per task type.

## 2026-09-25 -- market-sentiment-analysis-part-1 promoted to RUNNABLE-SAMPLE (steps 1-6)

- **Recipe:** market-sentiment-analysis-part-1, v0.2.0, `status: RUNNABLE-SAMPLE`, `todos_open: 2`.
- **Inputs:** `recipes/market-sentiment-analysis-part-1.md`, `conductor/market-sentiment-analysis-part-1.md`,
  `docs/architecture.md` 5.2 (script-layer contract), `SNICKERDOODLE.md` (lifecycle + verification
  stack), `data/raw/market-sentiment-analysis-part-1/sample/fixture-manifest.json` (the only
  declared schema for this recipe), and the named source workflow
  `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json`
  (read for the Aggregate node's arithmetic only).
- **Commands:** full pipeline, both fixture sets, all six steps:
  - `scripts/tools/...-verify-provenance.py` -> exit 0
  - `scripts/ingest/...-ingest-inputs.py --fixture-set {clean,defective}` -> exit 0
  - `scripts/gigo/...-validate-data-shape.py --fixture-set {clean,defective}` -> exit 0 / **1**
  - `scripts/gigo/...-transform-quality-check.py --fixture-set {clean,defective}` -> exit 0 / **1**
  - `scripts/tools/...-run-approved-tools.py --fixture-set {clean,defective}` -> exit 0
  - `scripts/tools/...-produce-human-report.py --fixture-set {clean,defective}` -> exit 0
  - Nonzero on the defective set is the designed behaviour: report every finding, then halt.
  - `node scripts/conformance.mjs` -> 187 files, all conform.
  - Gate-3 test as literally written -> all 26 JSON artifacts parse.
- **Outputs:**
  - `reports/generated/market-sentiment-analysis-part-1-2026-08-27-{clean,defective}.md` (15/15 sections)
  - `logs/market-sentiment-analysis-part-1-2026-08-27-{clean,defective}.json` (16/16 contract fields)
  - `data/verified/.../runs/sample-001-{clean,defective}/sample-001-{clean,defective}-audit.md`
  - `logs/gate-decisions/market-sentiment-analysis-part-1-gate-{1,2,3,4}.json`
  - This entry.
- **Result:** **18/18 catalogued corpus defects detected at their exact manifest locators**, split
  8 to step 3 and 10 to step 4, with every declared total in `expected_totals` matching --
  including `news_by_headline: 2`, which a short-circuiting dedupe reports as 1. Each step was also
  tested for what it must NOT catch: step 3 leaks none of step 4's ten. Clean set: 10 rows, zero
  findings. Defective set: 19 rows seen, 13 promoted, 6 withheld, 5 duplicates, 6 quality flags.
  Both sets score 64/100 SLIGHTLY BULLISH -- the same headline number, with four flagged rows
  feeding one of them, which is the argument for the flags existing.
- **Promotion evidence (SPECIFIED -> RUNNABLE-SAMPLE):** full sample run completes; conformance
  passes; audits generated and read. Gates 1-4 carry logged decisions naming a human.
  `RUNNABLE-LIVE` is not claimed and `attestation` stays null.
- **Changes made this session:**
  - Closed the six canonical-step `[TODO: DEV]` markers with their evidence. Resolved the six
    legacy n8n node markers as **mappings, not code**: four were absorbed by canonical steps, and
    two (`Parse Question & Extract Tickers`, `Webhook Response`) were **never built** and now say so.
  - Added lifecycle frontmatter. `todos_open: 2` -- one DEFINE on step 5's scoring constants, one
    APPROVE on gate 5. Both markers now sit in the recipe body so the count is greppable; note the
    same strings also appear inside the gate 1 and gate 5 test commands, where they are the test.
  - **Contract fix 1:** step 3 gained `type_errors`. A wrong-typed value was none of its five
    declared fields, so D02/D11/D17 had to be reported only in step 4 `flags`. Step 3 now reports
    them against a declared TYPE_CONTRACT; rows are still promoted (a wrong value is not a wrong
    shape), and step 4 still flags them for its quality assessment -- the same carry-forward
    pattern it already uses for step 3's rejects. Verified: 18/18 unchanged, step 4 totals unchanged.
  - **Contract fix 2:** the report Reader is now the compliance/audit reviewer the artifact actually
    serves. The report already carried source hashes, reproduced scoring parameters and a per-score
    trace chain; the declared reader now matches.
  - **Contract fix 3:** `reports/templates/market-sentiment-analysis-part-1.md` cited
    `logs/.../[RUN_ID].json` against the recipe's `logs/...-[DATE].json`. Recipe governs; template
    corrected.
  - **Gate 4's test was amended.** It previously passed if the script existed OR if a DEV-TODO
    marker was still present in the recipe -- satisfiable by doing nothing. It now compiles all six.
- **Design decisions worth recording:**
  - **Gates 5 and 6 were deliberately not written.** Gate 5 would be a false clearance: no live,
    external, or model call has ever run, and all three step-5 handoffs carry
    `approved_for_live_action: false`. Gate 6 is step 6's own output, not yet a human decision.
  - **Each gate record carries `residual_risk` and `voids_if`.** An audit reports what it found;
    it does not say pass. Gate 3's record states plainly that shape validation cannot catch a
    wrong-entity row.
  - **The legacy node section was relabelled historical, not closed as done.** Claiming six more
    scripts were written would have been false -- two of those nodes have no implementation at all.
- **Open issues:**
  - [DEFECT] **Gate 5's test is still self-satisfying** -- `test -f <approval>.json || rg "[TODO:
    APPROVE]"`. Now that `logs/gate-decisions/` exists, the approval file is absent, so the test
    falls through to the marker and reports a pass for a gate that has never been cleared. Same
    class as the gate-4 defect fixed above; left alone because it was not in scope, but it is now
    actively misleading and should be the next fix.
  - [OPEN] `[TODO: DEFINE]` scoring constants: the weights, thresholds and both keyword lists are
    ported verbatim from a source workflow that records no derivation, backtest or author.
    Reproduced so a historical score can be recomputed, not endorsed. Needs a named human.
  - [OPEN] `[TODO: APPROVE]` gate 5: live and model execution remain blocked.
  - [OPEN] Live mode is unimplemented. Needs real fetchers, credentials from the environment, and
    401/403/429/timeout/empty-200 handling the fixture corpus explicitly does not cover.
  - [OPEN] The step-scoped `TYPE_CONTRACT` is not a promoted schema. If accepted it belongs in
    `DATA_CONTRACT.md` with a named owner.
  - [NOT COVERED] Wrong-entity signals, upstream HTTP failure modes, encoding defects, and
    volume/pagination. The first of these is the class that reached a finished brief on 2026-08-26.
  - [OPEN] No independent test suite covers the six scripts, and CI runs none of the repo's 72
    existing Python test files.

## 2026-10-02 -- market-sentiment-analysis-part-1: both open TODOs closed, todos_open 0

- **Recipe:** market-sentiment-analysis-part-1, v0.2.0, `status: RUNNABLE-SAMPLE`, `todos_open: 0`.
  The steps 1-6 run itself is logged at `logs/RUN_LOG.md#2026-09-25`; this entry records the two
  typed-TODO closures, the gate-4/5 test fixes, and the rebase onto the current `origin/main`.
- **Inputs:** `recipes/market-sentiment-analysis-part-1.md`, `SNICKERDOODLE.md` (TODO closure table
  and the verification stack), `logs/gate-decisions/`, and the step-5 scoring parameters as ported
  from the named source workflow.
- **Commands:**
  - Full pipeline re-run, both fixture sets, after the rebase -> step 1 exit 0; clean set all exit 0;
    defective set steps 3 and 4 exit 1 by design, steps 2/5/6 exit 0.
  - All six gate tests as literally written -> all pass.
  - Gate-5 test break-tested across four cases (see below).
  - `node scripts/conformance.mjs` -> all conform.
- **Outputs:**
  - `logs/gate-decisions/market-sentiment-analysis-part-1-gate-5.json` -- **decision: deny**
  - Recipe: both typed TODOs closed in place; `todos_open` 2 -> 0; gate-5 test amended twice.
  - This entry.
- **Result:** `todos_open: 0`. Neither closure loosened anything -- one defines what the numbers are,
  the other refuses to switch anything on.
- **TODO closures:**
  - **[DEFINE] step 5 scoring constants -- closed by definition, not by endorsement.** The weights
    (price 0.40 / news 0.30 / social 0.30), the label thresholds (65/55/45/35), the price score map
    and both keyword lists are now restated in the recipe with their reasoning: they are inherited
    byte-for-byte from the `Aggregate & Calculate Sentiment` node so any score the original ever
    produced can be recomputed and audited. They carry **no claim** that the weighting or the word
    lists are analytically sound. Step 5 continues to raise `scoring_params_unattributed` on every
    run, and the report continues to file every score under inferred findings. Changing any value
    requires a new `scoring_params` version, because a score is only reconstructable against the
    parameter set that produced it.
  - **[APPROVE] gate 5 -- closed by a logged decision, and the decision is DENY.** The closure rule
    is "a logged gate decision", not "an approval", so a recorded refusal closes it honestly. Live
    execution was declined on four grounds: step 2 hard-stops in live mode, so approval would
    authorise a capability that does not exist; no credentials are configured, making approval a
    statement of intent rather than a decision; the frozen corpus explicitly does not cover
    401/403/429/timeout/empty-200, so live failure behaviour has never been exercised; and two of
    the three declined actions are outward-facing and irreversible once sent. Four preconditions to
    reopen are named in the record.
- **Design decisions worth recording:**
  - **Writing the deny record immediately re-created the defect it was meant to close.** The gate-5
    test at that moment read `test -f <record>.json || ...`, so the presence of a *refusal* cleared
    the gate exactly as an approval would. Caught on the same turn it was introduced. The test now
    reads `approved_for_live_action` out of the record instead of checking that the file exists.
    Break-tested four ways: no-call/no-record PASS; no-call/deny PASS; **live-call/deny FAIL**;
    live-call/approve PASS.
  - **A deny is a closure, not a loophole.** Recording "no" is what turns an unexamined gate into a
    decided one. The alternative -- leaving the TODO open indefinitely -- is how a gate quietly
    becomes decoration.
  - **The branch was rebased onto `origin/main` by cherry-pick, not by `git rebase`.** `origin/main`
    had moved to a lineage missing steps 4, 5 and 6, so replaying only the newer commits would have
    produced a branch whose recipe claims six working steps and whose gate-4 record asserts all six
    compile, while two scripts did not exist. Steps 4-5 were carried along deliberately.
- **Open issues:**
  - [OPEN] Live mode remains unimplemented, and is now explicitly declined rather than merely
    pending. Reopening requires the four preconditions in the gate-5 record.
  - [OPEN] The step-scoped `TYPE_CONTRACT` in steps 3 and 4 is still not a promoted schema. If
    accepted it belongs in `DATA_CONTRACT.md` with a named owner.
  - [OPEN] `attestation` stays null. `VERIFIED` needs an attestation bound to this recipe version,
    and the SNICKERDOODLE format requires a mandatory "Did not test" section.
  - [NOT COVERED] Wrong-entity signals, upstream HTTP failure modes, encoding defects, and
    volume/pagination. The first is the class that reached a finished brief on 2026-08-26.
  - [OPEN] No independent test suite covers the six scripts, and CI runs none of the repo's existing
    Python test files.

## 2026-10-02 -- attestation recorded for market-sentiment-analysis-part-1 v0.2.0 (status unchanged)

- **Recipe:** market-sentiment-analysis-part-1 v0.2.0, `status: RUNNABLE-SAMPLE` (**unchanged**),
  `attestation: logs/attestations/market-sentiment-analysis-part-1-v0.2.0.md`.
- **Inputs:** `SNICKERDOODLE.md` (attestation format + lifecycle table), the two prior RUN_LOG
  entries for this recipe, `logs/gate-decisions/` (5 records), the generated audits and reports.
- **Commands:** branch rebased onto the current `origin/main`; full pipeline re-run on both fixture
  sets -> step 1 exit 0, clean all exit 0, defective steps 3/4 exit 1 by design; all six gate tests
  pass; `node scripts/conformance.mjs` -> all conform.
- **Outputs:** `logs/attestations/market-sentiment-analysis-part-1-v0.2.0.md`; `attestation:` path
  recorded in the recipe frontmatter; this entry.
- **Result:** An attestation exists, bound to v0.2.0, in the SNICKERDOODLE format: 17 tested rows --
  of which **7 are deliberate attempts to break the thing** -- a mandatory Did-not-test section with
  10 entries, and 9 defects that broke during testing and were fixed.
- **Status NOT promoted to VERIFIED, deliberately.** The lifecycle is
  DRAFT -> SPECIFIED -> RUNNABLE-SAMPLE -> RUNNABLE-LIVE -> VERIFIED. Reaching VERIFIED requires
  passing through RUNNABLE-LIVE, whose gate test is "live run with a human clearing every gate".
  Neither condition holds: **no live run has ever happened** (live mode is unimplemented and step 2
  hard-stops before any fetch), and **not every gate is cleared** -- gate 5 is recorded
  `decision: deny` with `approved_for_live_action: false`. Setting the status today would assert a
  live run that never occurred and a clearance that was explicitly refused. Per the constitution,
  "editing the status field without the evidence is a violation, not a promotion."
- **What VERIFIED would require, in order:** implement live mode in step 2; add a second fixture set
  covering 401/403/429/timeout/empty-200 with declared expected detections; reopen gate 5 against
  the four preconditions in its record and log an approval naming the approver; perform a live run
  with every gate cleared, logged (that earns RUNNABLE-LIVE); then record a **fresh** attestation
  bound to the version that ran live, since any edit to the recipe or its scripts voids this one.
- **Design decisions worth recording:**
  - **The Did-not-test section is the load-bearing half.** It names live execution, whether the
    score is correct, wrong-entity signals, HTTP failure modes, encoding defects, volume, the
    untestable `redditMentions > 20` branch, the absence of any unit tests, cross-platform
    behaviour, and interrupted runs. An empty one would have been the new "it works".
  - **An attestation that cannot promote is still worth recording.** It fixes what was exercised, at
    which version, with its boundary stated -- which is what makes the next one comparable.
- **Open issues:**
  - [OPEN] Live mode unimplemented and explicitly declined; see the gate-5 record.
  - [OPEN] `TYPE_CONTRACT` in steps 3 and 4 is still step-scoped, not promoted to `DATA_CONTRACT.md`.
  - [OPEN] No unit tests for the six scripts; CI runs none of the repo's existing Python tests.
  - [NOT COVERED] Wrong-entity signals, HTTP failure modes, encoding defects, volume/pagination.

## 2026-10-04 -- contradiction-detection-agent: six step scripts built, sample run, promoted to RUNNABLE-SAMPLE

- **Recipe:** `recipes/contradiction-detection-agent.md` v0.2.0, status RUNNABLE-SAMPLE, todos_open 0. Before this change it had no lifecycle frontmatter and its six step scripts were still to be written (`[TODO: DEV]`). Its 16 per-node scripts are left unchanged.
- **Inputs:** the original workflow `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json` (26 nodes); a new frozen synthetic corpus `data/raw/contradiction-detection-agent/sample/` (16 fictional companies; 17 catalogued defects; `expected-flags.json` written from the original JavaScript before any port); `SNICKERDOODLE.md`; the recipe contract.
- **Commands:**
  - `python3 scripts/tools/contradiction-detection-agent-run-sample.py --fixture-set clean`: steps 1-6 exit 0 (16 companies, 13 flags)
  - `python3 scripts/tools/contradiction-detection-agent-run-sample.py --fixture-set defective`: step 3 exits **1** by design (13 shape defects); step 6 still writes the report and audit
  - `python3 scripts/tools/contradiction-detection-agent-parity-check.py`: exit 0, 16/16 companies match the original JavaScript (run under a Node shim)
  - `python3 scripts/tools/contradiction-detection-agent-self-test.py`: exit 0, 38/38 checks as expected
  - `python3 scripts/tools/contradiction-detection-agent-gate-check.py --gate 1` … `--gate 6`: all six pass
  - `node scripts/conformance.mjs`: all conform; `node scripts/manifest-check.mjs`: passed
- **Outputs:** step scripts `scripts/{tools,ingest,gigo}/contradiction-detection-agent-*.py` (6) and supporting scripts (run-sample, gate-check, parity-check, self-test); `data/raw|verified/contradiction-detection-agent/runs/sample-001-{clean,defective}/`; audits beside the verified data; `reports/generated/contradiction-detection-agent-2026-09-30-{clean,defective}.md`; `logs/contradiction-detection-agent-2026-09-30-{clean,defective}.json`; `logs/contradiction-detection-agent/self-test-results.{json,md}`; `logs/gate-decisions/contradiction-detection-agent-gate-{1..5}.json`.
- **Result:**
  - 17/17 catalogued defects detected at the step and row the manifest names, 0 false findings.
  - The parity check catches 3 deliberately broken ports.
  - Break tests (empty tree, live mode, changed fixture, repaired broken file, renamed node, step 5 before step 4, no half-built bundles) all stop as designed.
  - Every gate test fails on an empty tree.
  - Two clean runs are byte-identical.
  - **Promotion evidence (DRAFT -> SPECIFIED -> RUNNABLE-SAMPLE):** the typed TODOs closed (DEV by the scripts plus conformance plus handoff conditions; DEFINE and APPROVE by the decisions below), a full sample run, conformance passing, and audits generated and read.
- **Gate decisions:** Tanmay Kulkarni, 2026-10-04, verbatim "D1 clear, D2 deny, D3 keep, D4 log".
  - Gates 1-4 approved for the sample run.
  - Gate 5 **denied**: live mode declined, with four preconditions to reopen.
  - `[TODO: DEFINE]` closed: thresholds kept as inherited, unvalidated.
  - Pattern 3's wording kept as ported and logged in *Notes from porting*.
  - Gate 6 not yet decided.
- **Changes made this session:**
  - The six gate tests now call `gate-check.py`, so each checks its condition directly and can fail. The previous tests are kept in the recipe for the record.
  - New recipe sections: Notes from porting, Sample corpus and evidence, Supporting scripts.
  - One stop condition added: no live run until queries pass their values as parameters.
  - Per-node outline labelled historical, nothing deleted.
- **Open issues:**
  - [OPEN] Gate 6 decision.
  - [OPEN] Live mode: the four preconditions in the gate-5 record.
  - [NOT COVERED] Live behaviour, LLM output, and live failure modes.

## 2026-10-04 -- contradiction-detection-agent: report step fixed during gate-6 review; gate 6 approved

- **Recipe:** `recipes/contradiction-detection-agent.md` v0.2.0, status RUNNABLE-SAMPLE (unchanged), `last_gate` now gate 6.
- **Found while reviewing the reports for gate 6** (in this recipe's own report step, `scripts/tools/contradiction-detection-agent-produce-human-report.py`):
  - on the stopped (defective) run the report counted 13 rejects and the agent log 0, because the log counted step-4 rejects only;
  - checks a stopped run never reached (duplicates, the lookback) were shown as 0 instead of "not checked";
  - the clean report's recommendation still named gates 1-4, which were already decided.
- **Changes:** one reject list now feeds both the report and the log; unchecked items say "not checked" (and the log lists them in `not_checked`); the recommendation is built from the gate records. New self-test section G checks all three and was confirmed to fail on the previous version (3 unexpected).
- **Commands:**
  - `python3 scripts/tools/contradiction-detection-agent-run-sample.py --fixture-set clean` and `--fixture-set defective`: as before (clean exit 0, 13 flags; defective stops at step 3 by design)
  - `python3 scripts/tools/contradiction-detection-agent-parity-check.py`: exit 0, 16/16
  - `python3 scripts/tools/contradiction-detection-agent-self-test.py`: exit 0, 42/42 checks as expected
  - `python3 scripts/tools/contradiction-detection-agent-gate-check.py --gate 1` … `--gate 6`: all six pass
  - `node scripts/conformance.mjs`: all conform; `node scripts/manifest-check.mjs`: passed
- **Gate decisions:** Tanmay Kulkarni, 2026-10-04.
  - "D1 clear" reconfirmed after the fix; gate 3 and 4 evidence re-hashed.
  - Gate 6 **approved** ("D5 approve"): `logs/gate-decisions/contradiction-detection-agent-gate-6.json`, hashing both reports and both agent logs.
- **Open issues:**
  - [OPEN] Live mode: the four preconditions in the gate-5 record (needs live data access and a new decision by a named human).
  - [NOT COVERED] Live behaviour, LLM output, and live failure modes.

## 2026-10-10 -- portfolio-price-fetcher + portfolio-dashboard: four [TODO: DEV] closures (provenance, data shape, the calculation port), sample mode

- **Recipes:** `recipes/portfolio-price-fetcher.md` and `recipes/portfolio-dashboard.md` (the Portfolio Visualization Agent; the dashboard calls the price fetcher). Both now carry status frontmatter: `status: DRAFT`, v0.2.0; `todos_open` 4 and 7.
- **Closed (each with its script, a status line and evidence in the recipe):**
  - price fetcher step 1 `scripts/tools/portfolio-price-fetcher-verify-provenance.py`; step 3 `scripts/gigo/portfolio-price-fetcher-validate-data-shape.py`; step 5 `scripts/tools/portfolio-price-fetcher-run-approved-tools.py` (a Python port of Calculate Metrics and Aggregate Summary)
  - dashboard step 1 `scripts/tools/portfolio-dashboard-verify-provenance.py`
- **Inputs:** each recipe's declared workflow JSON (read as the named source file the recipe declares); a frozen sample corpus `data/raw/portfolio-price-fetcher/sample/` (5 clean responses for the workflow's own tickers, 5 catalogued defects, SHA-256 manifest; every price invented and labelled); `data/raw/portfolio-price-fetcher/run-envelope.json` (mode sample).
- **Outputs:** `logs/portfolio-price-fetcher-provenance-2026-10-10.json`, `logs/portfolio-dashboard-provenance-2026-10-10.json`, `data/verified/portfolio-price-fetcher/{clean,defective}/validated.json` + `validate-audit.md`, `data/verified/portfolio-price-fetcher/clean/portfolio-summary.json`, `logs/portfolio-price-fetcher-run-approved-tools-2026-10-10.json`, `logs/portfolio-price-fetcher/self-test-results.{json,md}`.
- **Commands:**
  - provenance: price fetcher exit 0 (node table matches, both portfolio definitions agree, fixtures intact); dashboard exit 0 (calls the Price Fetcher by name; placeholder workflow id noted)
  - step 3: clean exit 0 (5 promoted); defective exit 1 by design (5/5 catalogued defects rejected)
  - step 5: clean exit 0 (total 65098.13); defective refused (exit 1, nothing written)
  - `python3 scripts/tools/portfolio-price-fetcher-parity-check.py`: exit 0, 5/5 holdings and the summary agree with the original JavaScript (excluded: lastUpdatedFormatted, host-locale dependent)
  - `python3 scripts/tools/portfolio-price-fetcher-self-test.py`: exit 0, 15/15 checks as expected, including 7 deliberate breaks
  - `node scripts/conformance.mjs`: all conform; `node scripts/manifest-check.mjs`: passed
- **Fixed while building:** the port first wrote `lastUpdated` as `...00Z`; JavaScript's `toISOString()` writes `...00.000Z`. Caught by the parity check, fixed in the port.
- **Unchanged:** the four generated per-node scripts for these recipes (`scripts/ingest/portfolio-price-fetcher-fetch-stock-prices.py`, `scripts/tools/portfolio-price-fetcher-calculate-metrics.py`, `scripts/tools/portfolio-dashboard-call-portfolio-price-fetcher.py`, `scripts/tools/portfolio-dashboard-webhook.py`), byte-identical.
- **Open issues:**
  - [OPEN] Price fetcher steps 2, 4, 6 and the report-script mapping; dashboard steps 2-6 and its two script mappings: still `[TODO: DEV]`.
  - [OPEN] Live mode: no approval record; Yahoo Finance is never called (the handoff is recorded with `approved_for_live_action: false`).
  - [NOT COVERED] Real market data, live behaviour, and the dashboard's HTML generation.

## 2026-10-10 -- portfolio-price-fetcher: run instructions added

- **Artifact:** `logs/portfolio-price-fetcher/README.md`, covering how to run the closed steps of `recipes/portfolio-price-fetcher.md` and `recipes/portfolio-dashboard.md` (commands, stop conditions, outputs, the sample corpus, what is not covered). Documentation only; no script or data changed.

## 2026-10-17 -- what-if-simulation-agent: three [TODO: DEV] closures + two script mappings (provenance, data shape, the six-node port), sample mode

- **Recipe:** `recipes/what-if-simulation-agent.md`, which had no status frontmatter. It now carries `status: DRAFT`, `todos_open: 5`, `recipe_version: 0.2.0`, `attestation: null`. It stays `DRAFT`, which is honest: the recipe is not yet SPECIFIED.
- **Closed (each with its script, a status line and evidence in the recipe):**
  - step 1 `scripts/tools/what-if-simulation-agent-verify-provenance.py`; step 3 `scripts/gigo/what-if-simulation-agent-validate-data-shape.py`; step 5 `scripts/tools/what-if-simulation-agent-run-approved-tools.py`
  - mapped to those scripts, with the original notes kept: the Parse & Validate Input node (to step 3's contract and step 5's first node) and the Aggregate & Score All Simulations node (to step 5)
- **Inputs:** the recipe's declared workflow JSON (read as the named source file); a frozen sample corpus `data/raw/what-if-simulation-agent/sample/` (15 clean requests that reach all 9 growth-and-sentiment cells, all 3 risk appetites, all 3 horizons and all 5 final recommendations; 10 catalogued defective ones; SHA-256 manifest; every company and number invented); `data/raw/what-if-simulation-agent/run-envelope.json` declaring sample mode.
- **Outputs:** `logs/what-if-simulation-agent-provenance-2026-10-17.json`, `logs/what-if-simulation-agent-run-approved-tools-2026-10-17.json`, `data/verified/what-if-simulation-agent/{clean,defective}/validated.json` and `validate-audit.md`, `data/verified/what-if-simulation-agent/clean/simulation-results.json`, `logs/what-if-simulation-agent/{parity-results.json,self-test-results.json,self-test-results.md,README.md}`.
- **Commands:**
  - step 1: exit 0 (node table matches the workflow's 13 nodes, the connections form the chain the port assumes, fixtures intact)
  - step 3: clean exit 0 (15/15 accepted); defective exit 1 by design (10/10 rejected, each for its own reason)
  - step 5: clean exit 0 (15 results, each ending in the prompt the Groq node would send); defective refused (exit 1, nothing written)
  - `python3 scripts/tools/what-if-simulation-agent-parity-check.py`: exit 0, 23/23 requests identical to the original JavaScript (every field, every character of the prompt), with the clock and Math.random pinned inside the JavaScript run
  - `python3 scripts/tools/what-if-simulation-agent-self-test.py`: exit 0, 18/18 checks as expected, including 10 deliberate breaks (a renamed node, a skipped simulator, a changed fixture, the tools handed rejected data, and four breaks of the port: Python's round, Python's formatting, Python's min/max with NaN, Python's number printing; each caught)
  - `node scripts/conformance.mjs`: all conform; `node scripts/manifest-check.mjs`: passed
- **Fixed while building:** the parity check found that Python's `min` and `max` do not treat NaN the way JavaScript's `Math.min` and `Math.max` do (any NaN makes the answer NaN), which changed the aggregate verdict on the two NaN requests. The port now has `js_min` and `js_max`. The self-test's break for it is caught.
- **Observation, offered as an open question for the maintainers and not as a finding:** in JavaScript a value that parses to NaN passes every comparison, so the Parse & Validate Input node's own five rules accept it. The step-3 gate here adds one rule (numeric fields must be finite) and says so in every audit; the port itself still copies the node exactly, so the parity check can compare NaN behaviour too.
- **Unchanged:** the eight generated per-node scripts for this recipe (`scripts/gigo/what-if-simulation-agent-parse-groq-response.py`, `-parse-validate-input.py`, `-save-to-postgresql.py`; `scripts/tools/what-if-simulation-agent-aggregate-score-all-simulations.py`, `-build-ai-prompt.py`, `-groq-generate-investment-insights.py`, `-sim-2-risk-appetite-simulator.py`, `-webhook-receive-simulation-request.py`), and the sibling recipe `recipes/n8n-what-if-simulation-agent.md`.
- **Open issues:**
  - [OPEN] Steps 2, 4 and 6 and the script mappings for the respond-to-webhook and human-report nodes: still `[TODO: DEV]` (`todos_open` is 5).
  - [OPEN] Live mode: no approval record; the Groq call and the PostgreSQL write are only recorded handoffs (`approved_for_live_action: false`); the nodes after the prompt are not ported.
  - [NOT COVERED] Real market data, live behaviour, and whether the simulators' investment logic is sound (ported faithfully, not judged).


## 2026-10-25 -- scenariostresstestingagent: three [TODO: DEV] closures (provenance, data shape, the stress-test chain port), sample mode

- **Recipe:** `recipes/scenariostresstestingagent.md`, which had no status frontmatter. It now carries `status: DRAFT`, `todos_open: 5`, `recipe_version: 0.2.0`, `attestation: null`. It stays `DRAFT`, which is honest: the recipe is not yet SPECIFIED.
- **Closed (each with its script, a status line and evidence in the recipe):**
  - step 1 `scripts/tools/scenariostresstestingagent-verify-provenance.py`; step 3 `scripts/gigo/scenariostresstestingagent-validate-data-shape.py`; step 5 `scripts/tools/scenariostresstestingagent-run-approved-tools.py`
  - the step-5 port also covers, with the generated per-node scripts left unchanged, the Stress_Test_Engine and Save_Portfolio_Before_LLM nodes (an "Also covered" line under each), and the Validate Portfolio and Load_Template_Scenario code nodes, which the recipe does not list as steps
- **Inputs:** the recipe's declared workflow JSON (read as the named source file); a frozen sample corpus `data/raw/scenariostresstestingagent/sample/` (12 clean requests that reach all five template scenarios, the custom-scenario route, all four risk levels, both sides of the weight-rescale rule and the exact 10-percent threshold; 10 catalogued defective ones; SHA-256 manifest; every portfolio and number invented); `data/raw/scenariostresstestingagent/run-envelope.json` declaring sample mode.
- **Outputs:** `logs/scenariostresstestingagent-provenance-2026-10-25.json`, `logs/scenariostresstestingagent-run-approved-tools-2026-10-25.json`, `data/verified/scenariostresstestingagent/{clean,defective}/validated.json` and `validate-audit.md`, `data/verified/scenariostresstestingagent/clean/stress-results.json`, `logs/scenariostresstestingagent/{parity-results.json,self-test-results.json,self-test-results.md,README.md}`.
- **Commands:**
  - step 1: exit 0 (node table matches the workflow's 16 nodes, the 18 connections match the wiring the port assumes, fixtures intact)
  - step 3: clean exit 0 (12/12 accepted); defective exit 1 by design (10/10 rejected, each for its own reason)
  - step 5: clean exit 0 (11 stress-tested, 1 stopped at the Groq handoff; risk levels CRITICAL 7, HIGH 1, MODERATE 1, LOW 2); defective refused (exit 1, nothing written)
  - `python3 scripts/tools/scenariostresstestingagent-parity-check.py`: exit 0, 24/24 compared cases identical to the original code (Validate Portfolio under node; the three Python nodes by exec inside a small shim), one defective request (a string weight) not modelled and refused by the gate
  - `python3 scripts/tools/scenariostresstestingagent-self-test.py`: exit 0, 27/27 checks as expected, including 12 deliberate breaks (a renamed node, a rewired connection, a tampered fixture, a holding without a ticker, and eight breaks of the port: no rescale, a wrong threshold, `>=` for `>`, one-decimal rounding, an extra shock, a wrong default scenario, a wrong sector, a custom scenario on the template branch; each caught)
  - `node scripts/conformance.mjs`: all conform; `node scripts/manifest-check.mjs`: passed
- **Fixed while building:** none needed beyond a corpus design choice; the parity check matched on the first full run (including the engine's error branches and the `portfolio.holdings is not iterable` message).
- **Observations, offered as open questions for the maintainers and not as findings:**
  - the Stress_Test_Engine uses a fixed sector map (ten tickers; any other ticker is treated as `tech_sector`) and a fixed starting value of 10000; the two lists `ai_stocks` and `growth_stocks` are fixed too
  - two template shocks are defined but the engine never reads them: `volatility_spike` (every scenario) and `all_sectors` (black_swan), so black_swan applies only its market shock; `horizon_days` passes through Validate Portfolio and is not used
  - a holding with no weight passes Validate Portfolio when the other weights sum to 1.0 and then fails in the engine (`KeyError: 'weight'`); all-zero weights are rescaled by zero, become NaN, and the engine fails on them (`TypeError`); a negative weight, an unknown scenario_type, and an empty holdings array all run without a message (the step-3 gate rejects these four, says so in its audit, and the port reproduces the workflow's behaviour so parity holds either way)
  - the Fetch_Data node carries a placeholder API key string and a fixed symbol (NVDA); it is never called here
- **Unchanged:** the eight generated per-node scripts for this recipe (`scripts/gigo/scenariostresstestingagent-parse-input.py`; `scripts/ingest/scenariostresstestingagent-fetch-data.py`; `scripts/tools/scenariostresstestingagent-{basic-llm-chain,groq-chat-model,parse-llm-response,save-portfolio-before-llm,stress-test-engine,webhook-trigger}.py`).
- **Open issues:**
  - [OPEN] Steps 2, 4 and 6 and the script mappings for the respond-to-webhook and human-report nodes: still `[TODO: DEV]` (`todos_open` is 5).
  - [OPEN] Live mode: no approval record; the Alpha Vantage request, the Groq call and the webhook reply are only recorded handoffs (`approved_for_live_action: false`); Parse_LLM_Response is not ported, so a custom scenario stops at the Groq handoff.
  - [NOT COVERED] Real portfolios, live behaviour, and whether the template shocks and the engine's risk thresholds are sound (ported faithfully, not judged).

## 2026-10-26 -- Add Finance Investigator named materiality approval

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`). Closes the open issue every prior run of this project has carried: the materiality threshold was a fixture nobody had approved.
- **Inputs:** `data/verified/mycroft-finance-investigator` (2026-02 pack, six source files); `projects/Mycroft-Finance-Investigator/config/sample-materiality-approval.json` as a clearly-marked fixture, not an approval.
- **Commands:** Ran the complete project unit suite; ran `materiality-request` against the real verified pack; exercised the four refusal paths through `record-materiality` (agent-authored decision, placeholder reasoning, scope mismatch, overwrite of an existing approval); ran repo conformance on every added file.
- **Outputs:** `mycroft_finance_investigator/materiality.py`; `schemas/materiality-approval.schema.json`; `config/sample-materiality-approval.json`; `tests/test_materiality.py` (18 cases); `materiality-request` and `record-materiality` CLI commands.
- **Result:** A threshold can now reach `APPROVED` only through a record naming a human, stating a basis of at least twenty characters, and carrying the SHA-256 of all six source files as the approver saw them. Reading an approval back re-hashes the pack, so an approval recorded against one pack cannot authorise a different one. Approvals are append-only; a second write to the same path is refused. All 84 project tests pass (66 existing, 18 new).
- **Open issues:** No approved threshold is committed, by design -- the shipped sample is a fixture and says so. `APPROVED` records that a named human set the amount against specific data; it does not assert the amount is appropriate, and the engine cannot tell a considered basis from a plausible-sounding one. Causal explanation, adequacy, and distribution remain with a named human.

## 2026-10-26 -- Add Finance Investigator evidence freshness

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`). A variance report is a claim about a period; the age of the data behind it is invisible in the numbers.
- **Inputs:** `data/verified/mycroft-finance-investigator/provenance.json` (period 2026-02, created_on 2026-07-26).
- **Commands:** Ran the complete project unit suite; ran the `freshness` CLI against the project's own shipped pack; exercised the impossibility refusal, the missing-provenance refusal, and both limit boundaries; ran repo conformance on every added file.
- **Outputs:** `mycroft_finance_investigator/freshness.py`; `tests/test_freshness.py` (14 cases); `freshness` CLI command.
- **Result:** The engine measures two gaps separately -- arrival lag (period close to data creation) and shelf age (data creation to time of use) -- and reports FRESH, STALE or EXPIRED against supplied limits. Run against this project's own verified pack it returns **STALE at 148 days of lag**: the 2026-02 pack was created 2026-07-26. A pack with no provenance is refused rather than assumed fresh, and a pack whose created_on precedes the end of the period it claims to describe is refused as impossible rather than merely stale. All 98 project tests pass (84 existing, 14 new).
- **Open issues:** The engine measures the gaps; it cannot judge whether a gap disqualifies a claim. A 148-day lag is routine for an annual audit and disqualifying for a weekly flash report, and the limits are supplied, not derived. No limit policy is committed as approved.

## 2026-10-26 -- Add Finance Investigator reviewer disagreement log

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`). The review gate records approve, request-changes or block. It had no way to record the common case: the reviewer accepts the report but rejects one finding in it.
- **Inputs:** `logs/mycroft-finance-investigator-sample-2026-02.json` (the Week 2 investigation and its four category findings).
- **Commands:** Ran the complete project unit suite; appended a reviewer position against the real 2026-02 revenue finding; exercised the agent-authorship, unknown-claim, restated-value, placeholder-basis, duplicate-reviewer and detached-run refusals; ran repo conformance on every added file.
- **Outputs:** `mycroft_finance_investigator/disagreement.py`; `tests/test_disagreement.py` (13 cases); `record-disagreement` CLI command.
- **Result:** A named reviewer can record a position (`NOT_MATERIAL`, `MATERIAL_EXPECTED`, `MISCLASSIFIED`, `INSUFFICIENT_EVIDENCE`) against a category the engine actually reported on, with a stated basis. Both sides are kept: the engine's figure is copied from the run rather than from the record, and a record that tries to restate `engine_value` is refused. The log binds to the run's SHA-256, so if the run changes the log detaches rather than silently referring to findings that no longer exist. Two reviewers may disagree with the same finding; one reviewer may not restate a position. All 111 project tests pass (98 existing, 13 new).
- **Open issues:** A recorded disagreement resolves nothing. Neither side is adopted, the engine's numbers are unchanged, and no downstream artifact currently consumes the log. Whether a reviewer's position is correct is outside what this records.

## 2026-10-26 -- Add Finance Investigator evidence coverage

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`). Findings already carried evidence references. Nothing had ever resolved them.
- **Inputs:** `logs/mycroft-finance-investigator-sample-2026-02.json`; `data/verified/mycroft-finance-investigator` (six source files).
- **Commands:** Ran the complete project unit suite; ran the `coverage` CLI against the real 2026-02 run and pack; exercised all three failure modes plus malformed references; ran repo conformance on every added file.
- **Outputs:** `mycroft_finance_investigator/coverage.py`; `tests/test_coverage.py` (11 cases); `coverage` CLI command.
- **Result:** Every evidence reference is parsed into file, column and value, then resolved by reading the file and finding the row. Against the real 2026-02 investigation **all 21 references across 4 claims resolve**. Three failures are reported separately rather than collapsed into "unsourced": `UNCITED` (no evidence at all), `DANGLING` (file not in the pack) and `UNRESOLVED` (file present, no matching row). A malformed reference raises rather than being skipped. All 122 project tests pass (111 existing, 11 new).
- **Open issues:** Resolution proves the cited row exists. It does not prove the row supports the claim -- a figure can resolve perfectly and still be the wrong figure. Nothing yet blocks a report whose coverage is incomplete; the check reports, it does not gate.

## 2026-10-26 -- Add Finance Investigator distribution gate

- **Recipe:** `mycroft-finance-investigator` v0.1.0 (`DRAFT`). Every upstream feature produced an artifact and stopped. None of them prevented a report being sent to someone who would act on it.
- **Inputs:** the artifacts produced by the four preceding features -- materiality approval, freshness assessment, coverage report, review decision, disagreement log.
- **Commands:** Ran the complete project unit suite; ran `distribution-gate` end to end against the real artifacts generated today; verified the empty call blocks on four conditions rather than passing; ran repo conformance on every added file.
- **Outputs:** `mycroft_finance_investigator/distribution.py`; `tests/test_distribution.py` (13 cases); `distribution-gate` CLI command.
- **Result:** The gate is BLOCKED by default and clears only when every condition is positively demonstrated by an artifact on disk. A missing artifact blocks; it is never read as a pass. Run against today's real artifacts it returned **BLOCKED**, clearing materiality, freshness and coverage while blocking on a missing review decision and one open disagreement on revenue. `STALE` evidence is allowed through with the lag stated, because lateness is a fact a reader can weigh; `EXPIRED` is not. Every blocking reason is reported, not just the first. All 135 project tests pass (122 existing, 13 new).
- **Open issues:** `CLEARED` authorises sending, not believing. It means each precondition was demonstrated by an artifact, not that the report is correct or the judgements behind it sound. The gate does not send anything, and nothing yet prevents a human bypassing it.
