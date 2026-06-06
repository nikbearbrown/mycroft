# Research Notes: Chapter 09 - Forecasting and Scenario Stress Testing

**Source:** TIKTOC.md chapter entry  
**Notes file:** 09-forecasting-and-scenario-stress-testing_notes.md  
**Corresponding chapter:** chapters/09-chapter-09.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Treat forecasts as scenario discipline under uncertainty. The reader studies forecasting, what-if simulation, scenario stress testing, and funding intelligence workflows. The chapter separates forecast inputs, assumptions, scenario branches, and decision thresholds. Whole task: Design a three-scenario forecast for a company, sector, or portfolio theme. Assessment: Scenario table with assumptions, triggers, and non-claims.

---

## A. Conceptual foundations

### Forecasting as disciplined uncertainty
Forecasting should not be presented as prophecy. It is a structured way to state assumptions, define scenarios, identify triggers, and update beliefs when evidence changes. The strongest teaching frame is "forecasting as scenario discipline": base case, upside, downside, assumptions, observables, and what would change the view.

**Common misconception:** A forecast's value is whether it predicts the exact future. Its educational value is whether it makes assumptions explicit and updateable.

**Worked example:** Three-scenario AI infrastructure demand table: base case, supply-constrained upside, margin-compression downside. For each: assumption, evidence needed, trigger, prohibited claim.

**Source(s):** `_lib_The_Signal_and_the_Noise...`; `_lib_Fooled_by_Randomness...`; local `recipes/n8n-forecasting.md`, `recipes/n8n-scenariostresstestingagent.md`, `recipes/n8n-what-if-simulation-agent.md`.

### Stress testing
Stress testing asks what happens if key assumptions fail: demand slows, rates rise, supply chain breaks, regulation changes, funding closes, or sentiment reverses. It is especially useful in AI investing because hype cycles can compress time horizons and hide base-rate risk.

**Common misconception:** Stress testing is pessimism. It is robustness analysis.

**Worked example:** For a company dependent on GPU supply, test three shocks: input cost spike, customer capex slowdown, and export-control restriction. Record which claims survive each shock.

**Source(s):** Investor.gov risk/asset allocation guidance, https://www.investor.gov/introduction-investing/getting-started/assessing-your-risk-tolerance; `_lib_The_Black_Swan...`.

---

## B. Domain examples and cases

### Case 1: Funding intelligence
Funding announcements can indicate sector momentum, but they can also reflect late-cycle exuberance. Mycroft should classify funding as a scenario input, not proof.

### Case 2: What-if simulation agent
The local what-if workflow can teach controlled assumption changes: alter one variable, record expected effect, and note what is outside model scope.

### Failure case: Single-line target price
A model output that says "Company X will reach $Y" hides assumptions and can read as advice. Replace it with a scenario table and non-claims.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Comparison and contradiction logs - scenarios emerge from unresolved evidence.
- Signal caveats - inputs are uncertain.

**Unlocks (what this chapter makes possible):**
- Chapter 10 - portfolio risk framing uses scenarios.
- Chapter 12 - honest run must include uncertainty and non-claims.

**Adjacent chapter connections:**
- Chapter 8: comparison yields scenario drivers.
- Chapter 10: portfolio intelligence asks exposure under scenarios.

---

## D. Current state of the field

**Settled:**
- Forecasting under uncertainty should state assumptions, time horizons, and update criteria.

**Contested or emerging:**
- LLM-based forecasting reliability remains contested and should be treated as decision support, not a standalone oracle.

**Key references:**
1. Nate Silver, "The Signal and the Noise" - forecasting humility.
2. Taleb, "Fooled by Randomness" and "The Black Swan" - randomness and tail risk.
3. Mycroft forecasting/scenario/what-if recipes - workflow examples.
4. Investor.gov risk guidance - investor risk framing.
5. NIST AI RMF - monitoring and model-risk vocabulary.

**Recent developments (last 3 years):**
- Agent workflows make it easier to generate scenario tables quickly, increasing the need to separate assumptions from predictions.

---

## E. Teaching considerations

**Where students get stuck:**
- They write scenarios as narratives instead of tables with assumptions and triggers.

**Analogies and framings that work:**
- A forecast is a dashboard of assumptions with dates, not a crystal ball.

**Exercises that build the target recipe:**
- Build a three-scenario table for one AI sector theme with triggers and "must not claim" language. Bloom's level: Create/Evaluate.

---
