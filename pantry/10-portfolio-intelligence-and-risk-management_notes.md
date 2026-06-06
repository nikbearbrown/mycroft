# Research Notes: Chapter 10 - Portfolio Intelligence and Risk Management

**Source:** TIKTOC.md chapter entry  
**Notes file:** 10-portfolio-intelligence-and-risk-management_notes.md  
**Corresponding chapter:** chapters/10-chapter-10.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Connect research signals to portfolio questions without turning the system into an advice engine. The reader studies portfolio dashboard, portfolio intelligence, price fetcher, risk management, market sentiment, and earnings-call workflows. The chapter teaches the difference between portfolio observation, risk framing, and personalized recommendation. Whole task: Specify a portfolio intelligence report that avoids advice. Assessment: Report outline with observation/recommendation boundary.

---

## A. Conceptual foundations

### Portfolio observation versus recommendation
Portfolio intelligence can describe holdings, exposures, concentration, correlations, news events, volatility, and scenario sensitivity. It becomes advice when it tells a specific investor what to buy, sell, rebalance, or hold based on personal circumstances. Mycroft's safe zone is observation and risk framing with explicit non-advice language.

**Common misconception:** A portfolio dashboard that avoids "buy" and "sell" is automatically non-advisory. It can still imply recommendations through ranking, alerts, or action language.

**Worked example:** Observation: "As of date X, 42% of the sample portfolio is exposed to AI infrastructure names." Risk frame: "This concentration may increase sensitivity to AI capex narratives." Prohibited: "Reduce exposure to 25%."

**Source(s):** Investor.gov asset allocation/diversification, https://www.investor.gov/introduction-investing/getting-started/assessing-your-risk-tolerance; local `recipes/n8n-portfolio-dashboard.md`, `recipes/n8n-risk-management-agent.md`.

### Risk management
Risk management is not only volatility. It includes concentration, liquidity, time horizon, data staleness, model uncertainty, scenario exposure, and behavioral risk. Mycroft can teach readers to frame risks without tailoring recommendations.

**Common misconception:** Diversification eliminates risk. It may reduce concentration and volatility, but cannot remove market risk or bad assumptions.

**Worked example:** Portfolio report sections: data date, holdings source, exposure summary, concentration notes, scenario sensitivities, missing data, non-advice boundary, human review questions.

**Source(s):** Investor.gov; `_lib_The_Black_Swan...`; `_lib_Antifragile...` if used.

---

## B. Domain examples and cases

### Case 1: Portfolio price fetcher
The local price-fetcher recipe is useful for teaching data freshness. Prices are time-sensitive; any report must show as-of date/time and source.

### Case 2: Earnings-call intelligence
Earnings calls can update portfolio observations, but management commentary is not the same as audited financial data.

### Failure case: Hidden suitability
A chatbot says "your portfolio is too risky." Without knowing goals, age, income, liquidity needs, and risk tolerance, that is a suitability claim beyond Mycroft's educational scope.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Scenario forecasting - portfolio risk is scenario-dependent.
- Filing/news/patent caveats - portfolio reports synthesize weak and strong signals.

**Unlocks (what this chapter makes possible):**
- Chapter 11 - advisory interface boundaries.
- Chapter 12 - honest run can include a portfolio report outline.

**Adjacent chapter connections:**
- Chapter 9: scenarios become portfolio stress tests.
- Chapter 11: risk explanations become user-facing policy language.

---

## D. Current state of the field

**Settled:**
- Asset allocation, diversification, time horizon, and risk tolerance are central investor concepts.

**Contested or emerging:**
- AI-generated portfolio dashboards can blur the line between education and personalized advice, especially with chat interfaces.

**Key references:**
1. Investor.gov asset allocation/diversification - investor education baseline.
2. Mycroft portfolio dashboard and risk recipes - local workflow family.
3. Mycroft portfolio price fetcher - freshness example.
4. Mycroft earnings-call intelligence agent - event-update example.
5. Local `_lib_The_Black_Swan...` - tail-risk caution.

**Recent developments (last 3 years):**
- AI dashboards and chatbots make personalized-seeming reports cheap, increasing disclosure and boundary risk.

---

## E. Teaching considerations

**Where students get stuck:**
- They unconsciously write action verbs. Ban "should buy/sell/reduce/increase" in draft reports.

**Analogies and framings that work:**
- Portfolio intelligence is an x-ray, not a prescription.

**Exercises that build the target recipe:**
- Rewrite a recommendation-heavy portfolio report into observations, risks, missing data, and human-review questions. Bloom's level: Evaluate/Create.

---
