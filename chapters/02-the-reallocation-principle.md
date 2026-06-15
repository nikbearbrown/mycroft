# 02. The Reallocation Principle

## Concrete Failure or Work Scenario

An analyst saves three hours by asking AI to draft a report, then spends the meeting defending a number whose source was wrong. Execution got cheaper; review got worse.

The failure is not that AI was used. The failure is that preparation crossed into judgment without evidence, ownership, or a gate. Mycroft's finance rule is simple: automate the preparation layer, preserve the accountable layer.

## Capability Statement

After this chapter, you will be able to move finance effort from spreadsheet churn toward judgment, review, and release decisions.

**Assessment artifact:** Weekly reallocation hypothesis.

## Why This Matters for the Reader's Role

Entry- and mid-level finance practitioners spend much of their time gathering data, checking records, comparing periods, building reports, and preparing review surfaces. BLS role descriptions for financial analysts, accountants/auditors, and budget analysts all emphasize data review, financial statement review, budget monitoring, record inspection, and reporting. The opportunity is to make that preparation work more reliable without pretending the recipe can perform the professional judgment.

## The Recipe Concept

Inventory a recurring finance workflow. Label each step as preparation, evidence, transformation, judgment, approval, or release. Automate only the preparation layer unless a human gate is explicit.

The useful recipe is narrow, source-bound, and reviewable. It produces a machine-readable log for reproducibility and a human-readable report for decision support. It stops before accounting treatment, payment action, public disclosure, filing, investor communication, or release.

## Agentic Supervision Lens

AI can gather, normalize, compare, and format. The human owns materiality, explanation, accounting treatment, and release.

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

- The plan names the human decision that improves
- saved time is reinvested into review
- no approval gate disappears.

Machine conformance checks whether the file parses and the required fields exist. Human adequacy checks whether the work is good enough for the finance decision it supports.

## Human-Only Judgment Boundary

AI cannot decide what finance work should matter. That is a management and accountability decision.

That boundary is the phase gate. The recipe prepares the work surface on one side. The accountable finance human crosses it.

## Bridge to Next Chapter

Reallocation only works when the evidence layer is disciplined. Chapter 3 defines the finance data contract.

## Sources Used

- `TIKTOC.md`
- `MYCROFT.md`
- `DATA_CONTRACT.md`
- `docs/recipes.md`
- `docs/phase-gates.md`
- `reports/generated/entry-mid-finance-recipes-research.md`
- `reports/generated/mycroft-finance-recipe-opportunities-attached-research.md`
- `https://www.bls.gov/ooh/business-and-financial/financial-analysts.htm`
- `https://www.bls.gov/ooh/business-and-financial/accountants-and-auditors.htm`
- `https://www.bls.gov/ooh/business-and-financial/budget-analysts.htm`
- `https://pcaobus.org/oversight/standards/auditing-standards/details/AS1105`
- `pantry/02-the-reallocation-principle_notes.md`
