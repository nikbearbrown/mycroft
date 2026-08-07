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

## 2026-07-13 -- Add AI-Vendor-Intelligence project exercises

> Logged retroactively on 2026-08-22. Commit `d2039bc` changed artifacts without a
> RUN_LOG entry, which the logging rule requires; this entry backfills the record and
> is not a contemporaneous account.

- **Recipe:** vendor-intelligence-brief (supporting course material, not a recipe run).
- **Inputs:** Mycroft chapters 2-5; the vendor intelligence platform as worked example.
- **Commands:** None — authored content, no scripts run.
- **Outputs:** `projects/AI-Vendor-Intelligence/` — four exercise files for chapters
  2-1, 3, 4, and 5 (859 lines total), committed as `d2039bc`.
- **Result:** Chapter exercises available; recipe status unchanged (DRAFT).
- **Open issues:** Exercises were written against recipe v0.1.0 and the pre-purge
  signal counts. They may cite coverage figures corrected on 2026-08-22 — review them
  against recipe v0.2.0 before use.

## 2026-08-22 -- Entity verification: signal validation gate cleared, schema drift corrected

- **Recipe:** vendor-intelligence-brief v0.1.0 -> v0.2.0 (stays DRAFT).
- **Inputs:** Uncommitted work in the sibling repo
  `~/Documents/AI-Vendor-Intelligence-Platform`
  (github.com/MuskanKhandelwal/AI-Vendor-Intelligence-Platform, branch `main`):
  new `collector/entity_filter.py`, `collector/audit_entities.py`,
  `collector/backfill_edgar_summaries.py`; modified `collector/{arxiv,news,edgar}_collector.py`,
  `collector/db.py`, `collector/seed_companies.json`, `agents/llm.py`.
  Backup artifacts `backups/wrong_entity_signals_20260807T*.json`.
- **Commands:**
  - Read the platform diff and the authoritative DDL at `collector/db.py:16-38`.
  - Counted the purged rows directly from the backup JSON (not estimated).
  - Rewrote `data/verified/ai_company_signals-schema.yaml` to v0.2.0.
  - Updated `recipes/vendor-intelligence-brief.yaml` to v0.2.0 and closed gate 1.
  - Updated `DATA_CONTRACT.md`; verified with `node scripts/conformance.mjs`.

- **The defect that prompted this.** Signals were collected by name search alone, and
  a company name is not a unique identifier. Namesake organisations were stored as the
  tracked vendor and became citable evidence in procurement briefs. Observed harm,
  per the platform's own source comments: a **$28M Department of War contract awarded
  to Cohere Technologies (wireless RF) raised the AI vendor Cohere's Financial Health
  score by 25 points**; quantum-physics papers matched on the stemmed word "coherence"
  were counted as its technology momentum; Cohere Health (health insurance) executive
  changes were filed under the AI vendor. arXiv was worst — the old `all:"{name}"`
  query searched full text including bibliographies against a stemmed index, and
  **85% of collected papers were unrelated to the vendor they were filed under**.

- **[GATE CLEARED] Signal validation (Phase 2)** — Muskan Khandelwal, 2026-08-22.
  - *Evidence:* `collector/audit_entities.py` run 2026-08-07 purged **782 rows** --
    650 `research_paper`, 49 `other`, 34 `negative`, 17 `product_launch`,
    16 `partnership`, 12 `regulatory`, 2 `executive_change`, 2 `funding` (sums to
    782). Most affected: Writer (52), OpenAI (49), Cohere (46), Anthropic (43),
    Modal (43), Mistral (41). All rows backed up to
    `backups/wrong_entity_signals_20260807T010057Z.json` (780) and
    `...T010153Z.json` (2) before deletion; nothing was destroyed.
  - *Scope of the clearance:* **batch level, not per signal.** The gate's original
    wording asked for human validation of >= 50% of individual signals. What was done
    is broader in coverage and shallower in depth — every name-searched row was
    machine-checked and the failures purged. There is no per-row human sign-off, and
    the `validated_by` column that wording assumed does not exist in the DDL.
  - *What it does not establish:* removing rows that failed the check says nothing
    about whether the survivors are right.

- **[DEFECT] Schema drift (P6), corrected.** `ai_company_signals-schema.yaml` v0.1.0
  described columns that do not exist. Corrected against `collector/db.py:16`:
  `signal_id`/UUID -> `id`/SERIAL, `company_id` -> `company_name`,
  `signal_title` -> `headline`, `signal_value` -> `summary`, `score` ->
  `importance_score`, `occurred_date` -> `signal_date`, `ingested_at` -> `created_at`;
  `source_type` removed (no such column — source is inferred from `raw_data` keys);
  `ticker`, `raw_data`, `langfuse_trace_id` added. The four validation columns
  (`validated_by`, `validation_note`, `validation_date`, `used_in_brief`) are not in
  the DDL and were moved to a labelled `planned_fields` block rather than deleted.

- **[DEFECT] Schema file never passed conformance.** v0.1.0 ended with a stray `---`
  document separator, so `yaml.safe_load` — the exact check `scripts/conformance.mjs`
  runs — raised `expected a single document in the stream`. The file had been carried
  since 2026-07-09 as if it were valid. Separator removed; the file now parses.

- **Outputs:**
  - `data/verified/ai_company_signals-schema.yaml` v0.2.0 (real DDL; new
    `entity_verification` section; entity audit registered under `audit_checks`)
  - `recipes/vendor-intelligence-brief.yaml` v0.2.0 (gate 1 `[CLEARED]`,
    `todos_open` 3 -> 2, arXiv/News/EDGAR source entries corrected, Langfuse v3 noted)
  - `DATA_CONTRACT.md` (gate row now partially cleared; two rules added)
  - This entry
- **Result:** Mycroft's record now matches the running system. Recipe stays **DRAFT** —
  SPECIFIED requires zero open TODOs and two gates are still open. No attestation.
- **Open issues:**
  - [GATE OPEN] Supervisor routing review (Phase 2) — no Langfuse trace reviewed or logged.
  - [GATE OPEN] Brief approval (Phase 2) — no procurement owner review process.
  - [BLOCKER] All per-source signal counts are stale (pre-purge). Recount before citing.
  - [RESIDUAL RISK] Common-word vendor names (Adept, Writer, Notion, Glean, Modal,
    Replicate) can still admit unrelated text; the LLM `about_company` backstop fails
    open on API error, so signals admitted during a Groq outage carry only the
    deterministic check.
  - [BLOCKER] Groq token limit at company #33 of 50 — Phase 3 batch job still blocked.
  - ~~The platform-repo changes above are **uncommitted** in that repo. Mycroft now
    documents work that has no commit hash to cite; commit there to complete the
    provenance chain (P3).~~
    **CLOSED 2026-08-26:** committed as `5edd72c` "Updates after testing"
    (10 files, +1291/-92) in MuskanKhandelwal/AI-Vendor-Intelligence-Platform.
    The provenance chain is complete; everything in this entry cites that hash.

## 2026-08-26 -- Brief evaluation harness + UNKNOWN enforcement; wrong-entity claims found in a finished brief

- **Recipe:** vendor-intelligence-brief v0.2.0 -> v0.3.0 (stays DRAFT).
- **Inputs:** Two new commits in MuskanKhandelwal/AI-Vendor-Intelligence-Platform,
  branch `main`, tree clean:
  - `2b44793` "Evaluation" (2026-08-26) — `evaluation/eval_runner.py` (323L),
    `evaluation/labeled_briefs.csv`, README known-issues rewrite.
  - `0fa8a10` "Test workflows" (2026-08-26) — `_enforce_unknown_sections` in
    `agents/supervisor.py`, `evaluation/test_eval_runner.py` (17 tests), CI wiring.
- **Commands:** Read both commits and the working files; counted checks, banned
  phrases, tests and CSV rows from source; updated the recipe, the signal schema, and
  this log; ran `node scripts/conformance.mjs` and `npm run verify`.

- **What was added upstream.** A deterministic evaluation harness for generated briefs,
  with two severities. FAIL: `check_structure` (all six sections present),
  `check_score_fidelity` (the brief's N/100 must equal `compute_financial_health()`'s
  rubric — the regression test for an LLM inventing its own number),
  `check_unknown_discipline` (a dimension with no evidence must say UNKNOWN),
  `check_filler` (11 banned generic phrases). WARN: `check_date_grounding` and
  `check_amount_grounding` (every date and dollar figure must trace to a collected
  signal; WARN not FAIL because legitimate aggregates derived from tool output would
  otherwise show as red).
  The harness's stated principle — *where a rule can be written down, write the rule
  instead of trusting a model to judge* — is the verification stack arrived at
  independently: FAIL is layer 1 (conformance, halts), WARN is layer 2 (audit, reports
  for a human).

- **UNKNOWN enforcement.** `agents/supervisor.py` now computes the no-data dimension
  list before synthesis and names those sections in the prompt, then rewrites them to
  "UNKNOWN - no data collected" after generation. Reason on the record: when the Neo4j
  graph went offline the model filled COMPETITIVE POSITION with "a prominent player in
  the AI development space" rather than admitting it had nothing. Per the source
  comment, a prompt is a request, not a guarantee — this makes the honest answer
  structural. This is P1 enforced in code: the machine stops the pipeline from
  proceeding past a gap because no failure was detected.

- **CI.** `.github/workflows/test.yml` renamed "API Health Check" -> "Tests"; runs
  `python -m unittest discover -s evaluation -v` on push/PR to main. Fixture-based, so
  no database, AWS or Neo4j credentials. The full eval that generates real briefs needs
  a live environment and stays manual.

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
