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
