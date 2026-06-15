# Deep Research Prompt: Entry- and Mid-Level Finance Recipe Opportunities for Mycroft

## Objective

Research the kinds of repeatable, inspectable recipes that an entry- or mid-level finance professional would realistically create inside a Mycroft-style agentic operating system. The goal is not a generic list of AI use cases. The goal is a prioritized map of finance workflows that can become auditable recipes with inputs, transformations, outputs, phase gates, logs, reports, stop conditions, and human judgment boundaries.

## Context

Mycroft is a recipe operating system. Its governing claim is: AI made execution cheap; it did not make judgment cheap. Recipes should therefore automate pattern work, extraction, formatting, comparison, validation, and report assembly while preserving human gates for scope, source adequacy, interpretation, materiality, release, investment advice, compliance, and financial responsibility.

Existing Mycroft finance-adjacent recipes include SEC filings analysis, forecasting, portfolio dashboards, portfolio price fetching, risk management, financial regulatory intelligence, financial intelligence hub, and finance literacy bots. The research should identify useful gaps and adjacent opportunities for practitioners in corporate finance, FP&A, accounting, audit support, treasury, financial operations, risk, compliance, investor relations, and financial services analysis.

## Research Questions

1. What recurring tasks do entry- and mid-level finance practitioners actually perform?
2. Which tasks are good candidates for Mycroft recipes because they are repeated, data-bound, source-sensitive, multi-step, and reviewable?
3. Which tasks should not be automated end-to-end because they involve judgment, materiality, approval, trading, public disclosure, tax/legal/compliance advice, or fiduciary responsibility?
4. What recipe patterns are missing from the current Mycroft finance recipe set?
5. What local and external data sources would these recipes use?
6. What should each recipe produce for the agent log and for the human report?
7. What phase gates and stop conditions should protect each workflow?
8. Which recipes would be most useful to entry-level analysts, senior analysts, staff accountants, internal audit associates, treasury analysts, revenue analysts, and finance operations specialists?

## Source Requirements

Use local repository evidence first:

- `SNICKERDOODLE.md`
- `DOMAIN.md`
- `DATA_CONTRACT.md`
- `docs/recipes.md`
- Existing `recipes/` and `reports/templates/` finance files
- `logs/RUN_LOG.md`

Then use current external sources for grounding:

- BLS Occupational Outlook Handbook for financial analysts, accountants/auditors, and budget analysts
- SEC EDGAR API documentation
- FRED API documentation
- PCAOB audit evidence and internal control standards
- FinCEN and other current regulatory sources where relevant
- Finance/accounting professional guidance only where it clarifies workflow and evidence expectations

## Output Format

Write a practitioner-level report with these sections:

1. Executive summary
2. What finance work looks like at entry and mid levels
3. Existing Mycroft finance coverage
4. Recipe opportunity map by finance function
5. Highest-value recipe candidates, ranked
6. Recipe cards for the top opportunities
7. Human judgment and phase-gate rules
8. Data sources and evidence contracts
9. Stop conditions and anti-patterns
10. Recommended build sequence for Mycroft
11. Source notes and citations

For each recipe candidate include:

- Recipe name
- User role
- Trigger
- Inputs
- Steps
- Agent output
- Human report
- Phase gates
- Stop conditions
- Human-only judgment boundary
- Why it is useful
- Existing Mycroft adjacent recipes, if any

Flag each recommendation as one of:

- `HIGH`: strongly useful and close to Mycroft's existing architecture
- `MEDIUM`: useful but needs data or governance clarification
- `LOW`: niche, advanced, or high-risk until stronger controls exist

Do not recommend recipes that trade, publish filings, send investor communications, submit regulatory reports, change ERP records, or make financial/investment/tax advice without explicit human approval gates.
