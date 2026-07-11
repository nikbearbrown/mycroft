# Chapter 5: Verifying Finance Evidence

## Exercise 1

Source text (a period-end note): "Marketing spend was down sharply versus budget this month, which confirms the new campaign approval process is working. Impressions also indicate stronger efficiency per dollar, though we did not isolate channel mix from the total."

Verb-by-verb classification:

- "was down sharply versus budget" — **can say**. This is a direct read of the actuals-vs-budget comparison, which the note treats as reconciled.
- "confirms the new campaign approval process is working" — **cannot claim**, misclassified by the author as "can say." A lower spend number does not, by itself, establish that a process change caused it; the note gives no control for other explanations (a seasonal dip, a delayed invoice, a vendor pause). This is exactly the causal overreach the chapter warns about: correlation between two facts (spend down, process changed) dressed as confirmation.
- "indicate stronger efficiency" — **can suggest**, correctly hedged. The note already flags that channel mix wasn't isolated, so "indicate" is the right verb family here.
- "though we did not isolate channel mix" — this is the caveat that should sit next to the claim it qualifies, which it does; the one problem is that the same caveat doesn't get attached to the "confirms" sentence above it, where it's needed more.

Where I'd draw the line differently from a model that reads charitably: a model asked to classify in isolation might accept "confirms" at face value because the sentence is fluent and definite-sounding. The tell that it's actually "cannot claim" is asking what evidence a causal claim like that would require — a comparison against a control group, or at minimum against months where the process didn't change — and confirming that evidence isn't in the note.

## Exercise 2

Extract: a monthly accounts-payable aging file used for a payment-timing review.

Defined population: every open payable, across every entity and cost center, as of the close-of-business snapshot on the last calendar day of the month — not just the payables in the primary operating entity, and not just payables above a size threshold.

Completeness check: sum the aging file's total open balance by entity, and compare it to each entity's payables control total in the general ledger for the same date. A match within a small tolerance (rounding, in-transit items) passes; anything outside tolerance means either an entity was dropped from the extract or the extract ran against a different snapshot date than the GL close.

Recipe step:
```
1. Pull AP aging file, snapshot date = last calendar day of month, all entities.
2. Pull GL payables control balance, same date, same entity list.
3. Group aging file by entity, sum balances.
4. Compare each entity's summed balance to its GL control balance.
5. Flag any entity where the difference exceeds $500 or 0.1% of balance, whichever is larger.
6. Halt and report rather than proceed if any entity present in the GL control list is entirely absent from the aging file.
```

Where the model found the check could pass but the extract still be incomplete: the entity-level control total can tie exactly even if the aging file is missing individual invoices within an entity, as long as an offsetting error (a duplicate, a wrong sign) happens to cancel it out at the entity level. It also pointed out that a newly onboarded entity, not yet in the GL control list at all, would pass the check silently — the comparison only catches gaps between two files that both know an entity exists, not an entity missing from both.

## Exercise 3

Prompt used:
```
Draft a variance commentary for [account/period]. Use only warranted verbs —
distinguish explicitly between what the data confirms, what it suggests, and
what it cannot support. Flag any item where the evidence is insufficient for
a claim, using a "needs review" tag, rather than writing around the gap.
Do not use causal language ("caused," "resulted from," "because of") unless
the evidence includes a control or comparison that isolates the cause.
```

Comparison against an unconstrained prompt run on the same input:

The standard commentary used confident, uniform language throughout — "spend decreased because of the new approval process," "efficiency improved due to better targeting" — with no distinction between a reconciled fact and an inferred story. Every sentence read at the same confidence level, which made it impossible to tell, from the text alone, which claims were checked against a control total and which were the model's own explanation for a number it had never seen explained.

The constrained commentary split cleanly: it used "confirms" only for the two line items that tied to a control total in the input, "is consistent with" for the mix-shift explanation, and it added a "needs review" flag on a departmental line where the input variance data didn't include a stated reason at all — the unconstrained version had filled that gap with a plausible-sounding explanation instead of flagging it. The constrained version also declined the causal framing entirely, restating "spend decreased following the approval process change" instead of "because of," since the input didn't include anything that isolated the process change as the cause of the decrease.

What changed is the honesty of the confidence signal, not the underlying facts — same numbers, but the reader can now tell where to spend their attention, per the chapter's point about what warranted verbs actually do.
