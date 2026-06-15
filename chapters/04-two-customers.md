# 04. Two Customers

## Concrete Failure or Work Scenario

One workflow produces a perfect JSON log that the controller will never read. Another produces a polished memo that cannot be rerun. Both are failures.

The failure is not that AI was used. The failure is that preparation crossed into judgment without evidence, ownership, or a gate. Mycroft's finance rule is simple: automate the preparation layer, preserve the accountable layer.

## Capability Statement

After this chapter, you will be able to read recipes as both agent contracts and finance reviewer cards.

**Assessment artifact:** Two-customer recipe note.

## Why This Matters for the Reader's Role

Entry- and mid-level finance practitioners spend much of their time gathering data, checking records, comparing periods, building reports, and preparing review surfaces. BLS role descriptions for financial analysts, accountants/auditors, and budget analysts all emphasize data review, financial statement review, budget monitoring, record inspection, and reporting. The opportunity is to make that preparation work more reliable without pretending the recipe can perform the professional judgment.

## The Recipe Concept

Design every recipe for two customers. The agent needs inputs, steps, schemas, stop conditions, and logs. The human needs purpose, evidence, caveats, decisions, owners, and gates.

The useful recipe is narrow, source-bound, and reviewable. It produces a machine-readable log for reproducibility and a human-readable report for decision support. It stops before accounting treatment, payment action, public disclosure, filing, investor communication, or release.

## Agentic Supervision Lens

AI can follow the machine contract. The human must be able to judge the report without reverse-engineering the run.

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

- The recipe has both an agent output and a human report
- gates are visible
- a future maintainer can rerun it.

Machine conformance checks whether the file parses and the required fields exist. Human adequacy checks whether the work is good enough for the finance decision it supports.

## Human-Only Judgment Boundary

AI cannot decide what makes a workflow maintainable for a finance team.

That boundary is the phase gate. The recipe prepares the work surface on one side. The accountable finance human crosses it.

## Bridge to Next Chapter

The next chapter teaches how to verify finance evidence before trusting the recipe output.

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
- `pantry/04-two-customers_notes.md`
