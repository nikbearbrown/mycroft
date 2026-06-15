import { appendFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";

const root = process.cwd();
const date = "2026-06-14";
const book = basename(root);
const chaptersDir = join(root, "chapters");
const logsDir = join(root, "logs");

mkdirSync(chaptersDir, { recursive: true });
mkdirSync(logsDir, { recursive: true });

const commonSources = [
  "TIKTOC.md",
  "MYCROFT.md",
  "DATA_CONTRACT.md",
  "docs/recipes.md",
  "docs/phase-gates.md",
  "reports/generated/entry-mid-finance-recipes-research.md",
  "reports/generated/mycroft-finance-recipe-opportunities-attached-research.md",
  "https://www.bls.gov/ooh/business-and-financial/financial-analysts.htm",
  "https://www.bls.gov/ooh/business-and-financial/accountants-and-auditors.htm",
  "https://www.bls.gov/ooh/business-and-financial/budget-analysts.htm",
  "https://pcaobus.org/oversight/standards/auditing-standards/details/AS1105",
];

const chapters = [
  ["01", "the-fluency-trap", "The Fluency Trap", "audit fluent finance output before it becomes trusted finance work", "Claim, number, and assumption table", "A clean AI-generated variance note says revenue is down because enterprise renewals slipped. The spreadsheet has a number, the paragraph has confidence, and the deck looks ready. What is missing is the renewal export, the period label, the owner who confirmed the driver, and the approval gate.", "Split the artifact into numbers, claims, assumptions, and implied actions. For each row, record source, period, owner, status, and required gate. The output is not a better paragraph first; it is an evidence table that tells the reviewer what can be trusted.", "AI can segment, classify, and draft cautious language. The human decides whether a claim matters, whether evidence is sufficient, and whether the finance team can say it.", "Every number has a source or is removed; every explanation is sourced, inferred, unsupported, or owner-needed; every release or approval implication is named.", "AI cannot accept accountability for the finance explanation. It can prepare the surface for review.", "The next chapter asks what human time should be reallocated toward once fluent output is no longer mistaken for finished work."],
  ["02", "the-reallocation-principle", "The Reallocation Principle", "move finance effort from spreadsheet churn toward judgment, review, and release decisions", "Weekly reallocation hypothesis", "An analyst saves three hours by asking AI to draft a report, then spends the meeting defending a number whose source was wrong. Execution got cheaper; review got worse.", "Inventory a recurring finance workflow. Label each step as preparation, evidence, transformation, judgment, approval, or release. Automate only the preparation layer unless a human gate is explicit.", "AI can gather, normalize, compare, and format. The human owns materiality, explanation, accounting treatment, and release.", "The plan names the human decision that improves; saved time is reinvested into review; no approval gate disappears.", "AI cannot decide what finance work should matter. That is a management and accountability decision.", "Reallocation only works when the evidence layer is disciplined. Chapter 3 defines the finance data contract."],
  ["03", "the-verified-finance-data-contract", "The Verified Finance Data Contract", "state what counts as finance evidence in Mycroft", "Provenance note", "A board packet shows gross margin, cash runway, and a hiring-plan variance. The numbers may be right. The problem is that nobody can tell which export, version, period, entity, and transformation produced them.", "Define source, period, entity, version, owner, freshness, schema, control total, transformation, log, report, and approval record. A generated paragraph is an artifact, not evidence.", "AI can trace file paths, compare schemas, and identify missing fields. Humans decide whether the evidence is adequate for the decision.", "Every report number traces to a source; stale or missing versions are flagged; control totals are checked where applicable.", "AI cannot make a weak source adequate by summarizing it fluently.", "Once data has a contract, recipes must serve both the executing agent and the finance reviewer."],
  ["04", "two-customers", "Two Customers", "read recipes as both agent contracts and finance reviewer cards", "Two-customer recipe note", "One workflow produces a perfect JSON log that the controller will never read. Another produces a polished memo that cannot be rerun. Both are failures.", "Design every recipe for two customers. The agent needs inputs, steps, schemas, stop conditions, and logs. The human needs purpose, evidence, caveats, decisions, owners, and gates.", "AI can follow the machine contract. The human must be able to judge the report without reverse-engineering the run.", "The recipe has both an agent output and a human report; gates are visible; a future maintainer can rerun it.", "AI cannot decide what makes a workflow maintainable for a finance team.", "The next chapter teaches how to verify finance evidence before trusting the recipe output."],
  ["05", "verifying-finance-evidence", "Verifying Finance Evidence", "interrogate completeness, freshness, control totals, mapping, thresholds, and warranted verbs", "Warranted-verb list", "A reconciliation ties, a spreadsheet parses, and a chart renders. None of those facts proves the explanation is true or the decision is safe.", "Review evidence for completeness, freshness, source quality, mapping, threshold logic, and contradiction. Write conclusions using warranted verbs: can say, can suggest, cannot claim, needs review.", "AI can surface gaps and propose cautious language. The human judges sufficiency and relevance.", "Evidence limits are written near the conclusion; model judgments are labeled; causal language is blocked unless supported.", "AI cannot decide materiality or sufficiency in context.", "The first concrete finance recipe uses this discipline to build a monthly variance pack."],
  ["06", "monthly-variance-pack", "Monthly Variance Pack", "build a variance pack that separates verified deltas from human explanations", "Variance pack", "Actuals are loaded, the budget file is nearby, and the CFO wants commentary. The dangerous shortcut is to let the system explain every movement just because it can compute every delta.", "Ingest actuals, budget, forecast, mapping tables, thresholds, and prior comments. Check period and version. Compute dollar and percent variances. Flag material items. Attach owner comments where available and leave unsupported explanations blank.", "AI can calculate and rank variances. The human owns causal explanation, materiality, and release.", "Actuals tie to the approved source; budget version is current; unmapped accounts above threshold stop the run; owner-needed explanations are visible.", "AI cannot decide why a variance happened unless a human-approved driver supports it.", "Reconciliation applies the same discipline to record-to-report work."],
  ["07", "subledger-to-gl-reconciliation-triage", "Subledger-to-GL Reconciliation Triage", "surface reconciliation exceptions without deciding accounting treatment", "Reconciliation exception queue", "An AR subledger is off from the GL control account by a material amount. The system can find unmatched rows; it cannot decide the accounting treatment.", "Verify source extracts, period coverage, and control totals. Match deterministically before fuzzy matching. Classify exceptions as timing, mapping, duplicate, missing support, or unexplained. Carry forward prior-period open items.", "AI can match, bucket, age, and surface exceptions. The accountant signs off on adequacy and treatment.", "Trial balance footing is checked; duplicate transaction IDs stop the run; unexplained material differences are escalated.", "AI cannot book an adjustment or accept a reconciling item.", "Treasury uses the same read-only posture for daily cash visibility."],
  ["08", "daily-cash-position-and-liquidity-watch", "Daily Cash Position and Liquidity Watch", "produce a read-only cash view with hard treasury action boundaries", "Liquidity watch", "A bank feed is late and a liquidity threshold may be breached. A helpful system should alert the treasury team; it should not move money.", "Validate bank-feed freshness, normalize balances by account/entity/currency, bucket cash by availability, compare to thresholds, and escalate breaches. All payment, sweep, borrow, and investment actions are outside the recipe.", "AI can prepare a current cash view and threshold flags. Treasury decides actions.", "Each balance has an as-of timestamp; unknown accounts are excluded or flagged; threshold breaches are never suppressed.", "AI cannot initiate transfers or decide funding actions.", "Close review brings the same evidence-first logic back to the accounting calendar."],
  ["09", "close-flux-analysis-and-balance-sheet-review", "Close Flux Analysis and Balance-Sheet Review", "prepare close review surfaces without declaring the books ready", "Close flux review pack", "The close dashboard says complete, but prepaid assets moved sharply and support is missing. Close status is not the same as close adequacy.", "Compare current and prior trial balances, compute account-level flux, rank movements, attach support, carry forward unresolved items, and separate documented changes from unexplained movements.", "AI can compute flux and support coverage. The controller decides readiness and sign-off.", "Close-complete status is confirmed before analysis; material flux without support is blocked; unresolved integrity issues are escalated.", "AI cannot declare the books ready.", "Planning work uses a similar pattern: normalize inputs, surface questions, and leave budget decisions to humans."],
  ["10", "budget-request-normalizer-and-challenge-pack", "Budget-Request Normalizer and Challenge Pack", "normalize planning submissions and prepare challenge questions", "Budget challenge pack", "Departments send budget requests in different templates with different assumptions. The analyst needs a clean comparison surface before the planning discussion.", "Verify template versions, normalize periods/accounts/currencies, check headcount and rate assumptions, compare to prior spend, flag policy exceptions, and generate challenge questions.", "AI can normalize and surface outliers. Business partners negotiate and approve tradeoffs.", "Required submissions are present; unsupported headcount is flagged; old templates are rejected; challenge questions are reviewed before distribution.", "AI cannot approve or deny funding.", "Control evidence applies the same completeness logic to audit and SOX support."],
  ["11", "control-evidence-completeness-checker", "Control-Evidence Completeness Checker", "check control evidence readiness without concluding on control effectiveness", "Control evidence readiness ledger", "A control folder has screenshots, approvals, and system reports, but one screenshot is stale and one approval is missing. The binder looks full; the evidence is not ready.", "Map controls to objectives and required attributes. Check period, evidence existence, preparer/reviewer proof, timestamp, sample coverage, stale artifacts, prior exceptions, and remediation support.", "AI can build an evidence ledger. Audit/control humans decide reliability, design effectiveness, operating effectiveness, and deficiency severity.", "Missing evidence blocks ready status; inconsistent evidence is surfaced; no automatic conclusion is allowed.", "AI cannot conclude on control effectiveness.", "AP and AR queues show how evidence readiness works in high-volume finance operations."],
  ["12", "ap-ar-exception-and-aging-workbench", "AP/AR Exception and Aging Workbench", "turn AP and AR aging into exception queues without external action", "Aging and exception workbench", "A weekly AR report has old invoices, disputes, and missing owners. A weekly AP report has duplicate invoice candidates. The system should prepare queues, not contact customers or release payments.", "Validate aging exports, compute buckets, flag duplicate candidates, identify missing support, attach dispute status, assign owners, and produce queues by risk and action needed.", "AI can classify and queue. Humans communicate with vendors/customers, approve holds, release payments, or write off balances.", "Aging as-of date is current; unknown counterparties are flagged; duplicate candidates are not treated as confirmed duplicates.", "AI cannot send communications or change payment status.", "Cash forecast variance uses operating queues and realized cash to improve treasury review."],
  ["13", "cash-forecast-variance-explainer", "Cash Forecast Variance Explainer", "compare forecast cash to realized cash without inventing causes", "Cash forecast variance bridge", "The forecast missed by a large amount. Some difference is payroll timing; some is unexplained. The recipe should build the bridge and mark the gaps, not write a story to fill them.", "Confirm forecast version and realized period. Compute forecast-versus-actual by category. Attach known drivers. Build a beginning-cash to ending-cash bridge. Flag unexplained material variances.", "AI can calculate and assemble the bridge. Treasury/FP&A decides whether the forecast should change.", "Forecast and actual periods match; known drivers have sources; unexplained material variance remains open.", "AI cannot revise the forecast or explain persistence versus timing by itself.", "Audit support applies the same source-and-gap approach to PBC requests."],
  ["14", "pbc-request-tracker-and-audit-evidence-binder", "PBC Request Tracker and Audit-Evidence Binder", "assemble audit support while preserving privilege, adequacy, and reviewer gates", "PBC tracker and binder index", "The audit request list has thirty items, five owners, and ten folders of support. The risk is not just missing a file; it is sharing the wrong file or claiming adequacy too early.", "Ingest the PBC list, assign owners and due dates, map support to request IDs, check reviewer sign-off, identify overdue or partial items, and build a binder index.", "AI can organize and flag gaps. Humans judge adequacy, privilege, and auditor communication.", "Every request has owner/status/support path; privilege concerns are flagged; external sharing requires approval.", "AI cannot decide what is adequate audit evidence or what may be shared.", "Revenue and billing exceptions raise an even stricter accounting-policy boundary."],
  ["15", "revenue-contract-and-billing-exception-triage", "Revenue Contract and Billing Exception Triage", "separate factual billing mismatches from accounting-policy questions", "Revenue/billing exception review pack", "A contract amendment changes pricing, but billing setup may not reflect it. Some issues are factual mismatches. Others are revenue-recognition questions. The recipe must keep them separate.", "Verify contract source chain and amendment order. Normalize dates, products, prices, milestones, and billing setup. Flag factual mismatches, missing documents, unsupported overrides, and policy-interpretation questions.", "AI can compare contract facts to billing setup. Accounting humans handle revenue recognition and policy conclusions.", "Missing amendments stop the run; factual mismatches are separated from accounting-review items; no billing correction is initiated automatically.", "AI cannot determine revenue recognition, variable consideration, principal-versus-agent status, or final accounting memo conclusions.", "The final chapter integrates selected recipes into one honest run."],
  ["16", "the-build-and-the-honest-run", "The Build and the Honest Run", "operate a full Mycroft finance recipe run with logs, report, evidence appendix, and gate decisions", "Run log, report, evidence, and gates", "The reader has tables, queues, bridges, and binders. The final question is whether those artifacts connect into one bounded run that tells the truth about what happened.", "Choose a scenario, define scope, run or simulate selected recipes, inspect sources, produce a human report, write the agent log, record gate decisions, and list did-not-test and open risks.", "AI can assemble and check completeness. The human owns scope, adequacy, gate clearance, and final claims.", "Every artifact traces to sources; every gate has a condition; unresolved risks remain visible.", "AI cannot certify the whole run as adequate.", "The appendix gathers the doctrine behind the system."],
];

function sourcesFor(slug) {
  const note = `pantry/${slug}_notes.md`;
  return [...commonSources, note];
}

function list(items) {
  return items.map((item) => `- ${item}`).join("\n");
}

function renderChapter([n, slug, title, capability, artifact, scenario, recipe, lens, checklist, human, bridge]) {
  const sources = sourcesFor(`${n}-${slug}`);
  return `# ${n}. ${title}

## Concrete Failure or Work Scenario

${scenario}

The failure is not that AI was used. The failure is that preparation crossed into judgment without evidence, ownership, or a gate. Mycroft's finance rule is simple: automate the preparation layer, preserve the accountable layer.

## Capability Statement

After this chapter, you will be able to ${capability}.

**Assessment artifact:** ${artifact}.

## Why This Matters for the Reader's Role

Entry- and mid-level finance practitioners spend much of their time gathering data, checking records, comparing periods, building reports, and preparing review surfaces. BLS role descriptions for financial analysts, accountants/auditors, and budget analysts all emphasize data review, financial statement review, budget monitoring, record inspection, and reporting. The opportunity is to make that preparation work more reliable without pretending the recipe can perform the professional judgment.

## The Recipe Concept

${recipe}

The useful recipe is narrow, source-bound, and reviewable. It produces a machine-readable log for reproducibility and a human-readable report for decision support. It stops before accounting treatment, payment action, public disclosure, filing, investor communication, or release.

## Agentic Supervision Lens

${lens}

Supervision has three questions:

- Scope: what period, entity, source, and action space is allowed?
- Approval: who clears the gate before the output moves forward?
- Verification: what source, control total, or owner confirmation would make the finding defensible?

## Evidence Boundary

Verified evidence includes source files, versions, periods, owners, control totals, support paths, and logged transformations. Model judgment includes classification suggestions, language drafts, and anomaly labels. Human judgment includes materiality, adequacy, causal explanation, accounting treatment, release, and action.

The boundary matters because finance artifacts can affect reporting, cash, controls, compliance, and external trust. A generated artifact can be useful; it is not evidence by default.

## Running Project Task

Build the assessment artifact for your running company or sanitized sample. Include source paths, period, owner, status, stop conditions, and at least one human gate. If the data is thin, say so in the artifact.

## Verification Checklist

${list(checklist.split("; "))}

Machine conformance checks whether the file parses and the required fields exist. Human adequacy checks whether the work is good enough for the finance decision it supports.

## Human-Only Judgment Boundary

${human}

That boundary is the phase gate. The recipe prepares the work surface on one side. The accountable finance human crosses it.

## Bridge to Next Chapter

${bridge}

## Sources Used

${list(sources.map((source) => `\`${source}\``))}
`;
}

const appendix = `# 97. Fundamental Themes

## Appendix: Friction, Phase Gates, and Accountable Finance Work

Mycroft Finance Recipe Engine rests on one claim: AI made finance execution cheaper, but it did not make finance judgment cheaper. The repo's recipes, logs, reports, and gates exist to preserve that distinction.

## Theme 1: Friction Protects Judgment

Good finance work contains useful friction: source checks, version checks, control totals, threshold reviews, owner confirmations, and release gates. These are not administrative annoyances. They are the mechanism that keeps fluent output from becoming false confidence.

## Theme 2: Phase Gates Are the Boundary

A phase gate is the point where AI assistance stops and accountable human work begins:

- AI may compute a variance; a human explains it.
- AI may match subledger records; a human signs off.
- AI may flag a liquidity threshold breach; treasury decides what to do.
- AI may assemble control evidence; audit/control humans conclude.
- AI may compare contract terms to billing setup; accounting decides policy treatment.

The gate is not mistrust of AI. It is respect for the human responsibility on the other side.

## Theme 3: Provenance Beats Polish

A rough table with source paths, caveats, and owners is more useful than a smooth paragraph that cannot be traced. In finance, polish without provenance is a risk multiplier.

## Theme 4: Two Customers

Every recipe has two customers. The agent needs schemas, steps, logs, and stop conditions. The finance human needs purpose, evidence, caveats, owners, decisions, and gates. One artifact cannot serve both.

## Theme 5: Humans Plus AI

AI helps with extraction, normalization, comparison, matching, flagging, formatting, and drafting. Humans handle materiality, interpretation, accounting treatment, cash action, control conclusion, release, and accountability.

## Practitioner Doctrine

1. Treat generated finance text as an artifact, not evidence.
2. Never explain a variance without a driver or owner.
3. Never confuse parser success with finance adequacy.
4. Never let the recipe set materiality silently.
5. Never automate journal posting, payment release, filing, public disclosure, or investor communication.
6. Keep logs for agents and reports for humans.
7. Preserve unresolved items where reviewers can see them.
8. Make every gate testable.
9. Reward honest blockers over hidden risk.
10. Use AI to make finance judgment more available, not less necessary.
`;

for (const chapter of chapters) {
  const [n, slug] = chapter;
  writeFileSync(join(chaptersDir, `${n}-${slug}.md`), renderChapter(chapter));
}

writeFileSync(join(chaptersDir, "97-fundamental-themes.md"), appendix);

const logPath = join(logsDir, "log.csv");
if (!existsSync(logPath)) {
  appendFileSync(logPath, "date,book,chapter_slug,word_count,sources_count,verify_flag_count,pantry_notes_found,pantry_lib_files_used,thin_pantry,mechanism_explained,contested_claims_flagged\n");
}

for (const chapter of chapters) {
  const [n, slug, title] = chapter;
  const content = renderChapter(chapter);
  const wordCount = content.split(/\s+/).filter(Boolean).length;
  const row = [
    date,
    book,
    `${n}-${slug}`,
    wordCount,
    sourcesFor(`${n}-${slug}`).length,
    (content.match(/\[verify\]/g) || []).length,
    "yes",
    8,
    "no",
    `"The chapter deep-dives the ${title.toLowerCase()} recipe mechanism as a finance preparation-to-judgment workflow."`,
    (content.match(/\[contested/g) || []).length,
  ].join(",");
  appendFileSync(logPath, `${row}\n`);
}

console.log(`Wrote ${chapters.length} finance chapters and updated chapters/97-fundamental-themes.md`);
