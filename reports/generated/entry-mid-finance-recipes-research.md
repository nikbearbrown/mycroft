# Entry- and Mid-Level Finance Recipe Opportunities for Mycroft

Generated: 2026-06-14

## Executive Summary

The most useful Mycroft finance recipes are not "AI finance assistant" recipes. They are narrow, repeated, evidence-bound workflows that turn messy finance inputs into auditable logs and human decision reports.

Mycroft already has finance-adjacent recipes for SEC filings analysis, forecasting, portfolio dashboards, risk management, financial regulatory intelligence, portfolio price fetching, and finance literacy. The highest-value gaps are closer to day-to-day analyst and finance-operations work:

1. Monthly variance analysis pack
2. Budget-vs-actual commentary draft
3. Account reconciliation exception review
4. Close checklist and flux analysis
5. Accounts payable spend and duplicate-invoice review
6. Accounts receivable aging and collections prioritization
7. Cash forecast and liquidity bridge
8. KPI definition and metric lineage map
9. SEC filing change and risk-factor comparison
10. Covenant and debt-compliance monitor
11. Audit-support evidence binder
12. Board or CFO packet source checker

These recipes fit Mycroft because they are repeated, multi-step, source-sensitive, and risky if fluent prose outruns evidence. They also preserve a clean labor boundary: AI can fetch, parse, compare, reconcile, summarize, and draft; humans decide materiality, explanations, accounting treatment, disclosure, investor communications, trades, approvals, and release.

An additional attached research pass is preserved as `reports/generated/mycroft-finance-recipe-opportunities-attached-research.md`. Its most useful addition is the practitioner map: Mycroft's finance architecture is already appropriate, but current coverage leans toward public-market research and monitoring. The next useful expansion is internal comparison-and-evidence work: plan-to-actual, record-to-report, order-to-cash, procure-to-pay, treasury visibility, and audit/control evidence readiness.

**Do not automate end-to-end under any framing:** journal posting, ERP master-data changes, payment initiation, regulatory filings, public disclosures, investor communications, tax positions, final revenue-recognition conclusions, control-deficiency grading, suspicious-activity filing decisions, or anything that changes accounting, banking, trading, filing, or external communication state without explicit human approval.

## What Finance Work Looks Like at Entry and Mid Levels

Entry- and mid-level finance work is largely evidence assembly plus judgment support. Public occupational descriptions line up with that pattern. The U.S. Bureau of Labor Statistics describes financial analysts as workers who evaluate current and historical financial data, study business and economic trends, examine financial statements, and make recommendations to businesses and individuals ([BLS Financial Analysts](https://www.bls.gov/ooh/business-and-financial/financial-analysts.htm)). BLS describes accountants and auditors as workers who examine financial statements, compute taxes, inspect accounting systems for efficiency and accepted accounting procedures, and organize records ([BLS Accountants and Auditors](https://www.bls.gov/ooh/business-and-financial/accountants-and-auditors.htm)). Budget analysts help organizations plan finances, review budget proposals, monitor spending, and estimate future needs ([BLS Budget Analysts](https://www.bls.gov/ooh/business-and-financial/budget-analysts.htm)).

Translated into Mycroft terms, the everyday work clusters into:

- Collect inputs: ERP exports, GL detail, trial balances, invoices, budgets, forecasts, headcount files, CRM bookings, bank data, filings, market data, and operating metrics.
- Validate shape: parse files, check required fields, identify missing periods, duplicates, outliers, stale sources, and mapping breaks.
- Transform: group accounts, join actuals to budget, roll up entities, tag vendors, normalize dates, compute deltas, and build tables.
- Explain: draft variance drivers, flux narratives, cash bridges, working-capital notes, or metric movement summaries.
- Review: decide materiality, classify exceptions, choose explanations, approve comments, and route issues.
- Report: produce a human-readable packet and a machine-readable log.

The recipe opportunity is strongest where a junior person already prepares a recurring pack and a senior person reviews it.

The attached research adds a useful occupational baseline for prioritization:

| Occupational family | Typical entry/mid-level work | Recipe implication |
|---|---|---|
| Accountants and auditors | Reconciliation, workpapers, transaction matching, system and record inspection | Build evidence binders, reconciliation triage, close flux, and control-evidence recipes. |
| Financial and investment analysts | Data gathering, trend analysis, financial statement review, written reports | Build variance, SEC comparison, KPI lineage, board-packet source-check, and investment-memo source-check recipes. |
| Financial risk specialists | Risk assessment, compliance documentation, regulatory monitoring | Build regulatory change, covenant, control, and issue-routing recipes with strong human gates. |
| Budget analysts | Budget consolidation, proposal review, spending monitoring | Build budget-request normalizers, budget-vs-actual commentary, and planning challenge packs. |
| Bookkeeping and accounting clerks | AP/AR posting support, invoice matching, balance support, accuracy checks | Build AP duplicate detection, AR aging, billing exception, and payment-support review recipes, but never payment-release automation. |

## Existing Mycroft Finance Coverage

The repo already contains finance-oriented recipes and report templates:

- `recipes/mycroft-sec-filings-analysis.md`
- `recipes/mycroft-sec-filings-analysis-enhanced.md`
- `recipes/mycroft-sec-filings-analysis-agent.md`
- `recipes/mycroft-financial-intelligence-hub.md`
- `recipes/mycroft-financial-regulatory-intelligence-system-enhanced.md`
- `recipes/forecasting.md`
- `recipes/mycroft-forecasting-agent.md`
- `recipes/portfolio-dashboard.md`
- `recipes/portfolio-price-fetcher.md`
- `recipes/portfolio-intelligence-agent-complete-with-rag.md`
- `recipes/n8n-risk-management-agent.md`
- `recipes/finance-literacy-bot-rag-chatbot.md`

This coverage is strongest in external financial intelligence, market/portfolio signals, SEC analysis, and forecasting. It is thinner in internal corporate-finance operations: close, reconciliation, AP/AR, budget packs, cash, controls, audit support, and CFO packet preparation.

## Recipe Opportunity Map by Finance Function

| Function | Recurring work | Recipe fit | Risk level | Mycroft gap |
|---|---|---:|---:|---|
| FP&A | Budget vs actual, forecast updates, variance commentary, KPI packs | High | Medium | High |
| Accounting close | Reconciliations, flux analysis, close checklist, support binder | High | Medium-high | High |
| AP / spend | Duplicate invoices, vendor spend, payment terms, approval exceptions | High | Medium | High |
| AR / revenue ops | Aging, collections queues, invoice disputes, revenue dashboards | High | Medium | High |
| Treasury | Cash positioning, liquidity bridge, debt covenant monitor | Medium-high | High | Medium-high |
| SEC / investor analysis | Filing comparison, MD&A change review, risk factor drift | High | High | Existing base |
| Internal audit / controls | Evidence binder, control exception triage, policy mapping | High | High | High |
| Risk / compliance | Regulatory change digest, obligation routing, policy watch | Medium-high | High | Existing base |
| Portfolio / markets | Price fetch, portfolio dashboard, holdings commentary | Medium | High | Existing base |
| Tax | Provision support, tax calendar, document checklist | Medium | Very high | Low until stronger review gates |

The expanded opportunity set from the attached research identifies 22 candidate recipes:

- Monthly variance pack and commentary binder
- Subledger-to-GL reconciliation exception triage
- Daily cash position and liquidity watch
- Close flux analysis and balance-sheet review pack
- Budget-request normalizer and challenge pack
- Control-evidence completeness checker
- AP/AR exception and aging workbench
- Cash forecast variance explainer
- PBC request tracker and audit-evidence binder
- Revenue contract and billing exception triage
- Debt-covenant evidence pack
- KPI definition QA pack
- Bank-fee review
- Expense-policy exception review
- Regulatory change obligation watchlist
- Working-capital bridge
- Vendor concentration and contract renewal monitor
- Headcount and compensation forecast bridge
- Financial model change-log reviewer
- Investment memo source checker
- Revenue recognition support checklist
- Tax calendar and document checklist

## Highest-Value Recipe Candidates, Ranked

### 1. Monthly Variance Analysis Pack - HIGH

**User role:** FP&A analyst, finance analyst, senior analyst.

**Trigger:** Month-end actuals are available and budget/forecast comparison is due.

**Inputs:** GL actuals, budget, forecast, department/account mapping, prior-month pack, headcount or operational drivers, known one-time items.

**Steps:** Validate period and entity coverage; map accounts; calculate dollar and percentage variance; flag material deltas; join driver data; draft variance explanation candidates; route unsupported explanations for review.

**Agent output:** `logs/monthly-variance-analysis-[DATE].json` with rows seen, mapping rejects, variance thresholds, flagged accounts, source files, and stop conditions.

**Human report:** `reports/generated/monthly-variance-analysis-[DATE].md` with executive summary, variance table, proposed explanations, unsupported explanations, questions for business owners, and decision next steps.

**Phase gates:** Source gate, mapping gate, materiality threshold gate, explanation approval gate, report gate.

**Stop conditions:** Missing actuals, missing budget, unmapped accounts above threshold, stale mapping file, unsupported causal explanation, or request to post journal entries.

**Human-only judgment boundary:** Materiality, causal explanation, business-owner acceptance, and final commentary.

**Why useful:** This is one of the most repeated analyst workflows and has a clear two-customer shape: machine table plus human commentary.

**Adjacent Mycroft recipes:** `recipes/forecasting.md`, `recipes/mycroft-forecasting-agent.md`.

### 2. Budget-vs-Actual Commentary Draft - HIGH

**User role:** FP&A analyst, department finance partner.

**Trigger:** Department owners need monthly or quarterly performance comments.

**Inputs:** Budget/actual table, prior commentary, department owner notes, approved metric definitions, variance thresholds.

**Steps:** Compare current period, prior period, and forecast; detect repeated variance patterns; draft commentary using warranted verbs; mark each explanation as sourced, inferred, or owner-needed.

**Agent output:** Variance-commentary log with source rows and inference labels.

**Human report:** Draft commentary pack with review fields for each department.

**Phase gates:** Metric-definition gate, source-row gate, owner-review gate.

**Stop conditions:** Any commentary implying cause without supporting driver data; missing department owner; material variance without evidence.

**Human-only judgment boundary:** The department owner or finance lead approves the explanation.

**Why useful:** It turns repetitive narrative drafting into a supervised evidence workflow.

### 3. Account Reconciliation Exception Review - HIGH

**User role:** staff accountant, accounting analyst, senior accountant.

**Trigger:** Monthly account reconciliations are due.

**Inputs:** GL account balance, subledger detail, bank or third-party statement, prior recon, recon policy, threshold rules.

**Steps:** Validate files; compare balances; identify unmatched items; age exceptions; categorize known timing items vs unknown differences; assemble support links; draft reviewer questions.

**Agent output:** Reconciliation exception log with counts, unmatched items, aging, and support paths.

**Human report:** Reconciliation review memo with open exceptions and proposed owner actions.

**Phase gates:** Source completeness gate, threshold gate, exception classification gate, preparer/reviewer approval gate.

**Stop conditions:** Missing statement, unexplained difference above threshold, request to book adjustment without approval, or confidential account data outside approved environment.

**Human-only judgment boundary:** Accounting treatment, write-off, adjustment, or sign-off.

**Why useful:** Reconciliation is repetitive, evidence-bound, and control-sensitive.

### 4. Close Checklist and Flux Analysis - HIGH

**User role:** accounting analyst, close manager support, finance operations analyst.

**Trigger:** Month-end close process begins.

**Inputs:** close calendar, task owners, GL balances, prior-period balances, account groupings, close status exports.

**Steps:** Validate task status; compare balances period-over-period; flag unusual flux; link tasks to account groups; identify missing support; draft close risk summary.

**Agent output:** close-status and flux log.

**Human report:** close packet with blocker list, flux table, support gaps, and owner routing.

**Phase gates:** close-calendar gate, data freshness gate, material flux gate, controller review gate.

**Stop conditions:** Missing close status, unsupported material flux, or request to change close status automatically.

**Human-only judgment boundary:** Whether the books are ready to close.

**Why useful:** It makes close readiness inspectable without pretending the system can close the books by itself.

### 5. Duplicate Invoice and Spend Exception Review - HIGH

**User role:** AP analyst, procurement analyst, finance operations specialist.

**Trigger:** AP batch review, payment run, or monthly spend audit.

**Inputs:** invoice export, vendor master, purchase orders, payment status, approval workflow, duplicate-detection rules.

**Steps:** Normalize vendor names; detect duplicate invoice numbers, amounts, dates, and near matches; flag missing PO or approval; summarize spend by vendor/category; route exceptions.

**Agent output:** exception log with duplicate candidates and confidence labels.

**Human report:** AP exception report with recommended holds, reviewer fields, and vendor-owner routing.

**Phase gates:** data-shape gate, duplicate-rule gate, payment-hold approval gate.

**Stop conditions:** Request to block or release payment without approval; missing vendor master; uncertain duplicate above payment threshold.

**Human-only judgment boundary:** Hold/release decisions and vendor communication.

**Why useful:** It is high-volume, repeated, and directly benefits from pattern detection while needing explicit human approval.

### 6. AR Aging and Collections Prioritization - HIGH

**User role:** AR analyst, revenue operations analyst, collections support.

**Trigger:** Weekly AR aging review.

**Inputs:** AR aging, customer master, invoice details, payment history, dispute notes, account owner, credit terms.

**Steps:** Validate aging buckets; flag large or aged balances; identify repeat late payers; connect dispute notes; propose priority queue; draft internal follow-up notes.

**Agent output:** AR aging log with aged balances, missing owners, and dispute flags.

**Human report:** collections priority digest.

**Phase gates:** source completeness gate, customer-owner gate, communication approval gate.

**Stop conditions:** Any external customer communication without approval; missing dispute status; sensitive customer data outside approved workspace.

**Human-only judgment boundary:** Collections tone, customer escalation, credit hold, or write-off.

**Why useful:** It creates a weekly operating surface for cash collection without automating customer-facing action.

### 7. Cash Forecast and Liquidity Bridge - HIGH

**User role:** treasury analyst, FP&A analyst, finance manager.

**Trigger:** Weekly cash meeting or liquidity review.

**Inputs:** bank balances, AP schedule, AR forecast, payroll dates, debt service, planned capex, prior forecast, known one-time cash items.

**Steps:** Validate dates; classify inflows/outflows; reconcile starting cash; build weekly bridge; compare forecast to actual; flag liquidity thresholds; draft questions.

**Agent output:** cash-forecast log with source files, bridge rows, threshold flags, and rejects.

**Human report:** liquidity bridge and risk digest.

**Phase gates:** bank-source gate, forecast-assumption gate, liquidity-threshold gate, treasurer/CFO review gate.

**Stop conditions:** Missing bank source, stale AP/AR schedules, request to initiate transfer/payment, or covenant-sensitive conclusion without review.

**Human-only judgment boundary:** Liquidity interpretation, financing action, payment prioritization, and executive escalation.

**Why useful:** Treasury work has high consequences but many repeatable assembly steps.

### 8. KPI Definition and Metric Lineage Map - HIGH

**User role:** finance analyst, BI analyst, FP&A partner.

**Trigger:** A recurring dashboard or CFO packet uses metrics that need governance.

**Inputs:** dashboard export, metric names, source tables, formulas, owners, reporting cadence, business definitions.

**Steps:** Extract metrics; document formula; map source systems; identify stale or inconsistent definitions; assign owners; flag metrics without decision use.

**Agent output:** metric-lineage log.

**Human report:** KPI dictionary and gaps list.

**Phase gates:** source-system gate, formula-review gate, owner-approval gate.

**Stop conditions:** Unsupported metric in executive packet; conflicting formulas; missing owner.

**Human-only judgment boundary:** Whether a metric is meaningful and approved for executive use.

**Why useful:** This prevents dashboard drift and makes finance reporting maintainable.

### 9. SEC Filing Change and Risk-Factor Comparison - MEDIUM-HIGH

**User role:** financial analyst, investor relations analyst, competitive intelligence analyst.

**Trigger:** New 10-K, 10-Q, S-1, or competitor filing appears.

**Inputs:** SEC EDGAR company submissions, filings, prior filing, company facts, watchlist, comparison rules. The SEC provides EDGAR APIs including submissions and company facts endpoints ([SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)).

**Steps:** Fetch or load approved filing data; compare risk factors, MD&A, segment data, liquidity language, and footnotes; extract changes; label materiality as human review.

**Agent output:** filing-comparison log with accession numbers, sections compared, diffs, and source URLs.

**Human report:** filing change memo with review-needed items.

**Phase gates:** approved-source gate, accession gate, materiality-review gate.

**Stop conditions:** Investment recommendation, trading signal, legal conclusion, or missing filing provenance.

**Human-only judgment boundary:** Materiality, investment interpretation, legal/disclosure significance.

**Why useful:** Mycroft already has SEC recipes; this focuses them on a concrete analyst deliverable.

### 10. Covenant and Debt-Compliance Monitor - MEDIUM-HIGH

**User role:** treasury analyst, corporate finance analyst, controller support.

**Trigger:** Month-end or quarter-end debt compliance review.

**Inputs:** debt agreements, covenant definitions, trial balance, EBITDA adjustments, debt schedules, forecast, prior certificate.

**Steps:** Extract covenant formulas; map inputs; compute draft ratios; identify missing support; compare headroom; draft review memo.

**Agent output:** covenant-calculation log.

**Human report:** debt-compliance draft pack.

**Phase gates:** legal-document gate, formula-approval gate, controller/CFO review gate.

**Stop conditions:** Missing agreement, ambiguous definition, request to submit certificate, or covenant breach conclusion without human approval.

**Human-only judgment boundary:** Covenant interpretation and official compliance certification.

**Why useful:** The workflow is repeatable but too consequential for silent automation.

### 11. Audit-Support Evidence Binder - HIGH

**User role:** staff accountant, internal audit associate, controller support.

**Trigger:** External audit request list or internal audit testing.

**Inputs:** PBC request list, GL detail, reconciliations, invoices, approvals, policies, screenshots, prior-year support.

**Steps:** Parse request list; map requests to support; check completeness; identify missing approvals; create binder index; draft preparer notes.

**Agent output:** binder log with evidence paths and missing items.

**Human report:** audit support index and exception list.

**Phase gates:** evidence-path gate, completeness gate, reviewer approval gate.

**Stop conditions:** Missing support for material item, confidential data outside workspace, or request to respond to auditor without approval.

**Human-only judgment boundary:** Whether evidence is sufficient and ready to provide.

**Why useful:** Audit support is painful, repeated, provenance-heavy work. PCAOB AS 1105 emphasizes the sufficiency and appropriateness of audit evidence, including relevance and reliability ([PCAOB AS 1105](https://pcaobus.org/oversight/standards/auditing-standards/details/AS1105)).

### 12. CFO or Board Packet Source Checker - HIGH

**User role:** FP&A analyst, finance chief of staff, strategy analyst.

**Trigger:** Monthly leadership packet or board deck is being assembled.

**Inputs:** deck, tables, charts, KPI exports, source files, metric dictionary, prior packet, approval owners.

**Steps:** Extract claims and numbers; map every number to source; check period labels; detect stale charts; flag unsupported claims; create approval checklist.

**Agent output:** packet-source log with figure/table references and source status.

**Human report:** board-packet evidence review.

**Phase gates:** source-link gate, stale-chart gate, executive-approval gate.

**Stop conditions:** Unsupported public/company-sensitive claim, missing metric source, request to send deck externally.

**Human-only judgment boundary:** Executive narrative and release approval.

**Why useful:** It directly protects high-stakes communication from quiet evidence drift.

### 13. Budget-Request Normalizer and Challenge Pack - HIGH

**User role:** entry-level analyst, senior analyst, budget analyst.

**Trigger:** Annual planning cycle, quarterly replan, or ad hoc funding review.

**Inputs:** Department budget submissions, staffing requests, approved labor and overhead rates, prior-year spend, policy constraints, and template version.

**Steps:** Verify template version; normalize time buckets, accounts, and currencies; flag missing support; compare requests to prior spend and approved rates; compile department-level challenge questions.

**Agent output:** Submission registry, completeness status, normalization changes, policy exceptions, outlier flags, and reviewer queues.

**Human report:** Consolidated budget request summary with challenge questions and unresolved owner responses.

**Phase gates:** Intake completeness gate, policy-constraint gate, outlier-review gate, business-partner sign-off.

**Stop conditions:** Required department missing, unsupported headcount or rate assumption, unapproved template version, or request to approve/reject funding automatically.

**Human-only judgment boundary:** Funding negotiation, tradeoff prioritization, and final budget approval.

**Why useful:** The mechanical work is normalization and challenge preparation; the human work is deciding what deserves funding.

### 14. Daily Cash Position and Liquidity Watch - HIGH

**User role:** treasury analyst, senior analyst, controller-support staff.

**Trigger:** Start-of-day treasury run or intraday liquidity checkpoint.

**Inputs:** Bank balances, bank transactions, cash ledger, debt-service schedule, investment maturities, approved cash forecast, account master data, and liquidity thresholds.

**Steps:** Verify bank-data timestamps; normalize balances by account, entity, and currency; reconcile to GL cash where possible; bucket available and restricted cash; compare to thresholds and forecast; escalate breaches.

**Agent output:** Bank-source freshness log, balance table, reconciliation status, threshold flags, unknown accounts, and forecast-vs-actual position.

**Human report:** Current cash view, forecast gap analysis, threshold breach alerts, and treasury actions required.

**Phase gates:** Source freshness gate, account-completeness gate, threshold review gate, escalation gate.

**Stop conditions:** Missing bank feed, failed integrity check, unknown account, projected threshold breach, or any request for transfer/payment initiation.

**Human-only judgment boundary:** Funding actions, sweeps, borrow/invest decisions, and external bank instructions.

**Why useful:** It is a high-cadence dashboard workflow with a crisp read-only boundary.

### 15. Control-Evidence Completeness Checker - HIGH

**User role:** internal-audit associate, SOX associate, staff accountant supporting controls.

**Trigger:** Control testing window, walkthrough prep, remediation follow-up, or pre-audit readiness check.

**Inputs:** Control library, control objectives, attribute requirements, PBC request list, screenshots, system reports, approval records, role matrices, sample selections, prior exceptions, and remediation status.

**Steps:** Verify control identity and period; check whether required evidence exists and traces to the objective; check preparer/reviewer evidence and approval timestamps; surface stale screenshots or attribute failures; classify controls as ready, blocked, or needs follow-up.

**Agent output:** Control-by-control evidence ledger, missing artifacts, stale documents, attribute failures, and unresolved questions.

**Human report:** Controls ready for testing, blocked controls, documentation weaknesses, remediation actions, and owners.

**Phase gates:** Scope gate, evidence-completeness gate, reliability gate, remediation gate, no-automatic-conclusion gate.

**Stop conditions:** Missing evidence for key control, inconsistent evidence, request to conclude on design or operating effectiveness, or request to communicate deficiency grading automatically.

**Human-only judgment boundary:** Control design conclusions, operating-effectiveness conclusions, deficiency grading, and communication to management or external auditors.

**Why useful:** It extends Mycroft's evidence-and-gates discipline into internal control readiness without pretending to perform the audit conclusion.

### 16. Revenue Contract and Billing Exception Triage - MEDIUM

**User role:** revenue analyst, technical-accounting support, staff accountant.

**Trigger:** New contract intake, month-end revenue review, or billing discrepancy review.

**Inputs:** Contract metadata, executed documents, amendments, billing schedules, price lists, customer amendment chain, invoice history, fulfillment milestones, and policy mappings.

**Steps:** Verify all amendments are present; normalize dates, products, pricing, and amendment chains; compare contract terms to billing setup; flag pricing mismatches, missing milestones, unsupported overrides, and policy-interpretation questions.

**Agent output:** Contract registry, amendment-chain completeness status, mismatch taxonomy, missing artifacts, and policy-interpretation flags.

**Human report:** Factual billing discrepancies, contracts needing accounting review, missing documentation, and decisions required.

**Phase gates:** Source-chain gate, contract-completeness gate, accounting-policy review gate, release gate.

**Stop conditions:** Missing amendments, unclear amendment order, request to conclude on revenue recognition, request to initiate billing correction, or request to determine variable consideration automatically.

**Human-only judgment boundary:** Principal-vs-agent determination, standalone selling price allocation, variable consideration, contract modification assessment, revenue timing, disclosure, and final accounting memo.

**Why useful:** It separates operational mismatches from accounting-policy questions, which is exactly the kind of distinction a recipe can surface but not resolve.

## Additional Medium-Priority Recipes

- **Revenue recognition support checklist:** useful, but accounting policy and ASC/IFRS interpretation require stronger gates.
- **Expense accrual suggestion pack:** useful for missing invoice detection; must not post entries automatically.
- **Headcount and compensation forecast bridge:** useful for FP&A; sensitive HR data requires access controls.
- **Vendor concentration and contract renewal monitor:** useful for procurement finance and risk.
- **Working-capital bridge:** useful for CFO reporting; depends on clean AR/AP/inventory data.
- **Regulatory obligation calendar:** useful in financial services; depends on jurisdiction and human compliance owner.
- **Financial model change log reviewer:** useful for model governance; should not certify model correctness automatically.
- **Investment memo source checker:** useful for analysts; must avoid investment advice and trading triggers.

## Human Judgment and Phase-Gate Rules

Finance recipes need stricter gates than ordinary productivity recipes. The most important gates are:

1. **Source gate:** Are the files present, current, permitted, and from the right system?
2. **Data-shape gate:** Do rows, columns, periods, entities, and currencies parse as expected?
3. **Mapping gate:** Are accounts, vendors, customers, entities, products, and departments mapped?
4. **Threshold/materiality gate:** Who set the threshold, and is it appropriate for this report?
5. **Interpretation gate:** Are explanations sourced or merely plausible?
6. **Approval gate:** Who can clear commentary, accounting treatment, external communication, payment action, trade, filing, or release?
7. **Report gate:** Did the run produce both a machine log and a human report?

The attached research proposes this minimum finance gate stack for every high-risk recipe:

| Gate | Purpose | Who clears it |
|---|---|---|
| Problem gate | Confirm period, entity, scope, and version | Human |
| Source adequacy gate | Confirm completeness, freshness, and approved versions | Human |
| Data-shape gate | Confirm parseability and schema conformance | Agent validates; human reviews failures |
| Reconciliation gate | Confirm control totals or source agreement | Agent computes; human reviews discrepancies |
| Sensitive-action gate | Stop before anything touching disclosures, submissions, trading, payments, or accounting conclusions | Hard stop; human required |
| Interpretation gate | Materiality calls and narrative meaning | Human only |
| Release gate | Distribution outside the immediate working context | Human only |

A gate without a failure path is not a gate. A hard stop should serialize current state, raise a human-action request, and write the reason to `logs/RUN_LOG.md`.

Human-only decisions include:

- Materiality
- Accounting treatment
- Management representation
- Audit sufficiency
- Tax/legal/compliance interpretation
- Investment or trading action
- Public disclosure
- Customer/vendor communication
- Payment hold/release
- Cash transfer or financing action
- Board, investor, lender, regulator, or auditor release

## Data Sources and Evidence Contracts

Useful sources for finance recipes include:

| Source class | Examples | Evidence contract |
|---|---|---|
| Internal financial systems | ERP, GL, subledger, close tools, planning system | File path, export date, entity, period, owner, schema |
| Operating systems | CRM, billing, payroll, procurement, inventory | Source owner, refresh date, join keys, access approval |
| Banking/treasury | Bank balances, debt schedules, cash forecasts | Bank/source proof, date/time, no-transfer gate |
| Public markets and macro | SEC EDGAR, FRED, market data APIs | Source URL/API endpoint, timestamp, accession or series ID |
| Audit/control evidence | reconciliations, invoices, approvals, screenshots | Request ID, support path, preparer, reviewer, missing items |
| Governance | metric dictionary, accounting policy, approval matrix | version, owner, approval date |

The attached research adds concrete internal source contracts that should guide implementation:

| Source | Suggested local path | Required fields | Validation check |
|---|---|---|---|
| GL trial balance | `data/raw/gl/` | account_id, balance, date, currency, status | Debits and credits foot before processing |
| Bank transaction logs | `data/raw/bank/` | transaction_id, date, amount, type, description | No date gaps; ending balance ties to statement |
| Subledger exports | `data/raw/subledger/` | account_id, entity, date, amount, reference | Balance ties to GL control account |
| AP/AR aging | `data/raw/ap/`, `data/raw/ar/` | vendor/customer_id, invoice_id, due_date, amount, status | No future due dates without explanation |
| Budget and forecast files | `data/raw/budget/` | account_id, cost_center, period, amount, version | Version ID matches approved cycle |
| Contract documents | `data/raw/contracts/` | contract_id, amendment_chain, effective_date | Amendment chain completeness check |

External data surfaces that fit Mycroft's source model include SEC EDGAR APIs for company submissions and company facts ([SEC](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)) and FRED's API for economic data series ([FRED API](https://fred.stlouisfed.org/docs/api/fred/)). Live fetches still require the Mycroft source gate, rate-safety review, and no-write mode unless explicitly approved.

## Stop Conditions and Anti-Patterns

Stop the recipe when:

- A source file is missing, stale, or from the wrong period.
- The workflow would post a journal entry, release payment, send a customer/vendor message, trade, transfer cash, submit a filing, or publish external communications.
- A generated explanation implies cause without driver evidence.
- Materiality thresholds are absent or invented.
- Sensitive financial, payroll, customer, or banking data is outside approved storage.
- A formula, accounting policy, covenant definition, or regulatory requirement is ambiguous.
- The output omits provenance.

Common anti-patterns:

- **Variance story laundering:** plausible explanations for deltas with no source or owner.
- **Dashboard theater:** charts with no metric definition or decision use.
- **Silent materiality:** thresholds chosen by convenience rather than an approved standard.
- **Evidence-free close confidence:** declaring close readiness because no parser failed.
- **Automation of authority:** treating a generated report as approval.
- **Investment advice creep:** turning SEC/portfolio analysis into a recommendation.
- **Control bypass:** using AI to change ERP, payment, or reporting state without a logged human gate.

## Recommended Build Sequence for Mycroft

### Phase 1: Foundation

1. Monthly variance analysis pack
2. Budget-request normalizer and challenge pack
3. AP/AR exception and aging workbench

These have the highest frequency, easiest local data contracts, obvious human reports, and low outward-facing risk. They address a large share of entry-level finance time spent gathering, normalizing, comparing, and preparing review packs.

### Phase 2: Close

4. Subledger-to-GL reconciliation exception triage
5. Close flux analysis and balance-sheet review pack

These create the record-to-report backbone: strong value for staff accountants, excellent auditability, and clean stop paths.

### Phase 3: Treasury

6. Daily cash position and liquidity watch
7. Cash forecast variance explainer

These have high decision value with a clear read-only boundary around all payment, transfer, borrowing, and investment actions.

### Phase 4: Controls

8. Control-evidence completeness checker
9. PBC request tracker and audit-evidence binder

These extend Mycroft's evidence-and-gates philosophy into audit support. Governance and access control must be defined before deployment.

### Phase 5: Advanced Governed Workflows

10. Revenue contract and billing exception triage
11. Debt-covenant evidence pack
12. Regulatory change obligation watchlist

These are valuable, but they need policy interpretation rules, legal/compliance boundaries, and mature role-based approval design before building.

## What Is Actually Useful

The most useful finance recipes are the ones that sit one step before judgment:

- not "approve the forecast," but "assemble the forecast bridge and flag unsupported assumptions";
- not "close the books," but "show close blockers and unexplained flux";
- not "tell us why revenue moved," but "separate sourced drivers from owner-needed explanations";
- not "release the board deck," but "prove every number and claim in the packet has a source";
- not "advise on investment," but "compare filings and flag changes for human review."

That is the Mycroft pattern. Finance people do not need a magical CFO bot. They need recipe cards that make evidence, gaps, and gates visible before a human signs off.

## Source Notes and Citations

Local Mycroft sources used:

- `SNICKERDOODLE.md`
- `DOMAIN.md`
- `DATA_CONTRACT.md`
- `docs/recipes.md`
- `recipes/mycroft-financial-intelligence-hub.md`
- `recipes/forecasting.md`
- `recipes/mycroft-sec-filings-analysis.md`
- `recipes/portfolio-dashboard.md`
- `recipes/portfolio-price-fetcher.md`
- `recipes/n8n-risk-management-agent.md`
- `reports/templates/`
- `reports/generated/mycroft-finance-recipe-opportunities-attached-research.md`

External sources used for grounding:

- U.S. Bureau of Labor Statistics, [Financial Analysts](https://www.bls.gov/ooh/business-and-financial/financial-analysts.htm)
- U.S. Bureau of Labor Statistics, [Accountants and Auditors](https://www.bls.gov/ooh/business-and-financial/accountants-and-auditors.htm)
- U.S. Bureau of Labor Statistics, [Budget Analysts](https://www.bls.gov/ooh/business-and-financial/budget-analysts.htm)
- U.S. Securities and Exchange Commission, [EDGAR Application Programming Interfaces](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- Federal Reserve Bank of St. Louis, [FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/)
- Public Company Accounting Oversight Board, [AS 1105: Audit Evidence](https://pcaobus.org/oversight/standards/auditing-standards/details/AS1105)
