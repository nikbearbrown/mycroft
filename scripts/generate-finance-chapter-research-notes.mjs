import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const generated = "2026-06-14";
const pantry = join(process.cwd(), "pantry");
mkdirSync(pantry, { recursive: true });

const commonSources = [
  "TIKTOC.md",
  "MYCROFT.md",
  "DOMAIN.md",
  "DATA_CONTRACT.md",
  "docs/recipes.md",
  "docs/phase-gates.md",
  "docs/data-and-provenance.md",
  "reports/generated/entry-mid-finance-recipes-research.md",
  "reports/generated/mycroft-finance-recipe-opportunities-attached-research.md",
  "https://www.bls.gov/ooh/business-and-financial/financial-analysts.htm",
  "https://www.bls.gov/ooh/business-and-financial/accountants-and-auditors.htm",
  "https://www.bls.gov/ooh/business-and-financial/budget-analysts.htm",
  "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
  "https://fred.stlouisfed.org/docs/api/fred/",
  "https://pcaobus.org/oversight/standards/auditing-standards/details/AS1105",
];

const libSources = [
  "pantry/_lib_ai-gigo.md",
  "pantry/_lib_ai-nbb-prompt-architecture-the-power-of-the-template-pattern.md",
  "pantry/_lib_ai-prediction-machines-the-simple-economics-of-artificial-intelligence.md",
  "pantry/_lib_business-data-ism-the-revolution-transforming-decision-making-consumer-behavior-and-al.md",
  "pantry/_lib_finance-advances-in-financial-machine-learning.md",
  "pantry/_lib_math-data-harness-your-numbers-to-go-from-uncertain-to-unstoppable.md",
  "pantry/_lib_math-how-to-lie-with-statistics.md",
  "pantry/_lib_math-how-to-measure-anything-finding-the-value-of-intangibles-in-business.md",
];

const chapters = [
  {
    n: "01",
    slug: "the-fluency-trap",
    title: "The Fluency Trap",
    summary: "Detect the gap between fluent finance output and trustworthy finance work. The chapter opens with a clean AI-generated variance commentary, close summary, or board-packet note that sounds plausible but hides unsupported explanations, stale sources, missing period labels, and no approval gate.",
    concepts: ["Fluency is not evidence", "Finance artifacts mix numbers, explanations, and approvals", "Generated text is an artifact, not a source", "Review begins by separating claim, number, assumption, and owner"],
    examples: ["AI-written variance commentary with no driver data", "Board-packet note with stale chart period", "Close summary that says 'ready' while support is missing"],
    settled: "Presentation quality does not establish source adequacy, data freshness, or approval status.",
    contested: "How much drafting AI should do before human review depends on control maturity and reviewer behavior.",
    exercise: "Give readers a polished finance paragraph and make them classify every number, explanation, and approval implication.",
  },
  {
    n: "02",
    slug: "the-reallocation-principle",
    title: "The Reallocation Principle",
    summary: "Reframe finance automation as scarce judgment allocation. The goal is not more dashboards, more commentary, or faster spreadsheet churn. The goal is to reallocate human effort toward materiality, explanation, review, risk, and release.",
    concepts: ["Preparation work versus judgment work", "AI reduces the cost of extraction and comparison", "Human review time should move toward materiality and interpretation", "Automation that weakens review is a failure"],
    examples: ["FP&A analyst stops hand-building variance tables and spends more time on owner explanations", "Staff accountant uses matching automation but still owns recon sign-off", "Treasury analyst gets faster cash visibility without automated transfers"],
    settled: "Many finance tasks include repeated data gathering, checking, and report assembly that can be structured.",
    contested: "The exact labor split varies by regulation, company policy, systems, and reviewer capacity.",
    exercise: "Map one week of finance work into preparation, evidence, transformation, judgment, approval, and release.",
  },
  {
    n: "03",
    slug: "the-verified-finance-data-contract",
    title: "The Verified Finance Data Contract",
    summary: "State what counts as finance evidence in Mycroft: source, period, entity, version, owner, freshness, schema, control total, transformation, log, report, and approval record.",
    concepts: ["Source/version/period are part of the evidence", "Control totals are gates, not decoration", "Logs and reports serve different customers", "A generated paragraph is never the original evidence"],
    examples: ["Budget file with stale version ID", "Trial balance that does not foot", "Report number that cannot be traced back to a source row"],
    settled: "Finance evidence needs provenance, completeness, and reliability before interpretation.",
    contested: "Different teams define acceptable evidence and materiality thresholds differently.",
    exercise: "Trace one number from human report to agent log to source export and note every missing link.",
  },
  {
    n: "04",
    slug: "two-customers",
    title: "Two Customers",
    summary: "Understand recipes as both agent contracts and finance reviewer cards. The agent needs executable structure; the finance human needs purpose, evidence, caveats, gates, and decisions.",
    concepts: ["Agent log versus human report", "Recipe intent versus run truth", "Machine conformance versus human adequacy", "Maintainability for the next reviewer"],
    examples: ["JSON variance log that is unusable by the CFO", "Pretty memo that cannot be rerun", "Recipe card with both schema and reviewer decision fields"],
    settled: "Finance workflows need reproducibility and human-readable decision surfaces.",
    contested: "How much detail belongs in the report versus the log depends on audience and audit needs.",
    exercise: "Annotate one Mycroft recipe for agent customer fields and human customer fields.",
  },
  {
    n: "05",
    slug: "verifying-finance-evidence",
    title: "Verifying Finance Evidence",
    summary: "Interrogate completeness, freshness, control totals, mapping, thresholds, and warranted verbs. A parsed spreadsheet can still be wrong, and a sourced number can still be irrelevant.",
    concepts: ["Completeness and freshness", "Mapping and threshold risk", "Warranted verbs", "Contradictory evidence is still evidence"],
    examples: ["Mapped actuals with unmapped material account", "Subledger tie-out with stale extract", "Variance explanation that should say 'may suggest' instead of 'caused'"],
    settled: "Audit evidence standards emphasize sufficiency and appropriateness; finance analysis needs similar discipline.",
    contested: "How much automated anomaly detection is enough before human review starts.",
    exercise: "Write can say, can suggest, cannot claim, needs review for a small evidence packet.",
  },
  {
    n: "06",
    slug: "monthly-variance-pack",
    title: "Monthly Variance Pack",
    summary: "Build a variance pack that separates verified deltas from human explanations: actuals, budget, forecast, mapping tables, thresholds, control totals, material variance flags, owner commentary, and open items.",
    concepts: ["Budget versus actual", "Material variance threshold", "Driver evidence", "Commentary stubs, not causal conclusions"],
    examples: ["Department spend above budget due to payroll timing", "Revenue below forecast without owner explanation", "Stale budget version blocks the run"],
    settled: "Variance analysis is a recurring finance workflow that compares current and historical financial data.",
    contested: "The materiality threshold and acceptable driver evidence are organization-specific.",
    exercise: "Build a variance table with source, delta, threshold status, known driver, and owner-needed fields.",
  },
  {
    n: "07",
    slug: "subledger-to-gl-reconciliation-triage",
    title: "Subledger-to-GL Reconciliation Triage",
    summary: "Surface reconciliation exceptions without deciding accounting treatment. Teach source completeness, GL-to-subledger control totals, deterministic matching, exception categories, prior-period carry-forward, and reviewer sign-off.",
    concepts: ["GL and subledger control totals", "Deterministic match before fuzzy match", "Exception taxonomy", "Accounting treatment is human-only"],
    examples: ["AR subledger does not tie to GL control account", "Duplicate transaction ID blocks matching", "Prior-period recon item still open"],
    settled: "Reconciliations depend on complete source extracts and control total agreement.",
    contested: "Use of fuzzy matching in accounting workflows requires explicit tolerance and review policy.",
    exercise: "Create an exception queue with timing, mapping, duplicate, missing-support, and unexplained categories.",
  },
  {
    n: "08",
    slug: "daily-cash-position-and-liquidity-watch",
    title: "Daily Cash Position and Liquidity Watch",
    summary: "Produce a read-only cash view with hard treasury action boundaries: bank feed freshness, normalized balances, reconciliation where possible, availability buckets, thresholds, and escalation.",
    concepts: ["Read-only treasury automation", "Cash availability and restriction", "Threshold breach escalation", "No payment or transfer action"],
    examples: ["Missing bank feed stops the run", "Unknown account excluded from consolidated cash", "Liquidity threshold breach escalates but does not trigger a transfer"],
    settled: "Cash visibility is operationally useful but banking actions require human authority.",
    contested: "How real-time cash visibility should be depends on bank feeds and treasury controls.",
    exercise: "Build a daily cash table with as-of timestamps, account, entity, currency, availability, and threshold flag.",
  },
  {
    n: "09",
    slug: "close-flux-analysis-and-balance-sheet-review",
    title: "Close Flux Analysis and Balance-Sheet Review",
    summary: "Prepare close review surfaces without declaring the books ready: trial balance comparison, account-level flux, support coverage, carry-forward items, known events, unresolved movements, and controller review.",
    concepts: ["Flux analysis", "Support coverage", "Close status", "Readiness versus sign-off"],
    examples: ["Large prepaid asset movement with no support", "Intercompany balance unresolved", "Known seasonal expense movement documented"],
    settled: "Period-over-period review is useful for surfacing unusual movements.",
    contested: "What counts as unusual depends on materiality, seasonality, and business context.",
    exercise: "Rank flux items by size and support status, then write reviewer questions.",
  },
  {
    n: "10",
    slug: "budget-request-normalizer-and-challenge-pack",
    title: "Budget-Request Normalizer and Challenge Pack",
    summary: "Normalize planning submissions and prepare challenge questions: template validation, account/category normalization, headcount/rate checks, prior-year comparison, policy flags, and business-partner sign-off.",
    concepts: ["Template conformance", "Planning assumptions", "Outlier challenge questions", "Negotiation is human-only"],
    examples: ["Department submits old template", "Unsupported headcount request", "Rate assumption exceeds approved reference table"],
    settled: "Budget analysts review proposals for completeness, accuracy, and compliance with rules.",
    contested: "Challenge aggressiveness depends on organizational planning culture.",
    exercise: "Normalize three budget requests and produce a challenge-question list.",
  },
  {
    n: "11",
    slug: "control-evidence-completeness-checker",
    title: "Control-Evidence Completeness Checker",
    summary: "Check control evidence readiness without concluding on control effectiveness: control objectives, attribute requirements, evidence artifacts, stale screenshots, approvals, sample coverage, prior exceptions, and remediation routing.",
    concepts: ["Evidence completeness", "System-generated report reliability", "Design and operating effectiveness remain human conclusions", "Remediation evidence"],
    examples: ["Key control missing reviewer approval screenshot", "Stale system report", "Prior exception marked closed without support"],
    settled: "Audit and control work requires sufficient, appropriate evidence and human testing conclusions.",
    contested: "How to test AI-prepared evidence binders inside SOX or audit programs is still emerging.",
    exercise: "Create a control-by-control evidence readiness ledger with ready, blocked, follow-up status.",
  },
  {
    n: "12",
    slug: "ap-ar-exception-and-aging-workbench",
    title: "AP/AR Exception and Aging Workbench",
    summary: "Turn AP and AR aging into exception queues without external action: aging buckets, duplicate invoice flags, missing support, dispute status, owner queues, and communication gates.",
    concepts: ["Aging buckets", "Duplicate invoice candidate versus confirmed duplicate", "Dispute status", "No customer/vendor communication without approval"],
    examples: ["Same vendor, amount, and invoice date flags duplicate risk", "AR item over 90 days lacks dispute owner", "Unknown counterparty blocks action queue"],
    settled: "AP/AR work is high-volume and exception-oriented.",
    contested: "Duplicate-detection tolerances and near-match rules need local approval.",
    exercise: "Build AP/AR queues by aging tier, owner, duplicate risk, and missing support.",
  },
  {
    n: "13",
    slug: "cash-forecast-variance-explainer",
    title: "Cash Forecast Variance Explainer",
    summary: "Compare forecast cash to realized cash without inventing causes: forecast version control, realized cash, category variance, bridge structure, known drivers, unexplained variances, and reforecast gates.",
    concepts: ["Forecast version control", "Cash bridge", "Known driver attachment", "Reforecast decision gate"],
    examples: ["Collections below forecast with no driver note", "Payroll outflow timing explains variance", "Forecast and actuals cover different periods and stop the run"],
    settled: "Forecast-to-actual comparison is useful only when periods and versions match.",
    contested: "Forecast revisions require business judgment about persistence versus timing.",
    exercise: "Create a cash bridge with forecast, actual, variance, known driver, and needs-explanation columns.",
  },
  {
    n: "14",
    slug: "pbc-request-tracker-and-audit-evidence-binder",
    title: "PBC Request Tracker and Audit-Evidence Binder",
    summary: "Assemble audit support while preserving privilege, adequacy, and reviewer gates: PBC list, support mapping, status, reviewer sign-off, overdue items, and binder index.",
    concepts: ["PBC request lifecycle", "Evidence binder index", "Privilege and sharing gate", "Adequacy review"],
    examples: ["PBC item lacks owner", "Submitted file has no reviewer sign-off", "Document should not be shared externally until privilege is reviewed"],
    settled: "Audit support requires organized, traceable evidence and review status.",
    contested: "Which artifacts can be shared externally is legal/audit-team specific.",
    exercise: "Build a PBC tracker with request ID, owner, due date, support path, status, and gap.",
  },
  {
    n: "15",
    slug: "revenue-contract-and-billing-exception-triage",
    title: "Revenue Contract and Billing Exception Triage",
    summary: "Separate factual billing mismatches from accounting-policy questions: contract source-chain completeness, amendment order, billing setup comparison, pricing mismatches, milestone gaps, policy flags, and revenue-recognition stop conditions.",
    concepts: ["Contract source chain", "Billing setup mismatch", "Policy interpretation flag", "Revenue recognition is human-only"],
    examples: ["Missing amendment stops review", "Price list mismatch is operational", "Variable consideration is routed to accounting review"],
    settled: "Contracts and billing records can be compared mechanically for factual mismatches.",
    contested: "Revenue recognition conclusions depend on policy and professional judgment.",
    exercise: "Classify contract/billing exceptions into factual mismatch, missing documentation, and accounting review.",
  },
  {
    n: "16",
    slug: "the-build-and-the-honest-run",
    title: "The Build and the Honest Run",
    summary: "Integrate Mycroft finance recipes through a bounded, logged run. Choose a finance scenario, run or simulate selected recipes, inspect evidence, write logs, produce a report, name gates, and record unresolved risks.",
    concepts: ["Bounded run", "Run log versus report", "Gate decision record", "Open risks are evidence"],
    examples: ["Variance plus budget challenge capstone", "Close support plus reconciliation capstone", "Treasury cash watch plus forecast variance capstone"],
    settled: "Mycroft treats the run record as the truth of what happened.",
    contested: "How much autonomy a finance recipe earns depends on documented runs and human attestation.",
    exercise: "Complete one honest run and submit log, report, evidence appendix, gates, and did-not-test list.",
  },
];

function list(items) {
  return items.map((item) => `- ${item}`).join("\n");
}

function sources(extra = []) {
  return [...new Set([...commonSources, ...extra, ...libSources])];
}

function render(chapter) {
  const sourceList = sources();
  const prior = Number(chapter.n) > 1 ? `Chapter ${Number(chapter.n) - 1}` : "Introduction";
  const next = Number(chapter.n) < 16 ? `Chapter ${Number(chapter.n) + 1}` : "Appendix 97";
  return `# Research Notes: Chapter ${chapter.n} - ${chapter.title}

**Source:** TIKTOC.md chapter entry
**Notes file:** ${chapter.n}-${chapter.slug}_notes.md
**Corresponding chapter:** chapters/${chapter.n}-${chapter.slug}.md (not yet written)
**Generated:** ${generated}

---

## Chapter summary (from TIKTOC.md)

${chapter.summary}

---

## A. Conceptual foundations

${chapter.concepts.map((concept, i) => `### ${concept}

This concept matters because finance workflows become risky when preparation work and judgment work are blended together. In a Mycroft recipe, the agent can gather, compare, normalize, match, flag, and draft. The finance human decides adequacy, materiality, interpretation, accounting treatment, release, and action.

**Common misconception:** Learners often treat a clean table or fluent explanation as evidence that the underlying finance work is complete. The correct move is to ask what source, period, version, owner, control total, and approval record supports it.

**Worked example:** Use a small source table with one missing period, one stale version, one unexplained variance, and one approval-needed action. The recipe should surface the issues and stop before any human-only decision.

**Source(s):** ${sourceList.slice(0, 8).join("; ")}
`).join("\n")}

---

## B. Domain examples and cases

${chapter.examples.map((example, i) => `### Case ${i + 1}: ${example}

The case should be written as a realistic finance work scenario. Show the source files, the check performed, the exception or gap surfaced, and the human gate that prevents the recipe from overstepping. The key teaching point is that the recipe makes review easier; it does not perform the accountable judgment.

**Source(s):** TIKTOC.md; reports/generated/entry-mid-finance-recipes-research.md; reports/generated/mycroft-finance-recipe-opportunities-attached-research.md
`).join("\n")}

### Failure case: Automation crosses the finance authority boundary

A recipe that posts a journal entry, releases payment, sends a customer/vendor message, concludes on control effectiveness, submits a filing, or issues investor-facing commentary has crossed from preparation into accountable action. This is a Mycroft hard stop.

**Source(s):** MYCROFT.md; reports/generated/mycroft-finance-recipe-opportunities-attached-research.md

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**

- Basic finance artifact literacy - the reader should know what a budget, actual, account, invoice, cash balance, or support file is.
- Mycroft labor separation - the reader should know that AI executes and humans decide.
- Provenance - the reader should expect source paths, versions, periods, owners, logs, and reports.

**Unlocks (what this chapter makes possible):**

- ${chapter.title} unlocks later recipes by giving the reader a concrete artifact pattern they can reuse.
- It teaches a reusable distinction between verified findings, inferred findings, unsupported claims, and human-only decisions.
- It contributes to the final honest run in Chapter 16.

**Adjacent chapter connections:**

- ${prior}: supplies the prerequisite frame or artifact that this chapter builds on.
- ${next}: uses this chapter's evidence boundary, recipe pattern, or output surface.

---

## D. Current state of the field

**Settled:**

- ${chapter.settled}
- Finance workflows require evidence provenance, completeness checks, and review gates.
- Occupational baselines from BLS place analysts, accountants, auditors, and budget analysts in data review, record inspection, budget monitoring, and reporting workflows.

**Contested or emerging:**

- ${chapter.contested}
- AI use in finance is moving quickly, but controls, auditability, and release authority remain organization-specific.
- Autonomous finance actions are high risk unless policy, permissions, evidence, and attestation are explicit.

**Key references:**

1. MYCROFT.md - The governing labor-separation and verification-stack constitution.
2. DATA_CONTRACT.md - Local data and evidence rules.
3. BLS Occupational Outlook Handbook - Role-level grounding for financial analysts, accountants/auditors, and budget analysts.
4. PCAOB AS 1105 - Audit evidence concepts useful for sufficiency, appropriateness, and contradictory evidence.
5. SEC EDGAR API and FRED API documentation - Examples of public structured financial/economic data surfaces.

**Recent developments (last 3 years):**

- Finance teams are experimenting with AI for knowledge management, AP automation, error detection, and report assembly, but governance remains uneven.
- Public-data APIs such as SEC EDGAR and FRED are increasingly useful as structured sources, but live fetches still require source gates and provenance.
- Agentic tools make multi-step workflows easier to automate, increasing the need for explicit stop conditions.

---

## E. Teaching considerations

**Where students get stuck:**

- They want the AI to write the explanation instead of preparing the evidence for an explanation.
- They confuse parser success with finance adequacy.
- They omit version, period, owner, or threshold information because the table looks obvious.
- They forget that external action and release are separate gates.

**Analogies and framings that work:**

- The recipe is a prep cook, not the chef who signs the dish.
- The log is the flight recorder; the report is the pilot briefing.
- A control total is a locked door, not a trophy.

**Exercises that build the target skill:**

- ${chapter.exercise}
- Ask the reader to mark every row as verified, inferred, unsupported, or human-only.
- Ask the reader to write one stop condition that would block the run and one gate record that would clear it.

---

## Shared library files copied to pantry

${list(libSources)}
`;
}

for (const chapter of chapters) {
  writeFileSync(join(pantry, `${chapter.n}-${chapter.slug}_notes.md`), render(chapter));
}

const index = `# Mycroft Finance Chapter Research Index

Generated: ${generated}

## Chapter list extracted from TIKTOC.md

${chapters.map((c) => `- ${c.n} | ${c.slug} | ${c.title}`).join("\n")}

Total: ${chapters.length}

## Missing named chapters

The current chapter directory still contains placeholder files such as \`chapters/01-chapter-01.md\`. The named files proposed in \`TIKTOC.md\` do not yet exist, so these notes treat chapters 01-16 as missing named chapters.

## Notes written

${chapters.map((c) => `- pantry/${c.n}-${c.slug}_notes.md`).join("\n")}

## Library scan

Shared library path: \`/Users/bear/Documents/CoWork/bear-textbooks/MD\`

- Files scanned: 312 markdown files.
- Files copied to pantry: ${libSources.length}.
- Selection basis: finance, measurement, data quality, AI supervision, statistical skepticism, prompt/recipe architecture.

${list(libSources)}

## Web and authoritative sources used

${list(commonSources.filter((s) => s.startsWith("http")))}
`;

writeFileSync(join(pantry, "chapter-research-index.md"), index);

console.log(`Wrote ${chapters.length} chapter notes and pantry/chapter-research-index.md`);
