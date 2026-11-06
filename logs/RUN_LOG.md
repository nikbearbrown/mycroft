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

## 2026-08-30 -- Investigated "Unknown Source" Google News fallthrough (partial fix)

- **Recipe:** Project 29 regulatory intelligence hardening, follow-up investigation after the B2 fix.
- **Inputs:** live Google News feeds (FINRA + Investment Advisor searches); `scripts/regulatory-intel/workflow.dev.json`.
- **Commands / actions:** Pulled all 18 real items (live, 2026-08-30) currently falling through to `'Unknown Source'` and read every title. Found ~half use a synonym the classifier didn't check for ("adviser"/"advisor" alone, "RIA" acronym, "broker-dealer", "Reg BI"); added those as feed-agnostic secondary keywords in `identifySource()`. Verified against the real extracted node function run against all 5 live feeds: Unknown Source count 18 -> 8, zero unexpected reclassifications of already-correct items.
- **Outputs:** Updated `scripts/regulatory-intel/workflow.dev.json` (`Normalize Data` node); `scripts/regulatory-intel/UNKNOWN-SOURCE-INVESTIGATION.md`.
- **Result:** Partial, honest fix — 10/18 recovered. The remaining 8 are genuinely unclassifiable from title alone (generic overview pieces with no named regulator, or one item that's a different regulator entirely — the UK FCA, correctly left as Unknown Source since this pipeline doesn't track it).
- **Open issues:** The remaining 8 would need real content/NLP analysis to close, at a materially higher false-positive risk — left open per the explicitly-flagged tradeoff before starting. B3 (Google News URL unwrap) still open.

## 2026-08-31 -- Project 29 regulatory workflow: B3 fix (Google News URL unwrap)

- **Recipe:** Project 29 regulatory intelligence hardening (Layer 1), follow-up to the 2026-07-24, 2026-08-30 (A7/B2/Unknown-Source) entries.
- **Inputs:** `scripts/regulatory-intel/workflow.dev.json` (`Normalize Data` node); live Google News feeds.
- **Commands / actions:**
  - Confirmed live: modern Google News redirect links have no `url=` param and don't 302 to the real article; the real URL is only obtainable via the same internal `batchexecute` RPC call (`Fbv4je`) the Google News web page itself uses, keyed by a `data-n-a-id`/`data-n-a-ts`/`data-n-a-sg` triple embedded in the redirect page.
  - Prototyped in Python: 1 item, then 20/20 (10 per feed) decoded successfully.
  - Ported to the exact JS to go in the node; tested directly in Node (native `fetch`): 16/16 decoded.
  - Caught a critical ordering bug before deploying: `identifySource()`'s Google News branch depends on the link still being `news.google.com` — the old code's classification call happened after the (broken, no-op) unwrap, so it accidentally worked; with unwrapping now actually working, classifying after unwrapping would have silently broken the B2/Unknown-Source-Investigation fixes for every Google News item. Fixed by classifying on the original `rawLink` before unwrapping.
  - Added `gnewsSeen`/`gnewsUnwrapped` counters to the run summary log, so a future silent degradation (e.g. Google changing the internal API) shows up in the log instead of links quietly going back to being useless redirects.
  - Full end-to-end test of the actual post-fix node code (via `$input.all()` + top-level await, matching n8n's Code node execution model): 6 live FINRA Google News items + 3 live SEC items — all 6 unwrapped to real publisher URLs, all 6 still correctly classified `FINRA Enforcement News`, SEC items unaffected.
  - Ran `node scripts/conformance.mjs scripts/regulatory-intel/workflow.dev.json` — valid JSON.
- **Outputs:** Updated `scripts/regulatory-intel/workflow.dev.json` (`Normalize Data` node); `scripts/regulatory-intel/B3-VERIFICATION.md`.
- **Result:** B3 closed. Google News links now resolve to real, working article URLs instead of opaque redirects, with graceful fallback and visible seen/unwrapped counts on any failure.
- **Open issues:** Not verified here — whether the fellow's specific live n8n instance's Code node supports `fetch`/top-level `await` (confirm when pasting in); this relies on an undocumented Google endpoint that could change without notice (mitigated by fallback + logging, not guaranteed); request volume adds ~400 extra requests per run (deliberately sequential, not parallelized, to reduce rate-limit risk). Remaining 8 "Unknown Source" items (from the prior investigation) still open.

## 2026-09-29 -- Project 29 regulatory workflow: B5 fix (all-clear email under-reports sources)

- **Recipe:** Project 29 regulatory intelligence hardening (Layer 1), follow-up to the 2026-07-24, 2026-08-30 (A7/B2/Unknown-Source), and 2026-08-31 (B3) entries.
- **Inputs:** `scripts/regulatory-intel/workflow.dev.json` (`Send email` node).
- **Commands / actions:**
  - Investigated `FINDINGS.md`'s open item "apply A4/B4 to Generate Email" first — traced the full node graph and git history (`fa88e05`, the original hardening commit) and confirmed both `esc()` HTML-escaping and the aligned `>6` threshold were already present in `Generate Email` and `Generate HTML Report` before `FINDINGS.md` was even written. Closed as stale, no code change needed there.
  - While tracing the graph, found the legacy "all clear / no new items" status email (`Send email` node, fed by `If2`'s no-high-priority branch) has a static "Monitored Sources" grid and summary line listing only 4 of the workflow's 5 real RSS feed nodes — `Investment Advisor Rules` was missing from both.
  - Fixed: added the missing source card to the grid and the missing feed name to the prose line, matching the real `rssFeedRead` node name exactly.
  - Verified: regex-extracted every source-card label from the patched node and diffed against the workflow's actual 5 `rssFeedRead` node names — exact 5/5 match. Ran `node scripts/conformance.mjs scripts/regulatory-intel/workflow.dev.json` — valid JSON.
- **Outputs:** Updated `scripts/regulatory-intel/workflow.dev.json` (`Send email` node); `scripts/regulatory-intel/B5-VERIFICATION.md`.
- **Result:** B5 closed. The all-clear status email now accurately reports all 5 monitored sources instead of silently under-reporting 4. `FINDINGS.md`'s stale "apply A4/B4 to Generate Email" note also resolved (documented as already-fixed, not re-opened).
- **Open issues:** Remaining 8 "Unknown Source" items (Google News, no reliable title-only signal) still open, per the 2026-08-30 investigation.

## 2026-09-29 -- Project 29 regulatory workflow: C2 fix (Layer 2 LLM re-scoring for C1 misfires)

- **Recipe:** Project 29 regulatory intelligence hardening, follow-up to `FINDINGS.md`'s C1 (keyword scorer misfires, intentionally left unfixed as the Layer-2/3 baseline) and its own roadmap ("Layer 3: LLM second-pass, local Ollama, target the Immediate/Emergency misfire class").
- **Inputs:** `scripts/regulatory-intel/workflow.dev.json`; `Regulatory_QA/backend/app/config.py` (existing Ollama convention: `http://localhost:11434`, model `llama3.2:3b`); live `mycroft_intelligence` DB rows for the 2 named C1 false positives (ids 4, 966/967) and 1 genuine true positive (id 153, the SEC insider-trading case from A7-VERIFICATION.md).
- **Commands / actions:**
  - Ollama was not installed on this machine at all. Installed via `brew install ollama`, started via `brew services start ollama`, pulled `llama3.2:3b` (matching `Regulatory_QA`'s exact configured model) — verified live, not assumed.
  - Prototyped the re-score prompt in standalone Python against the 3 real rows; iterated once (added an explicit impact-level guide) after the first pass correctly separated confirm/downgrade but was imprecise about how far to downgrade.
  - Ported to a new n8n Code node, `Layer 2 - LLM Re-Score`, inserted between `Code in JavaScript` and `If2`. Only calls Ollama for items with `urgency_score > 6` (the same gate `High Priority Filter` uses) — skips items that were never going to alert anyway. Never overwrites the keyword scorer's original `urgency_score`/`impact_level` (already committed to Postgres upstream) — only adds new `llm_*` fields. Fails open on any error (network/timeout/bad JSON) so a broken re-score never blocks the run. Sequential, not parallelized (same deliberate choice as B3).
  - Updated `High Priority Filter`'s condition (legacy IF node) to require `urgency_score > 6 AND llm_downgrade == false` (added a `boolean` condition, `combineOperation` changed `any` -> `all`).
  - Verified live, twice: (1) extracted the exact shipped node code from `workflow.dev.json` and ran it via a `$input.all()` harness matching n8n's Code node execution model against all 3 real rows — both named C1 false positives (Medicare "Emergency Medical Treatment", Nasdaq "Immediate Effectiveness") correctly flagged `downgrade`; the genuine SEC case correctly skipped the LLM call entirely (its `urgency_score` of 5 never passes the alert gate regardless, matching existing behavior). (2) Separately pointed the same shipped code at an unreachable port to simulate an Ollama outage — confirmed fail-open: `llm_reviewed: false, llm_downgrade: false`, item unaffected.
  - Ran `node scripts/conformance.mjs scripts/regulatory-intel/workflow.dev.json` — valid JSON.
- **Outputs:** Updated `scripts/regulatory-intel/workflow.dev.json` (new `Layer 2 - LLM Re-Score` node; `High Priority Filter` condition); `scripts/regulatory-intel/C2-VERIFICATION.md`.
- **Result:** C2 closed for the 2 named false-positive patterns. Both real named misfires (Medicare/EMTALA "emergency", Nasdaq "Immediate Effectiveness") are now correctly caught and excluded from the alert path; the genuine SEC enforcement true positive is unaffected. Fail-open behavior confirmed live, not assumed.
- **Open issues:** Corrected impact level lands on "High" rather than Medium/Low for clearly-routine items even after prompt tuning — the `verdict` (confirm/downgrade) is the reliable signal driving alert routing, `corrected_impact_level` is a less-precise display/audit field only. Only tested against the 2 named patterns + 1 true positive, not a full labeled benchmark (`FINDINGS.md`'s own "Layer 2: freeze the baseline" benchmark step was never built separately). Adds real per-run latency: at the pipeline's historical urgency histogram (~111 items/run scoring above threshold), a full run could add several minutes of sequential local LLM calls — not measured at that scale, only per-item (3.3-3.6s for 2 calls). This entire feature depends on Ollama running on the deployment machine; not verified against the fellow's actual live environment.

## 2026-10-06 -- Project 29 regulatory workflow: B2 addendum (LLM fallback classification for the residual "Unknown Source" items)

- **Recipe:** Project 29 regulatory intelligence hardening, follow-up to the 2026-08-30 B2 fix and the 2026-08-30 "Unknown Source" investigation, which left 8 items open as a deliberate tradeoff (no reliable keyword signal, real risk of false-positiving on unrelated content with more rules).
- **Inputs:** `scripts/regulatory-intel/workflow.dev.json` (`Normalize Data`, `Layer 2 - LLM Re-Score`); live `mycroft_intelligence` DB — all 21 `Unknown Source` rows; `Regulatory_QA/backend/app/config.py`'s existing Ollama convention (already installed this session for C2).
- **Commands / actions:**
  - Re-ran the live `identifySource()` function (extracted from the current `workflow.dev.json`, not a stale copy) against all 21 DB rows tagged `Unknown Source` — confirmed 13 are already resolved by keyword-rule fixes landed since `FINDINGS.md`'s original 2026-07-24 snapshot (the Federal Register `dc:creator` fix and the 2026-08-30 synonym fix); the genuine residual is still exactly the same 8 items the 2026-08-30 investigation named.
  - Added a new Code node, `Layer 2 - LLM Source Classification`, inserted between `Normalize Data` and `Filter Valid Content`. Only calls Ollama (`llama3.2:3b`) for items where `source_feed === 'Unknown Source'` — every other item passes through untouched. Validates the model's reply against the fixed 5-category list (treats any invalid/unexpected reply the same as `Unknown Source`, never silently mis-labels). Fails open on any error, same pattern as `Layer 2 - LLM Re-Score` and the B3 Google News unwrap.
  - Verified live, twice: (1) built a Node.js harness running the exact extracted node code through the full two-stage pipeline (keyword rules, then the new node) against all 21 real rows — confirmed 0 of the 13 already-resolved items were touched, and of the 8 genuine residual items, 1 was resolved (`"Recent Enforcement Actions Define the 'Person' that Participates in a Partial Tender" -> FINRA Enforcement News`) while the model correctly declined to guess on the remaining 7 rather than force a label onto genuinely generic/ambiguous content. (2) Pointed the same extracted code at an unreachable Ollama port — confirmed fail-open: already-classified items pass through byte-identical, the `Unknown Source` item stays `Unknown Source` with `llm_source_error` logged, no crash.
  - Ran `node scripts/conformance.mjs scripts/regulatory-intel/workflow.dev.json` — valid JSON.
- **Outputs:** Updated `scripts/regulatory-intel/workflow.dev.json` (new `Layer 2 - LLM Source Classification` node); `scripts/regulatory-intel/B2-VERIFICATION.md`.
- **Result:** Honest, modest result — 1 of 8 residual items resolved, 7 correctly left as `Unknown Source` rather than guessed. Confirms the remaining backlog isn't a solvable keyword-matching problem; some of it is content that doesn't belong to any of the 4 tracked categories at all.
- **Open issues:** Net yield is small on this sample (1/8); yield on a larger, more varied future set of `Unknown Source` items is unverified. Adds one bounded Ollama call per `Unknown Source` item per run (same per-run latency tradeoff already accepted for C2). Not verified against the fellow's live n8n instance.

## 2026-10-15 -- Project 29 regulatory workflow: B6 fix (alert email dropped on exactly 1 high-priority item)

- **Recipe:** Project 29 regulatory intelligence hardening, new investigation this week (not a named `FINDINGS.md` item) — re-read `FINDINGS.md`'s "Implications for the plan" section for the next open gap, then grepped `workflow.dev.json` directly for suspicious hardcoded comparisons in nodes not yet touched by any prior fix.
- **Inputs:** `scripts/regulatory-intel/workflow.dev.json` (`Generate Email` node, the real alert-email path — distinct from the `Send email` all-clear node fixed in B5).
- **Commands / actions:**
  - Found `Generate Email`'s `hasData` guard reads `newItems.length > 1` where every other length check in the node (and the dead code two lines below it) implies the author meant "at least one item," not "more than one." Traced the downstream `If` node's connections and confirmed its true-output wire is empty (`[]`) — so `has_items: false` silently reaches a dead end, no email, no error, no log line a human would notice.
  - Built a live Node.js harness (`new Function('$', code)`) running the exact extracted `jsCode` from the node — not a rewritten copy — against synthetic 0/1/2-item batches, before and after the fix. Confirmed the bug for real: 1 item -> `has_items: false` (bug); 0 items -> `has_items: false` (correct, unchanged); 2 items -> `has_items: true` (already worked, unchanged after fix — no regression).
  - Fixed: `newItems.length > 1` -> `newItems.length > 0` in `workflow.dev.json`. One-character-class change; confirmed via `grep -o` the string appeared exactly once in the file before patching, so no unintended second match.
  - Re-ran the harness directly against the real patched file on disk (not the synthetic copy) to confirm the actual change works: 1 item -> `has_items: true, total_new: 1`, real HTML email body generated.
  - Ran `node scripts/conformance.mjs scripts/regulatory-intel/workflow.dev.json` — valid JSON, passes.
- **Outputs:** Updated `scripts/regulatory-intel/workflow.dev.json` (`Generate Email` node); `scripts/regulatory-intel/B6-VERIFICATION.md`.
- **Result:** B6 closed. A single urgent/critical filing — the exact scenario this alert path exists to catch — no longer silently fails to generate an email. No regression on the 0-item or 2+-item cases, both already correct before this fix.
- **Open issues:** None identified for this specific node. The now-still-unreachable `newItems.length === 0` dead-code check two lines below the fix was left in place (harmless, not worth touching in a minimal one-line fix). The `Regulatory_QA` `SourceFeed` enum / `source_feed` compatibility gap flagged during this week's investigation (identified but not yet fixed) remains open for a future week.

## 2026-10-27 -- Project 29 regulatory workflow: C3 fix (Layer 2 LLM's corrected severity discarded)

- **Recipe:** Project 29 regulatory intelligence hardening, new investigation this week (not a named `FINDINGS.md` item) — re-read `RUN_LOG.md`/`FINDINGS.md` for the known-fixed list, diffed `main` against `feature/regulatory-intelligence-hardening` to avoid re-finding anything already fixed, then traced every consumer of C2's `llm_corrected_impact_level` field.
- **Inputs:** `scripts/regulatory-intel/workflow.dev.json` (`Layer 2 - LLM Re-Score`, `Generate Email` nodes).
- **Commands / actions:**
  - Found `Generate Email` buckets/counts items into Critical/High sections using only the keyword scorer's original `impact_level`, never `llm_corrected_impact_level` — confirmed via grep that the field is written in exactly one place (`Layer 2 - LLM Re-Score`) and read nowhere in the repo.
  - Built a live Node.js harness running the exact extracted `jsCode` from `Generate Email` against a 3-item batch covering every real case (LLM-confirmed-but-recategorized, LLM-confirmed-unchanged, never-reviewed) — confirmed the bug for real: the recategorized item (Critical -> High per the LLM) stayed counted as Critical before the fix.
  - Fixed: added an `effectiveImpact()` helper preferring `llm_corrected_impact_level` when `llm_reviewed` is true, falling back to `impact_level` otherwise; `criticalItems`/`highItems` now filter on this instead of the raw field.
  - Re-ran the same harness against the real patched file on disk — recategorized item now counted High; unchanged and never-reviewed items unaffected (no regression).
  - Ran `node scripts/conformance.mjs scripts/regulatory-intel/workflow.dev.json` — valid JSON, passes.
- **Outputs:** Updated `scripts/regulatory-intel/workflow.dev.json` (`Generate Email` node); `scripts/regulatory-intel/C3-VERIFICATION.md`.
- **Result:** C3 closed. The Layer 2 LLM review's severity correction (C2's stated purpose) now actually affects the alert email's bucketing/counts for the first time since C2 shipped, instead of being computed and silently discarded.
- **Open issues:** A related, separate defect was also found this week in `Regulatory_QA/backend/app/crud.py`'s `get_stats()` — dashboard stats re-bucket by raw `urgency_score` with cutoffs that disagree with the `impact_level` column every other part of the system relies on (57/411 real rows land in a different tier in the stats than their own `impact_level` says). Not fixed this week; candidate for a future week.

## 2026-11-03 -- Project 29 regulatory dashboard: D1 fix (stats re-bucketed by stale urgency_score cutoffs instead of impact_level)

- **Recipe:** Project 29 regulatory intelligence hardening, closing the open item flagged during last week's C3 investigation (`Regulatory_QA/backend/app/crud.py`'s `get_stats()`).
- **Inputs:** `Regulatory_QA/backend/app/crud.py` (`FeedCRUD.get_stats()`); live `mycroft_intelligence` DB @ `localhost:5431` (411 real rows); `Regulatory_QA/frontend/src/components/Stats.jsx` (consumer, to confirm the key-name contract before changing the query).
- **Commands / actions:**
  - Confirmed live via `psql` that the mismatch is still real and current: 62/411 rows (15%) land in a different severity tier under `get_stats()`'s `urgency_score` cutoffs than their own `impact_level` column says (grown slightly from the 57/411 spotted during the C3 investigation, consistent with a live-queried table).
  - Confirmed `impact_level` only ever takes 3 of its 4 possible values in the current data (`Critical`/`High`/`Medium`; `Low` exists in the scorer's own code but never got produced in this fixture set) — not a defect, just means the `low` bucket reads 0 under both the old and new query.
  - Checked `Stats.jsx`, the only frontend consumer — it reads `urgency.critical`/`urgency.high` off the response's `urgency_distribution` object, so the key names had to stay exactly the same.
  - Fixed: `get_stats()`'s urgency/severity SQL now buckets by `impact_level = 'Critical'/'High'/'Medium'/'Low'` directly instead of re-deriving tiers from `urgency_score >= 8` / `BETWEEN 6 AND 7` / etc. Same `FILTER`/windowing structure, same response shape, different column.
  - Verified live against the real DB: old query (411 rows) → Critical 32 / High 139 / Medium 240 / Low 0; new query → Critical 33 / High 98 / Medium 280 / Low 0 — a real, substantial difference (old method overcounted High by 41 items, 30% inflated), not a no-op change.
  - Did not re-verify against the endpoint's actual 7-day/30-day rolling windows in production, since the fixture data's `created_at` range (14–24 Jul 2026) is months stale relative to "now" — both old and new queries return all-zero on that window for this dataset, a property of the stale fixture, not the fix; the unwindowed whole-table comparison is what demonstrates the real behavioral change.
  - `python3 -m py_compile` on the patched `crud.py` — clean.
- **Outputs:** Updated `Regulatory_QA/backend/app/crud.py` (`FeedCRUD.get_stats()`); `scripts/regulatory-intel/D1-VERIFICATION.md`.
- **Result:** D1 closed. Dashboard severity counts now reflect the same `impact_level` label the alert email and every other part of the system already treats as authoritative, instead of an independently-derived, silently-drifting approximation from `urgency_score`.
- **Open issues:** Not verified against a live, actively-populated deployment of this dashboard (only the stale local fixture DB) — the 7-day/30-day windowed queries themselves are unverified against real recent data, only the underlying bucketing logic. `impact_level` rows that are `NULL` (none currently exist, not checked for) would silently fall into none of the four buckets under the new query, same non-coverage as an out-of-range `urgency_score` would have under the old one — not a new gap, not addressed.
