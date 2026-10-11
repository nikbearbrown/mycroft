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
