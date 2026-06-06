# Research Notes: Chapter 08 - Comparative Analysis and Contradiction Detection

**Source:** TIKTOC.md chapter entry  
**Notes file:** 08-comparative-analysis-and-contradiction-detection_notes.md  
**Corresponding chapter:** chapters/08-chapter-08.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Compare companies without collapsing differences into a single false ranking. The reader studies comparative analysis, contradiction detection, research agent, and RAG grader workflows. The chapter emphasizes evidence conflicts, base-rate gaps, missing coverage, and how to preserve uncertainty in synthesis. Whole task: Build a comparison matrix for two or three AI companies. Assessment: Matrix plus contradiction log and "what would change my mind" section.

---

## A. Conceptual foundations

### Comparison matrix
A comparison matrix is not a ranking machine. It is a structure for keeping evidence categories separate: filings, news, patents, OSS, sentiment, financial metrics, risk factors, and missing data. Each row should have source, date, confidence, and caveat. The point is to prevent one vivid signal from dominating the whole story.

**Common misconception:** A matrix's final score is the analysis. In Mycroft, the score, if used at all, is secondary to the evidence and caveats.

**Worked example:** Compare three AI infrastructure firms across filing disclosures, AI revenue exposure, patent velocity, news sentiment, and risk factors. Mark "not comparable" when segment reporting differs.

**Source(s):** Local `recipes/n8n-comparativeanalysisagent.md`; `_lib_Calling_Bullshit...`; `_lib_Naked_Statistics...`.

### Contradiction detection
Contradiction detection preserves conflicts instead of smoothing them away. A news source may say demand is accelerating while filings show customer concentration risk. A patent signal may imply R&D direction while earnings commentary emphasizes cost control. Mycroft should surface contradictions as review items.

**Common misconception:** The agent should resolve every conflict. Sometimes the correct output is an unresolved contradiction with source notes.

**Worked example:** Claim A: "AI revenue is material." Claim B: filing does not break out AI revenue. Contradiction log: marketing/news claim unsupported by filing segmentation; human review needed.

**Source(s):** Local `recipes/n8n-contradiction-detection-agent.md`; ReAct, https://arxiv.org/abs/2210.03629.

---

## B. Domain examples and cases

### Case 1: RAG grader
The Mycroft RAG grader workflow can evaluate whether an answer is grounded in retrieved context. Use it to teach that retrieval does not guarantee correctness; grading checks support.

### Case 2: AI-washing comparison
Compare public AI claims with filings and enforcement language. This shows how contradiction detection can protect against overclaiming.

### Failure case: False ranking
Ranking companies from "best" to "worst" on mixed, incomplete evidence hides uncertainty and can resemble advice.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- News, filings, and patent signal caveats.
- Claim classification and provenance.

**Unlocks (what this chapter makes possible):**
- Chapter 9 - scenarios are built from competing evidence, not one conclusion.
- Chapter 10 - portfolio intelligence needs contradiction-aware synthesis.

**Adjacent chapter connections:**
- Chapters 5-7: provide signal families.
- Chapter 9: turns unresolved differences into scenario branches.

---

## D. Current state of the field

**Settled:**
- Multi-source research must preserve source differences, dates, and uncertainty.

**Contested or emerging:**
- Automated contradiction detection remains imperfect; LLMs can miss subtle conflicts or invent reconciliation.

**Key references:**
1. Mycroft comparative analysis recipe - local matrix workflow.
2. Mycroft contradiction detection recipe - local conflict workflow.
3. ReAct - exception handling and observations.
4. NIST AI RMF - measuring and managing AI risks.
5. Local statistics/skepticism library files - teaching support.

**Recent developments (last 3 years):**
- RAG systems made source-grounded answers more common, but grounding quality and contradiction handling remain active problems.

---

## E. Teaching considerations

**Where students get stuck:**
- They want a winner. Require an "unknown/missing/not comparable" column.

**Analogies and framings that work:**
- A contradiction log is a lab notebook margin note: do not erase the anomaly.

**Exercises that build the target recipe:**
- Build a two-company comparison matrix and a contradiction log with at least three unresolved items. Bloom's level: Analyze/Evaluate.

---
