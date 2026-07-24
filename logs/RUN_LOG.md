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

## 2026-07-20 -- Repository runtime and buildability audit

- **Recipe:** Repository-level diagnostic review; no recipe lifecycle promotion attempted.
- **Inputs:** Tier 1 governance files; non-quarantined recipes, conductors, scripts, reports, project exercises, verified schema, status, and run history.
- **Commands:** `npm run verify`; strict manifest check; explicit conformance over 460 Python files and 109 additional human/data surfaces; Python compile-all; recipe/conductor/script path cross-checks; three representative local sample-script invocations.
- **Outputs:** This audit entry only; no recipe output, verified records, gate decision, attestation, or human report was generated.
- **Result:** The default 136-file gate and strict manifest check pass. All 460 stored Python files compile. The extended surface check fails because `data/verified/ai_company_signals-schema.yaml` contains a second YAML document marker at line 173. Representative scripts fail at runtime because 10 imported underscore-named shared modules exist only under hyphenated filenames; 103 internal import statements depend on those modules. The 98 actual recipe specifications declare 1,613 unique script paths, of which 401 exist and 1,212 are absent; 97 legacy Markdown recipes lack lifecycle status metadata. All 32 unique conductor-declared script paths are absent under their documented underscore names. The documented `snickerdoodle` CLI and the vendor recipe's `agents/run_brief.py` entry point are not present locally.
- **Open issues:** Default conformance skips the verified schema and generated/imported step directories; no local verified records, operational generated reports, gate-decision files, or attestations were found; `status.md`, `DOMAIN.md`, and `_MANIFEST.md` counts/state lag the July vendor-intelligence additions. Human adequacy review and prioritization are still required before implementation.

## 2026-07-24 -- Import Earnings Call Sentiment Analyzer project

- **Recipe:** `earnings-call-sentiment-analyzer` v0.1.0 (`DRAFT`).
- **Inputs:** User-supplied full-stack project at `/Users/adwaitchangan/Study/Mycroft/Earnings_Call_Sentiment_Analyzer/`; user-created Northstar Cloud Systems Q3 FY2026 sample transcript.
- **Commands:** Copied 84 durable project files; compared the raw transcript copy with `cmp` and SHA-256; ran 9 Python worker tests; installed frontend dependencies; ran frontend production build and lint; validated Docker Compose configuration, Maven XML, Python compilation, 34-file targeted conformance, and repository verification.
- **Outputs:** `projects/Earnings-Call-Sentiment-Analyzer/`; `data/raw/earnings-call-sentiment-analyzer/`; `recipes/earnings-call-sentiment-analyzer.md`; `conductor/earnings-call-sentiment-analyzer.md`; `reports/templates/earnings-call-sentiment-analyzer.md`; updated project indexes, status, and data contract.
- **Result:** Source folder preserved; imported transcript hash is `b3f75b1f233281864121dbb5d5d372baf8e734c1c9c2670509b84c930e8ca14f`; worker tests pass 9/9; frontend build and lint pass; Compose configuration and targeted conformance pass. The transcript is explicitly classified as a user-created sample, not real issuer evidence.
- **Open issues:** Maven is unavailable locally and the Docker daemon is not running, so the Spring Boot test/build, full Compose startup, FinBERT inference, PostgreSQL/RabbitMQ processing, export log/report, and human evidence review remain unverified. `npm ci` reported a non-blocking ESLint dependency engine warning and Recharts 2.x deprecation. Three recipe TODOs remain open; no lifecycle promotion occurred.

## 2026-07-24 -- Full-stack Earnings Call Sentiment Analyzer sample run

- **Recipe:** `earnings-call-sentiment-analyzer` v0.1.0 (`DRAFT`); no lifecycle promotion attempted.
- **Inputs:** User-created Northstar Cloud Systems Q3 FY2026 sample at `data/raw/earnings-call-sentiment-analyzer/northstar-cloud-systems-q3-fy2026.txt`; SHA-256 `b3f75b1f233281864121dbb5d5d372baf8e734c1c9c2670509b84c930e8ca14f`.
- **Commands:** Built and started the five-service Docker Compose stack; checked health and Flyway v1; uploaded the sample through the API; waited for FinBERT completion; fetched transcript, job, chunk, summary, section, and speaker APIs; reconciled probabilities, scores, orders, counts, and database rows with `jq` and PostgreSQL; tested HTTP 400 validation; ran 9 worker tests, frontend lint/build, and the backend Maven test lifecycle; inspected the live transcript list, dashboard, evidence search, and upload screen in the in-app browser.
- **Outputs:** `logs/earnings-call-sentiment-analyzer-20260724-050407-ncs-q3fy2026.json`; `reports/generated/earnings-call-sentiment-analyzer-20260724-050407-ncs-q3fy2026.md`; PostgreSQL transcript/job/summary row 1 with 25 chunks and 25 sentiment results.
- **Result:** All services ran; `ProsusAI/finbert` loaded; job 1 completed in under one second after receipt. Overall model judgment was +16.74% net tone with 9 positive, 11 neutral, and 5 negative evidence labels. All aggregates and stored evidence reconcile. Worker tests pass 9/9; frontend lint/build pass; Maven compiles 36 backend sources and succeeds. The run exposed a UI explanation that conflated FinBERT argmax evidence labels with ±5% aggregate net-tone bands; the copy was corrected before the feature-branch commit.
- **Open issues:** Human adequacy review is not signed. Four chunks have unknown section attribution and two have unknown speaker attribution. The model revision is not pinned/persisted. Maven reports no backend test sources, and the frontend has no automated test suite. No result was promoted to `data/verified`.
