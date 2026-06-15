# 07. Subledger-to-GL Reconciliation Triage

## Concrete Failure or Work Scenario

An AR subledger is off from the GL control account by a material amount. The system can find unmatched rows; it cannot decide the accounting treatment.

The failure is not that AI was used. The failure is that preparation crossed into judgment without evidence, ownership, or a gate. Mycroft's finance rule is simple: automate the preparation layer, preserve the accountable layer.

## Capability Statement

After this chapter, you will be able to surface reconciliation exceptions without deciding accounting treatment.

**Assessment artifact:** Reconciliation exception queue.

## Why This Matters for the Reader's Role

Entry- and mid-level finance practitioners spend much of their time gathering data, checking records, comparing periods, building reports, and preparing review surfaces. BLS role descriptions for financial analysts, accountants/auditors, and budget analysts all emphasize data review, financial statement review, budget monitoring, record inspection, and reporting. The opportunity is to make that preparation work more reliable without pretending the recipe can perform the professional judgment.

## The Recipe Concept

Verify source extracts, period coverage, and control totals. Match deterministically before fuzzy matching. Classify exceptions as timing, mapping, duplicate, missing support, or unexplained. Carry forward prior-period open items.

The useful recipe is narrow, source-bound, and reviewable. It produces a machine-readable log for reproducibility and a human-readable report for decision support. It stops before accounting treatment, payment action, public disclosure, filing, investor communication, or release.

## Agentic Supervision Lens

AI can match, bucket, age, and surface exceptions. The accountant signs off on adequacy and treatment.

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

- Trial balance footing is checked
- duplicate transaction IDs stop the run
- unexplained material differences are escalated.

Machine conformance checks whether the file parses and the required fields exist. Human adequacy checks whether the work is good enough for the finance decision it supports.

## Human-Only Judgment Boundary

AI cannot book an adjustment or accept a reconciling item.

That boundary is the phase gate. The recipe prepares the work surface on one side. The accountable finance human crosses it.

## Bridge to Next Chapter

Treasury uses the same read-only posture for daily cash visibility.

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
- `pantry/07-subledger-to-gl-reconciliation-triage_notes.md`
