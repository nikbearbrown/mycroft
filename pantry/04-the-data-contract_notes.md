# Research Notes: Chapter 04 - The Data Contract

**Source:** TIKTOC.md chapter entry  
**Notes file:** 04-the-data-contract_notes.md  
**Corresponding chapter:** chapters/04-chapter-04.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Distinguish source data, generated data, imported workflow material, and reviewed evidence. The reader learns why provenance is central in investment research. The chapter uses `DATA_CONTRACT.md`, `docs/data-and-provenance.md`, and the Mycroft-main import record to show how original workflow JSON becomes inspectable recipes. Whole task: Trace one generated recipe back to its original workflow source. Assessment: Provenance chain with missing-data notes.

---

## A. Conceptual foundations

### Provenance
Provenance means the origin and transformation history of a claim or file. In Mycroft, a useful output should answer: where did the source data come from, when was it collected, which workflow processed it, what generated summary was produced, and what human review occurred? Provenance is central because investment claims depend heavily on dates, source authority, and interpretation boundaries.

**Common misconception:** A citation is provenance. A citation points outward; provenance also records local import paths, transformations, and review status.

**Worked example:** Trace `recipes/n8n-mycroft-patent-intelligence-agent.md` to its original workflow JSON under `data/mycroft-main/`, then label any missing runtime data or credentials.

**Source(s):** Mycroft `DATA_CONTRACT.md`; Mycroft `docs/data-and-provenance.md`.

### Source data versus generated data
Source data includes original exports, approved reference records, imported workflow JSON, and curated assets. Generated data includes audits, reports, summaries, and model-produced classifications. Generated data can be evidence of a run, but it is not automatically a source of truth.

**Common misconception:** If a generated report has a timestamp, it is verified. Timestamping is necessary but not sufficient.

**Worked example:** A generated sentiment summary says "negative sentiment rose." The source data is the article/post set; the generated summary is an interpretation; reviewed evidence requires a sample check against original items.

**Source(s):** Mycroft `docs/data-and-provenance.md`; NIST AI RMF, https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10.

---

## B. Domain examples and cases

### Case 1: SEC filings
SEC filings are public, structured source evidence, but extracted tables or summaries are generated artifacts. A Mycroft filing chapter should preserve CIK, form type, filing date, section, and extraction method. Source: Investor.gov 10-K/10-Q guide, https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/how-read.

### Case 2: USPTO patent datasets
USPTO research datasets are public source data. Patent velocity summaries become generated data; they need assignee matching, date-window rules, and caveats. Source: https://www.uspto.gov/ip-policy/economic-research/research-datasets.

### Failure case: Missing data inferred
If a source field is absent, Mycroft's contract says mark it missing. Do not infer counts, rates, confidence, holdings, prices, or performance.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Recipe cards and phase gates - provenance is checked before execution.
- Difference between observation and recommendation - provenance supports observations.

**Unlocks (what this chapter makes possible):**
- Chapters 5-9 - every signal workflow needs source/date boundaries.
- Chapter 12 - honest run audit depends on provenance chain.

**Adjacent chapter connections:**
- Chapter 3: recipe cards point to original workflow sources.
- Chapter 5: news/sentiment requires timestamp and source-quality discipline.

---

## D. Current state of the field

**Settled:**
- Financial research claims need source authority, dates, and traceability.

**Contested or emerging:**
- How to persist and expose provenance for LLM-generated research remains a live tooling problem.

**Key references:**
1. Mycroft `DATA_CONTRACT.md` - local hard rules.
2. Mycroft `docs/data-and-provenance.md` - provenance checklist.
3. SEC Investor.gov 10-K/10-Q guide - filing source literacy.
4. USPTO research datasets - public patent source model.
5. NIST AI RMF - governance and measurement frame.

**Recent developments (last 3 years):**
- Agentic systems now routinely combine external APIs, local files, and generated summaries, increasing the need for explicit data lineage.

---

## E. Teaching considerations

**Where students get stuck:**
- They cite the generated report instead of the original source.

**Analogies and framings that work:**
- Provenance is the chain of custody for a claim.

**Exercises that build the target recipe:**
- Draw a provenance chain from original workflow JSON to recipe card to generated report to reviewed claim. Bloom's level: Analyze/Create.

---
