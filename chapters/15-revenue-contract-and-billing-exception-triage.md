# Chapter 15 — Revenue Contract and Billing Exception Triage
*Two kinds of wrong, and why mixing them makes both harder to fix.*

A contract amendment arrives in the middle of the quarter. Pricing has changed — a discount was renegotiated, a milestone was restructured, a product was swapped for a different SKU at a different rate. The amendment gets filed. The billing setup, somewhere in the sequence of handoffs between the deal team and the billing system, may or may not reflect the change.

Now there are two questions on the table, and they look similar but they are not.

The first question is factual: does the billing setup match what the amended contract says? This is a comparison problem. The contract specifies a price; the billing system has a price configured; either they agree or they do not. If they do not, something in the setup needs to be corrected before the next invoice runs.

The second question is interpretive: how should the revenue from this contract be recognized under the applicable accounting standard? This is an accounting question. ASC 606 governs when and how revenue is recognized for contracts with customers, and the answer depends on how you identify the performance obligations, how you allocate the transaction price among them, and when control transfers. Variable consideration, principal-versus-agent status, contract modifications — these are judgment calls that require a trained accountant reading the contract in light of the standard and the company's accounting policy.

The failure I want to start with is mixing these two questions together. When factual mismatches and accounting-policy questions land in the same queue, processed by the same review, both of them get handled worse. The factual mismatch — which could be resolved quickly by someone checking the contract against the billing configuration — waits while the accounting question gets escalated. The accounting question — which requires a policy interpretation — gets superficially resolved by someone who corrected the billing line and assumed the accounting treatment followed automatically. It does not always follow automatically.

The recipe in this chapter keeps the two questions separate from the moment it runs.

---

## The Contract Source Chain

Before you can check whether billing matches the contract, you need to know which version of the contract is authoritative. This sounds simple and is not.

A customer relationship of any complexity will have an original agreement, one or more amendments, possibly an order form or a statement of work that modifies pricing or scope, and sometimes a side letter or email exchange that was intended to constitute an agreement but was never formally executed. The billing setup may be tracking any of these, or a mixture of them, or a version that someone reconstructed from memory when the original file was unavailable.

The source chain is the ordered sequence of documents that constitutes the current contract: original agreement, then each amendment in chronological order, with each amendment superseding or supplementing the relevant provisions of what came before. The recipe starts here, not with the billing system.

Verifying the source chain means checking that every amendment is present, that the amendments are in the correct chronological order, that each amendment references the prior document it modifies, and that there are no gaps — no evidence of a missing amendment, no reference in a later document to a change that does not appear in the chain. A missing amendment stops the run. The recipe cannot compare billing setup to a contract it does not fully have.

<!-- → [DIAGRAM: Contract source chain — linear sequence showing: "Master agreement (v1, executed date)" → "Amendment 1 (date, references master)" → "Amendment 2 (date, references amendment 1)" → "Amendment 3 (date, references amendment 2)" → "Current billing configuration" — below the chain, a parallel track showing what the recipe checks at each link: "executed?", "references prior document?", "no gap?", "billing reflects this version?" — a stop signal after any missing link labeled "amendment gap: run stops here"] -->

This discipline matters because billing exceptions that look like simple mismatches are often downstream effects of a broken source chain. The billing system is configured to an older version of the contract because no one updated it after amendment two. Or the billing system was updated after amendment two but not after amendment three, which was a small pricing adjustment that seemed minor at the time. The source chain check surfaces this before the comparison runs, so the exception log reflects the real problem rather than a symptom of it.

---

## Normalizing the Contract Data

Once the source chain is verified, the recipe normalizes the contract terms into a structured format that can be compared field by field to the billing setup. This is the most technically demanding part of the recipe, because contracts are written for lawyers and billing systems are configured by operations teams, and the two representations of the same commercial arrangement can look very different.

Normalization extracts five categories of information from the contract chain.

**Dates.** Effective dates, term start and end, billing cycle start, any milestone dates that trigger a billing event. Contracts often have multiple date fields that interact in non-obvious ways — a term that started in one quarter but had a billing cycle that started in the next, a milestone date that was moved by amendment two but whose original date is still in the billing system.

**Products and services.** What the customer purchased, at what unit definition, and how each item maps to the billing system's product catalog. Product descriptions in contracts and product codes in billing systems are often maintained independently, which means a contract that says "Enterprise tier, unlimited users" and a billing system that says "SKU-4471, 500 seat license" might be the same thing or might not be, and the recipe needs a mapping table to resolve the ambiguity.

**Prices.** The contracted price for each product or service, net of any discounts, at each billing interval. Variable pricing — prices that change at specified dates, or that depend on usage, or that are subject to escalation clauses — needs to be represented in a way that the comparison can check against the configured billing rate at any given point in the billing cycle.

**Milestones.** Any performance obligations with specific delivery dates or completion events that trigger revenue recognition or billing. Milestone-based arrangements are where factual mismatches and accounting questions are most likely to collide, because a billing system that sends an invoice on a milestone date is making an implicit statement about when the performance obligation was satisfied — which is an accounting conclusion, not just a billing configuration.

**Modifications.** The specific changes made by each amendment, with the effective date of each change and the provisions superseded. This is what the recipe uses to check whether the billing configuration reflects the current version of the contract or an earlier one.

<!-- → [TABLE: Normalized contract data structure — column headers: "Field category", "Contract source", "Billing system field", "Comparison logic" — rows: Dates (effective date, term, billing cycle, milestones) vs. billing system configuration dates; "Match within one billing cycle or flag"; Products (description, tier, unit definition) vs. billing system SKU and product code; "Match via mapping table or flag as unmapped"; Prices (contracted rate, discount, escalation) vs. configured billing rate; "Match to current period rate or flag variance"; Milestones (delivery event, completion trigger) vs. billing event configuration; "Match event definition or flag for accounting review"; Modifications (amendment date, superseded provision) vs. last billing update date; "Amendment post-dates last billing update: flag"] -->

---

## The Two Exception Buckets

After normalization, the comparison runs and produces exceptions. This is where the separation between factual mismatches and accounting-policy questions happens, and it is the most important design decision in the recipe.

A factual mismatch is an exception where the billing configuration differs from the contract in a way that does not require an accounting interpretation to resolve. The contract says $4,200 per month; the billing system is configured at $4,000 per month. The contract has an effective date of March 1; the billing system has March 15. The contract specifies a specific SKU that was renamed in a product refresh, and the billing system still has the old name. These are setup errors. They do not require an accounting memo. They require someone to update the billing configuration to match the contract.

An accounting-policy question is an exception where the difference between the contract and the billing setup reflects a question about how the contract should be interpreted under the applicable standard. A contract modification that changes the scope and price of the arrangement — does it constitute a modification of the original contract or a new contract? A milestone payment — when was the performance obligation actually satisfied, and is the billing date the right date to recognize revenue? A discount that was granted for reasons related to a separate commercial relationship — is it a concession that reduces the transaction price, or is it a separate arrangement?

These are ASC 606 questions. The recipe flags them. It does not resolve them.

The practical test for which bucket an exception belongs in is this: can a billing operations team member resolve this by comparing the contract language to the billing setup, without making a judgment about accounting treatment? If yes, it is a factual mismatch. If the resolution requires an accounting interpretation, it is a policy question.

<!-- → [DIAGRAM: Exception triage — a funnel shape with two outputs; input at top labeled "All flagged exceptions from comparison"; two exit paths: left path "Factual mismatches" with examples (wrong price, wrong date, renamed SKU, missing amendment reflected in billing); right path "Accounting-policy questions" with examples (contract modification type, milestone timing, variable consideration, principal-versus-agent); below the left path: "Route to billing ops for correction"; below the right path: "Route to accounting team for policy memo"; between the two paths: "Triage rule: can billing ops resolve this without an accounting interpretation? Yes → left. No → right."] -->

---

## What the Exception Review Pack Contains

The assessment artifact for this chapter is the revenue and billing exception review pack — a structured output that presents the exceptions in a format that the two different reviewing teams can actually use.

The pack has two sections.

The factual mismatch section lists each exception with the contract source, the specific field where the mismatch was found, the contract value, the billing-system value, the amendment that established the contract value, the effective date, and a one-line description of what needs to be corrected. Each item has a status: open, in progress, or resolved. No billing correction is initiated automatically; the pack is a review surface, not a change management system. The billing team receives the pack, makes the corrections, and updates the status.

The accounting-policy questions section lists each exception with the contract source, the specific question the exception raises, the relevant ASC 606 consideration (performance obligation identification, transaction price allocation, variable consideration, modification type, or principal-versus-agent), and a description of the facts that need to be analyzed. No accounting treatment is proposed in this section. The recipe cannot propose an accounting treatment, because the treatment depends on a policy interpretation that requires the accounting team's judgment. The pack presents the facts; the accounting memo presents the conclusion.

The pack also includes a source-chain summary at the top: which contracts were reviewed, which amendments were present and verified, which source chains had gaps that stopped the run. A clean exception pack covers a defined population with a verified source chain. An exception pack that ran on an incomplete source chain says so explicitly.

<!-- → [TABLE: Exception review pack structure — two-section layout; Section 1 "Factual mismatches" columns: Contract ID, Field, Contract value, Billing value, Amendment source, Effective date, Correction needed, Status; Section 2 "Accounting-policy questions" columns: Contract ID, Exception description, ASC 606 topic, Facts for analysis, Assigned to, Status; Header section: "Source-chain summary" showing Contract ID, Amendments verified, Gaps found, Run status (complete / stopped)] -->

---

## Unsupported Overrides and Missing Documents

Two exception types deserve specific attention because they are more serious than a configuration mismatch and need to be surfaced with more urgency.

An unsupported override is a billing configuration that differs from the contract and does not correspond to any amendment in the source chain. The billing system shows a price that is neither the original contract price nor any amended price — it is a number that appears to have been entered manually, without a documented authorization. This might be a legitimate adjustment that was made without a formal amendment, or it might be an error, or it might be something more serious. The recipe cannot tell which. What it can do is flag the override clearly, with the specific field, the configured value, the expected value from the contract, and a notation that no amendment supports the difference.

A missing document is an amendment referenced by a later document in the source chain that is not present in the contract folder. A contract that says "as amended by Amendment 3 dated October 15" when the folder contains only Amendments 1 and 2 has a gap. The recipe logs the missing document and stops the comparison for that contract. It does not try to reconstruct what Amendment 3 might have said. It does not use the billing configuration as a proxy for the missing amendment's content. It stops and flags.

Both of these — unsupported overrides and missing documents — are escalation items. They go to the contract owner and the accounting team simultaneously, because they represent situations where the normal preparation-plus-judgment workflow cannot proceed until the underlying documentation problem is resolved.

---

## What AI Cannot Determine

The human-only boundary in this chapter is specific and consequential: AI cannot determine revenue recognition, variable consideration, principal-versus-agent status, or final accounting memo conclusions.

Revenue recognition under ASC 606 is a five-step model, and each step requires judgment. Identifying the contract with a customer requires determining whether a legally enforceable arrangement exists — which can be ambiguous when pricing has been communicated verbally or when an amendment was not formally executed. Identifying performance obligations requires determining which promised goods and services are distinct — which depends on whether the customer can benefit from each on its own and whether the obligations are separately identifiable in context. Allocating the transaction price requires determining the standalone selling price for each obligation when the contract price is a bundle — which may not be directly observable. Recognizing revenue requires determining when control transfers — which for services depends on whether the customer simultaneously receives and consumes the benefits as the entity performs.

The recipe can check whether the billing date matches the contract milestone date. It cannot determine whether that milestone date corresponds to the point at which control transferred under the standard. The recipe can flag a discount that was not in the original contract. It cannot determine whether that discount represents variable consideration that should constrain the transaction price, or a modification that changes the contract terms, or a concession that reflects a separate commercial arrangement. These are accounting judgments that belong to a trained accountant with knowledge of the company's accounting policy, the facts of the specific contract, and the relevant guidance.

This boundary matters especially in the exception triage because the pressure to treat an accounting question as a factual question is real. A billing team member who sees a mismatch and knows the right number — because they talked to the sales rep, because they saw the email chain, because the correct price is obvious from context — may be tempted to correct the billing configuration and close the exception without routing it to accounting. Sometimes that is fine. Sometimes the billing correction is the easy part and the revenue recognition question is still open, and closing the exception without routing it means the accounting question never gets answered.

The triage bucket is the structural fix for this. If the exception is in the accounting-policy bucket, it cannot be closed by a billing correction alone.

---

## Building the Exception Review Pack

The exception review pack for this chapter should cover at least three contracts, with at least one factual mismatch and at least one accounting-policy question represented. For each contract, document the source chain, the normalized terms, the exceptions flagged, and the bucket each exception belongs in.

If the data is from a sanitized sample, label it as such. If the source chain for any contract is incomplete, flag it and explain what is missing. The value of the exercise is in practicing the triage discipline — distinguishing what can be corrected by operations from what requires an accounting interpretation — not in having a complete set of production data.

The verification checklist for this chapter: missing amendments stop the run, not just flag it. Factual mismatches and accounting-review items are in separate sections of the pack, not interleaved. No billing correction is initiated automatically from the pack; it is a review surface.

Machine conformance checks whether the pack parses and the required sections exist. Human adequacy checks whether the triage is correct — whether the items in the factual mismatch bucket actually can be resolved without an accounting interpretation, and whether the items in the accounting-policy bucket have enough factual description that the accounting team can analyze them without going back to the original documents.

---

## What Would Change My Mind

The triage boundary I have drawn — billing ops resolves factual mismatches, accounting resolves policy questions — is clean in principle and messier in practice. There are exceptions that have both a factual component and a policy component, and routing them to one bucket or the other means the other dimension gets less attention.

A contract modification that changes both the price and the scope, for instance, has a factual component (the new price and scope need to be reflected in the billing setup) and a policy component (does this modification create a new contract or modify the existing one, and how does the answer affect revenue recognition). Routing it to the factual bucket means the billing gets corrected but the accounting question may not get formally answered. Routing it to the policy bucket means the accounting team handles it but someone may not update the billing setup.

The practical answer is probably a third bucket — "both" — for exceptions that have both components, with routing to both teams simultaneously. I did not include that in the design here because it adds complexity, but if someone showed me a control environment where the dual-component exceptions were common enough to create systematic gaps, I would add it.

---

## Still Puzzling

The mapping problem between contract product descriptions and billing system SKUs is harder than it looks. The recipe needs a mapping table to resolve ambiguities, but mapping tables go stale — products get renamed, SKUs get retired, new offerings get introduced — and a stale mapping table produces false passes on exceptions that are actually mismatches.

I know the mapping table needs to be maintained and versioned, with a change log that shows when each mapping was added or modified. I have not worked out who owns that table in practice — whether it lives with the billing team, the contract management team, or finance — or how the recipe should behave when it encounters a product description that is not in the mapping table. Flag it as unmapped, which is conservative, or attempt a fuzzy match, which risks false resolution. The conservative answer is probably right for a first implementation, but it produces a lot of flags in environments where the naming conventions are inconsistent, and a lot of flags can cause the pack to lose credibility with the teams who review it.

---

## LLM Exercises

**Exercise 1.** Take a contract you have worked with — or construct a simplified version with an original agreement and one amendment. Write out the source chain, the key terms (price, product, effective date, any milestone), and the billing configuration as you know it. Ask the model to identify any mismatches between the contract and the billing setup, and to classify each mismatch as a factual mismatch or an accounting-policy question. Review the classifications: where does the model draw the line, and where do you disagree?

**Exercise 2.** Write a prompt that instructs an AI to produce an exception review pack for a contract with a modification — a change in scope and price that occurred mid-contract. Specify that the model must separately list factual mismatches and accounting-policy questions, and must not propose an accounting treatment for any policy question. Compare the output to a prompt that does not include that instruction. What does the unconstrained model assert about revenue recognition that the constrained model correctly holds for human review?

**Exercise 3.** For one accounting-policy question in your exception review pack, write the facts-for-analysis section that the accounting team would need to assess the revenue recognition treatment. Specify the ASC 606 consideration at issue, the relevant contract language, and the factual questions that need to be answered before the accounting judgment can be made. Then ask the model to draft a preliminary accounting memo conclusion for the same item. Review what it proposes, and write a one-paragraph explanation of why that conclusion belongs in a human accounting memo rather than in the exception review pack.
