# Research Notes: Chapter 02 - The Mycroft Architecture

**Source:** TIKTOC.md chapter entry  
**Notes file:** 02-the-mycroft-architecture_notes.md  
**Corresponding chapter:** chapters/02-chapter-02.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Explain Mycroft's agent families and orchestration layer. The reader studies analytical agents, portfolio agents, advisory agents, intelligence agents, and the Mycroft orchestration layer. The chapter explains why specialized agents are easier to audit than a single black-box mega-agent. Whole task: Map one research question to the correct Mycroft agent family. Assessment: Agent-family selection with input, output, and review point.

---

## A. Conceptual foundations

### Specialized agents as audit boundaries
Mycroft's architecture is strongest when agents are treated as bounded roles rather than autonomous investors. A news agent collects and classifies time-stamped public narratives; an SEC agent extracts filing-grounded claims; a patent agent reads innovation signals; a portfolio agent summarizes exposures and risk frames; an advisory interface explains limits to users. Each role has different inputs, outputs, and verification checks.

**Common misconception:** More agents means more intelligence. More agents also means more interfaces where data can be stale, transformed incorrectly, or overinterpreted.

**Worked example:** Research question: "How exposed is Company X to AI infrastructure demand?" Map it to SEC filings for revenue/risk disclosures, news intelligence for recent narratives, patent/technology signals for R&D direction, and contradiction detection for conflicts. The orchestrator does not decide; it routes and records.

**Source(s):** Mycroft `recipes/README.md`; n8n docs, https://docs.n8n.io/; AutoGen, https://arxiv.org/abs/2308.08155.

### Orchestration
Orchestration is the coordination layer: it decides sequence, passes outputs, checks gates, and records where a workflow stopped. Graph-based systems like n8n make paths explicit and inspectable. Conversation-based multi-agent systems like AutoGen enable flexible agent collaboration but can be harder to audit if roles and message histories are not tightly controlled.

**Common misconception:** The orchestrator is the boss. In Mycroft it is a traffic controller and audit recorder; humans retain judgment.

**Worked example:** A Mycroft orchestrator receives "compare AI chip exposure for three firms." It routes filing extraction, news sentiment, patent signals, and comparison matrix generation, then requires human review before conclusions.

**Source(s):** n8n docs, https://docs.n8n.io/; AutoGen Microsoft Research, https://www.microsoft.com/en-us/research/?p=962712; ReAct, https://arxiv.org/abs/2210.03629.

---

## B. Domain examples and cases

### Case 1: n8n workflow cards
Mycroft has generated recipes from imported n8n workflow JSON. This is an excellent repo-grounded case: workflow JSON becomes a human-readable recipe with required reads, phase gates, output contracts, and stop conditions.

### Case 2: ReAct inside a research agent
A filing agent can reason that a 10-K risk factor section is needed, act by retrieving the filing, observe the extracted text, then reason about which claims are direct facts versus interpretations.

### Failure case: The mega-agent
A single prompt that asks for "investment thesis, risks, patents, news, portfolio action" collapses all provenance and makes failures hard to locate.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Chapter 1 claim audit - motivates why agents need boundaries.
- Basic workflow idea - inputs, transformations, outputs.

**Unlocks (what this chapter makes possible):**
- Chapter 3 - recipe cards become operational interfaces.
- Chapters 5-11 - each signal family maps to an agent family.

**Adjacent chapter connections:**
- Chapter 1: fluent prose is dangerous because the process is invisible.
- Chapter 3: makes the process visible through recipes and phase gates.

---

## D. Current state of the field

**Settled:**
- Tool-using LLM systems need explicit tool boundaries, observations, and recovery behavior.

**Contested or emerging:**
- The right balance between graph orchestration and conversational orchestration is still context-dependent; financial research favors auditability.

**Key references:**
1. Yao et al., "ReAct," 2023 - reasoning/action/observation loop.
2. Wu et al., "AutoGen," 2023 - multi-agent conversation framework.
3. n8n documentation - workflow automation and AI node model.
4. NIST AI RMF - risk management vocabulary.
5. Mycroft `recipes/n8n-orchestrator.md` - local architecture example.

**Recent developments (last 3 years):**
- Agent frameworks have moved from demos into workflow tooling with human-in-the-loop, durability, and audit concerns.

---

## E. Teaching considerations

**Where students get stuck:**
- They map tasks by desired answer instead of source type. Ask: what evidence is needed, and which agent has that source?

**Analogies and framings that work:**
- Treat agent families like a newsroom desk system: filings desk, markets desk, patents desk, risk desk, editor desk.

**Exercises that build the target recipe:**
- Given five research questions, choose the first agent family, input, output, and human review point. Bloom's level: Apply.

---
