# Research Notes: Chapter 04 - Two Customers

**Source:** TIKTOC.md chapter entry
**Notes file:** 04-two-customers_notes.md
**Corresponding chapter:** chapters/04-two-customers.md (not yet written)
**Generated:** 2026-06-14

---

## Chapter summary (from TIKTOC.md)

Understand recipes as both agent contracts and finance reviewer cards. The agent needs executable structure; the finance human needs purpose, evidence, caveats, gates, and decisions.

---

## A. Conceptual foundations

### Agent log versus human report

This concept matters because finance workflows become risky when preparation work and judgment work are blended together. In a Mycroft recipe, the agent can gather, compare, normalize, match, flag, and draft. The finance human decides adequacy, materiality, interpretation, accounting treatment, release, and action.

**Common misconception:** Learners often treat a clean table or fluent explanation as evidence that the underlying finance work is complete. The correct move is to ask what source, period, version, owner, control total, and approval record supports it.

**Worked example:** Use a small source table with one missing period, one stale version, one unexplained variance, and one approval-needed action. The recipe should surface the issues and stop before any human-only decision.

**Source(s):** TIKTOC.md; MYCROFT.md; DOMAIN.md; DATA_CONTRACT.md; docs/recipes.md; docs/phase-gates.md; docs/data-and-provenance.md; reports/generated/entry-mid-finance-recipes-research.md

### Recipe intent versus run truth

This concept matters because finance workflows become risky when preparation work and judgment work are blended together. In a Mycroft recipe, the agent can gather, compare, normalize, match, flag, and draft. The finance human decides adequacy, materiality, interpretation, accounting treatment, release, and action.

**Common misconception:** Learners often treat a clean table or fluent explanation as evidence that the underlying finance work is complete. The correct move is to ask what source, period, version, owner, control total, and approval record supports it.

**Worked example:** Use a small source table with one missing period, one stale version, one unexplained variance, and one approval-needed action. The recipe should surface the issues and stop before any human-only decision.

**Source(s):** TIKTOC.md; MYCROFT.md; DOMAIN.md; DATA_CONTRACT.md; docs/recipes.md; docs/phase-gates.md; docs/data-and-provenance.md; reports/generated/entry-mid-finance-recipes-research.md

### Machine conformance versus human adequacy

This concept matters because finance workflows become risky when preparation work and judgment work are blended together. In a Mycroft recipe, the agent can gather, compare, normalize, match, flag, and draft. The finance human decides adequacy, materiality, interpretation, accounting treatment, release, and action.

**Common misconception:** Learners often treat a clean table or fluent explanation as evidence that the underlying finance work is complete. The correct move is to ask what source, period, version, owner, control total, and approval record supports it.

**Worked example:** Use a small source table with one missing period, one stale version, one unexplained variance, and one approval-needed action. The recipe should surface the issues and stop before any human-only decision.

**Source(s):** TIKTOC.md; MYCROFT.md; DOMAIN.md; DATA_CONTRACT.md; docs/recipes.md; docs/phase-gates.md; docs/data-and-provenance.md; reports/generated/entry-mid-finance-recipes-research.md

### Maintainability for the next reviewer

This concept matters because finance workflows become risky when preparation work and judgment work are blended together. In a Mycroft recipe, the agent can gather, compare, normalize, match, flag, and draft. The finance human decides adequacy, materiality, interpretation, accounting treatment, release, and action.

**Common misconception:** Learners often treat a clean table or fluent explanation as evidence that the underlying finance work is complete. The correct move is to ask what source, period, version, owner, control total, and approval record supports it.

**Worked example:** Use a small source table with one missing period, one stale version, one unexplained variance, and one approval-needed action. The recipe should surface the issues and stop before any human-only decision.

**Source(s):** TIKTOC.md; MYCROFT.md; DOMAIN.md; DATA_CONTRACT.md; docs/recipes.md; docs/phase-gates.md; docs/data-and-provenance.md; reports/generated/entry-mid-finance-recipes-research.md


---

## B. Domain examples and cases

### Case 1: JSON variance log that is unusable by the CFO

The case should be written as a realistic finance work scenario. Show the source files, the check performed, the exception or gap surfaced, and the human gate that prevents the recipe from overstepping. The key teaching point is that the recipe makes review easier; it does not perform the accountable judgment.

**Source(s):** TIKTOC.md; reports/generated/entry-mid-finance-recipes-research.md; reports/generated/mycroft-finance-recipe-opportunities-attached-research.md

### Case 2: Pretty memo that cannot be rerun

The case should be written as a realistic finance work scenario. Show the source files, the check performed, the exception or gap surfaced, and the human gate that prevents the recipe from overstepping. The key teaching point is that the recipe makes review easier; it does not perform the accountable judgment.

**Source(s):** TIKTOC.md; reports/generated/entry-mid-finance-recipes-research.md; reports/generated/mycroft-finance-recipe-opportunities-attached-research.md

### Case 3: Recipe card with both schema and reviewer decision fields

The case should be written as a realistic finance work scenario. Show the source files, the check performed, the exception or gap surfaced, and the human gate that prevents the recipe from overstepping. The key teaching point is that the recipe makes review easier; it does not perform the accountable judgment.

**Source(s):** TIKTOC.md; reports/generated/entry-mid-finance-recipes-research.md; reports/generated/mycroft-finance-recipe-opportunities-attached-research.md


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

- Two Customers unlocks later recipes by giving the reader a concrete artifact pattern they can reuse.
- It teaches a reusable distinction between verified findings, inferred findings, unsupported claims, and human-only decisions.
- It contributes to the final honest run in Chapter 16.

**Adjacent chapter connections:**

- Chapter 3: supplies the prerequisite frame or artifact that this chapter builds on.
- Chapter 5: uses this chapter's evidence boundary, recipe pattern, or output surface.

---

## D. Current state of the field

**Settled:**

- Finance workflows need reproducibility and human-readable decision surfaces.
- Finance workflows require evidence provenance, completeness checks, and review gates.
- Occupational baselines from BLS place analysts, accountants, auditors, and budget analysts in data review, record inspection, budget monitoring, and reporting workflows.

**Contested or emerging:**

- How much detail belongs in the report versus the log depends on audience and audit needs.
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

- Annotate one Mycroft recipe for agent customer fields and human customer fields.
- Ask the reader to mark every row as verified, inferred, unsupported, or human-only.
- Ask the reader to write one stop condition that would block the run and one gate record that would clear it.

---

## Shared library files copied to pantry

- pantry/_lib_ai-gigo.md
- pantry/_lib_ai-nbb-prompt-architecture-the-power-of-the-template-pattern.md
- pantry/_lib_ai-prediction-machines-the-simple-economics-of-artificial-intelligence.md
- pantry/_lib_business-data-ism-the-revolution-transforming-decision-making-consumer-behavior-and-al.md
- pantry/_lib_finance-advances-in-financial-machine-learning.md
- pantry/_lib_math-data-harness-your-numbers-to-go-from-uncertain-to-unstoppable.md
- pantry/_lib_math-how-to-lie-with-statistics.md
- pantry/_lib_math-how-to-measure-anything-finding-the-value-of-intangibles-in-business.md
