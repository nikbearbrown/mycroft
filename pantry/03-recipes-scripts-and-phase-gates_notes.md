# Research Notes: Chapter 03 - Recipes, Scripts, and Phase Gates

**Source:** TIKTOC.md chapter entry  
**Notes file:** 03-recipes-scripts-and-phase-gates_notes.md  
**Corresponding chapter:** chapters/03-chapter-03.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Read and use a Mycroft recipe card safely. The reader learns the repo's operating loop: read the docs, check local data, prefer stored scripts, run small, verify, review, and log. Recipes become operating cards for agents and audit cards for humans. Whole task: Select one `recipes/n8n-*.md` card and identify required reads, phase gates, output contract, and stop conditions. Assessment: Recipe-readiness note.

---

## A. Conceptual foundations

### Recipe cards as executable documentation
A Mycroft recipe card is not just prose. It is an operating contract: executive summary, original workflow source, required reads, phase gates, trigger surface, node inventory, output contract, logging rule, and stop conditions. The chapter should teach the reader to inspect a recipe before use and to treat missing credentials, missing source data, or missing workflow invariants as stop signs.

**Common misconception:** A recipe is a prompt. In Mycroft, a recipe is closer to a standard operating procedure for an agent/human pair.

**Worked example:** For `n8n-mycroft-sec-filings-analysis.md`, identify original workflow path, required local data, expected filing output, and the stop condition for missing EDGAR data.

**Source(s):** Mycroft `recipes/README.md`; Mycroft `recipes/n8n-orchestrator.md`.

### Phase gates
Phase gates reduce the blast radius of automation. Mycroft's gates are local data, script, dry-run, validation, automation, review, and logging. They mirror AI governance principles: map the context, measure risks, manage controls, and govern accountability.

**Common misconception:** Gates slow down work. In research systems, gates prevent expensive false certainty and make results reusable.

**Worked example:** Before a full news run, do a one-company, one-day dry run, inspect duplicate handling, source timestamps, and output schema.

**Source(s):** NIST AI RMF, https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10; n8n docs, https://docs.n8n.io/.

---

## B. Domain examples and cases

### Case 1: Orchestrator recipe
The local `n8n-orchestrator.md` recipe shows node count, trigger surface, node types, output contract, and stop conditions. This is the cleanest first recipe-reading case.

### Case 2: Workflow security and credentials
n8n workflows can connect APIs and services, which means credentials, webhooks, and writes matter. The teaching point: workflow automation is not neutral; each integration expands risk.

### Failure case: Prompt-before-script
If a vetted parser or audit script already exists but the agent summarizes from memory instead, the output loses provenance and repeatability.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Mycroft agent families - needed to understand which recipe is relevant.
- Basic file navigation - needed to inspect local docs and recipes.

**Unlocks (what this chapter makes possible):**
- Chapter 4 - provenance chains depend on recipe/source links.
- Chapters 5-12 - every workflow run begins with recipe readiness.

**Adjacent chapter connections:**
- Chapter 2: architecture becomes actionable through recipe cards.
- Chapter 4: recipes point back to data and workflow provenance.

---

## D. Current state of the field

**Settled:**
- AI workflows with tools need input/output contracts, stop conditions, and human review gates.

**Contested or emerging:**
- Tooling conventions for agent audit logs are not standardized across n8n, LangGraph, AutoGen, and custom stacks.

**Key references:**
1. NIST AI RMF 1.0 - governance, mapping, measuring, managing.
2. n8n docs - workflow and integration model.
3. LangGraph human-in-the-loop docs, https://docs.langchain.com/langgraph-platform/add-human-in-the-loop - approval and interruption pattern.
4. Local `recipes/README.md` - Mycroft recipe shape.
5. Local `_lib_Software Engineering at Google...` if copied later - maintainability mindset [verify if used].

**Recent developments (last 3 years):**
- Human-in-the-loop and durable execution have become explicit features in agent frameworks, not just design wishes.

---

## E. Teaching considerations

**Where students get stuck:**
- They skip required reads. Make "required reads completed?" the first line of every recipe-readiness note.

**Analogies and framings that work:**
- A recipe card is a preflight checklist plus flight plan.

**Exercises that build the target recipe:**
- Annotate one Mycroft recipe card: required reads, phase gates, output contract, stop conditions. Bloom's level: Analyze.

---
