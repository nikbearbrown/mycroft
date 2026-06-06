# Research Notes: Chapter 06 - SEC Filings and Regulatory Intelligence

**Source:** TIKTOC.md chapter entry  
**Notes file:** 06-sec-filings-and-regulatory-intelligence_notes.md  
**Corresponding chapter:** chapters/06-chapter-06.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Treat filings and regulatory sources as structured evidence with interpretation limits. The reader studies SEC filings analysis and financial regulatory intelligence workflows. The focus is not "what did the filing mean for the stock?" but "what can this filing support, what can it not support, and what needs human review?" Whole task: Write a filing-analysis output contract. Assessment: Filing claim table separating direct facts, inferred interpretations, and prohibited recommendations.

---

## A. Conceptual foundations

### Filings as structured evidence
SEC filings such as 10-K and 10-Q reports are authoritative company disclosures, but they still require interpretation. A filing can directly support facts such as reported revenue, named risk factors, segment descriptions, legal proceedings, and management discussion. It cannot by itself support "the stock will rise" or "management is trustworthy." Mycroft should extract, cite, and classify claims.

**Common misconception:** A filing is objective, so any conclusion drawn from it is objective. The filing is source evidence; the conclusion is analysis.

**Worked example:** Claim table columns: claim, filing/form, filing date, section, direct quote or line reference, classification (direct fact/inference/prohibited), human review needed.

**Source(s):** Investor.gov 10-K/10-Q guide, https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/how-read; SEC EDGAR company search, https://www.sec.gov/edgar/search/.

### Regulatory intelligence
Regulatory sources include SEC enforcement, investor alerts, rulemaking, and litigation disclosures. They help identify risks and boundaries, especially around AI claims, but they should not be overread as comprehensive evidence of all misconduct or all compliance quality.

**Common misconception:** No enforcement action means no regulatory risk. Absence of action is not evidence of absence.

**Worked example:** For a company claiming AI capabilities, compare public marketing claims, 10-K risk factors, and any SEC statements about AI washing.

**Source(s):** SEC AI-washing enforcement, https://www.sec.gov/newsroom/press-releases/2024-36; SEC Chair statement on AI washing, https://www.sec.gov/newsroom/speeches-statements/sec-chair-gary-gensler-ai-washing.

---

## B. Domain examples and cases

### Case 1: How to read a 10-K/10-Q
Investor.gov explains that companies file 10-Ks annually and 10-Qs quarterly, including financial statements and management discussion. Use this as a beginner source for what filings contain.

### Case 2: SEC AI-washing enforcement
Delphia and Global Predictions show that claims about AI use can become securities-law issues when public representations are misleading.

### Failure case: Filing-to-recommendation leap
A filing says R&D spending increased. A bad workflow says "buy." A good workflow says "R&D spending increased; interpretation requires segment context, revenue traction, cash runway, and comparison."

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Provenance - filing date, form, and section are required.
- Claim classification - direct facts versus interpretation.

**Unlocks (what this chapter makes possible):**
- Chapter 8 - filings anchor comparison matrices.
- Chapter 10 - portfolio reports can include filing-grounded observations.

**Adjacent chapter connections:**
- Chapter 5: news is fast and noisy; filings are slower and more structured.
- Chapter 7: patents are weaker technology signals; filings are stronger disclosure signals.

---

## D. Current state of the field

**Settled:**
- SEC filings are core source evidence for public company research.

**Contested or emerging:**
- How companies disclose AI risk and AI strategy is evolving; investor committees and regulators continue discussing AI disclosure expectations.

**Key references:**
1. Investor.gov 10-K/10-Q guide - filing literacy.
2. SEC EDGAR - source database.
3. SEC AI-washing press release - AI-claim enforcement case.
4. SEC Chair statement on AI washing - public claim boundary.
5. Local Mycroft SEC filing recipes - repo-grounded workflow cards.

**Recent developments (last 3 years):**
- AI-related disclosures and AI-washing enforcement made AI claims in filings and marketing a live regulatory topic.

---

## E. Teaching considerations

**Where students get stuck:**
- They quote risk factors without explaining whether the risk is generic, company-specific, or newly changed.

**Analogies and framings that work:**
- A filing is sworn map data; analysis is the route you draw on top of it.

**Exercises that build the target recipe:**
- Build a filing claim table from one 10-K risk factor section. Bloom's level: Analyze.

---
