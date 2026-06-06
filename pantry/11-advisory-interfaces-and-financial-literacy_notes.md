# Research Notes: Chapter 11 - Advisory Interfaces and Financial Literacy

**Source:** TIKTOC.md chapter entry  
**Notes file:** 11-advisory-interfaces-and-financial-literacy_notes.md  
**Corresponding chapter:** chapters/11-chapter-11.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Design investor-facing interactions that educate rather than overclaim. The reader studies financial literacy bots, chatbot memory, RAG chatbots, product recommendation agents, and advisory workflows. The chapter focuses on disclosure, user expertise, simplification risk, and human escalation. Whole task: Write an advisory-interface policy card. Assessment: Capability statement, prohibited behaviors, escalation triggers, and user-facing limitation language.

---

## A. Conceptual foundations

### Educational interface policy
An advisory-facing interface needs a policy card before it needs clever prompts. The policy card should define capability, user assumptions, prohibited behaviors, escalation triggers, data retention/memory rules, source requirements, and limitation language. For Mycroft, the goal is financial literacy and research explanation, not personalized advice.

**Common misconception:** A disclaimer alone is enough. Behavior must match the disclaimer: no personalized recommendations, no guaranteed outcomes, no fabricated expertise.

**Worked example:** Capability: explain what a 10-K risk factor is. Prohibited: "Given your $20,000 portfolio, buy X." Escalate: user asks about personal retirement allocation, taxes, debt, or urgent losses.

**Source(s):** FINRA/SEC/NASAA AI investment fraud warning, https://www.finra.org/investors/insights/artificial-intelligence-and-investment-fraud; Investor.gov risk tolerance guidance.

### RAG and memory risk
RAG chatbots can ground answers in retrieved documents, but retrieval can be incomplete, stale, or misunderstood. Memory can improve continuity but also create privacy and suitability risks if the bot starts tailoring responses based on personal financial details.

**Common misconception:** RAG prevents hallucination. RAG reduces some hallucination risk but introduces retrieval, chunking, ranking, and context-use failure modes.

**Worked example:** A financial literacy bot retrieves an SEC filing section and explains a risk factor. The answer must cite the filing/date and say what it cannot infer.

**Source(s):** Local `recipes/n8n-finance-literacy-bot-rag-chatbot.md`, `recipes/n8n-finance-literacy-bot-chatbot-w-memory.md`, `recipes/n8n-rag-grader.md`; NIST AI RMF.

---

## B. Domain examples and cases

### Case 1: Finance literacy bot
Use the Mycroft financial literacy bot as the positive case: teach concepts, cite sources, and escalate personal advice.

### Case 2: Product recommendation agent
This is a boundary case because recommendations can quickly become suitability claims. The chapter should require extra policy constraints here.

### Failure case: Simplification overclaim
A bot explains diversification as "safe." Correct: diversification can reduce some risks, but it does not guarantee against loss.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Portfolio observation/advice boundary.
- Data provenance and RAG limitations.

**Unlocks (what this chapter makes possible):**
- Chapter 12 - honest run can include user-facing limitation language.

**Adjacent chapter connections:**
- Chapter 10: portfolio risk language becomes interface policy.
- Chapter 12: policy card becomes one gate in a full run.

---

## D. Current state of the field

**Settled:**
- Investor-facing systems should disclose limitations and avoid misleading claims.

**Contested or emerging:**
- Regulatory and professional norms for AI financial chat interfaces are still developing, especially around memory and personalization.

**Key references:**
1. FINRA/SEC/NASAA AI investment fraud warning - investor protection framing.
2. Investor.gov investor education - safe educational language.
3. NIST AI RMF - trustworthy AI risk controls.
4. Mycroft financial literacy bot recipes - local interface examples.
5. Mycroft RAG grader recipe - grounding quality example.

**Recent developments (last 3 years):**
- Memory-enabled and RAG chatbots have made personalized-feeling financial conversations easy to deploy, increasing policy-card importance.

---

## E. Teaching considerations

**Where students get stuck:**
- They write helpful answers that are too personalized. Teach escalation triggers.

**Analogies and framings that work:**
- The bot is a tutor at a whiteboard, not an adviser across a desk.

**Exercises that build the target recipe:**
- Write an advisory-interface policy card with capabilities, prohibited behaviors, escalation triggers, and limitation language. Bloom's level: Create.

---
