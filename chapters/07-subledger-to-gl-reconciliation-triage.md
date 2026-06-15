# Chapter 7 — Subledger-to-GL Reconciliation Triage
*How to surface what doesn't match — and why surfacing it is not the same as fixing it.*

The AR subledger is off from the GL control account by $47,000.

That sentence lands differently depending on where you sit. To the system, it is a number: two tables were compared, a subtraction was performed, the result was not zero. To the accountant, it is a question with several possible answers: a timing difference that will clear on its own, a mapping error that requires a journal entry, a duplicate transaction that needs to be voided, missing support for an item that should have been there, or something genuinely unexplained that needs to go up the chain. Each of those answers implies a different action, a different owner, and a different level of urgency.

The system can tell you the $47,000 exists. It cannot tell you which answer applies.

This is the central fact about reconciliation work: the hard part is not finding the gap. Given clean source data and a deterministic matching algorithm, finding the gap is a solved problem. The hard part is classifying what the gap means, and that classification is accounting judgment. It requires someone who understands the chart of accounts, knows how the business processes transactions, can read supporting documentation, and carries accountability for the conclusion.

What AI-assisted reconciliation does well is build the queue that makes that judgment possible. What it must not do is substitute for the judgment itself.

---

## What a Subledger Reconciliation Is Actually Doing

The general ledger is the authoritative record. Every balance in the financial statements flows from it. But the GL does not record transactions at the detail level where they originate — that is what subledgers are for. The accounts receivable subledger holds the individual customer invoices, payments, credits, and adjustments. The GL holds the control account: a single balance that is supposed to equal the sum of all the open items in the AR subledger.

When they match, the GL is grounded. When they don't, one of three things has happened: a transaction was posted to one and not the other, a transaction was posted to both but with different amounts, or a transaction was posted to both with the same amount but in the wrong period or to the wrong account.

The reconciliation process is the systematic search for which of those things happened. It is not a complicated concept. The execution is where it gets difficult, because real AR subledgers contain hundreds or thousands of open items, transactions cross period boundaries in ways that are legitimate but look wrong if you don't know the business cycle, and the same transaction can appear under slightly different identifiers in different systems because of how data gets imported.

This is exactly the kind of work where automation adds value: matching at scale, applying consistent rules, flagging exceptions without tiring. And it is exactly the kind of work where the output requires a human before it becomes actionable, because the exception classifications are hypotheses until an accountant confirms them.

<!-- → [DIAGRAM: Flow showing AR subledger (individual invoices, payments, credits, adjustments) and GL control account (single balance) with a reconciliation process in the middle. The reconciliation produces two outputs: "Matched items — clear" and "Exception queue — requires accountant judgment." The GL control account has a note: "Should equal sum of all open subledger items." Caption: The subledger holds the detail. The GL holds the summary. The reconciliation finds where they diverge.] -->

---

## The Source Verification Problem

Before any matching begins, there is a step that is easy to skip and expensive to skip: verifying that the source extracts are right.

This is not paranoia. Subledger exports have period-boundary problems that are more common than most practitioners realize. An AR aging export pulled at 5:00 PM on the last day of the month does not necessarily contain all transactions that posted that day — depending on how the system batches, some late postings may appear in the next morning's extract instead. A GL trial balance export may use a different period-end convention than the subledger export, producing a mismatch that is entirely an artifact of the extraction timing rather than an actual difference in the records.

The recipe has to check four things before it touches the data. First, the source files: what system did each extract come from, what version of the export, what timestamp? Second, period coverage: do both extracts cover exactly the same date range? Third, control totals: does the AR subledger total in the export match the AR subledger total reported by the system it came from? Does the GL control account balance in the export match the GL trial balance? If the exports don't agree with their own source systems, the reconciliation will find differences that aren't real and miss differences that are.

Fourth, and often forgotten: are there duplicate transaction IDs in the subledger export? Duplicate IDs are a known failure mode in systems that import from multiple sources or that have had data migrations. A single transaction appearing twice in the subledger will produce a phantom difference in the reconciliation — the match will fail not because the records disagree but because one side has been double-counted. The recipe should halt if duplicates are found and require human review before continuing.

Stop conditions matter here more than in most finance workflows. A reconciliation that proceeds on bad source data produces an exception queue that looks real and isn't. The accountant spends time chasing differences that were artifacts of the extract, not actual breaks in the records. Worse, a clean exception queue built on bad data can give false assurance — the reconciliation "cleared" because the errors canceled each other out, not because the records were actually in agreement.

<!-- → [TABLE: Four-row table. Columns: Verification Check, What It Catches, Stop Condition if Failed. Rows: Source file identity (system, version, timestamp — catches wrong-version extracts — halt, re-pull from system), Period coverage match (same date range on both sides — catches period-boundary artifacts — halt, confirm period convention with controller), Control totals (export matches source system totals — catches truncated or partial exports — halt, reconcile export to system before proceeding), Duplicate transaction IDs (double-counted transactions in subledger — catches data migration artifacts — halt, require human review). Caption: Source verification is not optional setup. It is the first gate in the reconciliation recipe.] -->

---

## Matching: Deterministic Before Fuzzy

Once the sources are verified, the matching step has a rule that is easy to state and important to follow: deterministic matching before fuzzy matching, always.

Deterministic matching means: match on exact transaction ID, exact amount, exact period. Two records are a match if and only if they agree on all three. This sounds strict, and it is. The strictness is a feature. Every item that clears a deterministic match is a confirmed reconciled item — no judgment required, no ambiguity, fully traceable. The matched population is solid ground.

What remains after deterministic matching is the exception population: items that did not find a match on exact criteria. This is where fuzzy matching enters, and where the recipe has to be careful about what it is doing.

Fuzzy matching means relaxing one or more of the matching criteria to look for near-matches: same transaction ID but slightly different amount (possible timing or rounding difference), same amount but different period (possible cutoff difference), similar but not identical IDs (possible system import artifact). Fuzzy matching is useful for generating hypotheses about what each exception might be. It is not useful for confirming those hypotheses.

The output of fuzzy matching is a suggested classification, not a confirmed one. "This item looks like a timing difference based on the date proximity and amount match" is a useful starting point for the accountant. It is not accounting treatment. The accountant may look at the item, check the supporting documentation, and confirm it is indeed a timing difference that will clear in the next period. Or they may find that what looked like a timing difference is actually a payment applied to the wrong invoice — a different problem with a different fix.

The recipe should make this distinction explicit in the exception queue. Each item gets: the unmatched record from the subledger, the unmatched record from the GL (if any), the deterministic match result (no match found), the fuzzy match suggestion (if applicable), the suggested exception class, and the status: unreviewed. The accountant's job is to change that status to confirmed or reclassified, with a note. Until that happens, the exception is a hypothesis.

<!-- → [DIAGRAM: Two-stage funnel. Stage 1 "Deterministic matching" — all items in, matched items exit as "Cleared — no judgment needed." Remaining items pass to Stage 2 "Fuzzy matching" — produces "Suggested classification" for each item, labeled explicitly as hypothesis. Exception queue output shows items with status "Unreviewed." Arrow from exception queue to "Accountant review" with label "Confirmation required before status changes." Caption: Deterministic matching produces certainty. Fuzzy matching produces hypotheses. The accountant converts hypotheses into conclusions.] -->

---

## The Exception Classifications

The exception queue organizes unmatched items into five classes. The classes are mutually exclusive by design — each item gets one primary classification — and they map to different actions and different levels of urgency.

**Timing differences** are items that appear in one system before they appear in the other because of how the business processes and posts transactions. A payment received on the last day of the month may post to the bank and the subledger before the GL journal entry runs. A timing difference is expected to clear in the next period without a correcting entry. It is the lowest-urgency exception class, but it still requires confirmation — the accountant needs to verify that the timing explanation is plausible and that the item does clear in the subsequent period rather than aging indefinitely.

**Mapping errors** are items that posted to the wrong account. A transaction that should have hit the AR control account hit a different GL account instead, or an item in the subledger was associated with the wrong entity. Mapping errors require a correcting journal entry. They are not self-correcting.

**Duplicates** are transactions that appear more than once on one side. A payment posted twice in the subledger, an invoice imported twice from a sales system. Duplicates need to be voided or reversed. They are relatively easy to identify but require care — voiding the wrong transaction can create a new problem.

**Missing support** means the transaction exists in one or both systems but the underlying documentation — invoice, contract, approval — cannot be located. Missing support is not an accounting error, but it is a control finding. An item without support cannot be confirmed as a valid transaction.

**Unexplained** is the residual category: items that don't fit the other four classes after review. An unexplained material difference is an escalation. It goes to the controller with full documentation of what was checked and what was not resolved.

<!-- → [TABLE: Five-row table. Columns: Exception Class, What It Means, Expected Resolution, Urgency. Rows: Timing difference (posts to one system before other — clears in next period, no entry — low, confirm it clears), Mapping error (posted to wrong account — correcting journal entry — medium, requires entry before close), Duplicate (posted more than once — void or reverse — medium, confirm which posting is correct), Missing support (transaction without documentation — locate or escalate to controller — medium-high, control finding), Unexplained (does not fit other classes — escalate with full documentation — high, material items escalate immediately). Caption: The five exception classes map to five different actions. The classification is a hypothesis; the accountant confirms.] -->

---

## Aging the Queue and Carrying Forward

A reconciliation exception that was open last month and is still open this month is not the same as a new exception. It is an aged item, and aged items are a different kind of finding.

Timing differences are supposed to clear in one period. If a timing difference is still open after two periods, it is no longer a timing difference — something else is happening. Mapping errors and duplicates should clear within one close cycle; if they haven't, the correcting entries were not made. Missing support items that stay open become audit findings.

The recipe should carry forward prior-period open items and display their age in the current exception queue. An item that has been open for three periods should look different in the queue than an item that is new this period. The aging is not a judgment — it is a fact about how long the item has been unresolved. The judgment is why it is still open, and what needs to happen to close it.

The carry-forward also catches a failure mode that is more common than it should be: the "cleared by aging out" problem, where an item disappears from the queue not because it was resolved but because the reconciliation was re-run with a shorter lookback window. If the recipe always carries forward open items from prior periods, items cannot silently disappear from the queue without a resolution record.

<!-- → [TABLE: Aging schedule example. Columns: Item ID, Description, Original Period, Periods Open, Current Class, Status. Example rows showing items aging from 1 period (new timing difference, unreviewed) to 3+ periods (escalated unexplained item, requires controller sign-off before close). Caption: Aged items are a different kind of finding. A timing difference that has been open for three periods is not a timing difference.] -->

---

## The Exception Queue as Review Surface

Everything the recipe produces — the verified sources, the deterministic match results, the fuzzy suggestions, the exception classifications, the aging — feeds into a single artifact: the exception queue.

The exception queue is a review surface, not a conclusion. It is designed to make the accountant's review faster and more systematic, not to replace it. Every item in the queue has a status of "unreviewed" when it arrives. The accountant works through the queue, confirms or reclassifies each item, notes the basis for the classification, and marks the gate: this queue has been reviewed, the open items are at these aging levels, material unexplained differences have been escalated, and I am confirming that the reconciliation is adequate for the close.

The gate confirmation is the moment when the preparation work becomes accountable work. Before the gate, the queue is a set of hypotheses. After the gate, it is a signed-off workpaper. The accountant's signature on the gate is not a formality — it is the point where someone who carries accountability for the conclusion has looked at the evidence and decided it is sufficient.

The recipe cannot open that gate. The recipe cannot decide whether the evidence is sufficient. The recipe cannot accept a reconciling item or book an adjustment. All of those are human judgments that belong on the other side of the gate.

What the recipe can do — what it is built to do — is ensure that the accountant arrives at the gate with a well-organized, fully documented queue that makes the judgment as efficient and well-informed as possible. A good reconciliation recipe is not a substitute for accounting judgment. It is the infrastructure that makes accounting judgment faster, more consistent, and more defensible.

---

## What Would Change My Mind

If accounting systems maintained a continuous, system-level reconciliation between subledger and GL in real time — posting to both simultaneously and flagging any divergence at the transaction level the moment it occurs — the batch reconciliation process would change significantly. The exception queue would still exist, but it would be much smaller and the items in it would be much fresher. The classification work would be the same; the timing pressure would be lower. The human judgment requirement would not change at all, because the question of what an exception *means* and what to do about it is not a function of how quickly you find it.

## Still Puzzling

The five exception classes are designed to be mutually exclusive, and in most cases they are. But there are items that genuinely fit more than one class — a duplicate that also has missing support, a timing difference that upon review turns out to be a mapping error. The recipe assigns a primary class based on fuzzy matching signals, but the basis for that assignment is a heuristic, not a rule. How do you design the accountant review workflow so that the primary classification is treated as a starting point rather than a conclusion, without adding so much friction to the confirmation step that practitioners skip it?

---

## Exercises

**Warm-up**

1. *(Low difficulty)* Explain in plain terms why the control total verification step must happen before matching begins. What specific failure does it catch that matching alone would not catch? *What this tests: understanding of why source verification is a prerequisite, not a formality.*

2. *(Low difficulty)* Classify each of the following exceptions using the five-class framework: (a) a payment that posted to the subledger on March 31 but to the GL on April 2; (b) a $5,000 invoice that appears twice in the AR subledger with the same transaction ID; (c) an invoice in the subledger with no corresponding purchase order or contract on file. *What this tests: application of the five exception classes to realistic examples.*

3. *(Low difficulty)* A timing difference has been open in the exception queue for three consecutive periods. What does this tell you, and what action does it require? *What this tests: understanding of the aging function and why aged items are a different kind of finding.*

**Application**

4. *(Medium difficulty)* Design the stop condition logic for a subledger-to-GL reconciliation recipe. For each stop condition, specify: the condition that triggers it, what the recipe does when it fires, and who must act before the run can continue. *What this tests: ability to translate the source verification principles into operational recipe design.*

5. *(Medium difficulty)* An exception queue contains forty items after deterministic matching. Thirty-two have fuzzy match suggestions; eight have no suggestion. Walk through how you would structure the accountant's review workflow to confirm, reclassify, or escalate each item efficiently, without treating the fuzzy suggestions as pre-confirmed. *What this tests: application of the "suggestions are hypotheses" principle to a realistic review workflow.*

6. *(Medium difficulty)* The carry-forward requirement means prior-period open items must appear in the current exception queue. A colleague argues this adds noise to the queue and slows down the review. Make the case for carry-forward despite that friction, and explain what failure mode it prevents. *What this tests: understanding of why carry-forward is a control feature, not a documentation overhead.*

**Synthesis**

7. *(High difficulty)* You are designing a reconciliation recipe for a company that closes monthly across five entities, each with its own AR subledger feeding a consolidated GL. The entities use different ERP systems, and the subledger exports use different transaction ID formats. Design the recipe structure: source verification, matching logic, exception classification, aging, and gate. Identify where the two-customer design from Chapter 4 applies and how the agent contract and human report card would differ for this multi-entity scenario. *What this tests: integration of reconciliation design principles with the two-customer framework across a realistic multi-entity scenario.*

8. *(High difficulty)* The "unexplained" exception class is a residual — items that don't fit the other four categories after review. Evaluate the risk of a large unexplained population in the exception queue: what does it tell you about the quality of the matching logic, the exception classifications, or the underlying records? Design a protocol for investigating unexplained items that distinguishes between "the recipe couldn't classify it" and "no one can explain it." *What this tests: ability to evaluate exception queue quality as a signal about recipe design, not just record accuracy.*

**Challenge**

9. *(Advanced)* The "Still Puzzling" section identifies a real design tension: the five exception classes are mutually exclusive in the recipe, but real items sometimes fit more than one class, and the primary classification is a heuristic that practitioners may accept without reviewing. Design an accountant review workflow that treats the primary classification as a starting point, not a conclusion — including what the confirmation interface looks like, how reclassifications are logged, and how the recipe uses reclassification data over time to improve the fuzzy matching heuristics. Address explicitly how you prevent the confirmation step from becoming a rubber stamp while keeping the review efficient enough that practitioners don't bypass it. *What this tests: ability to close the loop between human review and recipe improvement — operationalizing the principle that classification suggestions are hypotheses, not outputs.*
