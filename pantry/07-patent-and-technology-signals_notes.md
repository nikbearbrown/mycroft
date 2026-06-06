# Research Notes: Chapter 07 - Patent and Technology Signals

**Source:** TIKTOC.md chapter entry  
**Notes file:** 07-patent-and-technology-signals_notes.md  
**Corresponding chapter:** chapters/07-chapter-07.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Use patent and technology workflows as weak signals, not proof of commercial success. The reader studies patent intelligence, patent velocity, tech-stack comparison, and open-source signals. The chapter teaches signal humility: patents, repositories, and stack choices suggest direction, but they do not prove market outcomes. Whole task: Compare two technology-signal workflows for the same company or sector. Assessment: Signal-strength note with caveats and contradiction checks.

---

## A. Conceptual foundations

### Patents as innovation indicators
Patent data can indicate technological activity, research direction, and competitive positioning. Classic work by Griliches frames patents as economic indicators while warning that patent counts are noisy: industries differ in propensity to patent, patent value is highly skewed, and assignee matching is hard. Patent velocity can suggest direction, but it is not proof of product-market fit or future returns.

**Common misconception:** More patents means more valuable innovation. Patent quality, claims, citations, family size, litigation, renewal, and commercial connection matter.

**Worked example:** Company A files 50 AI patents; Company B files 10. Before ranking, check technology classes, grant/application status, assignee subsidiaries, forward citations, and whether filings connect to disclosed products.

**Source(s):** USPTO research datasets, https://www.uspto.gov/ip-policy/economic-research/research-datasets; Griliches, "Patent Statistics as Economic Indicators," https://www.nber.org/papers/w3301.

### Technology and open-source signals
Tech-stack and OSS signals can reveal engineering direction, ecosystem traction, or developer attention. They are also easy to overread. A GitHub repo can be popular but not monetized; a stack choice can be trendy but operationally irrelevant.

**Common misconception:** Technical signal equals business signal. Technology is one layer; commercialization, distribution, margins, and risk remain separate.

**Worked example:** Compare patent velocity with open-source activity and SEC R&D language. Contradiction: high patenting but little product disclosure; or high OSS activity but no revenue connection.

**Source(s):** Local `recipes/n8n-mycroft-patent-intelligence-agent.md`, `recipes/n8n-patent-filing-velocity-tracker.md`, `recipes/n8n-oss-signals-workflow.md`.

---

## B. Domain examples and cases

### Case 1: USPTO public datasets
USPTO releases patent and trademark datasets for public and academic research. This supports transparent patent workflows but also requires careful matching and filtering.

### Case 2: Corporate patent datasets
The UVA Darden Global Corporate Patent Dataset links USPTO patents to publicly listed companies, showing how patent data can support firm-level research when mapping is documented. Source: https://patents.darden.virginia.edu/.

### Failure case: Patent roadmap fallacy
Companies patent many ideas they never ship. A patent can be defensive, exploratory, or abandoned.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Data provenance - assignee matching and date windows matter.
- Filing literacy - patents should be checked against disclosed strategy.

**Unlocks (what this chapter makes possible):**
- Chapter 8 - technology signals enter comparison matrices.
- Chapter 9 - technology signals become scenario inputs, not forecasts.

**Adjacent chapter connections:**
- Chapter 6: filings constrain what patent signals can support.
- Chapter 8: contradiction detection keeps weak signals from becoming false rankings.

---

## D. Current state of the field

**Settled:**
- Patents are useful but noisy indicators of innovation activity.

**Contested or emerging:**
- The investment value of AI patent signals depends on sector, patent quality, commercialization path, and data-matching quality.

**Key references:**
1. Griliches, "Patent Statistics as Economic Indicators," 1990 - foundational caveats.
2. USPTO research datasets - source data.
3. Harvard USPTO Patent Dataset, https://arxiv.org/abs/2207.04043 - ML-ready patent corpus.
4. UVA Darden corporate patent dataset - firm-level mapping example.
5. Local Mycroft patent and OSS recipes - workflow cases.

**Recent developments (last 3 years):**
- Patent datasets and company mappings have become easier to use in computational workflows, increasing both opportunity and overinterpretation risk.

---

## E. Teaching considerations

**Where students get stuck:**
- They count patents before defining the population and matching method.

**Analogies and framings that work:**
- Patents are footprints in the lab, not proof of a finished product.

**Exercises that build the target recipe:**
- Write a signal-strength note comparing patent velocity and OSS activity for one company, with three caveats. Bloom's level: Evaluate.

---
