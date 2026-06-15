# Chapter 12 — AP/AR Exception and Aging Workbench

*The system should prepare queues. It should not contact anyone or move any money.*

The AR aging report lands in the inbox every Monday. Ninety-three invoices, sorted by age. Seventeen are past ninety days. Four have dispute notes from last month. Three have no owner assigned. One customer appears twice under slightly different names — possibly the same account, possibly two different entities.

The AP report is similar. Two hundred eleven open invoices, sorted by vendor and due date. Eight pairs look like potential duplicates — same vendor, same amount, close dates, different invoice numbers. One of those pairs might be a legitimate two-part delivery. Seven might be errors waiting to happen.

Here is the question the system cannot answer: what should you do about any of it?

The system can sort, age, flag, and queue. It can identify which invoices are overdue, which have no owner, which share enough characteristics with another invoice to warrant a closer look. What it cannot do is decide whether a disputed invoice gets escalated or written off, whether a duplicate candidate is a genuine duplicate or a two-part shipment, whether the customer with two records is one account or two. Those decisions require talking to people, reviewing contracts, understanding relationships, and accepting accountability for the outcome. The system hands you a prepared workbench. The judgment is yours.

---

## What Aging Measures

An aging report is a snapshot. It shows the current balance of every open invoice or payable, classified by how long it has been outstanding. The buckets are conventional: current, one to thirty days past due, thirty-one to sixty, sixty-one to ninety, over ninety. Some organizations add more granularity; some use fewer buckets. The shape is consistent — it is a distribution of outstanding balances across time, anchored to the as-of date.

The as-of date is the first thing the recipe checks. An aging report generated with yesterday's as-of date and reviewed today is one day stale. An aging report generated with last week's as-of date and reviewed today has a week of cash receipts, new invoices, and payment activity that is not reflected. The as-of date is not a formatting detail. It determines whether the snapshot corresponds to reality closely enough to support the decisions that will be made from it.

The second thing the recipe checks is whether every invoice in the aging has an identifiable counterparty. An invoice with a missing or unrecognized vendor or customer name cannot be routed, cannot be communicated about, and cannot be resolved. It is an orphan in the system. Unknown counterparties above a materiality threshold stop the run — not because the recipe cannot process them arithmetically, but because any action taken on them requires a human to first establish what the counterparty actually is.

These two checks — as-of date and counterparty completeness — are not audits. They are the minimum verification that the aging is usable for its stated purpose. A report that passes both checks is ready for the workbench. A report that fails either one needs to be corrected before the workbench is built.

<!-- → [DIAGRAM: Aging bucket visualization — horizontal bar chart showing invoice balance distribution across five aging buckets (current, 1–30 days, 31–60 days, 61–90 days, 90+ days) for both AR and AP side by side. AR bars in one color, AP in another. Caption: the aging snapshot is only valid as of its date; the recipe confirms the as-of date before any downstream processing.] -->

---

## The Duplicate Candidate Problem

The AP side of this chapter has a specific structural challenge that deserves its own treatment: the duplicate candidate.

A duplicate payment is what happens when the same invoice is paid twice. It is a real problem — the Association of Certified Fraud Examiners estimates that billing schemes, which include duplicate payments, represent a significant share of occupational fraud by frequency. AP teams in organizations of any size run some form of duplicate detection. The question for this chapter is what the recipe does and does not do with what it finds.

The recipe finds candidates. An AP duplicate candidate is a pair of invoices that share enough matching attributes — same vendor, same amount, dates within a defined window, different invoice numbers — to be worth human review. The recipe identifies these pairs, flags them, and routes them to a review queue. It does not confirm them as duplicates. It does not place a hold on either invoice. It does not generate a communication to the vendor. It produces a queue of pairs that a human needs to evaluate.

This distinction — candidate versus confirmed — matters because the consequences of acting prematurely are real. Placing a payment hold on an invoice that turns out to be a legitimate two-part shipment delays a vendor payment, potentially damages a supplier relationship, and triggers a resolution process that costs more than the hold was worth. The recipe's job is to make sure no genuine duplicate escapes notice. The human's job is to evaluate each flagged pair against the purchase order, the delivery record, and the vendor's invoice documentation, and to decide whether a hold is warranted.

The verification standard for a duplicate candidate is specific: same vendor confirmed by master data match, same amount within tolerance, date window within the defined range, invoice numbers distinct. A pair that meets all four criteria is a strong candidate. A pair that meets three is a weaker one. The recipe should surface both, with the match strength visible, so the reviewer can prioritize.

<!-- → [TABLE: Duplicate candidate match criteria — columns: criterion, what the recipe checks, match strength weight, failure mode. Rows: vendor (master data match, not just name string — same string can match two vendors if master data is inconsistent), amount (exact match or within defined tolerance — tolerance too wide catches non-duplicates; too narrow misses rounding variants), date window (invoice dates within N days of each other — window definition is a human parameter, not model-inferred), invoice number (distinct numbers required — same number on two records is a different problem: a processing error, not a duplicate candidate). Caption: candidates are flagged by the recipe; only a human can confirm.] -->

---

## AR Exceptions: More Than Age

The AR workbench is not just an aging report with flags. It is a surface for managing the exceptions that age creates — and age is only one of several dimensions along which an invoice can become problematic.

**Disputes** are invoices where the customer has raised an objection to the amount, the delivery, or the terms. A disputed invoice should not be in the same queue as a clean past-due invoice. It requires a different action: review of the dispute record, communication with the customer, and a resolution decision that may involve a credit memo, a payment adjustment, or escalation. The recipe identifies invoices with dispute status attached, pulls the dispute record, and routes them to a separate queue. The dispute queue is not an aging queue. It is a resolution queue, and it requires a different kind of attention.

**Missing owners** are invoices with no assigned collections contact. An unowned invoice is an invoice that will not be collected, not because the customer will not pay but because no one is responsible for asking. The recipe flags unowned past-due invoices and routes them to a supervisor queue for assignment. Assignment is a human decision — it depends on portfolio structure, relationship history, and workload — but the system can make the unowned population visible so the assignment can happen.

**Counterparty anomalies** are invoices where the customer record is incomplete, inconsistent, or potentially duplicated in the customer master. A customer who appears twice under slightly different names — "Acme Corp" and "Acme Corporation" — may be one account split across two records, or may be two genuinely different entities. The recipe flags the pairing and routes it to a data quality queue. Resolution requires a human who can look at the contract, the billing address, the tax ID, and the relationship history to determine whether the records should be merged, kept separate, or escalated for further review.

<!-- → [DIAGRAM: AR exception routing — three input queues from the aging export: (1) past-due, no dispute, owner assigned → collections follow-up queue; (2) dispute status attached → dispute resolution queue; (3) no owner assigned → supervisor assignment queue. A fourth path: counterparty anomaly detected → data quality queue. All four queues flow to human action; none flow directly to customer communication. Caption: the workbench routes exceptions; humans decide what happens next.] -->

---

## The Action Boundary

The boundary in this chapter is unusually concrete, and it is worth stating plainly: the recipe does not send communications. It does not place payment holds. It does not release payments. It does not write off balances. It does not merge customer records.

Each of those actions has consequences that extend beyond the system. A collection email sent to a customer is a business communication. It affects a relationship. It may have legal implications if the invoice is disputed. It reflects on the organization. A payment hold placed on a vendor invoice delays cash out of the organization and signals to the vendor that something is wrong. A balance write-off affects the income statement and may require authorization under the organization's internal controls. A customer record merge changes the financial history of both records permanently.

None of these are preparation work. They are actions in the world, taken on behalf of the organization, with accountability attached. The recipe prepares the queues so the humans who take those actions have complete, accurate, prioritized information when they make the decision. That is the full scope of the recipe's authority.

A recipe that can send a collection email — even a well-drafted, professionally worded one — has crossed the line. Not because the email will necessarily be wrong. Because the decision to send it, the judgment about whether the relationship can tolerate a direct communication at this stage, the assessment of whether there is a dispute that should be resolved before contact is made — these belong to a person. The recipe can draft the email and place it in a review queue. Sending it requires a human to read it, evaluate it, and press send.

This is Mycroft's principle stated in the specific context of AP and AR: AI can classify and queue. Humans communicate with vendors and customers, approve holds, release payments, and write off balances. The queue is the boundary. Everything before the queue is preparation. Everything after it is judgment.

---

## Supervision in a Transactional Workflow

Transactional workflows — AP and AR processing — run at higher frequency than close or variance workflows. They may run daily or weekly rather than monthly. This changes the supervision stakes. An error in a close flux analysis affects one period. An error in an AP duplicate detection workflow that runs weekly can propagate across many weeks before it is caught.

The three supervision questions apply here with this frequency in mind.

Scope: what invoices, what entity, what date range, and what action space is the recipe operating in? For AP, the date range matters because the duplicate window is defined relative to the as-of date — a window that is too wide catches old invoices that are not actually related; a window that is too narrow misses near-term duplicates. For AR, the entity matters because customer master data is often entity-specific, and a multi-entity organization may have customers who transact with multiple subsidiaries under different records. The action space must be explicitly limited to queue preparation — no holds, no communications, no payment releases — and that limit should be enforced structurally, not by instruction.

Approval: who reviews the queues before action is taken? For AP duplicate candidates, this is the AP lead or controller who evaluates each pair against source documentation. For AR disputes, this is the collections manager or account owner. For unowned invoices, this is the supervisor who assigns the account. Each queue has a designated reviewer. The reviewer is accountable for the actions taken from their queue — not accountable for the classification the recipe produced, but accountable for the decision that follows from it.

Verification: what would make a flagged item defensible? For a duplicate candidate, the answer is: purchase order confirmation that only one delivery was authorized, vendor invoice documentation that shows two distinct invoices, and a reviewer who examined both and made a determination. "The recipe flagged it as a candidate" is not verification. The reviewer's documented evaluation is.

<!-- → [TABLE: Supervision questions in AP/AR context — columns: question, AP application, AR application. Rows: scope (invoice range, entity, duplicate window defined by human, action space limited to queue — entity coverage, as-of date confirmed, owner-assignment queue not auto-populated), approval (AP lead reviews duplicate candidates against PO and delivery docs — collections manager or account owner reviews dispute and past-due queues), verification (PO confirmation + vendor docs + reviewer determination for duplicates — dispute record + customer communication history + reviewer decision for AR exceptions). Caption: transactional frequency increases propagation risk — supervision questions must be answered before each run, not just at workflow setup.] -->

---

## Building the Assessment Artifact

The aging and exception workbench is the assessment artifact for this chapter. Build it for a real AP and AR dataset — your organization's current aging exports, or sanitized samples — and demonstrate that it produces queues without taking action.

The workbench should show its source contracts: AR aging export with as-of date and version, AP aging export with the same, entity, duplicate window parameters, materiality thresholds. It should show the AR queue structure: past-due collections queue, dispute resolution queue, unowned invoice queue, counterparty anomaly queue. It should show the AP queue structure: duplicate candidate queue with match strength, missing support queue, items pending owner review. Each queue should identify the designated reviewer and the action scope available to that reviewer.

The workbench should show what it did not do: no holds placed, no emails drafted for sending, no payments released, no records merged. The absence of action is part of the artifact. It demonstrates that the boundary held.

If the data is thin — if the aging exports are incomplete, if the counterparty master is not available for matching, if the duplicate window parameters have not been set — the workbench should name those gaps and describe what would be needed to close them. A workbench that honestly documents what it cannot yet do is more useful than one that produces confident-looking queues on inadequate inputs.

---

The AR report lands every Monday. Seventeen invoices past ninety days. Four disputes. Three without owners. One counterparty that might be two.

The recipe built the queues in minutes. It confirmed the as-of date. It flagged the unknown counterparty. It routed the disputes separately. It placed the unowned invoices in the supervisor queue.

Then it stopped.

What happens next — the calls, the holds, the decisions about relationships and write-offs and payment terms — belongs to the people whose names are on the queues. The system prepared the workbench. The work begins when a human picks it up.

---

## Exercises

**Warm-up**

1. *Difficulty: Low* — Name the two minimum verification checks the recipe performs on an aging export before building the workbench, and explain what fails downstream if either check is skipped.
*What this tests: understanding that as-of date and counterparty completeness are prerequisites for usability, not optional quality improvements.*

2. *Difficulty: Low* — A recipe identifies an AP invoice pair as a duplicate candidate. List the four match criteria it checks, and explain the difference between "candidate" and "confirmed duplicate." What does that distinction require from a human reviewer?
*What this tests: recall of the candidate criteria and understanding that confirmation requires source document review, not just algorithmic matching.*

3. *Difficulty: Low* — The chapter identifies four AR exception queues: collections follow-up, dispute resolution, supervisor assignment, and data quality. For each queue, name the type of exception it contains and the human role responsible for acting on it.
*What this tests: understanding of the queue routing logic and the accountability structure behind each queue.*

**Application**

4. *Difficulty: Medium* — A recipe is configured to draft and send collection emails to customers with invoices more than sixty days past due. Using the chapter's action boundary argument, explain specifically why this crosses the line — not just that it does, but what accountability the recipe cannot carry and what could go wrong that a human would have caught.
*What this tests: ability to apply the action boundary to a specific automated behavior and articulate the stakes, not just cite the rule.*

5. *Difficulty: Medium* — Apply the three supervision questions to this scenario: an AR workbench recipe runs weekly but the customer master was last updated three months ago. A customer was acquired by a competitor and the record was not updated. The recipe has been routing invoices to the original collections owner, who left the company two months ago. Which supervision question would have caught this, and what ongoing verification practice would prevent it recurring?
*What this tests: application of the supervision framework to a data-staleness failure in a high-frequency transactional workflow.*

6. *Difficulty: Medium* — An AP duplicate candidate pair has the following characteristics: same vendor (confirmed by master data match), same amount ($14,750), invoice dates nine days apart, different invoice numbers. The purchase order covers a two-part delivery with equal installments. Write the reviewer's determination note — what they need to examine, what they need to confirm, and what the outcome should be if the two-part delivery is verified.
*What this tests: ability to walk through the confirmation process for a specific candidate and produce a documented determination, not just identify that review is needed.*

**Synthesis**

7. *Difficulty: High* — A finance team decides to automate the dispute resolution queue: for disputes under $5,000, the recipe will generate a credit memo draft and route it to the customer for acceptance without human review of the underlying dispute record. Using the three-layer evidence taxonomy (verified evidence, model judgment, human judgment), evaluate this proposal. Which layer does the credit memo draft belong to, and what does the proposal require the recipe to do that it cannot do?
*What this tests: ability to apply the taxonomy to a specific automation proposal and identify the layer violation — the recipe is being asked to perform human judgment (evaluate the dispute, determine the appropriate resolution) not just model judgment (draft a communication).*

8. *Difficulty: High* — Design an AP/AR workbench for an organization with three business units, each with its own vendor and customer master, running separate AP and AR processes but consolidating for reporting. Specify: the source contracts for each business unit's aging exports, the duplicate detection strategy (should candidates be checked within each unit or across units?), the queue structure and reviewer assignments, the gate design, and the two points in the design where cross-unit data creates the highest risk of misclassification.
*What this tests: integration of all chapter concepts into a multi-entity transactional workflow, with explicit attention to the cross-unit matching problem and gate sequencing.*

**Challenge**

9. *Difficulty: Advanced* — The chapter states that "AI can classify and queue. Humans communicate with vendors and customers, approve holds, release payments, or write off balances." A fintech argument holds that this boundary is already obsolete: modern payment systems authorize and release payments algorithmically at scale, collections platforms send automated communications, and write-off rules are encoded in policy engines — all without human review of individual transactions. The chapter's boundary, the argument goes, describes a workflow that barely exists anymore. Construct the strongest version of this argument, drawing on what automated payment and collections systems actually do. Then evaluate it: does high-frequency algorithmic action eliminate the accountability requirement, or does it relocate it? If the boundary moves — from individual transaction review to policy design and exception escalation — does the chapter's core principle still hold, and in what form?
*What this tests: ability to engage with the most direct challenge to the chapter's premise, reason from what automated systems actually do rather than the chapter's assumptions, and determine whether the principle survives under changed conditions or requires reformulation.*
