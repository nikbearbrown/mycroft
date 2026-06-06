# Research Notes: Chapter 98 - Appendix: Best Practices for Agentic Operation

**Source:** TIKTOC.md chapter entry  
**Notes file:** 98-appendix-best-practices-for-agentic-operation_notes.md  
**Corresponding chapter:** chapters/98-appendix-best-practices.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Maintain the repo as both book and agentic system. The appendix documents repo structure, data contracts, recipes, scripts, phase gates, logging, and documentation expectations. Whole task: Audit the repo or a workflow family using the appendix checklist. Assessment: Maintenance note with risks and next actions.

---

## A. Conceptual foundations

### Two-audience documentation
Agentic book repos have two readers: humans who need to understand scope, risks, and provenance, and agents that need executable recipes. Good docs make both groups safer. Human docs explain why a workflow exists and when to stop; agent recipes specify required reads, gates, output contracts, and stop conditions.

**Common misconception:** Docs are separate from the system. In agentic repos, docs are part of the control surface.

**Worked example:** `docs/data-and-provenance.md` explains the rule; `DATA_CONTRACT.md` states hard constraints; `recipes/n8n-orchestrator.md` operationalizes them.

**Source(s):** Mycroft docs; NIST AI RMF.

### Maintenance as risk control
Maintenance includes keeping README, docs, recipes, data contracts, scripts, and logs aligned. A stale doc can cause an agent to use the wrong source, skip a gate, or overclaim. The appendix should teach lightweight audits: path existence, source freshness, generated/source distinction, script availability, recipe completeness, and log coverage.

**Common misconception:** If a workflow ran once, it is maintained. APIs, credentials, schemas, and data locations change.

**Worked example:** Audit one workflow family: original JSON exists, recipe exists, required reads are current, data paths resolve, output contract is clear, stop conditions are specific, recent run is logged.

**Source(s):** n8n docs, https://docs.n8n.io/; LangGraph durable execution docs, https://langchain-5e9cc07a.mintlify.app/oss/python/langgraph/durable-execution.

---

## B. Domain examples and cases

### Case 1: 48 imported n8n recipes
The Mycroft import converted workflow JSON into recipe cards. The appendix can show how a repo turns operational material into teachable artifacts.

### Case 2: Data contract and provenance docs
These docs prevent generated summaries from being mistaken for source evidence.

### Failure case: Stale workflow path
If a recipe points to a moved workflow JSON file, agents may improvise. Path audits are a real safety task.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Honest run structure.
- Recipe cards, data contract, phase gates.

**Unlocks (what this chapter makes possible):**
- Future course runs and repo reuse.
- Safer agent collaboration in book production.

**Adjacent chapter connections:**
- Chapter 12: a run produces artifacts that must be maintained.
- Front matter/back matter: appendix explains how the book repo stays trustworthy.

---

## D. Current state of the field

**Settled:**
- AI systems with external tools require documentation of data, permissions, evaluation, and human oversight.

**Contested or emerging:**
- Best practices for agent-readable repo documentation are still young; local conventions matter.

**Key references:**
1. NIST AI RMF - broad governance frame.
2. n8n docs - workflow/integration maintenance.
3. LangGraph durable execution/human-in-loop docs - modern agent operations.
4. Mycroft `docs/` - local human docs.
5. Mycroft `recipes/` - local agent-readable recipes.

**Recent developments (last 3 years):**
- Agentic coding and workflow repos now need documentation that is executable enough for agents and legible enough for human review.

---

## E. Teaching considerations

**Where students get stuck:**
- They audit content but not paths, scripts, and logs.

**Analogies and framings that work:**
- Repo maintenance is instrument calibration.

**Exercises that build the target recipe:**
- Audit one workflow family and write a maintenance note with broken paths, stale docs, missing logs, and next actions. Bloom's level: Evaluate/Create.

---
