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
