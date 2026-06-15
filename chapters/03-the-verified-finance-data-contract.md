# 03. The Verified Finance Data Contract

## Concrete Failure or Work Scenario

A board packet shows gross margin, cash runway, and a hiring-plan variance. The numbers may be right. The problem is that nobody can tell which export, version, period, entity, and transformation produced them.

The failure is not that AI was used. The failure is that preparation crossed into judgment without evidence, ownership, or a gate. Mycroft's finance rule is simple: automate the preparation layer, preserve the accountable layer.

## Capability Statement

After this chapter, you will be able to state what counts as finance evidence in Mycroft.

**Assessment artifact:** Provenance note.

## Why This Matters for the Reader's Role

Entry- and mid-level finance practitioners spend much of their time gathering data, checking records, comparing periods, building reports, and preparing review surfaces. BLS role descriptions for financial analysts, accountants/auditors, and budget analysts all emphasize data review, financial statement review, budget monitoring, record inspection, and reporting. The opportunity is to make that preparation work more reliable without pretending the recipe can perform the professional judgment.

## The Recipe Concept

Define source, period, entity, version, owner, freshness, schema, control total, transformation, log, report, and approval record. A generated paragraph is an artifact, not evidence.

The useful recipe is narrow, source-bound, and reviewable. It produces a machine-readable log for reproducibility and a human-readable report for decision support. It stops before accounting treatment, payment action, public disclosure, filing, investor communication, or release.

## Agentic Supervision Lens

AI can trace file paths, compare schemas, and identify missing fields. Humans decide whether the evidence is adequate for the decision.

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

- Every report number traces to a source
- stale or missing versions are flagged
- control totals are checked where applicable.

Machine conformance checks whether the file parses and the required fields exist. Human adequacy checks whether the work is good enough for the finance decision it supports.

## Human-Only Judgment Boundary

AI cannot make a weak source adequate by summarizing it fluently.

That boundary is the phase gate. The recipe prepares the work surface on one side. The accountable finance human crosses it.

## Bridge to Next Chapter

Once data has a contract, recipes must serve both the executing agent and the finance reviewer.

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
- `pantry/03-the-verified-finance-data-contract_notes.md`
