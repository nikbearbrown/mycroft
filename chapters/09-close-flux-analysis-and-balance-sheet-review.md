# Chapter 9 — Close Flux Analysis and Balance-Sheet Review

*The dashboard says complete. That is not the same as ready.*

The close dashboard shows green across every task. Journals posted, reconciliations submitted, intercompany eliminations done. The status column reads "complete" on every line. The controller is about to sign off.

Then someone looks at the trial balance and notices that prepaid assets jumped by $1.2 million compared to last month. There is no support attached. No memo. No journal entry explanation. The account moved — sharply, in a direction that requires explanation — and the close process did not catch it because the close process was tracking task completion, not account adequacy.

This is the distinction at the center of the chapter: close status is not close adequacy. Status is whether the tasks were done. Adequacy is whether the books are ready to be released. A checklist can measure status. A flux review measures adequacy.

The recipe in this chapter computes flux, ranks movements, checks support coverage, and carries forward unresolved items. It cannot declare the books ready. Only the controller can do that — and only after reviewing what the recipe surfaced. The recipe's job is to make sure the controller is looking at the right things.

---

## What Flux Is and Why It Matters

Flux is the change in an account balance between two points in time — typically the current period's ending balance and the prior period's ending balance. It is arithmetic: ending balance minus beginning balance, expressed in dollars and as a percentage of the prior balance. The calculation is deterministic. Given two trial balances, there is exactly one correct flux for each account.

What flux measures is movement. An account that moved needs to be understood. An account that moved sharply needs support. An account that moved in an unexpected direction needs scrutiny. This is not because movement is bad — prepaid assets should move as prepayments are made and amortized. It is because unexplained movement is a signal that something happened and no one has yet accounted for it professionally.

The accountant's tool for this is the flux analysis. It sits between the trial balance and the controller's sign-off. It is the surface on which the question "does every material movement in the balance sheet have support?" gets answered. Before the recipe, this was manual work: someone pulled two trial balances, computed the deltas in a spreadsheet, sorted by magnitude, and started asking questions. The recipe does the computational part of that. The asking-questions part remains human.

<!-- → [DIAGRAM: Timeline showing close workflow — left to right: period end → journals posted, reconciliations submitted, intercompany done (close tasks complete → status: green) → trial balance extracted → flux analysis computed (material movements ranked, support checked) → gate: controller reviews (support adequate? unexplained items resolved?) → sign-off and release. The "status: green" and "gate: controller reviews" are visually distinct, with a gap between them labeled "adequacy gap." Caption: the dashboard measures task completion; the flux review measures account adequacy — these are not the same question.] -->

---

## Two Trial Balances

The recipe needs two trial balances: the current period and the prior period. Both have contracts.

The current trial balance is the period's recorded ending balances after all journals have posted. Not a preliminary pull during close — that balance changes as journals continue to post. The recipe should run after close tasks are complete, on the version of the trial balance that reflects all posted activity. The version identifier and extraction timestamp belong in the source contract.

The prior trial balance is the prior period's closing balance — the same version used for last period's flux review, if one was run. This matters more than it might seem. If the prior balance was restated — an adjustment was made to a prior period — and the recipe is comparing the current balance to the pre-restatement prior balance, the flux will be wrong. Not wrong in the arithmetic sense. Wrong in the analytical sense, because the movement it measures includes the restatement rather than just the current period's activity. The prior balance version needs to match the approved close of the prior period.

With two sourced, versioned, approved trial balances, the recipe computes. Every account gets a dollar flux and a percent flux. The dollar flux is the change in absolute terms. The percent flux is that change divided by the absolute value of the prior balance — which avoids the sign confusion that arises when balances cross zero. Both are logged for every account in the balance sheet.

<!-- → [TABLE: Source contracts for flux analysis — columns: input, source, version requirement, failure mode if wrong. Rows: current trial balance (close-complete GL extract, version + timestamp after all journals post, mid-close extract includes incomplete activity — flux overstates movement), prior trial balance (prior-period approved close, same version used for prior flux review, restated prior balance inflates flux with restatement — obscures current-period activity), threshold parameters (human-set materiality by account category, set before run, model-inferred thresholds may not reflect risk profile of this entity's balance sheet). Caption: flux is only meaningful if both inputs are the right version.] -->

---

## The Support Coverage Problem

Computing flux is fast. Checking whether support exists for every material movement is slower, and this is where most close review processes break down.

Support, in this context, means documentation that explains why an account moved. For a prepaid asset account, support might be the prepayment invoice and a schedule showing the amortization timeline. For an accrued liability, it might be the accrual memo and the supporting estimate. For a deferred revenue balance, it might be the contract and the revenue recognition schedule. The form of the support varies by account type. What does not vary is the requirement: every material movement in the balance sheet should have documentation that allows a reviewer to understand why the balance changed and whether the change is appropriate.

The recipe can check support coverage. It can look for whether a support file exists, whether it is attached to the account or the journal entry, whether the file has a current-period date. What it cannot do is evaluate whether the support is adequate — whether the invoice actually explains the movement, whether the accrual estimate is reasonable, whether the revenue recognition treatment is correct. That evaluation requires professional judgment about the specific facts of the specific transaction. It requires a human.

The recipe's output on support coverage is therefore binary: supported or unsupported. A material account movement with an attached, current-dated support file is flagged as supported — it still needs human review, but the surface is there. A material movement with no attached support, or with support from a prior period that has not been updated, is flagged as unsupported. Unsupported material movements stop the close review. They do not get carried past the gate by the recipe. They wait for human resolution.

<!-- → [DIAGRAM: Support coverage decision tree for a flagged account movement — starting node: material flux detected. Branch 1: support file exists, current-dated → flagged "supported, needs review." Branch 2: support file exists, prior-period dated → flagged "stale support, needs update." Branch 3: no support file → flagged "unsupported, blocks gate." All three branches flow to the human review gate. Only "supported, needs review" can exit to sign-off after review; the other two require additional human action before the gate can be cleared. Caption: the recipe routes; the controller decides.] -->

---

## Ranking, Carrying Forward, and the Residual Problem

Once flux is computed and support coverage is checked, the recipe produces a ranked list. The ranking is by absolute dollar flux, descending. The top of the list is where the controller's attention should go first. This is not a judgment about which movements matter — that is the controller's call — but a presentation of where the largest movements are so the reviewer is not hunting for them.

Carrying forward is what happens to unresolved items from prior periods. A balance sheet account that had unexplained movement last period, was flagged, and was never resolved does not disappear because a new close started. The recipe carries it forward on the current period's flux review, labeled with its age: flagged in period X, still unresolved. An item that has been unresolved for two periods requires more urgency than one flagged for the first time. The carryforward makes that aging visible.

The residual problem is the accounts that did not move. A balance sheet account with zero flux — the same balance as last period — could mean the account is stable and nothing happened. Or it could mean two offsetting entries were posted that cancel each other out in the net balance but represent real activity that should be understood. The recipe cannot distinguish these cases. It flags zero-flux accounts in categories where offsetting activity is common — intercompany balances, clearing accounts, suspense accounts — and leaves the resolution to the reviewer. A suspense account with a net-zero balance that hid $400,000 of offsetting entries is not a clean account. It requires explanation regardless of the flux number.

---

## Agentic Supervision in a Close Workflow

The three supervision questions apply here, and the close context gives each one a specific shape.

Scope: what period, entity, source, and action space is the agent operating in? Close flux analysis is entity-specific — a consolidated trial balance and a subsidiary trial balance are different documents with different account structures. A recipe scoped to the subsidiary should not silently expand to the consolidated balance. The period should be confirmed before the run, because trial balances exist for every period and pulling the wrong one produces plausible-looking but meaningless flux. The action space matters too: can the recipe write to the support file system, or only read and report? A recipe that can attach documents to accounts has a wider action space than one that only produces a report, and that wider space requires more explicit scope definition.

Approval: who clears the gate before the close is released? This is the controller — or the designated sign-off authority — who reviews the ranked flux list, evaluates the supported items, resolves the unsupported ones, and decides whether the books are adequate for release. The approval is not a review of the recipe's output in the abstract. It is a statement that this entity's balance sheet, for this period, is ready to go. That statement requires a named person, a defined scope of review, and a record.

Verification: what would make a flagged item defensible? For a material movement, the answer is specific: the support file exists, it is current-period, it explains the movement in terms that connect to the accounting treatment, and it was reviewed by someone with the standing to evaluate it. "The model confirmed the file exists" is not verification. "The controller reviewed the support and confirmed the accounting treatment is appropriate" is.

<!-- → [TABLE: Supervision questions in close context — columns: question, close-specific application, failure if unasked. Rows: scope (period confirmed, entity specific, action space limited to read-and-report — if unasked: recipe may pull wrong period or expand entity coverage silently), approval (named controller, sign-off authority, approval record dated to this close cycle — if unasked: release happens before gate, unresolved items travel forward), verification (support exists, current-period, treatment confirmed by reviewer with standing — if unasked: "supported" label on flux item does not mean support was evaluated). Caption: in a close workflow, the gate is the controller's sign-off — not the dashboard's green light.] -->

---

## What the Recipe Cannot Do

The recipe cannot declare the books ready. This is worth stating directly, because the recipe does a lot of things that resemble readiness assessment. It confirms the trial balance was extracted after close tasks completed. It checks support coverage. It flags unresolved items. It ranks movements by magnitude. It carries forward open items with their age. After all of that, it knows a great deal about the balance sheet's movement — and it still cannot say the books are ready.

The reason is what "ready" means. Ready is not a property of the data. It is a professional judgment about the adequacy of the evidence for the purposes of release, reporting, and the decisions that will be made on the basis of these numbers. That judgment requires understanding the entity's business — what happened in the period, what the unusual items represent, whether the movements make sense given the operating context. It requires knowing which movements are material in context, not just by dollar amount. It requires the professional standing to be accountable for the assessment.

None of that is in the trial balance. All of it is in the controller.

The recipe's job is to make the controller's review faster and more reliable — to ensure that no material unsupported movement escapes notice, that carryforward items are visible, that the ranking puts the largest movements at the top. What it does not do is make the judgment that should follow from that review. The close-complete status was never the gate. The controller's adequacy assessment is the gate.

---

## Building the Assessment Artifact

The close flux review pack is the assessment artifact for this chapter. Build it for a real balance sheet — your company's trial balance or a sanitized sample — and demonstrate the separation between what the recipe verified and what a human still needs to decide.

The pack should show its source contracts: current trial balance with version and extraction timestamp, prior trial balance with the same, period, entity, threshold parameters. It should show the ranked flux list, with dollar and percent movements for every material account. It should show the support coverage status for each flagged item — supported, stale, or unsupported. It should show carryforward items from prior periods with their age. It should show the zero-flux accounts in high-risk categories that warrant review despite the flat balance.

The pack should make visible what is still open. Unsupported items should be clearly labeled. Items requiring controller resolution before sign-off should be distinguished from items ready for review. The pack is a work surface, not a sign-off document. The controller uses it to conduct the review. The controller's sign-off is what converts the work surface into a released close.

If the data is thin — if the trial balance is incomplete, if support files are unavailable, if the prior period is not a clean comparison — the pack should say so. A flux review that honestly documents its gaps is more useful than one that produces a confident-looking output by papering over them. The gaps tell the controller what additional work is required before adequacy can be assessed.

---

The close dashboard said complete. That was true. Every task was checked off. Every reconciliation was submitted.

The prepaid asset account had $1.2 million of unsupported movement.

The recipe found it. The controller evaluated it. The books were not released until the support existed and had been reviewed.

That is the workflow. Not slower — more reliable. The dashboard was never the gate. It was always the controller.

---

## Exercises

**Warm-up**

1. *Difficulty: Low* — Explain the difference between close status and close adequacy. Give a concrete example of a balance sheet that is status-complete but not adequate, distinct from the prepaid asset example in the chapter.
*What this tests: understanding of the core distinction and ability to generate an independent instance of it.*

2. *Difficulty: Low* — A recipe uses the current period's trial balance and the prior period's trial balance to compute flux. The prior period's balance was restated after the original close. What goes wrong if the recipe uses the pre-restatement prior balance? Which field in the source contract catches this?
*What this tests: understanding of why version integrity matters specifically in the prior-balance input, not just the current one.*

3. *Difficulty: Low* — The recipe flags material account movements as supported, stale, or unsupported. Describe what each label means, and explain why the recipe treats all three as requiring human review rather than clearing "supported" items automatically.
*What this tests: understanding that support coverage is a necessary condition for the gate, not a sufficient one — human evaluation of the support is still required.*

**Application**

4. *Difficulty: Medium* — A suspense account shows zero flux between the current and prior period. A colleague says it can be skipped in the review because nothing changed. Using the chapter's argument about the residual problem, explain why this is wrong and describe what the recipe should do with zero-flux high-risk accounts.
*What this tests: application of the residual problem concept to a specific account type and ability to explain why net balance is not the same as account adequacy.*

5. *Difficulty: Medium* — Apply the three supervision questions to this scenario: a recipe runs a close flux analysis for a subsidiary, but the controller wants to use it for the consolidated entity. The consolidated trial balance has a different account structure and includes intercompany balances not present in the subsidiary file. Which supervision question catches this, and what scope parameter would prevent the error?
*What this tests: application of the scope question to an entity-mismatch failure and ability to write a specific corrective parameter.*

6. *Difficulty: Medium* — A carryforward item has been unresolved for three consecutive close cycles. It is a $90,000 movement in an accrued liabilities account with no support attached. Write the escalation language that should appear in the flux review pack, naming what the controller needs to do before sign-off and what the approval record should show.
*What this tests: application of the carryforward and gate concepts to a specific aging scenario, and ability to specify what "resolution" means concretely.*

**Synthesis**

7. *Difficulty: High* — A controller reviews a flux review pack and signs off on the close. Three weeks later, an auditor discovers that a deferred revenue account had $600,000 of unsupported movement that was not flagged in the pack. Investigation reveals that the account was below the materiality threshold used in the recipe. Using the three-layer evidence taxonomy, analyze what went wrong and at which layer. Was this a failure of verified evidence, model judgment, or human judgment — or some combination? What would need to change in the workflow to prevent recurrence?
*What this tests: ability to apply the taxonomy retrospectively to a failure, identify where the breakdown occurred, and propose a structural rather than symptomatic fix.*

8. *Difficulty: High* — Design a close flux workflow for a company that closes twelve subsidiaries and then consolidates. The workflow must handle: separate flux reviews for each subsidiary, a consolidated flux review that catches intercompany eliminations, carryforward tracking across the full close cycle, and a gate structure that allows subsidiary controllers to sign off independently before the corporate controller signs off on the consolidated close. Specify the source contracts, the gate sequence, and the two highest-risk points in the design.
*What this tests: integration of all chapter concepts into a multi-entity close workflow, with explicit gate sequencing and risk identification.*

**Challenge**

9. *Difficulty: Advanced* — The chapter argues that the recipe "cannot declare the books ready" because readiness is a professional judgment requiring knowledge the model does not have: the entity's operating context, the materiality of movements in context, and the standing to be accountable. A skeptic argues this is a temporary limitation — that a sufficiently trained model, given enough historical close data for the same entity, could in principle develop the contextual knowledge required to assess adequacy and that the "human judgment" boundary is a policy choice, not a logical necessity. Construct the strongest version of this argument. Then evaluate it against the chapter's claim: is the boundary a limitation of current models, or is there something about the accountability requirement that cannot be satisfied by a model regardless of its contextual knowledge? What would need to be true — about the model, the legal framework, and the professional standards — for the skeptic's argument to hold?
*What this tests: ability to engage with the chapter's deepest claim about the nature of professional judgment, reason from the accountability requirement rather than capability, and evaluate whether the boundary is contingent or structural.*
