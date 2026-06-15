# Chapter 8 — Daily Cash Position and Liquidity Watch
*What a read-only view is for, and why read-only is the hard part.*

The bank feed is late. It was supposed to arrive at 7 a.m. and it is 8:45. The treasury team has a liquidity threshold review at 9:30, and the morning cash position — the thing that tells them whether they are above the minimum operating balance, whether the credit facility is untouched, whether the overnight sweep settled — is sitting in a system that has not updated.

A helpful automated system should do one thing in this situation: alert the team that the feed is late. It should not estimate the position from yesterday's data and proceed as if the number were current. It should not flag a threshold breach on stale information. It should not, under any circumstances, initiate a transfer or a sweep to preempt a breach that may not exist.

This distinction — alert, do not act — is the organizing principle of the daily cash position recipe. And the reason it needs to be stated plainly is that the line between "helpful preparation" and "unauthorized action" is exactly where agentic systems go wrong in treasury work. Cash is not a reporting artifact. Cash moves. When a system crosses from observation into action, the consequences are immediate and sometimes irreversible.

---

## Why Cash Is Different

Most finance automation involves artifacts — reports, summaries, variance analyses, review surfaces. The thing that gets produced is a document. If the document is wrong, the damage is informational: a bad decision gets made, but there is usually time to catch it before the error becomes permanent.

Cash is different. A payment that goes out cannot be recalled with the same ease it was sent. A sweep that moves funds between accounts changes the position in a way that has downstream effects — on interest calculations, on covenant compliance, on the counterparty's records. A borrow against a credit facility triggers fees and covenants. These are not reporting errors; they are operational events with real financial consequences.

This is why the treasury action boundary in this chapter is absolute. The recipe can see the cash position. It can compare balances to thresholds. It can flag breaches and escalate alerts. It cannot move money, cannot initiate a sweep, cannot trigger a borrow, cannot place or liquidate an investment. These actions belong to a named treasury professional who is accountable for the decision and the outcome.

The question is not whether the recipe could be designed to initiate those actions — it obviously could. The question is whether it should, and the answer in any well-governed treasury function is no, for the same reason that a well-designed alarm system rings a bell rather than calling the fire department and authorizing a controlled burn.

<!-- → [DIAGRAM: Two-zone layout — left zone labeled "Recipe scope" containing: bank feed ingestion, balance normalization, availability bucketing, threshold comparison, breach flagging, escalation alert; right zone labeled "Treasury action boundary" containing: payment initiation, account sweeps, credit facility draws, investment placement or liquidation, wire transfers; a hard vertical line separating the two zones labeled "hard boundary — recipe stops here"] -->

---

## The Five Steps of the Cash Position Recipe

The recipe for a daily cash position watch has five steps, and each one has a specific failure mode worth understanding before you design the workflow.

**Step one: validate bank-feed freshness.** Before anything else, the recipe checks whether the feed is current. This means comparing the feed's as-of timestamp to the expected delivery time for each account and each bank. If the feed is late, the recipe stops and alerts. If the feed arrived but covers a different period than expected — yesterday's closing balance delivered as today's opening, which happens more often than it should — the recipe flags the mismatch rather than proceeding on stale data.

The failure mode here is accepting a feed without checking its timestamp. A balance that parses cleanly and reconciles to yesterday's position is not a current balance. Using it as if it were produces a cash position report that looks right and is wrong in a way that will not become apparent until a threshold breach occurs that the report did not show.

**Step two: normalize balances by account, entity, and currency.** A treasury function with multiple legal entities, multiple banks, and multiple currencies has feeds arriving in different formats, with different account numbering conventions, in different denominations. Normalization converts all of these into a consistent structure: one row per account, with entity identifier, account type, currency, local-currency balance, and functional-currency equivalent using the period's designated exchange rate.

The failure mode here is normalization that silently drops accounts. If the recipe does not recognize an account number — because it was opened recently, because the numbering convention changed, because a new entity was onboarded — it should flag the unknown account rather than excluding it. A cash position that omits an account is not a partial cash position; it is an incorrect one.

<!-- → [TABLE: Cash position normalization structure — column headers: "Field", "Description", "Validation rule" — rows: Entity (legal entity identifier) must match master entity list; Account (bank account number) must match known account registry or flag as unknown; Account type (operating / restricted / investment / credit facility) must be classified or flagged; Currency (ISO code) must have designated rate or flag; Local balance (balance in account currency) must reconcile to bank statement; Functional equivalent (balance in reporting currency) must use designated rate with timestamp; As-of timestamp (feed delivery time) must match expected window or flag as late] -->

**Step three: bucket cash by availability.** Not all cash is the same. Operating account balances are available immediately. Restricted accounts — escrow, collateral, regulatory reserve — are not available for general use. Investment account balances may have same-day or next-day liquidity depending on the instrument. Credit facility availability depends on what is drawn versus what is committed. The cash position report should show each bucket separately, because the treasury decision about whether the position is adequate depends on which cash is actually accessible.

The failure mode here is aggregating all balances into a single total that looks healthy when the operational liquidity — the cash available for payments today — is below threshold. This is a presentation error, but it is one that produces bad decisions.

**Step four: compare to thresholds.** Each entity, each account type, and each currency may have a different minimum balance threshold — a floor below which the treasury team wants to be alerted. The recipe compares normalized, bucketed balances to these thresholds and flags any breach. Threshold breaches are never suppressed: if the data shows a breach, the alert goes out, even if the breach is expected (because a large payment was scheduled), even if it is temporary (because an incoming wire is in transit), even if the treasury team already knows about it.

The failure mode here is suppression logic — rules that say "if the breach is less than X or if it is expected to resolve by Y, do not alert." Suppression logic is a judgment call about materiality, and materiality calls belong to the treasury team, not the recipe. The recipe surfaces the fact. The team decides how to respond.

**Step five: escalate breaches.** When a breach is flagged, the recipe generates an alert to the designated treasury contact with enough information to act: which account, which entity, which threshold, what the current balance is, what the as-of timestamp is, and what the expected resolution time is if known. The alert is a preparation output. It is not a recommended action. It does not say "consider sweeping from account X" or "draw on the credit facility." It says "here is what the position shows and here is who needs to know."

<!-- → [DIAGRAM: Five-step pipeline — boxes in sequence: "1. Validate feed freshness (flag if late or stale)" → "2. Normalize by account / entity / currency (flag unknown accounts)" → "3. Bucket by availability (operating / restricted / investment / facility)" → "4. Compare to thresholds (flag breaches, never suppress)" → "5. Escalate to treasury team (information only, no recommended action)" — below the pipeline: "Recipe stops here. Treasury decides what happens next."] -->

---

## The Read-Only Discipline

I want to spend a moment on why "read-only" is a harder constraint to maintain than it sounds, because the pressure to cross it is real and the arguments for crossing it are often genuinely reasonable.

Here is the argument you will hear: the system can see that account X is below threshold, and it can see that account Y has excess cash, and a sweep from Y to X is the obvious action, and the sweep instruction is simple, and waiting for a human to do it introduces latency, and in treasury work latency has a cost. All of that is true. The sweep may well be the right action. The human treasury professional, when alerted, may take exactly that action within minutes.

The argument for staying read-only is not that the action is wrong. It is that the system cannot know whether the action is appropriate in the context it cannot see. The account Y balance may look like excess cash, but there may be a large payment scheduled against it that the recipe does not know about. The sweep may create a balance in account X that looks fine but triggers a covenant in a credit agreement the recipe has not read. The treasury professional may be in the process of renegotiating a bank relationship that makes a sweep right now, from this particular bank, strategically inadvisable.

These are not edge cases designed to justify an overcautious rule. They are the normal conditions of treasury work. The read-only boundary exists because the system's view of the cash position is always narrower than the treasury professional's view of the situation. The system sees the data. The professional sees the data in context.

This is the same principle that runs through every chapter in this book, but it has a specific urgency in treasury work because the consequences of acting on an incomplete view are immediate and financial. A report that is wrong gets corrected. A wire that goes out has to be recalled.

---

## What the Liquidity Watch Actually Shows

The assessment artifact for this chapter — the liquidity watch — is a structured output with a specific format. It is not a dashboard and it is not a summary; it is a read-only position statement with provenance on every number.

Each balance has an as-of timestamp. This is not optional. A balance without a timestamp is a number without a location in time, and a number without a location in time is not evidence — it is a figure. The timestamp connects the balance to the feed, and the feed connects the balance to the bank's record.

Unknown accounts are excluded or flagged. If the normalization step encounters an account it does not recognize, the watch shows the flag rather than silently omitting the balance. A treasury professional looking at the watch needs to know whether the position they are seeing covers all accounts or only the recognized ones.

Threshold breaches are never suppressed. Every breach that the data shows appears in the watch. The treasury team decides which breaches require action, which are expected, and which have already been addressed. The watch does not make that decision; it makes the facts available.

The watch also includes a freshness summary at the top: which feeds arrived on time, which are late, and which are missing entirely. A watch that covers twelve accounts but is missing two bank feeds is not a complete picture, and the person reading it needs to know that before they make any decisions based on it.

<!-- → [TABLE: Liquidity watch structure — section headers and fields: "Feed status" (account, expected time, actual time, status: current / late / missing); "Cash position" (entity, account, type, currency, local balance, functional equivalent, as-of time, vs. threshold, status: above / breach / unknown); "Threshold alerts" (entity, account, threshold, current balance, shortfall, as-of time, escalation sent); "Coverage notes" (accounts excluded, unknown accounts flagged, feeds missing)] -->

---

## The Supervision Questions in Treasury

The three supervision questions from Chapter 2 take a specific form in treasury work, and it is worth working through them explicitly because the stakes are higher here than in most finance contexts.

Scope defines what the recipe is allowed to touch. For a daily cash position watch, scope means: which entities, which accounts, which currencies, and which period. Scope also means what the recipe is not allowed to initiate — and in treasury work, this is more important than what it is allowed to read. A recipe scoped to read-only access on bank feeds is categorically different from a recipe with write access to payment systems. The technical access controls should enforce the scope; the workflow design should make the boundary visible.

Approval defines who clears the gate. For a cash position watch, the gate is not about whether the report gets released — it is about whether a threshold breach triggers a treasury action. The report goes to the treasury team automatically; that is the escalation. The action — the sweep, the draw, the payment — requires a named approver with the authority to make that call. The recipe surfaces the need; the approver decides the response.

Verification defines what makes a finding defensible. For a cash position, this is the chain from bank statement to normalized balance to bucketed position to threshold comparison. If someone asks tomorrow why a balance appeared as it did, the answer should be traceable: this balance came from this feed, delivered at this timestamp, normalized using this rate, compared to this threshold. The machine-readable log is what makes that chain reconstructible.

---

## What AI Cannot Decide

The boundary in this chapter is the clearest one in the book: AI cannot initiate transfers or decide funding actions. This is not a philosophical position; it is a governance requirement. In most jurisdictions and most organizational structures, payment authority is a delegated power with specific controls — dual approval, spending limits, segregation of duties. A recipe that initiates a payment, even a correct one, bypasses those controls.

There is a deeper reason that goes beyond compliance. Funding decisions in treasury work are not just about the current position; they are about the relationship between the current position and future obligations, counterparty relationships, market conditions, and strategic priorities that the recipe cannot see. A treasury professional deciding whether to draw on a credit facility is weighing the current balance shortfall against the cost of the draw, the signal it sends to the bank, the effect on covenants, and where the business is in its operating cycle. None of that is in the bank feed.

The recipe sees the water level. The treasury professional decides whether to open the valve.

---

## What Would Change My Mind

The absolute read-only boundary made sense when I wrote it, and I still think it is right for most organizations. But I can imagine a narrow exception worth thinking about.

There are treasury structures — large corporate treasury functions with sophisticated control environments — where pre-approved, rule-based sweeps are a normal part of operations. The sweep rule is defined in advance, approved at the policy level, logged automatically, and reviewed by the treasury team after the fact. In that context, the recipe executing the sweep is not bypassing controls; it is implementing a control that a human already set.

If someone showed me an organization where the pre-approved sweep rules are well-defined, the audit trail is complete, and the exceptions are reviewed and handled by treasury professionals, I would not argue that the recipe must stay read-only. I would argue that the recipe is implementing a human decision that was made in advance, which is a different thing from making a funding decision autonomously. The distinction is between executing a rule and exercising judgment. The former can be automated; the latter cannot.

---

## Still Puzzling

The threshold question is harder in treasury than in most finance contexts because liquidity thresholds are dynamic. An operating minimum that is appropriate in a normal month may be inadequate in a month with large scheduled payments, a debt maturity, or a seasonal cash trough. Static thresholds will produce false comfort in stressed periods and false alerts in flush ones.

I know the threshold should be calibrated to the entity's cash flow cycle and upcoming obligations. I do not have a clean rule for how the recipe should handle threshold updates — whether the treasury team updates them manually before each period, whether the recipe has access to a payment schedule that adjusts the threshold dynamically, or whether the threshold is always set conservatively and the team interprets the alerts in context. That design question connects to the data contract and the phase-gate structure, but I have not worked out the right answer.

---

## LLM Exercises

**Exercise 1.** Design the feed validation step for a cash position recipe that covers three banks and two currencies. Specify: what is the expected delivery window for each feed, what timestamp field the recipe checks, what happens when a feed is late, and what happens when a feed arrives but covers the wrong period. Ask the model to review your design and identify any cases where the validation would pass but the position would still be stale.

**Exercise 2.** Write a prompt that instructs an AI to produce a liquidity watch summary from a normalized cash position dataset. Specify that the output must include an as-of timestamp for every balance, flag any unknown accounts, and list all threshold breaches without suppression. Then write a second prompt that omits those specifications. Compare the outputs: what does the unconstrained model include or omit that the constrained model handles correctly?

**Exercise 3.** For one threshold breach scenario in your liquidity watch artifact, write the escalation alert that the recipe would generate. Specify: which account, which entity, which threshold, what the current balance is, what the as-of timestamp is. Then ask the model to add a recommended action to the alert. Review what it proposes, and write a one-paragraph explanation of why that recommendation should not be in the recipe output and what would need to be true for it to be appropriate.
