# Research Notes: Chapter 00 - Using AI to Invest in AI, Carefully

**Source:** TIKTOC.md chapter entry  
**Notes file:** 00-using-ai-to-invest-in-ai-carefully_notes.md  
**Corresponding chapter:** chapters/00-introduction.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Understand Mycroft as an educational experiment, not an advice engine. The introduction frames Mycroft's purpose: learning how agentic systems gather, challenge, and synthesize investment intelligence about AI companies. It names the central boundary: the system can support research, but humans remain accountable for conclusions and actions. Whole task: Write a one-paragraph Mycroft research question and name what the system is not allowed to decide. Assessment: Research question plus human-only boundary.

---

## A. Conceptual foundations

### Research support versus advice
The chapter needs to separate three activities: gathering evidence, interpreting evidence, and recommending an action. Mycroft can help with the first two when scoped and verified; it must not be framed as deciding what a reader should buy, sell, or hold. FINRA, SEC, NASAA, and CFTC warnings about AI investment fraud are useful framing: bad actors exploit AI language to imply prediction, guaranteed returns, or special insight. The clean definition: Mycroft is a supervised research workflow that produces auditable observations and uncertainty notes, not personalized investment advice.

**Common misconception:** If a system reads filings, news, and market data, its output is "investment intelligence" by default. It is only intelligence after provenance, timestamps, contradictions, and limits are visible.

**Worked example:** A reader asks, "Is Company X a good AI investment?" The Mycroft rewrite is: "What public evidence from filings, news, patents, and sentiment supports or weakens the claim that Company X has durable AI revenue exposure as of a named date?"

**Source(s):** FINRA/SEC/NASAA AI investment fraud warning, https://www.finra.org/investors/insights/artificial-intelligence-and-investment-fraud; CFTC AI trading bot advisory, https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/AITradingBots.html.

### Supervised delegation
The Claude-agentic discipline supplies the operating model: tools extend capability and risk, so every run needs scope, approval, and verification. In the investment context, scope includes ticker universe, source set, data date, output type, prohibited claims, and whether the workflow is exploratory or report-producing.

**Common misconception:** "Human in the loop" means a human approves the final answer. In Mycroft, the human should also approve the question, source window, workflow family, and escalation points.

**Worked example:** Before running a news/sentiment workflow, define company, time window, source classes, duplicate handling, and a rule that no price target or recommendation may be generated.

**Source(s):** NIST AI RMF 1.0, https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10; ReAct, https://arxiv.org/abs/2210.03629.

---

## B. Domain examples and cases

### Case 1: AI washing enforcement
In March 2024, the SEC charged two investment advisers, Delphia and Global Predictions, with false or misleading statements about AI use. This is a strong introduction case because the issue was not that AI is useless; it was that public claims outran what the firms could substantiate. Source: https://www.sec.gov/newsroom/press-releases/2024-36.

### Case 2: AI trading-bot fraud
CFTC warns that scammers use AI language to sell bots and signal services promising unrealistic or guaranteed returns. This case gives the introduction its non-advice boundary and makes "AI cannot predict sudden market changes" concrete. Source: https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/AITradingBots.html.

### Failure case: Dashboard confidence
A clean dashboard can make weak evidence feel strong. Mycroft should teach the reader to ask: what data entered, what workflow transformed it, what claims are directly supported, and what remains unverified?

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Basic AI assistant use - needed to understand why fluency feels persuasive.
- Basic investment vocabulary - needed to distinguish company, security, portfolio, and advice.

**Unlocks (what this chapter makes possible):**
- Chapter 1 - gives the reader a skepticism framework for fluent investment prose.
- Chapter 2 - motivates why Mycroft uses agent families instead of one oracle.

**Adjacent chapter connections:**
- Chapter 1: turns the non-advice boundary into a claim-audit exercise.
- Chapter 12: returns to the original research question and asks for an honest audit note.

---

## D. Current state of the field

**Settled:**
- AI-generated investment text can be fluent without being verified; regulators explicitly warn investors about AI-related fraud and overclaiming.

**Contested or emerging:**
- The right governance pattern for agentic financial research is still emerging. NIST AI RMF provides general risk categories, but investment-specific agent governance remains a developing practice.

**Key references:**
1. SEC, "SEC Charges Two Investment Advisers..." 2024 - anchor case for AI-washing.
2. FINRA/SEC/NASAA, "Artificial Intelligence and Investment Fraud," 2024 - investor-facing risk framing.
3. CFTC, "AI Won't Turn Trading Bots into Money Machines," 2024 - bot and return-promise warning.
4. NIST AI RMF 1.0, 2023 - governance vocabulary for trustworthy AI.
5. Yao et al., "ReAct," 2023 - agent reasoning/action/observation model.

**Recent developments (last 3 years):**
- Regulators have moved from abstract warnings to enforcement and investor alerts around AI claims in finance.

---

## E. Teaching considerations

**Where students get stuck:**
- They ask advice-shaped questions. Require conversion into research questions.

**Analogies and framings that work:**
- Mycroft is a lab notebook, not a broker. The lab notebook records methods, observations, and uncertainty.

**Exercises that build the target recipe:**
- Rewrite five investment-advice prompts into research prompts. Bloom's level: Apply/Analyze.

---
