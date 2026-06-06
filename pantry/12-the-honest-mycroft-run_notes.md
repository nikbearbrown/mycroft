# Research Notes: Chapter 12 - The Honest Mycroft Run

**Source:** TIKTOC.md chapter entry  
**Notes file:** 12-the-honest-mycroft-run_notes.md  
**Corresponding chapter:** chapters/12-chapter-12.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Supervise a complete bounded workflow from question to audit note. The reader selects one Mycroft workflow family, defines scope, checks local data, reads the recipe, runs or simulates a small workflow, verifies output, and writes an audit note. The goal is honest operation: what happened, what was verified, what remains uncertain, and what must not be claimed. Whole task: Complete one honest Mycroft run. Assessment: Run log entry plus audit note.

---

## A. Conceptual foundations

### Honest run
An honest run is a bounded, inspectable workflow execution or simulation. It begins with a research question and human-only boundary, then proceeds through required reads, local data check, recipe selection, dry run, validation, verification sample, contradiction note, limitation statement, and log entry. The output is useful even if it finds missing data or stops early.

**Common misconception:** A successful run is one that produces a confident answer. A successful Mycroft run is one that accurately reports what happened.

**Worked example:** "Run a bounded SEC filing analysis for Company X's latest 10-K risk factors." If local data is missing, record missing data and simulate expected output contract rather than inventing.

**Source(s):** Mycroft `DATA_CONTRACT.md`; Mycroft `logs/RUN_LOG.md`; Mycroft `recipes/README.md`.

### Audit note
The audit note is the final learning artifact. It should include question, scope, sources, workflow/recipe used, data date, validations, sample checked, contradictions, claims supported, claims not supported, prohibited recommendations, and next review.

**Common misconception:** Audit notes are bureaucracy. In agentic research, the audit note is the product that makes the result reusable.

**Worked example:** Audit note line: "The workflow found three risk-factor passages mentioning supply-chain constraints. I manually checked all three against the 2025 10-K; no price or recommendation claim is supported."

**Source(s):** NIST AI RMF; ReAct; local Mycroft operating docs.

---

## B. Domain examples and cases

### Case 1: SEC small run
Use one company, one filing, one section. Verify every extracted claim manually.

### Case 2: News/sentiment small run
Use one company and a seven-day window. Deduplicate and inspect a sample before summarizing.

### Failure case: Full automation first
Running a broad multi-agent synthesis before validating source access and output schema produces impressive but untrustworthy reports.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- All earlier workflow families and boundaries.
- Recipe cards, phase gates, provenance, verification.

**Unlocks (what this chapter makes possible):**
- A complete course/practitioner capstone.
- Future repo maintenance and reusable audit practice.

**Adjacent chapter connections:**
- Chapter 11: interface limits become part of the final boundary statement.
- Appendix 98: turns the run into maintenance discipline.

---

## D. Current state of the field

**Settled:**
- Auditable AI workflows require records of inputs, transformations, outputs, and validation.

**Contested or emerging:**
- There is no universal standard for agentic research audit notes; Mycroft can model a practical local standard.

**Key references:**
1. Mycroft `DATA_CONTRACT.md` - source and missing-data rules.
2. Mycroft `recipes/README.md` - recipe-card requirements.
3. Mycroft `recipes/n8n-orchestrator.md` - phase-gated run model.
4. NIST AI RMF - govern/map/measure/manage model.
5. ReAct - reasoning/action/observation loop.

**Recent developments (last 3 years):**
- Agentic workflows increasingly combine multiple tools and sources, making run-level audits essential.

---

## E. Teaching considerations

**Where students get stuck:**
- They feel stopped runs are failures. Grade honesty, not only completion.

**Analogies and framings that work:**
- The audit note is the flight recorder.

**Exercises that build the target recipe:**
- Complete one small run or simulation and write a 500-word audit note with supported claims and prohibited claims. Bloom's level: Create/Evaluate.

---
