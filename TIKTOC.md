# Mycroft Finance Recipe Engine
## Tik TOC Architecture

**Working title:** Mycroft Finance Recipe Engine: Verified Workflows for Entry- and Mid-Level Finance Practitioners  
**Repository:** `books/mycroft`  
**Source adaptation:** Mycroft operating system, existing Mycroft finance recipes, attached finance recipe research, and the full TIKTOC detail template from the Causal Reasoning book architecture.  
**Document:** TIKTOC silent intake and chapter architecture  
**Status:** Architecture draft for manuscript rewrite, chapter renaming, and practitioner-guide production planning  

---

## Document Structure

1. Book Concept and Thesis
2. Learner Profile
3. Book Type and Deployment Specification
4. Repository-Specific Grounding
5. Field Positioning
6. Three-Act Learning Arc
7. Sequencing Model
8. Prerequisite Map
9. Chapter-by-Chapter TOC
10. Learning Outcomes by Chapter
11. Running Project Spine
12. Chapter Anatomy Template
13. Recipe and Case Strategy
14. Hard Topics, Contested Claims, and Aging Risk
15. Market Positioning
16. Feature List
17. Out of Scope
18. Adoption Risk Register
19. Open Questions

---

# Part 1 - Book Concept and Thesis

## Book Concept Summary

This book teaches entry- and mid-level finance practitioners how to build, read, and supervise Mycroft recipes for repeated finance work: variance packs, reconciliations, close support, AP/AR exception queues, cash visibility, control evidence, audit binders, contract/billing exception triage, and executive packet source checks.

The book is not about replacing finance judgment with AI. It is about turning repeated preparation work into verified workflows so human reviewers can spend more time on materiality, interpretation, accounting treatment, release, and accountability.

Mycroft is the book and the working repository, built on the Snickerdoodle framework. The manuscript teaches the method; the repo shows recipes, phase gates, logs, reports, and data contracts. The reader learns by building a bounded finance recipe system that produces both machine-readable logs and human-readable decision reports.

## One-Sentence Logline

Mycroft helps finance practitioners automate the preparation layer while preserving the human judgment layer that makes finance work accountable.

## Central Thesis

AI made finance execution cheaper; it did not make finance judgment cheaper. The useful opportunity is not a finance oracle, CFO bot, or autonomous analyst. The useful opportunity is a verified recipe system that gathers data, checks shape, matches records, surfaces exceptions, drafts review packs, and stops at explicit human gates before materiality, interpretation, accounting treatment, payment, disclosure, investor communication, tax position, regulatory filing, or release.

This book argues that entry- and mid-level finance people can create substantial value by turning their recurring work into inspectable Mycroft recipes. The recipe does the repetitive evidence assembly. The human does the work that cannot be delegated: deciding whether the evidence is sufficient, what the numbers mean, which explanation is warranted, which risk matters, and whether the output can move forward.

## Thesis Test

The proposed book structure mirrors `the-reallocation-engine/chapters/`:

- Chapters 1-5 establish the framework: fluency trap, reallocation principle, verified data contract, two customers, and evidence verification.
- Chapters 6-15 teach concrete finance recipes that entry- and mid-level practitioners actually run.
- Chapter 16 integrates the system through one bounded, logged, honest run.
- Appendices synthesize principles and operating best practices.

**Thesis test:** PASS. Every chapter builds a usable artifact and names the judgment AI cannot perform.

## The Irreducibly Human Layer

The attached Causal Reasoning architecture names the irreducibly human layer: problem formulation, identification, trust assessment, causal defense, metacognitive calibration, institutional judgment, and accountability. This finance book translates that layer into workplace finance:

- Materiality is human.
- Accounting treatment is human.
- Causal explanation of a variance is human.
- Control effectiveness conclusion is human.
- Revenue-recognition judgment is human.
- Payment release is human.
- Public disclosure is human.
- Investor or lender communication is human.
- Regulatory filing and suspicious-activity decisions are human.

AI can prepare the work surface. It cannot become the accountable finance professional.

---

# Part 2 - Learner Profile

## Primary Reader

An entry- or mid-level finance practitioner who spends much of the week gathering data, normalizing spreadsheets, comparing actuals to budget, preparing close support, chasing explanations, building dashboards, answering audit requests, or assembling management packets.

Specific roles:

- FP&A analyst
- Budget analyst
- Staff accountant
- Senior accountant
- Treasury analyst
- Revenue analyst
- Finance operations specialist
- Internal-audit associate
- Financial risk or compliance analyst
- Early-career financial analyst using public company data

## Prior Knowledge Assumed

- Basic spreadsheet fluency.
- Basic understanding of budgets, actuals, accounts, invoices, reports, and approvals.
- Comfort reading tables and following file paths.
- Willingness to work with structured recipe cards, logs, and report templates.
- Basic awareness that finance work is reviewed and controlled.

## Prior Knowledge Not Assumed

- Python programming.
- Advanced accounting policy.
- SEC reporting expertise.
- Audit methodology expertise.
- Treasury operations expertise.
- n8n workflow design.
- Multi-agent orchestration.
- Formal AI governance.

## Misconceptions the Book Must Correct

1. "AI can explain the numbers." AI can draft candidate explanations, but causal explanation and materiality require human review.
2. "If the reconciliation ties, the account is fine." Control totals are necessary, not sufficient.
3. "A dashboard is a decision." A dashboard is only useful if metrics have definitions, owners, sources, and decision use.
4. "Automation should remove review." In finance, automation should make review more focused and more traceable.
5. "Variance commentary is just writing." Variance commentary is evidence, interpretation, and accountability.
6. "The recipe can approve the work." A recipe can prepare the work; humans clear gates.

## Motivation Type

Professional and practical. The reader wants to be faster, more reliable, and more valuable at work. They do not primarily want theory. They want recipes that make repeated finance work cleaner, more inspectable, and easier to review.

The book should reward useful caution. The reader should finish with a portfolio of artifacts that show they can supervise AI-assisted finance work without surrendering judgment.

---

# Part 3 - Book Type and Deployment Specification

## Book Type

**Primary type:** Practitioner guide with course-textbook utility.

**Not:** A finance theory textbook, a valuation textbook, an accounting standards manual, a tax guide, an audit methodology manual, or an investment advice book.

## Primary Deployment Context

Workshops, applied finance analytics courses, AI-for-finance courses, finance transformation labs, business analytics programs, and self-guided workplace learning.

## Secondary Deployment Context

Professional development for analysts, finance operations teams, internal audit teams, and AI builders creating supervised workflows for finance teams.

## Terminal Capability

By the end of the book, the reader can design and supervise a bounded Mycroft finance recipe that:

- names the finance task and period;
- identifies source data, owners, versions, and freshness;
- validates shape and control totals;
- transforms data into an exception or review surface;
- separates verified findings from inferred or unexplained findings;
- produces an agent log and human report;
- stops at materiality, interpretation, approval, release, or sensitive-action gates;
- records the run honestly.

---

# Part 4 - Repository-Specific Grounding

## Constitution and Domain Layer

- `SNICKERDOODLE.md`: governing constitution, labor separation, verification stack, recipe lifecycle, TODO closure, attestation, and logging.
- `DOMAIN.md`: project index, runnable surfaces, quarantine rules, and relationship to Madison.
- `DATA_CONTRACT.md`: evidence and data-layer rules.
- `AGENTS.md` and `CLAUDE.md`: generated instruction adapters.

## Existing Chapter Layer

The current top-level chapter files are generic placeholders:

- `chapters/01-chapter-01.md` through `chapters/12-chapter-12.md`

This TIKTOC replaces that placeholder architecture with named finance-practitioner chapters. A later chapter-writing pass should rename or rewrite the current placeholders to the proposed chapter filenames.

## Recipe Layer

Existing finance-adjacent recipe coverage includes:

- SEC filings analysis
- Forecasting
- Portfolio dashboards
- Portfolio price fetching
- Portfolio intelligence with RAG
- Risk management
- Financial regulatory intelligence
- Financial intelligence hub
- Finance literacy bots

The coverage is strongest in external market/public-company intelligence and thinner in internal finance operations.

## Research Layer

Core research sources for this TIKTOC:

- `reports/generated/entry-mid-finance-recipes-research.md`
- `reports/generated/mycroft-finance-recipe-opportunities-attached-research.md`
- `reports/generated/entry-mid-finance-recipes-deep-research-prompt.md`
- attached `Mycroft Finance Recipe Opportunities`
- attached `Causal Reasoning: Irreducibly Human`

## Data and Evidence Layer

The finance book should teach these source classes:

- GL and trial balance exports
- budget and forecast files
- subledger exports
- AP and AR aging
- bank and cash data
- contract and billing records
- control evidence
- audit PBC request lists
- SEC EDGAR data
- FRED or ALFRED macro data
- metric dictionaries and approval matrices

---

# Part 5 - Field Positioning

## Comparable Categories

**Finance transformation books** discuss operating-model change, but often do not show how an analyst builds auditable recipes.

**AI-for-finance books** emphasize prediction, automation, or modeling, but often understate evidence contracts, logs, phase gates, and human adequacy review.

**Accounting and FP&A guides** explain processes, but usually do not translate them into agent-ready recipes.

**Agentic AI guides** explain tools, permissions, and orchestration, but usually work through coding or general productivity examples rather than finance operations.

## Positioning Statement

Mycroft Finance Recipe Engine is a practitioner guide for finance people who want to automate repeated preparation work without automating professional responsibility.

## Competitive Difference

The book's difference is the combination of:

- finance work that entry and mid-level practitioners actually do;
- Mycroft's two-customer recipe model;
- hard phase gates;
- machine-readable logs plus human-readable reports;
- explicit judgment boundaries;
- concrete recipe artifacts rather than general AI advice.

---

# Part 6 - Three-Act Learning Arc

## Act One - Judgment Before Finance Automation

The reader learns why fluent finance output is dangerous without evidence, why automation should reallocate attention toward judgment, and how Mycroft treats data, recipes, logs, and reports.

**Chapters:** 1-5  
**Capability at end of act:** The reader can audit a finance artifact, trace its evidence, read a recipe, and state what the evidence can and cannot support.

## Act Two - Build the Finance Recipe Components

The reader builds core recipes for repeated finance workflows: variance packs, reconciliations, daily cash, close flux, budget requests, control evidence, AP/AR exceptions, cash forecast variance, audit binders, and revenue/billing triage.

**Chapters:** 6-15  
**Capability at end of act:** The reader can produce finance review surfaces that separate verified facts, inferred explanations, missing evidence, and human decisions.

## Act Three - Operate the Engine

The reader integrates multiple recipes into one bounded finance run and records what actually happened.

**Chapter:** 16  
**Capability at end of act:** The reader can complete a logged run with source evidence, machine conformance, human adequacy checks, gate decisions, and open risks.

## Arc Statement

The book moves from "AI can make finance artifacts look finished" to "I can build a finance workflow that makes evidence, gaps, and human judgment visible."

---

# Part 7 - Sequencing Model

The sequence mirrors `the-reallocation-engine/chapters/`:

1. Fluency trap: output can look finished before the work is done.
2. Reallocation: AI should move human time toward judgment.
3. Data contract: finance evidence needs source, version, period, owner, and freshness.
4. Two customers: recipes serve both the agent and the finance reviewer.
5. Verification: sourced data still has limits.
6. First concrete recipe: monthly variance pack.
7. Record-to-report recipe: reconciliation exception triage.
8. Treasury visibility recipe: daily cash position.
9. Close recipe: flux and balance-sheet review.
10. Planning recipe: budget-request normalizer.
11. Control recipe: evidence completeness checker.
12. Operations recipe: AP/AR exception and aging workbench.
13. Treasury analysis recipe: cash forecast variance.
14. Audit recipe: PBC tracker and evidence binder.
15. Higher-risk recipe: revenue contract and billing exception triage.
16. Integrated run: build and honest run.

---

# Part 8 - Prerequisite Map

| Prerequisite | Safe to assume? | Where addressed |
|---|---:|---|
| Basic finance vocabulary | Mostly | Introduction and chapter examples |
| Budget vs actual | Mostly | Chapter 6 |
| GL/subledger basics | Not always | Chapter 7 |
| Cash and treasury basics | Not always | Chapters 8 and 13 |
| Close and flux analysis | Not always | Chapter 9 |
| Internal control evidence | No | Chapter 11 |
| AP/AR aging | Mostly | Chapter 12 |
| Audit PBC process | No | Chapter 14 |
| Revenue contract risk | No | Chapter 15 |
| Mycroft recipe format | No | Chapters 3 and 4 |
| AI governance | No | Chapters 1, 2, 4, 5 |

---

# Part 9 - Chapter-by-Chapter TOC

## Proposed Chapter Files

This structure mirrors `the-reallocation-engine/chapters/`:

```text
chapters/
  00-frontmatter.md
  00-introduction.md
  01-the-fluency-trap.md
  02-the-reallocation-principle.md
  03-the-verified-finance-data-contract.md
  04-two-customers.md
  05-verifying-finance-evidence.md
  06-monthly-variance-pack.md
  07-subledger-to-gl-reconciliation-triage.md
  08-daily-cash-position-and-liquidity-watch.md
  09-close-flux-analysis-and-balance-sheet-review.md
  10-budget-request-normalizer-and-challenge-pack.md
  11-control-evidence-completeness-checker.md
  12-ap-ar-exception-and-aging-workbench.md
  13-cash-forecast-variance-explainer.md
  14-pbc-request-tracker-and-audit-evidence-binder.md
  15-revenue-contract-and-billing-exception-triage.md
  16-the-build-and-the-honest-run.md
  97-fundamental-themes.md
  98-appendix-best-practices.md
  99-back-matter.md
```

## Introduction - Finance Work AI Did Not Make Cheap

**Capability built:** Understand Mycroft as a book and recipe engine for finance work.

The introduction frames the central shift: AI makes execution cheaper, but it does not make materiality, interpretation, accounting treatment, cash decisions, control conclusions, or release judgment cheap. It introduces `SNICKERDOODLE.md`, `DOMAIN.md`, `DATA_CONTRACT.md`, `recipes/`, `logs/`, and `reports/`.

**Whole task:** Inventory one recurring finance workflow and label each step as preparation, evidence, transformation, judgment, approval, or release.  
**Assessment:** Baseline finance-work allocation note.

## Chapter 1 - The Fluency Trap

**Capability built:** Detect the gap between fluent finance output and trustworthy finance work.

The chapter opens with a clean AI-generated variance commentary, close summary, or board-packet note that sounds plausible but hides unsupported explanations, stale sources, missing period labels, and no approval gate.

**Whole task:** Audit a fluent finance artifact.  
**Assessment:** Claim, number, and assumption table labeled verified, inferred, unsupported, judgment, or approval-needed.

## Chapter 2 - The Reallocation Principle

**Capability built:** Reframe finance automation as scarce judgment allocation.

The reader learns that the goal is not more dashboards, more commentary, or faster spreadsheet churn. The goal is to reallocate human effort toward materiality, explanation, review, risk, and release.

**Whole task:** Build a one-week reallocation plan for a finance workflow.  
**Assessment:** Time budget with preparation/judgment split and one reallocation hypothesis.

## Chapter 3 - The Verified Finance Data Contract

**Capability built:** State what counts as finance evidence in Mycroft.

The chapter introduces source, period, entity, version, owner, freshness, schema, control total, transformation, log, report, and approval record. It teaches why a generated paragraph is never a source.

**Whole task:** Trace one number from report to log to source file.  
**Assessment:** Provenance note with missing links flagged.

## Chapter 4 - Two Customers

**Capability built:** Understand recipes as both agent contracts and finance reviewer cards.

Every recipe has two customers: the agent that executes the workflow and the human who must judge the output. Logs are not reports; reports are not logs.

**Whole task:** Read one finance recipe and identify what the agent does, what the human decides, and what evidence connects them.  
**Assessment:** Two-customer recipe note.

## Chapter 5 - Verifying Finance Evidence

**Capability built:** Interrogate completeness, freshness, control totals, mapping, thresholds, and warranted verbs.

The reader learns that a parsed spreadsheet can still be wrong, a tied control total can still hide a bad explanation, and a sourced number can still be irrelevant to the decision.

**Whole task:** Review one evidence set and write what it can and cannot support.  
**Assessment:** Warranted-verb list: can say, can suggest, cannot claim, needs human review.

## Chapter 6 - Monthly Variance Pack

**Capability built:** Build a variance pack that separates verified deltas from human explanations.

The chapter teaches a monthly variance recipe: actuals, budget, forecast, mapping tables, thresholds, control totals, material variance flags, owner commentary, and open items.

**Whole task:** Build a budget-vs-actual variance pack.  
**Assessment:** Variance table, source log, commentary stub column, and owner-question list.

## Chapter 7 - Subledger-to-GL Reconciliation Triage

**Capability built:** Surface reconciliation exceptions without deciding accounting treatment.

The chapter teaches source completeness, GL-to-subledger control totals, deterministic matching, exception categories, prior-period carry-forward, and reviewer sign-off.

**Whole task:** Create a reconciliation exception queue for one account family.  
**Assessment:** Reconciliation log and exception triage memo.

## Chapter 8 - Daily Cash Position and Liquidity Watch

**Capability built:** Produce a read-only cash view with hard treasury action boundaries.

The reader learns to verify bank feed freshness, normalize balances, reconcile cash where possible, bucket availability, compare against thresholds, and escalate breaches without initiating transfers.

**Whole task:** Build a daily cash position report.  
**Assessment:** Liquidity watch table with threshold flags and human-action fields.

## Chapter 9 - Close Flux Analysis and Balance-Sheet Review

**Capability built:** Prepare close review surfaces without declaring the books ready.

The chapter teaches trial balance comparison, account-level flux, support coverage, carry-forward items, known events, unresolved movements, and controller review.

**Whole task:** Build a close flux review pack.  
**Assessment:** Flux table, support gap list, and reviewer questions.

## Chapter 10 - Budget-Request Normalizer and Challenge Pack

**Capability built:** Normalize planning submissions and prepare challenge questions.

The chapter teaches template validation, account/category normalization, headcount/rate checks, prior-year comparison, policy flags, and business-partner sign-off.

**Whole task:** Build a budget request challenge pack.  
**Assessment:** Submission registry, normalized request table, and challenge-question list.

## Chapter 11 - Control-Evidence Completeness Checker

**Capability built:** Check control evidence readiness without concluding on control effectiveness.

The chapter teaches control objectives, attribute requirements, evidence artifacts, stale screenshots, approvals, sample coverage, prior exceptions, and remediation routing.

**Whole task:** Build a control evidence readiness pack.  
**Assessment:** Control-by-control evidence ledger with ready/blocked/follow-up status.

## Chapter 12 - AP/AR Exception and Aging Workbench

**Capability built:** Turn AP and AR aging into exception queues without external action.

The chapter teaches aging buckets, duplicate invoice flags, missing support, dispute status, owner queues, and communication gates.

**Whole task:** Build an AP/AR exception workbench.  
**Assessment:** Aging table, duplicate candidates, owner queues, and stop-condition list.

## Chapter 13 - Cash Forecast Variance Explainer

**Capability built:** Compare forecast cash to realized cash without inventing causes.

The chapter teaches forecast version control, realized cash, category variance, bridge structure, known drivers, unexplained variances, and reforecast gates.

**Whole task:** Build a cash forecast variance bridge.  
**Assessment:** Cash bridge, driver attachment table, and unresolved-variance list.

## Chapter 14 - PBC Request Tracker and Audit-Evidence Binder

**Capability built:** Assemble audit support while preserving privilege, adequacy, and reviewer gates.

The reader learns to parse a PBC list, map requests to support, track status, flag missing reviewer sign-off, identify overdue items, and prepare a binder index.

**Whole task:** Build an audit evidence binder for a small request list.  
**Assessment:** PBC tracker, binder index, and gap list.

## Chapter 15 - Revenue Contract and Billing Exception Triage

**Capability built:** Separate factual billing mismatches from accounting-policy questions.

The chapter teaches contract source-chain completeness, amendment order, billing setup comparison, pricing mismatches, milestone gaps, policy interpretation flags, and revenue-recognition stop conditions.

**Whole task:** Build a revenue/billing exception review pack.  
**Assessment:** Contract registry, mismatch taxonomy, missing-artifact list, and accounting-review queue.

## Chapter 16 - The Build and the Honest Run

**Capability built:** Integrate Mycroft finance recipes through a bounded, logged run.

The reader chooses a finance scenario, runs or simulates selected recipes, inspects evidence, writes logs, produces a report, names gates, and records unresolved risks.

**Whole task:** Complete one Mycroft finance recipe run from intake to report.  
**Assessment:** Run log, human report, evidence appendix, gate decision record, and open-risk list.

## Chapter 97 - Fundamental Themes

**Capability built:** Synthesize the principles behind the system.

The appendix gathers fluency vs evidence, friction, phase gates, two customers, provenance, human-only judgment, and AI+finance labor separation.

**Whole task:** Write a personal doctrine for safe finance automation.  
**Assessment:** Practitioner doctrine memo.

## Chapter 98 - Appendix: Best Practices

**Capability built:** Maintain a Mycroft finance recipe system.

The appendix covers recipe lifecycle, logging, source contracts, no-delete/archive behavior, conformance, attestation, report templates, and stop conditions.

**Whole task:** Audit a recipe for maintainability.  
**Assessment:** Maintenance audit.

## Chapter 99 - Back Matter

Glossary, references, acknowledgments, and future recipe index.

---

# Part 10 - Learning Outcomes by Chapter

| Chapter | Capability | Assessment Artifact |
|---|---|---|
| Introduction | Orient to Mycroft as finance book and engine | Baseline allocation note |
| 1 | Audit fluent finance output | Claim/number/assumption table |
| 2 | Reallocate effort toward judgment | Weekly reallocation hypothesis |
| 3 | Trace finance evidence | Provenance note |
| 4 | Read recipes for two customers | Two-customer recipe note |
| 5 | Interrogate evidence limits | Warranted-verb list |
| 6 | Build variance review pack | Variance pack |
| 7 | Triage reconciliations | Exception queue |
| 8 | Build cash position view | Liquidity watch |
| 9 | Review close flux | Close flux pack |
| 10 | Normalize budget requests | Challenge pack |
| 11 | Check control evidence | Evidence readiness ledger |
| 12 | Build AP/AR workbench | Aging and exception queues |
| 13 | Explain cash forecast variance | Cash bridge |
| 14 | Assemble audit binder | PBC tracker and binder index |
| 15 | Triage revenue/billing exceptions | Contract/billing review pack |
| 16 | Operate a full run | Log, report, evidence, gates |
| 97 | Synthesize doctrine | Practitioner doctrine memo |
| 98 | Maintain the system | Maintenance audit |

---

# Part 11 - Running Project Spine

## Default Track

Build and operate a Mycroft finance recipe system for a fictional or real-but-sanitized company, department, or project.

## Running Deliverables

1. Baseline finance-work allocation note.
2. Fluent artifact audit.
3. Weekly reallocation hypothesis.
4. Finance data-provenance note.
5. Two-customer recipe note.
6. Warranted-verb evidence list.
7. Monthly variance pack.
8. Reconciliation exception queue.
9. Daily cash position report.
10. Close flux review pack.
11. Budget challenge pack.
12. Control evidence readiness ledger.
13. AP/AR exception workbench.
14. Cash forecast variance bridge.
15. PBC tracker and audit binder index.
16. Revenue/billing exception review pack.
17. Honest-run log and report.

## Portfolio Outcome

The reader finishes with a coherent professional portfolio of finance artifacts. The portfolio demonstrates not merely that the reader can use AI, but that they can supervise AI-assisted finance work with evidence, gates, and accountability.

---

# Part 12 - Chapter Anatomy Template

Each chapter should include:

1. **Concrete failure or work scenario.** Open with a real finance artifact: variance commentary, reconciliation, cash report, close pack, PBC tracker, or billing exception.
2. **Capability statement.** State what the reader will be able to do.
3. **Why this matters for the reader's role.** Tie to entry/mid-level finance work.
4. **The recipe concept.** Name inputs, steps, outputs, gates, logs, and report.
5. **Agentic supervision lens.** Scope, approval, verification.
6. **Evidence boundary.** What can be verified, what is model judgment, what is human judgment, what is out of scope.
7. **Running project task.** A concrete artifact the reader produces.
8. **Verification checklist.** Machine conformance plus human adequacy checks.
9. **Human-only judgment boundary.** The decision AI cannot make.
10. **Bridge to next chapter.** Show how this artifact feeds the next recipe.

Do not open chapters with abstract AI capability. Open with the finance artifact and what can go wrong when it is fluent, formatted, and unsupported.

---

# Part 13 - Recipe and Case Strategy

## Recipe Strategy

The concrete recipes should be narrow enough to run in a sample setting:

- Monthly variance pack
- Subledger-to-GL reconciliation triage
- Daily cash position
- Close flux review
- Budget request challenge pack
- Control evidence readiness
- AP/AR exception workbench
- Cash forecast variance bridge
- PBC tracker and audit binder
- Revenue/billing exception triage

Each recipe should include:

- source inventory;
- input schema;
- phase gates;
- stop conditions;
- agent log contract;
- human report contract;
- human-only judgment boundary.

## Case Strategy

Cases should use realistic but sanitized finance scenarios:

- a budget file with stale version ID;
- an unmapped GL account;
- a variance without owner explanation;
- a duplicate invoice candidate;
- a cash threshold breach;
- a stale control screenshot;
- an incomplete amendment chain;
- a PBC request with missing reviewer sign-off.

## What Makes a Case Mycroft-Specific

A case is Mycroft-specific when it has:

- a recipe;
- source files or declared source paths;
- machine checks;
- human report;
- stop conditions;
- logs;
- gate decisions;
- an explicit refusal to cross the human-only boundary.

---

# Part 14 - Hard Topics, Contested Claims, and Aging Risk

## Hard Topics

- Finance data often contains sensitive company, employee, vendor, customer, and banking information.
- Materiality is contextual and cannot be invented by the model.
- A tied reconciliation does not prove account adequacy.
- Revenue recognition, control effectiveness, tax positions, and regulatory filings are high-risk human judgment areas.
- AI-generated explanations can sound plausible while being unsupported.
- Silent scheduled automation is dangerous in finance unless every gate and revocation condition is explicit.

## Contested Claims

- How much finance work is automatable varies by organization, controls maturity, data quality, and regulation.
- The right materiality threshold is not universal.
- AI usefulness in finance depends less on model quality than on source contracts, gates, and reviewer behavior.
- A recipe that saves time but weakens review is a failure.

## Aging Risk

The book will age in:

- model capabilities;
- finance software APIs;
- SEC/FRED and other public data interfaces;
- regulatory expectations;
- accounting standards and audit guidance;
- workplace adoption of AI controls.

The book should reduce aging risk by teaching stable design principles: source contracts, phase gates, two customers, logs, reports, and human judgment boundaries.

---

# Part 15 - Market Positioning

## Primary Market

- Applied finance analytics courses
- AI in finance courses
- Business analytics programs
- Finance transformation workshops
- Early-career finance teams
- Internal audit and FP&A training

## Secondary Market

- AI builders creating finance workflows
- Finance operations teams
- Controllers and CFO staff groups
- Risk and compliance analysts
- Finance clubs and student consulting groups

## Adoption Promise

The reader will not merely learn about AI in finance. They will build usable, inspectable finance recipe artifacts that can survive review.

---

# Part 16 - Feature List

## Core Features

- Full Mycroft recipe anatomy.
- Finance-specific data contract.
- Phase gates and stop conditions for every recipe.
- Agent log and human report distinction.
- Warranted-verb evidence language.
- Do-not-automate list.
- Running project spine.
- Build sequence from low-risk foundation recipes to advanced governed workflows.

## Pedagogical Features

- Concrete failure scenarios.
- Whole-task assessments.
- Tables and checklists.
- Artifact-first chapters.
- Human-only judgment boundaries.
- Honest-run capstone.

---

# Part 17 - Out of Scope

This book does not teach:

- investment advice;
- trading automation;
- tax advice;
- legal advice;
- final accounting policy interpretation;
- autonomous journal entry posting;
- payment initiation;
- public disclosure drafting without review;
- regulatory filing submission;
- suspicious-activity filing decisions;
- full ERP implementation;
- advanced valuation theory;
- advanced audit methodology.

When these appear, the book routes them to human review, professional standards, legal/compliance owners, auditors, controllers, CFOs, or domain-specific training.

---

# Part 18 - Adoption Risk Register

| Risk | Severity | Why it matters | Mitigation |
|---|---:|---|---|
| Reader treats recipe output as approval | High | Finance outputs can affect reporting, cash, compliance, and external communication | Repeat human-only boundary and release gates in every chapter |
| Examples feel too generic | Medium | Finance readers need recognizable artifacts | Use variance packs, recons, close flux, AP/AR, cash, PBC, and contract cases |
| Data sensitivity blocks practice | High | Real finance data is sensitive | Use synthetic or sanitized sample data and teach source approval |
| Book overlaps with accounting manuals | Medium | Standards manuals are not the goal | Keep focus on recipe supervision, not technical accounting instruction |
| Too many recipes overwhelm reader | Medium | Practitioner guide must feel buildable | Use a running project and staged build sequence |
| Existing chapters are placeholders | High | Current chapter files do not match the new architecture | Later rewrite/rename chapters according to proposed files |
| Current Mycroft recipes lean public-market | Medium | Book promise is broader finance work | Use existing recipes as scaffolding and add internal finance recipe chapters |

---

# Part 19 - Open Questions

1. Should the sample company be a single fictional business used across all recipes?
2. Should the chapter-writing pass rename existing placeholder chapters or create new named files alongside them first?
3. Which recipes should get sample CSV/JSON data before drafting chapters?
4. Should the first edition include SEC/public-company recipes as full chapters, or keep them as adjacent examples in the appendix?
5. How much accounting standards language should appear in Chapter 15 without becoming a technical accounting textbook?
6. Should `reports/generated/entry-mid-finance-recipes-research.md` become a pantry source for chapter research notes?

---

# Summary

Mycroft Finance Recipe Engine should be a practitioner guide that mirrors `the-reallocation-engine`: first teach the framework, then build concrete tools, then run the system honestly.

The key architectural decision is to shift Mycroft from a primarily agentic investment-intelligence book into a broader finance recipe engine for entry- and mid-level practitioners. Investment and public-market research remain part of the repo, but the book's spine should be internal finance work: variance, reconciliation, close, cash, controls, AP/AR, audit support, and revenue/billing exceptions.

The promise is practical: use AI to make preparation cheaper and review better, while keeping finance judgment where it belongs - with accountable humans.
