# Mycroft
## Tik TOC Architecture

**Working title:** Mycroft: Agentic Investment Intelligence as Supervised Research  
**Repository:** `books/mycroft`  
**Source adaptation:** Mycroft agentic investment repository plus the generic Claude agentic coding/supervision model in `pantry/claude-agentic-ai.md`  
**Document:** Tik TOC silent intake and chapter architecture  
**Status:** Architecture draft for manuscript alignment, chapter repair, and production planning  

---

## 1. Book Concept and Thesis

### Concept Summary

This book teaches readers how to understand, design, and supervise an agentic
investment intelligence system without mistaking automation for investment
wisdom. It uses the Mycroft repository as the practical ground: imported n8n
workflows, generated recipe cards, verified local data, script-first operating
rules, and human review gates.

Mycroft is an educational experiment in using AI to study AI. Its purpose is
not to promise superior investment returns. Its purpose is to make investment
research workflows inspectable: what data entered, what agent processed it,
what assumptions were made, what output was produced, what was verified, and
where a human must intervene.

### One-Sentence Logline

An investment agent is not a financial oracle; it is delegated research under
scope, evidence, approval, and verification.

### Central Thesis

Mycroft argues that agentic AI can improve investment learning only when the
system is designed as supervised research rather than autonomous advice. The
reader learns to decompose investment intelligence into bounded agent roles:
research, verification, comparison, news monitoring, SEC analysis, patent
signals, sentiment, forecasting, portfolio intelligence, risk management,
advisory interfaces, and orchestration. The value is not that the system thinks
for the investor. The value is that the system makes the research process more
structured, auditable, and educational.

### Adaptation From Claude Agentic AI

The generic Claude agentic AI book contributes the operating discipline:

- agentic work is supervised delegation, not autonomous replacement;
- every workflow needs scope, approval, and verification;
- tools and permissions expand both capability and risk;
- plans are proposals, not proof;
- humans remain accountable for judgment and public-facing outputs.

Mycroft adapts that discipline to investment intelligence:

- **Scope** becomes ticker universe, data sources, workflow permissions,
  output type, and advisory boundary.
- **Approval** becomes human review before claims, portfolio conclusions,
  public reports, recommendations, or any action that could be read as advice.
- **Verification** becomes source checks, data-date checks, audit trails,
  contradiction detection, provenance notes, and separation between observation
  and recommendation.

The result is a book about agentic financial research: not "let AI invest for
you," but "build a transparent system that helps humans learn how investment
signals are gathered, challenged, synthesized, and reviewed."

---

## 2. Learner Profile

### Primary Reader

Technically curious students, early-career analysts, finance learners,
builders, and AI practitioners who want to understand how agentic systems can
support investment research while preserving human judgment and evidence
discipline.

### Prior Knowledge Assumed

- Basic comfort with AI assistants.
- Basic familiarity with financial news, public companies, and portfolios.
- Basic digital literacy: files, dashboards, workflows, spreadsheets, and web
  sources.
- Willingness to read workflow documentation and audit notes.

### Prior Knowledge Not Assumed

- Professional investment analysis.
- SEC filing expertise.
- Patent analytics.
- n8n workflow design.
- Multi-agent orchestration.
- Portfolio optimization theory.
- Formal AI governance.

### Misconceptions the Book Must Correct

1. "AI can pick stocks." Mycroft is an educational research system, not an
   oracle or trading engine.
2. "More agents means better intelligence." More agents expand the failure
   surface unless roles, inputs, outputs, and checks are explicit.
3. "A clean dashboard means the analysis is true." Presentation quality is not
   verification.
4. "Forecasting is prediction." Forecasting in this book is scenario discipline
   and uncertainty communication, not certainty.
5. "The orchestrator decides." The orchestration layer coordinates evidence;
   humans decide how much weight to give it.

---

## 3. Book Type and Deployment

### Primary Book Type

Practitioner handbook with course-textbook utility.

### Primary Adoption Context

Graduate or advanced undergraduate courses in AI for finance, computational
finance, agentic AI systems, investment research methods, financial literacy,
or AI product design.

### Secondary Adoption Context

Professional development workshops, finance clubs, AI labs, open-source
learning groups, and self-guided builders studying how to make agentic systems
auditable.

### Terminal Capability

By the end of the book, the reader can design and supervise a bounded Mycroft
workflow that:

- names its research question;
- identifies local source data and workflow JSON;
- selects the appropriate agent recipe;
- defines inputs, outputs, and stop conditions;
- runs only within documented phase gates;
- verifies output against source evidence;
- separates observations from recommendations;
- writes a short audit note.

---

## 4. Repository-Specific Grounding

This Tik TOC is grounded in the active Mycroft repo.

### Manuscript Layer

- `book.md`: high-level book positioning.
- `outline.md`: current outline placeholder.
- `chapters/00-introduction.md`: introduction.
- `chapters/01-chapter-01.md` through `chapters/12-chapter-12.md`: main
  chapter placeholders.
- `chapters/98-appendix-best-practices.md`: operational appendix.
- `chapters/99-back-matter.md`: back matter.

### Agentic System Layer

- `AGENTS.md`: cross-agent operating rules.
- `CLAUDE.md`: Claude/Cowork rules.
- `DATA_CONTRACT.md`: local data and evidence rules.
- `docs/`: human-readable system documentation.
- `recipes/`: agent-readable workflow recipes.
- `logs/RUN_LOG.md`: durable run log.
- `scripts/`: maintained scripts.
- `data/mycroft-main/`: imported Mycroft source data and assets.
- `docs/mycroft-main/`: import notes and source documentation.
- `scripts/mycroft-main/`: imported code/configuration retained for review.

### Workflow Recipe Layer

The import record in `docs/mycroft-main/MOVED-FROM-PANTRY.md` records 48 n8n
workflows and 48 generated recipes. These recipes are the teaching spine for the
repo's agentic workflows.

Major recipe families:

- research and analytics;
- news and sentiment monitoring;
- SEC filing analysis;
- patent intelligence;
- portfolio intelligence;
- risk management and stress testing;
- forecasting;
- financial literacy and advisory interfaces;
- orchestration and cross-agent synthesis;
- open-source engineering health signals;
- retail investor anxiety and behavioral analysis.

### Operating Rule

The repo's short rule is load-bearing:

**Run the script and read the audit before you prompt. If the script does not
exist, say so before inventing one.**

This is the Mycroft version of the Claude control triad. Scope comes first,
approval protects judgment, and verification makes the output usable.

---

## 5. Field Positioning

### Comparable Categories

**Investment books** teach valuation, portfolio theory, market behavior, or
financial statements, but rarely show how agentic AI workflows should be
documented and supervised.

**AI-for-finance books** often emphasize predictive modeling, automation, or
tooling, but may understate the need for provenance, audit trails, and advisory
boundaries.

**Agentic AI books** explain tool use, permissions, orchestration, and
verification, but usually work through coding or knowledge-work examples rather
than investment intelligence.

**Financial literacy materials** teach concepts for individual investors, but
rarely expose how research workflows are assembled, checked, and challenged.

### Positioning Statement

Mycroft is a course-ready practitioner handbook for readers who want to learn
agentic investment research by building and auditing workflows, not by trusting
black-box recommendations.

---

## 6. Three-Act Learning Arc

### Act One - Foundation: From Market Curiosity to Verified Research

The reader learns why investment intelligence requires evidence discipline,
what makes an agentic research system different from a chatbot, and how Mycroft
decomposes research into specialized roles.

**Chapters:** 1-4  
**Capability at end of act:** The reader can explain Mycroft's research
architecture, identify the difference between observation and recommendation,
and read a recipe card before running a workflow.

### Act Two - Signal Workflows: Gathering and Challenging Evidence

The reader learns how Mycroft gathers signals from news, SEC filings, patents,
social sentiment, market data, open-source activity, and company comparisons.
The emphasis is not signal quantity. It is provenance, contradiction detection,
and uncertainty.

**Chapters:** 5-9  
**Capability at end of act:** The reader can run or specify a bounded signal
workflow, trace its inputs and outputs, and challenge its claims.

### Act Three - Portfolio Intelligence: Synthesis, Advisory Boundaries, and Audit

The reader learns how signal outputs feed portfolio intelligence, risk
management, forecasting, advisory interfaces, and orchestration. The act ends
with an honest run: a bounded workflow, verified output, and audit note.

**Chapters:** 10-12  
**Capability at end of act:** The reader can supervise a Mycroft workflow from
research question to reviewed output without presenting it as financial advice.

### Arc Statement

This book takes the reader from AI-investing curiosity to supervised investment
research practice by first defining evidence and agent roles, then running
bounded signal workflows, then synthesizing outputs through human-reviewed
portfolio intelligence.

---

## 7. Sequencing Model

**Primary model:** Research question -> evidence pipeline -> signal family ->
synthesis -> human review  
**Secondary model:** Concrete -> abstract with spiral returns

The book opens with a concrete problem: AI can produce fluent investment
analysis faster than humans can verify it. It then builds an operating method:
define the question, constrain the data, run the workflow, inspect the result,
verify the claim, and write the audit.

Spiral returns:

- **Scope** begins as a research boundary, then becomes tool boundary,
  workflow boundary, advisory boundary, and portfolio boundary.
- **Verification** begins as source checking, then becomes contradiction
  detection, audit logging, signal triangulation, and human review.
- **Orchestration** begins as workflow sequencing, then becomes cross-agent
  synthesis and conflict resolution.
- **Education** begins as financial literacy, then becomes self-supervision:
  knowing what the system can and cannot warrant.

---

## 8. Prerequisite Map

| Prerequisite | Safe to Assume? | Where Introduced |
|---|---|---|
| Basic AI assistant use | Yes | Introduction |
| Difference between output and action | No | Chapter 1 |
| Investment research vs. advice | No | Chapter 1 |
| Mycroft repo structure | No | Chapter 2 |
| Recipe cards and phase gates | No | Chapter 3 |
| Local data and provenance | No | Chapter 4 |
| News and sentiment signals | No | Chapter 5 |
| SEC filing analysis | No | Chapter 6 |
| Patent and technology signals | No | Chapter 7 |
| Comparative analysis | No | Chapter 8 |
| Forecasting and uncertainty | No | Chapter 9 |
| Portfolio intelligence and risk | No | Chapter 10 |
| Advisory boundaries | No | Chapter 11 |
| Honest run and audit note | No | Chapter 12 |

---

## 9. Chapter-by-Chapter TOC

## Introduction - Using AI to Invest in AI, Carefully

**Capability built:** Understand Mycroft as an educational experiment, not an
advice engine.

The introduction frames Mycroft's purpose: learning how agentic systems gather,
challenge, and synthesize investment intelligence about AI companies. It names
the central boundary: the system can support research, but humans remain
accountable for conclusions and actions.

**Whole task:** Write a one-paragraph Mycroft research question and name what
the system is not allowed to decide.  
**Assessment:** Research question plus human-only boundary.

## Chapter 1 - The Agentic Investor's Trap

**Capability built:** Recognize why fluent investment analysis is not verified
investment intelligence.

The reader learns the difference between generated commentary, delegated
research, and investment advice. The chapter adapts the Claude principle:
agents act, and action expands responsibility.

**Whole task:** Audit one AI-generated investment paragraph for unsupported
claims.  
**Assessment:** Claim list labeled as sourced, unsourced, stale, or advisory.

## Chapter 2 - The Mycroft Architecture

**Capability built:** Explain Mycroft's agent families and orchestration layer.

The reader studies analytical agents, portfolio agents, advisory agents,
intelligence agents, and the Mycroft orchestration layer. The chapter explains
why specialized agents are easier to audit than a single black-box mega-agent.

**Whole task:** Map one research question to the correct Mycroft agent family.  
**Assessment:** Agent-family selection with input, output, and review point.

## Chapter 3 - Recipes, Scripts, and Phase Gates

**Capability built:** Read and use a Mycroft recipe card safely.

The reader learns the repo's operating loop: read the docs, check local data,
prefer stored scripts, run small, verify, review, and log. Recipes become
operating cards for agents and audit cards for humans.

**Whole task:** Select one `recipes/n8n-*.md` card and identify required reads,
phase gates, output contract, and stop conditions.  
**Assessment:** Recipe-readiness note.

## Chapter 4 - The Data Contract

**Capability built:** Distinguish source data, generated data, imported
workflow material, and reviewed evidence.

The reader learns why provenance is central in investment research. The chapter
uses `DATA_CONTRACT.md`, `docs/data-and-provenance.md`, and the Mycroft-main
import record to show how original workflow JSON becomes inspectable recipes.

**Whole task:** Trace one generated recipe back to its original workflow source.  
**Assessment:** Provenance chain with missing-data notes.

## Chapter 5 - News, Sentiment, and Market Awareness

**Capability built:** Use news and sentiment workflows without treating volume
as truth.

The reader studies news monitoring, AI news sentiment, social sentiment, and
retail investor anxiety workflows. The chapter emphasizes timestamps, source
quality, duplication, sentiment uncertainty, and narrative drift.

**Whole task:** Design a bounded news/sentiment run for one AI company or
subsector.  
**Assessment:** Source list, time window, output contract, and verification
sample.

## Chapter 6 - SEC Filings and Regulatory Intelligence

**Capability built:** Treat filings and regulatory sources as structured
evidence with interpretation limits.

The reader studies SEC filings analysis and financial regulatory intelligence
workflows. The focus is not "what did the filing mean for the stock?" but
"what can this filing support, what can it not support, and what needs human
review?"

**Whole task:** Write a filing-analysis output contract.  
**Assessment:** Filing claim table separating direct facts, inferred
interpretations, and prohibited recommendations.

## Chapter 7 - Patent and Technology Signals

**Capability built:** Use patent and technology workflows as weak signals, not
proof of commercial success.

The reader studies patent intelligence, patent velocity, tech-stack comparison,
and open-source signals. The chapter teaches signal humility: patents,
repositories, and stack choices suggest direction, but they do not prove market
outcomes.

**Whole task:** Compare two technology-signal workflows for the same company or
sector.  
**Assessment:** Signal-strength note with caveats and contradiction checks.

## Chapter 8 - Comparative Analysis and Contradiction Detection

**Capability built:** Compare companies without collapsing differences into a
single false ranking.

The reader studies comparative analysis, contradiction detection, research
agent, and RAG grader workflows. The chapter emphasizes evidence conflicts,
base-rate gaps, missing coverage, and how to preserve uncertainty in synthesis.

**Whole task:** Build a comparison matrix for two or three AI companies.  
**Assessment:** Matrix plus contradiction log and "what would change my mind"
section.

## Chapter 9 - Forecasting and Scenario Stress Testing

**Capability built:** Treat forecasts as scenario discipline under uncertainty.

The reader studies forecasting, what-if simulation, scenario stress testing,
and funding intelligence workflows. The chapter separates forecast inputs,
assumptions, scenario branches, and decision thresholds.

**Whole task:** Design a three-scenario forecast for a company, sector, or
portfolio theme.  
**Assessment:** Scenario table with assumptions, triggers, and non-claims.

## Chapter 10 - Portfolio Intelligence and Risk Management

**Capability built:** Connect research signals to portfolio questions without
turning the system into an advice engine.

The reader studies portfolio dashboard, portfolio intelligence, price fetcher,
risk management, market sentiment, and earnings-call workflows. The chapter
teaches the difference between portfolio observation, risk framing, and
personalized recommendation.

**Whole task:** Specify a portfolio intelligence report that avoids advice.  
**Assessment:** Report outline with observation/recommendation boundary.

## Chapter 11 - Advisory Interfaces and Financial Literacy

**Capability built:** Design investor-facing interactions that educate rather
than overclaim.

The reader studies financial literacy bots, chatbot memory, RAG chatbots,
product recommendation agents, and advisory workflows. The chapter focuses on
disclosure, user expertise, simplification risk, and human escalation.

**Whole task:** Write an advisory-interface policy card.  
**Assessment:** Capability statement, prohibited behaviors, escalation triggers,
and user-facing limitation language.

## Chapter 12 - The Honest Mycroft Run

**Capability built:** Supervise a complete bounded workflow from question to
audit note.

The reader selects one Mycroft workflow family, defines scope, checks local
data, reads the recipe, runs or simulates a small workflow, verifies output, and
writes an audit note. The goal is honest operation: what happened, what was
verified, what remains uncertain, and what must not be claimed.

**Whole task:** Complete one honest Mycroft run.  
**Assessment:** Run log entry plus audit note.

## Chapter 98 - Appendix: Best Practices for Agentic Operation

**Capability built:** Maintain the repo as both book and agentic system.

The appendix documents repo structure, data contracts, recipes, scripts, phase
gates, logging, and documentation expectations.

**Whole task:** Audit the repo or a workflow family using the appendix
checklist.  
**Assessment:** Maintenance note with risks and next actions.

---

## 10. Chapter Dependency Map

| Chapter | Depends On | Feeds |
|---|---|---|
| Introduction | None | Research question and boundaries |
| 1 | Introduction | Advice boundary and fluency skepticism |
| 2 | 1 | Agent-family map |
| 3 | 2 | Recipe execution discipline |
| 4 | 3 | Data and provenance discipline |
| 5 | 3-4 | News and sentiment workflows |
| 6 | 3-4 | SEC and regulatory workflows |
| 7 | 3-4 | Patent and technology signals |
| 8 | 5-7 | Cross-signal comparison |
| 9 | 8 | Forecast and scenario work |
| 10 | 5-9 | Portfolio intelligence |
| 11 | 10 | Advisory and financial literacy interfaces |
| 12 | 3-11 | Honest run and audit |
| 98 | Whole repo | Maintenance |

**Load-bearing chapters:** 1, 2, 3, 4, 8, 10, 12.  
**Most fragile transition:** Chapter 10 to Chapter 11, because the system moves
from analysis about portfolios to user-facing advisory interaction.  
**Highest adoption-risk chapter:** Chapter 9, if forecasting reads as prediction
rather than scenario discipline.  

---

## 11. Running Project Spine

Every chapter should advance one running project.

### Default Track: AI Sector Research Run

The reader studies one AI company, subsector, or portfolio theme through
Mycroft's evidence layers.

### Alternative Track: Financial Literacy Interface

The reader designs an educational investor-facing interface that explains
signals, risk, and uncertainty without giving advice.

### Running Deliverables

1. Research question and human-only boundary.
2. Fluency audit of an AI-generated investment claim.
3. Agent-family map.
4. Recipe-readiness note.
5. Provenance chain.
6. News/sentiment run design.
7. Filing-analysis output contract.
8. Technology-signal caveat note.
9. Comparative matrix and contradiction log.
10. Scenario forecast table.
11. Portfolio intelligence report outline.
12. Advisory policy card.
13. Honest run audit note.

---

## 12. Chapter Anatomy Template

Each chapter should include:

1. Concrete research scenario or failure mode.
2. Capability statement.
3. Why the capability matters for investment intelligence.
4. Mycroft workflow or repo-grounded example.
5. Claude-agentic supervision lens: scope, approval, verification.
6. Evidence and provenance rule.
7. Running project task.
8. Verification checklist.
9. Non-advice boundary.
10. Bridge to the next chapter.

Do not open chapters with abstract finance theory unless the reader has first
seen the research problem the theory solves.

---

## 13. Assessment Architecture

### Formative Assessments

- Claim classification tables.
- Recipe-readiness notes.
- Provenance chains.
- Source-window definitions.
- Filing claim tables.
- Technology signal caveat notes.
- Contradiction logs.
- Scenario tables.
- Portfolio observation outlines.
- Advisory policy cards.

### Summative Assessment

The final assessment is an honest Mycroft run:

- bounded research question;
- selected workflow recipe;
- named local data and source workflow;
- small run or simulation;
- output contract;
- verification sample;
- contradiction check;
- non-advice statement;
- run log entry;
- audit note.

### Final Exam Style Question

Given a polished AI-generated investment report about an AI company, identify
the unsupported claims, name the required Mycroft workflow families, define the
scope and stop conditions, design a verification sample, and rewrite the
conclusion so that observations, uncertainty, and prohibited recommendations
are separated.

---

## 14. Case Strategy

Cases should teach evidence discipline.

### Case Types

- AI market-hype cases where fluent narratives outran evidence;
- filing-analysis cases where direct facts and interpretations must be
  separated;
- patent/technology cases where weak signals were overread;
- sentiment cases where social volume did not equal truth;
- forecasting cases where scenario planning was mistaken for prediction;
- advisory-interface cases where simplification became overclaiming.

### Repo-Grounded Cases

- Mycroft's 48 imported n8n workflows as a workflow taxonomy.
- `recipes/n8n-orchestrator.md` and `recipes/n8n-orchestrator-v2-enhanced.md` as
  orchestration examples.
- SEC, patent, news, sentiment, forecasting, and portfolio recipes as separate
  signal families.
- `DATA_CONTRACT.md` as the claim-discipline standard.
- `logs/RUN_LOG.md` as the durable audit trail.

---

## 15. Adoption Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Book reads like investment advice | High | High | Repeat education/research boundary; require non-advice language in every applied chapter. |
| Workflow catalog overwhelms learners | High | Medium | Teach by families, not by all 48 recipes one by one. |
| Agentic AI becomes tool taxonomy | Medium | High | Keep every chapter tied to a concrete research task and verification step. |
| Forecasting chapter overclaims | High | High | Frame forecasting as scenario discipline and uncertainty communication. |
| Portfolio chapter implies recommendation | High | High | Separate observation, risk framing, and recommendation; require human review. |
| Imported workflows lack current execution environment | Medium | Medium | Treat recipes as inspectable workflow cards; run small tests only when environment is verified. |
| Data provenance is incomplete | Medium | High | Require provenance chain and missing-data labels. |
| Readers trust dashboards over audits | Medium | High | Make audit reading a chapter-level recurring exercise. |

---

## 16. Production Notes

### Primary Production Target

Replace the placeholder chapter titles in `outline.md` and align
`chapters/01-chapter-01.md` through `chapters/12-chapter-12.md` to this
architecture.

### Repo Docs to Keep in Sync

- `docs/README.md`
- `docs/manuscript.md`
- `docs/workflows.md`
- `docs/recipes.md`
- `docs/data-and-provenance.md`
- `DATA_CONTRACT.md`
- `recipes/README.md`

### Verification Commands

Current command surface:

```bash
npm run verify
npm run svg-to-png
```

`npm run verify` is currently a placeholder, so architecture verification still
requires human readback, path checks, source inspection, and recipe review.

---

## 17. Open Questions

These are not blockers for silent intake, but they should be resolved before a
final proposal package:

- Should the public title be `Mycroft`, `Using AI to Invest in AI`, or
  `Mycroft: Agentic Investment Intelligence`?
- Is the primary adoption target a finance course, an AI systems course, or a
  practitioner handbook?
- Which workflow family should be the main worked example: SEC, news, patent,
  portfolio, or orchestration?
- Should the book teach one running company/subsector throughout, or allow
  readers to choose their own target?
- How much executable workflow material is expected versus workflow-card
  inspection?

---

## 18. Compact TOC

1. The Agentic Investor's Trap
2. The Mycroft Architecture
3. Recipes, Scripts, and Phase Gates
4. The Data Contract
5. News, Sentiment, and Market Awareness
6. SEC Filings and Regulatory Intelligence
7. Patent and Technology Signals
8. Comparative Analysis and Contradiction Detection
9. Forecasting and Scenario Stress Testing
10. Portfolio Intelligence and Risk Management
11. Advisory Interfaces and Financial Literacy
12. The Honest Mycroft Run

Appendix: Best Practices for Agentic Operation
