# Mycroft Finance Recipe Opportunities
## Entry- and Mid-Level Practitioner Map

---

## 1. Executive Summary

Mycroft's operating philosophy is already correct for corporate finance: local evidence before external lookup, hard phase gates, separate agent logs and human reports, and explicit preservation of human judgment for scope, interpretation, materiality, and release. The gap is not architectural. It is coverage: Mycroft's current finance recipes are concentrated on public-market research and monitoring, while day-to-day entry- and mid-level finance work is dominated by internal comparison-and-evidence tasks — budget variance packs, reconciliations, close support, cash visibility, control evidence gathering, AP/AR exception handling, and report assembly.

The core principle throughout: AI made execution cheap. It did not make judgment cheap. Every recipe in this report automates the preparation layer — data gathering, matching, comparison, exception surfacing, and report assembly — while reserving materiality calls, interpretation, approval, release, and all externally consequential actions for humans.

This report identifies 22 recipe candidates across seven finance functions, ranks them by Mycroft fit, and provides full recipe cards for the top 10.

**What Mycroft should not automate end-to-end under any framing:** journal posting, ERP master-data changes, payment initiation, regulatory filings, public disclosures, investor communications, tax positions, final revenue-recognition conclusions, control-deficiency grading, or suspicious-activity filing decisions. These sit on the wrong side of Mycroft's labor-separation boundary and, in several cases, on the wrong side of formal regulatory or audit obligations.

---

## 2. What Finance Work Looks Like at Entry and Mid Levels

### BLS occupational baseline (2024–2034)

| Occupational Title | SOC Code | US Employment (2024) | Median Pay (2024) | Projected Growth | Primary Workflow Characteristics |
|---|---|---|---|---|---|
| Accountants and Auditors | 13-2011 | 1,579,800 | $81,680 | 5% (average) | Reconciliation, audit workpapers, transaction matching, subledger integrity |
| Financial and Investment Analysts | 13-2051 | 368,500 | $101,350 | 6% (faster than average) | Data gathering, trend analysis, budget support, written reports |
| Financial Risk Specialists | 13-2054 | 60,500 | $106,000 | 6% | Risk assessment, compliance docs, regulatory monitoring |
| Budget Analysts | 13-2031 | 55,200 | $87,930 | 4% (average) | Budget consolidation, variance tracking, funding requests |
| Bookkeeping and Accounting Clerks | 43-3031 | 1,500,000+ | $49,210 | Declining | AP/AR posting, invoice matching, balance-sheet support |

### What entry-level people actually do

BLS and O*NET descriptions consistently identify the same pattern: the work is not building models from scratch each day. It is evaluating current and historical data, extracting from ERP systems, matching transactions against purchase orders, tracking budget-to-actual variances, reconciling subledger balances, preparing written reports, and assembling evidence for review. That combination is exactly the kind of repeated, source-sensitive, documentation-heavy work that becomes a good recipe once inputs, thresholds, and review gates are made explicit.

For accountants, staff accountants, and internal-audit-adjacent workers, the pattern is even more operational: preparing and examining records, checking compliance, inspecting account books and systems, identifying discrepancies, and producing reports for managers. Bookkeeping and accounting clerks post transactions, classify debits and credits, produce reports, and check the accuracy of figures, postings, and calculations. These are recipe-native tasks because they rely on defined records, recurrent control totals, and exception handling.

### Where the time goes

Industry data (Deloitte, Gartner 2025 AI in Finance Survey) finds:
- ~41% of finance team time is spent gathering and processing data
- Month-end close still takes six or more business days at half of all finance teams
- The top AI use cases in finance are knowledge management (49%), AP automation (37%), and error detection (34%)

The implication: the largest time sinks are all pre-judgment — data extraction, reconciliation, and report assembly.

---

## 3. Existing Mycroft Finance Coverage and the Biggest Gaps

Mycroft's current recipe architecture already provides a strong chassis for new finance recipes. The existing docs establish local-first evidence, provenance requirements, hard gates, a split between intents in recipes and truth in runs, and a two-customer model: the agent gets detailed parseable logs; the human gets a short decision-oriented report. Finance recipe cards in the repo already standardize agent-output fields — run mode, records seen, rejects, duplicates, flags, stop conditions, source files, gate decisions, and report path.

Existing finance-adjacent coverage includes: SEC filings analysis, forecasting, portfolio dashboards, portfolio price fetching, scenario stress testing, financial regulatory intelligence, financial intelligence hub, earnings-call intelligence, and finance-literacy bots.

The gap is structural. This coverage is concentrated on public-market research and monitoring. Compared with what BLS and O*NET describe, Mycroft is relatively light on:

- Plan-to-actual workflows (budget variance, flux analysis)
- Record-to-report workflows (reconciliation, close support)
- Order-to-cash and procure-to-pay exception work (AP/AR aging and exception queues)
- Day-to-day treasury operations (cash position, covenant monitoring)
- Audit-support evidence operations (PBC tracking, control evidence completeness)

The architecture is ready before the practitioner-finance operating surface is.

---

## 4. Recipe Opportunity Map by Finance Function

| Finance Function | Best Recipe Families | Best-Fit Roles | Mycroft Fit |
|---|---|---|---|
| FP&A and corporate finance | Monthly variance packs, budget-request normalization, KPI QA, forecast bridges | Entry analysts, senior analysts, budget analysts | Very high |
| Accounting and close | Reconciliation exception triage, close flux analysis, accrual support packs, close checklist evidence assembly | Staff accountants, senior analysts | Very high |
| Treasury | Daily cash position, cash forecast variance, bank fee review, debt and covenant evidence packs | Treasury analysts, senior analysts | High |
| Internal audit and controls | PBC trackers, control-evidence completeness checks, walkthrough prep packs, remediation evidence packs | Internal-audit associates, staff accountants | High |
| Revenue and finance operations | Billing and contract exception triage, AR dispute workbenches, AP duplicate-payment scans, invoice/PO discrepancies | Revenue analysts, finance-operations specialists, staff accountants | High |
| Regulatory and financial-services analysis | Regulatory change watchlists, exam-prep evidence packs, advisory tagging | Risk and compliance analysts | Medium — controls must mature first |

---

## 5. Highest-Value Recipe Candidates, Ranked

| Rank | Recipe | Primary Roles | Priority | Why it ranks here | Adjacent Mycroft Recipes |
|---|---|---|---|---|---|
| 1 | Monthly variance pack and commentary binder | Entry analysts, senior analysts, FP&A | HIGH | Very frequent, data-bound, explainable, close to forecasting scaffolds | Forecasting, financial intelligence hub |
| 2 | Subledger-to-GL reconciliation exception triage | Staff accountants, finance ops | HIGH | Core close work, rule-based matching, strong audit trail, zero autonomous judgment needed | No direct equivalent — inherits standard skeleton |
| 3 | Daily cash position and liquidity watch | Treasury analysts | HIGH | Daily cadence, clear inputs, dashboard fit, clear human-only payment boundary | Portfolio dashboard, price fetcher |
| 4 | Close flux analysis and balance-sheet review pack | Staff accountants, senior analysts | HIGH | Common monthly task, comparison-heavy, easy to log and escalate | Forecasting-style compare/flag/report scaffolds |
| 5 | Budget-request normalizer and challenge pack | Entry analysts, budget analysts | HIGH | Standard review and consolidation workflow with strong review gates | Forecasting, financial intelligence hub |
| 6 | Control-evidence completeness checker | Internal-audit associates, staff accountants | HIGH | Excellent rule-based fit; evidentiary rather than interpretive | Financial regulatory intelligence, SEC filings analysis |
| 7 | AP/AR exception and aging workbench | Finance operations, revenue analysts | HIGH | High-volume exception handling; inspectable; clear stop paths | No direct equivalent |
| 8 | Cash forecast variance explainer | Treasury analysts, senior analysts | HIGH | Strong treasury value; combines internal forecast with realized balances | Forecasting, portfolio dashboard |
| 9 | PBC request tracker and audit-evidence binder | Internal-audit associates, staff accountants | MEDIUM | Strong value; workflow design depends on local audit methods and privilege rules | Standard log/report scaffolds |
| 10 | Revenue contract and billing exception triage | Revenue analysts, staff accountants | MEDIUM | Valuable, but governance must be stricter because revenue-recognition judgment risk is higher | No direct equivalent |

**MEDIUM (build after foundation is stable):** Debt-covenant evidence packs, KPI definition QA packs, bank-fee review, expense-policy exception review, regulatory change obligation watchlists.

**LOW / do not automate until governance matures:** Public-disclosure preparation, investor communications, AML/SAR workflow automation, filing submission, anything that changes ERP records or initiates payments without explicit human approval architecture.

---

## 6. Recipe Cards

### Recipe 1 — Monthly Variance Pack and Commentary Binder

**Priority:** HIGH
**User role:** Entry-level analysts, senior analysts, budget analysts, management accountants
**Trigger:** Month-end close, weekly business review, or reforecast cycle

**Inputs:**
- `data/raw/actuals_monthly.csv` — approved ERP actuals for the period
- `data/raw/budget_fy.csv` — approved budget and forecast versions
- Account and cost-center mapping tables
- KPI definitions and threshold table
- Prior-period bridge and owner comments

**Steps:**
1. Verify source provenance, period label, and version IDs; reject stale or unapproved versions
2. Test control totals: actuals must foot to closed trial balance
3. Compute budget-vs-actual, forecast-vs-actual, and period-over-period deltas by account and cost center
4. Filter variances below both dollar materiality and percentage threshold; rank material items
5. Attach owner commentary where available; surface missing explanations as open items
6. Pull prior-period trend for each flagged item (no causal explanation — stubs only)
7. Assemble management-ready pack with summary, exception table, commentary stubs, and open items

**Agent output (log):**
- Source file hashes (SHA-256), version IDs, row counts
- Control total validation result
- Variance count by category (favorable/unfavorable, above/below threshold)
- Missing commentary items
- Gate decisions and run timestamp

**Human report:**
- Period header and scope
- Summary: total variance, favorable/unfavorable split
- Material variance table: account, cost center, budget, actual, $Δ, %Δ, prior-period trend
- Commentary stub column (analyst writes causal explanations)
- Open items requiring owner response
- Explicit separation: **verified findings** vs. **inferred/unexplained**

**Phase gates:**
1. Scope/materiality — human confirms period, entity, threshold before run
2. Source-version — human confirms actuals tie to closed trial balance
3. Commentary-adequacy — human reviews whether explanations cover material items
4. Release — human approves distribution

**Stop conditions:**
- Actuals don't tie to trial balance → stop; log discrepancy
- Budget version is prior-cycle (stale) → stop; request current version
- Missing mapping tables → stop; log unmapped accounts
- Control totals fail → stop immediately

**Human-only boundary:** Causal explanation of every variance; materiality judgment; reforecast decisions; distribution.

**Why useful:** Budget analysts review requests for completeness and accuracy, consolidate budgets, and monitor spending against plan. Management accountants prepare budgets and evaluate performance. This recipe eliminates the computational layer entirely, leaving the analytical layer — the part that requires judgment — intact.

**Adjacent Mycroft recipes:** Forecasting, Mycroft forecasting agent, financial intelligence hub.

---

### Recipe 2 — Subledger-to-GL Reconciliation Exception Triage

**Priority:** HIGH
**User role:** Staff accountants, accounting analysts, finance operations specialists
**Trigger:** Close calendar milestone or reconciliation deadline

**Inputs:**
- `data/raw/gl/` — GL detail export: account_id, balance, date, currency, status
- `data/raw/subledger/` — subledger exports (AR, AP, fixed assets, prepaid, accrued liabilities)
- Chart-of-accounts mapping
- Prior-period reconciliation status and open items
- Approved tolerance rules per account category

**Data contract validation (per PCAOB AS 1105 — Audit Evidence):**
- Confirm `∑ Debits + ∑ Credits = 0` in GL trial balance before any processing
- Verify no date gaps in subledger export sequence
- Hash all source files at ingestion

**Steps:**
1. Verify source extracts and period coverage; reject incomplete exports
2. Reconcile control totals: GL balance must agree to trial balance
3. Match GL records to subledger records using deterministic rules first, then approved fuzzy rules
4. Classify exceptions: timing difference, mapping error, duplication, missing support, or unexplained
5. Cross-reference prior-period open items: resolved vs. still open
6. Generate exception queue per account with evidence links and aging

**Agent output (log):**
- Source file hashes and row counts (in/out)
- Match rate by account
- Exception taxonomy with counts and amounts
- Tolerance thresholds used
- Prior-period items: resolved count, still-open count
- Unresolved material items flagged separately

**Human report:**
- Reconciliation status summary by account
- Exception aging (count and amount per category)
- Material differences requiring accountant investigation
- Prior-period open items carry-forward
- Actions required by owner
- **Verified findings** vs. **unexplained differences** clearly labeled

**Phase gates:**
1. Source completeness — human confirms all required subledger exports are present
2. Tolerance approval — human sets dollar and percentage tolerances per account type
3. Exception-classification review — human reviews unexplained differences before any proposed treatment
4. Sign-off — human accepts reconciliation or escalates

**Stop conditions:**
- GL trial balance does not foot → stop immediately
- Missing extract completeness proof → stop; log which subledger is absent
- Duplicate transaction IDs in any source file → stop; potential double-payment risk
- Unexplained material difference → stop; escalate; do not suppress

**Human-only boundary:** Final acceptance of all reconciling items; journal entry decisions; any proposed posting treatment.

**Why useful:** Accountants and auditors organize, analyze, and maintain records, inspect books and systems, and explain findings in reports. This recipe handles the matching and classification mechanically, isolating the judgment work — what to *do* about the exceptions — for the accountant.

**Adjacent Mycroft recipes:** No direct close-equivalent today; inherits standard Mycroft recipe skeleton and report model.

---

### Recipe 3 — Daily Cash Position and Liquidity Watch

**Priority:** HIGH
**User role:** Treasury analysts, senior analysts, controller-support staff
**Trigger:** Start-of-day treasury run or intraday liquidity checkpoint

**Inputs:**
- `data/raw/bank/` — bank-balance feeds or prior-day statements: transaction_id, date, amount, type, description
- Cash ledger (GL cash accounts, prior-day close)
- Debt-service schedule and investment maturities
- Approved cash forecast (inflows and outflows by day)
- Entity/bank-account master data
- Minimum liquidity thresholds per entity or account

**Steps:**
1. Verify bank-data timestamps; reject stale feeds (configurable freshness threshold)
2. Normalize balances across accounts, entities, and currencies
3. Reconcile bank balances to GL cash where period aligns
4. Bucket cash by entity, currency, restriction type, and availability
5. Compare to forecast and minimum-liquidity thresholds; flag breaches
6. Apply known scheduled outflows (debt service, payroll, AP runs) over configurable horizon
7. Assemble liquidity watch report; escalate threshold breaches immediately regardless of run schedule

**Agent output (log):**
- As-of timestamps per bank account
- Balances by account/entity/currency
- Reconciliation status per account
- Threshold breach flags (hard stop — never suppressed)
- Unresolved or unmapped accounts
- Forecast vs. actual position

**Human report:**
- Current cash view: account, balance, entity, currency, availability
- Forecast gap analysis: N-day horizon
- Threshold breach alerts (prominent)
- Actions requiring treasury attention
- Action column blank — treasury analyst fills

**Phase gates:**
1. Source freshness — human confirms bank data is within acceptable window
2. Balance completeness — human confirms all accounts are represented
3. Threshold review — human sets minimum liquidity thresholds
4. Escalation gate — any threshold breach requires human action before close of day

**Stop conditions:**
- Bank data feed not received or fails integrity check → stop; alert immediately
- Projected threshold breach → escalate immediately; never suppress
- Unknown account in master data → flag; do not include in consolidated position without confirmation
- Any request for payment initiation or fund transfer → stop; this is a human action

**Human-only boundary:** All funding actions, sweeps, borrow/invest decisions, and external bank instructions. The recipe is strictly read-only on bank systems.

**Why useful:** Treasury/controller work centers on monitoring cash flow and resources, preparing financial reports, and monitoring compliance. This fits Mycroft's existing dashboard and price-fetch/report patterns architecturally.

**Adjacent Mycroft recipes:** Portfolio dashboard, portfolio price fetcher.

---

### Recipe 4 — Close Flux Analysis and Balance-Sheet Review Pack

**Priority:** HIGH
**User role:** Staff accountants, senior analysts, accounting managers
**Trigger:** Monthly or quarterly close review

**Inputs:**
- Current and prior period trial balances
- Account detail for flagged accounts
- Entity hierarchy and elimination schedule
- Materiality thresholds and expected seasonality/known events
- Prior review comments and unresolved items

**Steps:**
1. Verify period close-complete status before running
2. Compute account-level and category-level flux: absolute and percentage change
3. Rank movements by size and unusualness relative to seasonality
4. Attach available supporting documentation
5. Distinguish expected (documented) from unexplained changes
6. Prepare review packet with verified findings separated from open inferences
7. Carry forward prior-period unresolved items

**Agent output (log):**
- Account movements with prior-period comparison
- Threshold hits (count and amount)
- Support-coverage status per flagged account
- Carry-forward items from prior period
- Open review questions

**Human report:**
- Top flux items ranked by size
- Unexplained movements with evidence gap noted
- Accounts requiring additional support
- Approval or escalation options
- **Verified observations** vs. **unresolved inferences** explicitly labeled

**Phase gates:**
1. Period close-complete gate — human confirms close is fully posted
2. Support-coverage gate — human reviews whether flagged items have adequate documentation
3. Reviewer gate — accounting manager reviews open inferences before sign-off
4. Release gate — controls sign-off on the review package

**Stop conditions:**
- Incomplete close data → stop; note which entities are not closed
- Missing support on material balance → stop; request documentation
- Unresolved intercompany or balance-sheet integrity issues → stop; escalate

**Human-only boundary:** Adequacy of all explanations; materiality conclusions; reserve decisions; sign-off.

**Adjacent Mycroft recipes:** No direct close-review recipe in repo today; structurally closest to forecasting compare/flag/report scaffolds.

---

### Recipe 5 — Budget-Request Normalizer and Challenge Pack

**Priority:** HIGH
**User role:** Entry-level analysts, senior analysts, budget analysts
**Trigger:** Annual planning cycle, quarterly replan, or ad hoc funding review

**Inputs:**
- Departmental budget submissions (normalized template required)
- Staffing and headcount requests
- Reference rates: approved labor, overhead, and escalation rates
- Prior-year spend by department and account
- Policy constraints and template version

**Steps:**
1. Verify template version and submission completeness; reject non-conforming formats
2. Normalize time buckets, account categories, and currency across submissions
3. Check completeness: flag missing headcount support, missing rate assumptions, or incomplete narratives
4. Compare requests to prior-year spend and approved reference rates; surface outliers
5. Cross-reference with known organizational constraints
6. Compile a challenge pack: consolidated view with flagged items and open questions per department

**Agent output (log):**
- Submission registry with completeness status
- Normalization changes applied (logged for traceability)
- Policy exceptions and outlier flags
- Missing field list per submission
- Reviewer queues by department

**Human report:**
- Consolidated budget request summary
- Challenge questions per department (flagged assumptions, unsupported headcount)
- Unresolved items requiring owner response
- Decisions required: which submissions need revision before consolidation

**Phase gates:**
1. Intake completeness — human confirms all department submissions are received
2. Policy-constraint gate — human reviews policy exceptions before challenge questions are sent
3. Outlier-review gate — human approves which items go into the challenge pack
4. Business-partner sign-off — human approves consolidated view before planning cycle advances

**Stop conditions:**
- Incomplete submission from required department → stop consolidation; flag
- Unsupported headcount or rate assumptions → flag; do not consolidate without resolution
- Unapproved template version → reject; request resubmission

**Human-only boundary:** Negotiating funding; prioritizing tradeoffs; final budget approval.

**Why useful:** BLS describes budget analysts as reviewing budget proposals for completeness, accuracy, and compliance, consolidating budgets, and helping managers find alternatives if plans are unsatisfactory. The recipe handles the mechanical consolidation and challenge-generation; the negotiation is human.

**Adjacent Mycroft recipes:** Forecasting, financial intelligence hub.

---

### Recipe 6 — Control-Evidence Completeness Checker

**Priority:** HIGH
**User role:** Internal-audit associates, SOX associates, staff accountants supporting controls
**Trigger:** Control testing window, walkthrough preparation, remediation follow-up, or pre-audit readiness check

**Inputs:**
- Control library with control objectives and attribute requirements
- Evidence request list (PBC list)
- Evidence artifacts: screenshots, system reports, approval records, role matrices
- Period and sample selection parameters
- Prior exceptions and remediation status

**PCAOB alignment:** PCAOB AS 1105 (Audit Evidence) requires sufficient and appropriate evidence; AS 2201 (Audit of Internal Control Over Financial Reporting) requires testing design and operating effectiveness. Both place the sufficiency, reliability, and control-conclusion decisions squarely in human judgment territory. The recipe prepares the evidence readiness pack; the conclusion is human-only.

**Steps:**
1. Verify control identity, period coverage, and attribute requirements against control library
2. For each control: check whether required evidence exists, is complete, and traces to the control objective
3. Check preparer/reviewer evidence, approval timestamps, and segregation signals
4. Surface missing approvals, stale screenshots, or attribute failures
5. Cross-reference against prior exceptions: resolved vs. still open
6. Assemble evidence-readiness pack classified by status: ready, blocked, needs follow-up

**Agent output (log):**
- Control-by-control evidence ledger
- Missing artifacts list
- Stale documents (beyond configurable age threshold)
- Attribute failures by type
- Unresolved questions

**Human report:**
- Controls ready for testing
- Controls blocked by evidence gaps (with specific missing artifact listed)
- Recurring documentation weaknesses
- Remediation actions and owners

**Phase gates:**
1. Scope gate — human approves control population and period before run
2. Evidence-completeness gate — human reviews missing-artifact list before testing begins
3. Reliability gate — human assesses whether system-generated reports have sufficient precision
4. Remediation gate — human confirms whether prior exceptions are adequately resolved
5. No automatic conclusion gate — recipe cannot conclude on control design or operating effectiveness

**Stop conditions:**
- Missing evidence for any key control → flag; do not mark as testable
- Inconsistent evidence from different sources → flag; treat as contradictory evidence per PCAOB AS 1105
- Any request to auto-conclude on effectiveness → stop; this is human-only

**Human-only boundary:** All design and operating-effectiveness conclusions; deficiency grading; communication to management or external auditors.

**Why useful:** PCAOB requires sufficient and appropriate evidence, resolution of inconsistent information, and explicit human testing conclusions. Mycroft's existing regulatory-intelligence and SEC-analysis recipes already show how to structure source-sensitive evidence workflows — this extends that pattern inward to internal controls.

**Adjacent Mycroft recipes:** Financial regulatory intelligence system, SEC filings analysis.

---

### Recipe 7 — AP/AR Exception and Aging Workbench

**Priority:** HIGH
**User role:** Finance operations specialists, revenue analysts, staff accountants
**Trigger:** Daily queue review, weekly collections meeting, or close cutoff

**Inputs:**
- `data/raw/ap/` — AP aging: vendor_id, invoice_id, invoice_date, due_date, amount, status, dispute_reason
- AR aging: customer_id, invoice_id, invoice_date, due_date, amount, status, dispute_reason
- Payment status and dispute history
- Customer/vendor master data
- PO or receipt references where applicable
- Prior exception notes and owner assignments

**Steps:**
1. Verify source completeness; confirm as-of date
2. Compute days outstanding = as-of date − due date
3. Bucket items into aging tiers (current, 1–30, 31–60, 61–90, 90+)
4. Classify past-due or blocked items: operational miss, data-quality issue, disputed, or missing support
5. Match items to supporting documents where available
6. Identify duplicate invoice risk (same vendor, amount, date within configurable window)
7. Create exception queues by owner, root cause, and aging bucket

**Agent output (log):**
- Aging buckets: count and amount per tier
- Exception taxonomy with counts
- Duplicate invoice flags
- Missing support references
- Owner queues

**Human report:**
- Overdue concentrations by vendor/customer and aging tier
- Root-cause summary (operational, data quality, disputed)
- At-risk items: high-value or long-aged
- Duplicate flags requiring review
- Actions required (blank — analyst fills collection or payment action)

**Phase gates:**
1. Source completeness — confirm all aging exports are current-period
2. Queue classification review — human reviews classification before queues are distributed
3. Collection/escalation gate — human approves collection actions or credit holds
4. Close gate — human confirms exception disposition before period close

**Stop conditions:**
- Missing invoice support → flag; do not route for payment
- Unknown counterparty in master data → flag; do not include in action queue
- Any request to change ERP records, waive policy, or promise customer terms → stop; human-only

**Human-only boundary:** Customer or vendor communications; write-off decisions; credit holds; policy exceptions.

**Why useful:** Bookkeeping and accounting clerks work directly with payables and receivables and verify postings; billing clerks verify accuracy, resolve discrepancies, and keep support records. BLS data shows these are among the highest-volume roles in finance — automation impact is substantial.

**Adjacent Mycroft recipes:** No direct equivalent today.

---

### Recipe 8 — Cash Forecast Variance Explainer

**Priority:** HIGH
**User role:** Treasury analysts, senior analysts
**Trigger:** Weekly treasury review or post-period reconciliation

**Inputs:**
- Approved cash forecast (prior week or month)
- Realized cash position (from daily cash position recipe or bank statement)
- Actuals by category: collections, disbursements, debt service, investments, other
- Known drivers (payroll dates, large AP runs, debt payments)

**Steps:**
1. Verify forecast version and realization period match
2. Compute forecast-vs-actual variance by cash flow category
3. Rank variances by absolute size
4. For each material variance, attach known driver if present in the driver file
5. Flag categories with no known driver as requiring analyst explanation
6. Assemble a structured bridge: beginning cash → categories → ending cash, forecast vs. actual

**Agent output (log):**
- Forecast version and period
- Variance by category: forecast, actual, Δ$, Δ%
- Known drivers attached
- Unexplained variances flagged (count and amount)
- Bridge reconciliation status

**Human report:**
- Cash flow bridge (waterfall format)
- Material variances with driver or "requires explanation" flag
- Trend: same category variance vs. prior periods
- Implications for next period forecast (blank — analyst fills)

**Phase gates:**
1. Version confirmation — human confirms correct forecast version
2. Driver review — human confirms which variances have adequate explanations
3. Forecast update gate — any reforecast decision requires human approval

**Stop conditions:**
- Forecast and actuals cover different periods → stop
- Unexplained material variance > threshold → flag and hold; do not carry forward silently

**Human-only boundary:** Forecast revision decisions; root-cause interpretation; communication to CFO or management.

**Adjacent Mycroft recipes:** Forecasting, portfolio dashboard, daily cash position recipe (upstream).

---

### Recipe 9 — PBC Request Tracker and Audit-Evidence Binder

**Priority:** MEDIUM
**User role:** Internal-audit associates, staff accountants supporting external audit
**Trigger:** Audit fieldwork initiation; weekly status during audit window

**Inputs:**
- PBC (provided-by-client) request list from auditors
- Prepared documents and supporting files
- Preparer and reviewer assignments
- Due dates and audit firm contacts
- Prior-year PBC list for reference

**Steps:**
1. Ingest PBC list and verify all items have owners and due dates
2. Match submitted documents to open requests by item ID
3. Compute status: received, partially received, overdue, or not started
4. Flag items past due or missing required reviewer sign-off
5. Identify items submitted without adequate description or support
6. Assemble status binder with document inventory and gap list

**Agent output (log):**
- PBC item count and status distribution
- Overdue items (count and days overdue)
- Items missing reviewer sign-off
- Items submitted with inadequate description
- Document inventory with file references

**Human report:**
- PBC status dashboard: item, owner, due date, status, notes
- Overdue and at-risk items highlighted
- Gap list: what is still needed and from whom
- Escalation items for audit manager review

**Phase gates:**
1. Scope gate — human confirms PBC list matches current audit scope
2. Adequacy review — human assesses whether submitted documents meet auditor requirements
3. Privilege gate — human confirms which documents can be shared with external auditors

**Stop conditions:**
- PBC item with no assigned owner → flag; do not include in status without owner
- Document submission with access or privilege concerns → flag; human resolves before sharing

**Human-only boundary:** Adequacy judgments; auditor communications; privilege determinations; any response to auditor findings.

**Adjacent Mycroft recipes:** Control-evidence completeness checker (complementary); standard log/report scaffolds.

---

### Recipe 10 — Revenue Contract and Billing Exception Triage

**Priority:** MEDIUM
**User role:** Revenue analysts, technical-accounting support, staff accountants
**Trigger:** New contract intake, month-end revenue review, or billing discrepancy review

**Inputs:**
- Contract metadata and executed contract documents
- Billing schedules and price lists
- Customer amendments and amendment chain
- Invoice history and fulfillment milestones
- Policy mappings for performance obligation classification

**Steps:**
1. Verify contractual source set: confirm all amendments are present
2. Normalize dates, products, pricing, and amendment chains
3. Compare contract terms to billing setup: flag pricing mismatches, missing milestones, or unsupported overrides
4. Identify inconsistencies in the amendment chain
5. Classify exceptions: factual mismatch (billing error) vs. policy-interpretation question (needs accounting review)
6. Assemble a review pack that explicitly separates the two categories

**Agent output (log):**
- Contract registry with amendment chain completeness status
- Mismatch taxonomy: pricing, milestone, override, amendment gap
- Missing artifact list
- Policy-interpretation flags (these are human-only)

**Human report:**
- Factual billing discrepancies (operational fixes)
- Contracts needing accounting review (policy-interpretation questions)
- Missing documentation
- Decisions required

**Phase gates:**
1. Source-chain gate — human confirms all amendments are present before analysis
2. Contract-completeness gate — human reviews missing-artifact list
3. Accounting-policy review gate — human reviews all policy-interpretation flags; recipe cannot conclude
4. Release gate — human approves before any billing corrections are initiated

**Stop conditions:**
- Ambiguous contract hierarchy (amendment order unclear) → stop; request clarification
- Missing amendments → stop; do not analyze an incomplete contract chain
- Any request to auto-conclude on revenue recognition, timing, or allocation → stop immediately

**Human-only boundary:** Principal-vs-agent determination; SSP allocation; timing conclusions; disclosure; final accounting memo. ASC 606 variable consideration and contract modification assessments are human-only in all cases — these are not stop conditions that fire occasionally; they are the normal substance of the judgment work.

**Adjacent Mycroft recipes:** No direct equivalent; structurally closest to source-sensitive finance scaffolds already in the repo.

---

## 7. Phase Gates, Judgment Boundaries, and Anti-Patterns

### Minimum phase-gate stack for all finance recipes

Every finance recipe should implement these gates in sequence:

| Gate | Purpose | Who clears it |
|---|---|---|
| Problem gate | Confirm period, entity, scope, and version | Human |
| Source adequacy gate | Confirm completeness, freshness, and approved versions | Human |
| Data-shape gate | Confirm parseability and schema conformance | Agent validates; human reviews failures |
| Reconciliation gate | Confirm control totals or source agreement | Agent computes; human reviews discrepancies |
| Sensitive-action gate | Stop before anything touching disclosures, submissions, trading, or accounting conclusions | Hard stop — human required |
| Interpretation gate | Materiality calls, narrative meaning | Human only |
| Release gate | Any distribution outside the immediate working context | Human only |

A gate without a failure path is not a gate. Every hard stop must serialize current state to a staging directory, raise a human-action request, and wait. It must also log the stop in `logs/RUN_LOG.md` with the reason.

### The dual-artifact model

Every finance recipe produces two outputs:

**Agent log** (detailed, parseable, for audit and reproducibility): run ID, source file hashes (SHA-256), version IDs, row counts, control totals used, records processed/rejected/duplicated, flags raised, gate decisions, stop conditions triggered, run timestamp.

**Human report** (short, decision-oriented): summary, key findings, decisions required, anomalies and flags, link to full log. Finance reports should add four fields consistently: data-as-of timestamp, version IDs for internal sources, control totals used, and an explicit separation between **verified findings** and **inferred or unexplained findings**. That last split directly implements the PCAOB requirement that contradictory information is also evidence.

### Anti-patterns (hard prohibitions)

| Anti-pattern | Why dangerous |
|---|---|
| Agent writes variance explanations | This is the analytical judgment. If the agent explains "why," the human stops reading critically. |
| Agent recommends or posts journal entries | JE posting is a control. Recommendations become instructions with one click. |
| Agent sets materiality thresholds | Materiality has legal and audit significance. Must be human-set each run. |
| Agent concludes on control effectiveness | PCAOB AS 2201 requires human testing conclusions. |
| Agent distributes reports directly | Release gate must be human. Wrong numbers at scale are worse than slow numbers. |
| Recipes run silently on a schedule with no human confirmation | Finance recipes must be human-initiated or explicitly confirmed before execution. |
| Output formatted as final before human review | Final-looking formatting discourages scrutiny. All outputs should be DRAFT until human approves. |
| Variable consideration treated as a stop condition in ASC 606 workflows | Variable consideration is common in real contracts. A stop condition that fires constantly makes the recipe useless. The correct design treats it as a policy-interpretation flag routed to human review. |

---

## 8. Data Sources and Evidence Contracts

### Internal sources (user-supplied)

| Source | Local Path | Required Schema Fields | Validation Check | PCAOB AS 1105 Relevance |
|---|---|---|---|---|
| GL trial balance | `data/raw/gl/` | account_id, balance, date, currency, status | `∑ Debits + ∑ Credits = 0` | Completeness and accuracy of ledger source |
| Bank transaction logs | `data/raw/bank/` | transaction_id, date, amount, type, description | Consecutive dates; ending balance ties to statement | Completeness; no temporal gaps |
| Subledger exports | `data/raw/subledger/` | account_id, entity, date, amount, reference | Balance ties to GL control account | Subledger integrity |
| AP/AR aging | `data/raw/ap/`, `data/raw/ar/` | vendor/customer_id, invoice_id, due_date, amount, status | No future due dates without explanation | Accuracy of open-item records |
| Budget and forecast files | `data/raw/budget/` | account_id, cost_center, period, amount, version | Version ID matches approved cycle | Approved-version provenance |
| Contract documents | `data/raw/contracts/` | contract_id, amendment_chain, effective_date | Amendment chain completeness check | Completeness of contractual evidence |

### External sources (agent-fetched)

| Source | Access Method | Use in Mycroft Recipes | Notes |
|---|---|---|---|
| SEC EDGAR (submissions, XBRL facts, company concepts) | `data.sec.gov` — free, no API key; identify via user agent | Peer comparison, SEC filings analysis, covenant benchmarks | Updates near real-time; compliant automated access required |
| FRED / ALFRED | Federal Reserve API — free | Macro context for variance analysis (e.g., PPI for freight cost correlation); ALFRED vintage dates preserve "what was known when" | ALFRED is the better choice for audit-grade macro inputs — preserves historical vintage |
| Treasury yield curve | FRED or TreasuryDirect | Debt covenant, interest rate sensitivity in treasury recipes | |
| SEC, FinCEN, Federal Register, FINRA, CFTC | Official regulatory feeds | Regulatory change obligation watchlists, compliance monitoring | FinCEN advisories useful as tagged source material; SAR filing decisions are strictly human |
| Regulatory calendars | SEC.gov, FinCEN.gov, state regulator sites | Regulatory filing deadline tracker | |

---

## 9. Stop Conditions (Consolidated)

| Condition | Action |
|---|---|
| GL trial balance debits ≠ credits | Hard stop on all accounting and reconciliation recipes |
| Duplicate transaction IDs in any source file | Hard stop; log as potential double-payment risk |
| Date gaps in bank statement or ERP export | Hard stop; partial reconciliation is worse than no reconciliation |
| Control totals fail to agree between sources | Hard stop; log and request resolution |
| Stale source version (budget file from prior cycle) | Hard stop; request current version |
| Threshold breach in cash position | Escalate immediately; never suppress regardless of run schedule |
| Unknown account or counterparty in master data | Flag; do not include in consolidated output without confirmation |
| External data feed unavailable | Log; proceed with internal data only; note gap prominently in report |
| Any request for payment initiation, fund transfer, ERP write, or filing submission | Hard stop; this is a human action |
| Any request to conclude on materiality, control effectiveness, or revenue recognition | Hard stop; this is a human judgment |

---

## 10. Recommended Build Sequence

| Build Wave | Recipes | Rationale |
|---|---|---|
| **Foundation** | Monthly variance pack; budget-request normalizer; AP/AR exception workbench | Highest frequency, easiest local data contracts, obvious human reports, low outward-facing risk. These address the largest single category of entry-level finance time consumption. |
| **Close** | Subledger-to-GL reconciliation triage; close flux analysis | Strong value for staff accountants; excellent auditability and clean stop paths. |
| **Treasury** | Daily cash position; cash forecast variance explainer | High decision value with clear human-only boundary around all payment and investment actions. |
| **Controls** | Control-evidence completeness checker; PBC tracker | Extends Mycroft's evidence-and-gates philosophy directly into audit support. Governance must be defined before deployment. |
| **Advanced** | Revenue contract and billing exception triage; debt-covenant evidence pack; regulatory change obligation watchlist | Valuable, but needs policy interpretation rules, legal/compliance boundaries, and mature role-based approval design before building. |

---

## 11. Source Notes

**Mycroft repository materials:** MYCROFT.md, DOMAIN.md, DATA_CONTRACT.md, docs/recipes.md, docs/phase-gates.md, docs/workflows.md, docs/data-and-provenance.md, logs/RUN_LOG.md, existing finance recipe cards, finance report templates.

**BLS Occupational Outlook Handbook (2024–2034):** Financial analysts, accountants/auditors, budget analysts, financial risk specialists, bookkeeping/accounting clerks. Employment, wage, and workflow characteristics.

**O*NET:** Financial analysts, management accountants, treasury/controller, financial risk specialists, billing/posting clerks. Task and work-activity profiles.

**PCAOB standards:** AS 1105 (Audit Evidence) — sufficiency, appropriateness, and treatment of contradictory evidence. AS 2201 (Audit of Internal Control Over Financial Reporting) — design and operating effectiveness testing requirements. Both standards are foundational to the human-judgment boundaries in recipes 6 and 9.

**SEC EDGAR APIs:** `data.sec.gov` — submissions history, company concepts, company facts, frame-level XBRL data. Free public access; no API key required; compliant automated access expected.

**FRED / ALFRED:** Federal Reserve Economic Data and Archival FRED. ALFRED vintage dates make macro inputs audit-grade by preserving historical knowledge state.

**FinCEN:** Advisories and typology guidance as tagged source material for compliance watchlists. SAR filing decisions remain formal regulatory obligations and are human-only in all cases.

**ASC 606:** Revenue recognition standard. Governs recipe 10. Variable consideration, contract modifications, and principal-vs-agent determinations are human-only judgment territory — not stop conditions that fire on individual contracts, but permanent boundaries on what the recipe can conclude.

**Industry research:** Gartner 2025 AI in Finance Survey (60% of finance functions using AI); Deloitte (41% of finance time on data gathering); McKinsey (42% of finance activities fully automatable). Cited for scale context only; operational design comes from BLS/O*NET and PCAOB standards.

---

*22 recipe candidates identified across seven finance functions. 10 full recipe cards provided. Build sequence: Foundation wave → Close wave → Treasury wave → Controls wave → Advanced governed wave.*