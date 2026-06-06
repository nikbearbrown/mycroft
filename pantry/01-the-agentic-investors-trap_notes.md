# Research Notes: Chapter 01 - The Agentic Investor's Trap

**Source:** TIKTOC.md chapter entry  
**Notes file:** 01-the-agentic-investors-trap_notes.md  
**Corresponding chapter:** chapters/01-chapter-01.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Recognize why fluent investment analysis is not verified investment intelligence. The reader learns the difference between generated commentary, delegated research, and investment advice. The chapter adapts the Claude principle: agents act, and action expands responsibility. Whole task: Audit one AI-generated investment paragraph for unsupported claims. Assessment: Claim list labeled as sourced, unsourced, stale, or advisory.

---

## A. Conceptual foundations

### Fluency is not verification
LLMs are optimized to produce plausible language, not automatically warranted financial claims. A paragraph can sound like professional analysis while hiding stale data, missing source dates, ungrounded causal claims, and advice-shaped conclusions. The chapter should teach claim decomposition: break every paragraph into atomic claims, label each as directly sourced, inferential, stale, unsupported, advisory, or prohibited.

**Common misconception:** A balanced tone means balanced evidence. A model can produce hedged prose without having checked any source.

**Worked example:** "Company X is undervalued because its AI patents are accelerating and sentiment is improving." Split into: valuation claim, patent velocity claim, causal link from patent velocity to value, sentiment trend claim, and implied recommendation. Each needs separate evidence.

**Source(s):** FINRA/SEC/NASAA AI fraud warning, https://www.finra.org/investors/insights/artificial-intelligence-and-investment-fraud; CFTC advisory, https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/AITradingBots.html.

### Delegated research versus advice
Delegated research asks an agent to gather, organize, compare, or summarize evidence under constraints. Advice considers an investor's goals, risk tolerance, time horizon, tax situation, and suitability. Mycroft can support research literacy but should not simulate fiduciary judgment.

**Common misconception:** "This is not financial advice" at the end fixes advice-shaped content. The body must also avoid recommendations, suitability claims, and certainty language.

**Worked example:** Bad: "Buy Company X before earnings." Better: "As of the latest 10-Q and the last 30 days of news, summarize evidence that could affect an earnings-risk discussion."

**Source(s):** Investor.gov risk tolerance and asset allocation guidance, https://www.investor.gov/introduction-investing/getting-started/assessing-your-risk-tolerance.

---

## B. Domain examples and cases

### Case 1: Delphia and Global Predictions
SEC's 2024 AI-washing actions show that AI claims in investment contexts must match actual practice. The chapter can use this as a claim-audit model: what did the firms say, what did regulators say was unsupported, and what documentation would have been needed? Source: https://www.sec.gov/newsroom/press-releases/2024-36.

### Case 2: AI investment fraud alerts
FINRA's joint article says bad actors use AI popularity and complexity to lure victims. This is directly relevant to the "trap": complex-sounding AI lowers skepticism when it should raise the demand for documentation.

### Failure case: Guaranteed returns
CFTC warns against AI bots or signal services that promise huge or guaranteed returns. The failure mode is confusing automation with epistemic power.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Basic investing terms - so the reader can recognize advisory language.
- Basic AI use - so the reader knows why fluent generated analysis feels credible.

**Unlocks (what this chapter makes possible):**
- Chapter 2 - explains why Mycroft decomposes work into auditable agents.
- Chapter 4 - prepares the reader to demand provenance for every claim.

**Adjacent chapter connections:**
- Introduction: supplies the research/advice boundary.
- Chapter 2: turns claim-audit needs into architecture.

---

## D. Current state of the field

**Settled:**
- Regulators warn that AI can be used to make investment scams and misleading claims more persuasive.

**Contested or emerging:**
- How much disclosure is sufficient for AI-assisted financial research products is still evolving; enforcement is moving faster than textbook conventions.

**Key references:**
1. SEC 2024-36 - first AI-washing investment adviser enforcement actions.
2. FINRA/SEC/NASAA AI investment fraud article - investor warning taxonomy.
3. CFTC AI trading bots advisory - automation/prediction warning.
4. NIST AI RMF - risk management vocabulary.
5. Local `_lib_Calling_Bullshit...` - useful for teaching claim skepticism and evidence discipline.

**Recent developments (last 3 years):**
- AI washing became an explicit enforcement category in securities communications.

---

## E. Teaching considerations

**Where students get stuck:**
- They classify whole paragraphs instead of claims. Force sentence-level or clause-level labeling.

**Analogies and framings that work:**
- Treat every generated paragraph as a receipt with missing line items.

**Exercises that build the target recipe:**
- Give students an AI-generated "bull case" and have them label each claim as sourced, unsourced, stale, inferential, or advisory. Bloom's level: Analyze.

---
